
from __future__ import annotations

import time
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import json

from engine.xer_reader import XERReader
from engine.cpm import CPMEngine
from engine.cost import CostEngine
from engine.optimizer import CrashOptimizer


# -----------------------------
# PAGE
# -----------------------------
st.set_page_config(
    page_title="PRIMAVERA // TIME–COST LAB",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --bg: #07090c;
    --panel: rgba(18,22,28,.72);
    --panel2: rgba(25,30,38,.72);
    --line: rgba(255,255,255,.10);
    --muted: #8d96a3;
    --text: #f4f7fb;
    --accent: #d7ff42;
    --accent2: #7dd3fc;
    --danger: #ff6b6b;
}

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}
.stApp {
    background:
      radial-gradient(circle at 15% 0%, rgba(215,255,66,.08), transparent 28%),
      radial-gradient(circle at 85% 12%, rgba(125,211,252,.08), transparent 28%),
      linear-gradient(180deg, #06080b 0%, #0a0d11 45%, #06080b 100%);
    color: var(--text);
}
.block-container {
    max-width: 1500px;
    padding-top: 1.5rem;
    padding-bottom: 5rem;
}
section[data-testid="stSidebar"] {
    background: rgba(7,9,12,.92);
    border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] * { color: #eef2f6; }

.hero {
    position: relative;
    overflow: hidden;
    min-height: 390px;
    border: 1px solid var(--line);
    border-radius: 32px;
    padding: 52px 56px;
    background:
      linear-gradient(135deg, rgba(255,255,255,.055), rgba(255,255,255,.012)),
      radial-gradient(circle at 80% 40%, rgba(215,255,66,.11), transparent 30%);
    box-shadow: 0 30px 100px rgba(0,0,0,.34);
    animation: heroIn .9s ease both;
}
.hero:before {
    content: "";
    position: absolute;
    width: 520px; height: 520px;
    border-radius: 50%;
    border: 1px solid rgba(215,255,66,.12);
    right: -120px; top: -170px;
    animation: orbit 18s linear infinite;
}
.hero:after {
    content: "";
    position: absolute;
    width: 280px; height: 280px;
    border-radius: 50%;
    border: 1px solid rgba(125,211,252,.10);
    right: 70px; bottom: -160px;
    animation: orbit 12s linear infinite reverse;
}
.eyebrow {
    font-family: "DM Mono", monospace;
    color: var(--accent);
    letter-spacing: .18em;
    font-size: .78rem;
    text-transform: uppercase;
}
.hero h1 {
    font-size: clamp(3rem, 7vw, 7rem);
    line-height: .88;
    letter-spacing: -.065em;
    margin: 18px 0;
    font-weight: 900;
}
.hero p {
    color: #b8c0cb;
    max-width: 760px;
    font-size: 1.05rem;
    line-height: 1.7;
}
.hero-badge {
    display:inline-flex;
    gap:8px;
    align-items:center;
    padding:9px 13px;
    border:1px solid rgba(215,255,66,.28);
    border-radius:999px;
    color:#eaffb0;
    background:rgba(215,255,66,.06);
    font-family:"DM Mono",monospace;
    font-size:.75rem;
}

.section {
    margin: 38px 0 18px;
    animation: rise .65s ease both;
}
.section-title {
    font-size: 1.45rem;
    font-weight: 800;
    letter-spacing: -.03em;
}
.section-sub {
    color: var(--muted);
    margin-top: 4px;
}

.glass {
    border:1px solid var(--line);
    background:linear-gradient(145deg, rgba(255,255,255,.055), rgba(255,255,255,.018));
    border-radius:22px;
    padding:22px;
    box-shadow:0 16px 55px rgba(0,0,0,.22);
    animation: rise .7s ease both;
}
.metric {
    min-height: 150px;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
}
.metric .label {
    font-family:"DM Mono",monospace;
    font-size:.72rem;
    color:#909aa7;
    text-transform:uppercase;
    letter-spacing:.12em;
}
.metric .value {
    font-size:2.5rem;
    font-weight:900;
    letter-spacing:-.06em;
}
.metric .delta { color:var(--accent); font-family:"DM Mono",monospace; font-size:.78rem; }

.step-card {
    border:1px solid rgba(255,255,255,.10);
    border-radius:24px;
    padding:26px;
    background:rgba(15,19,24,.86);
    box-shadow:0 20px 80px rgba(0,0,0,.28);
    animation: pulseIn .55s ease both;
}
.step-no {
    width:42px;height:42px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    background:var(--accent);color:#0b0d0f;
    font-weight:900;
}
.formula {
    font-family:"DM Mono",monospace;
    padding:18px;
    margin:14px 0;
    border-radius:16px;
    background:#05070a;
    border:1px solid rgba(215,255,66,.18);
    color:#dcff7b;
    font-size:.9rem;
}
.console {
    font-family:"DM Mono",monospace;
    color:#b7c1cd;
    background:#05070a;
    border:1px solid rgba(255,255,255,.08);
    border-radius:18px;
    padding:18px;
    min-height:120px;
}
.kicker {
    color:#7f8a98;
    font-family:"DM Mono",monospace;
    font-size:.7rem;
    text-transform:uppercase;
    letter-spacing:.14em;
}
.path-pill {
    display:inline-block;
    padding:8px 11px;
    margin:4px;
    border-radius:999px;
    border:1px solid rgba(255,255,255,.09);
    background:rgba(255,255,255,.035);
    font-family:"DM Mono",monospace;
    font-size:.72rem;
}
.path-critical {
    border-color:rgba(255,107,107,.35);
    color:#ffb2b2;
    background:rgba(255,107,107,.07);
}
.divider {
    height:1px;
    background:linear-gradient(90deg, transparent, rgba(255,255,255,.14), transparent);
    margin:30px 0;
}
.stButton > button {
    border-radius:999px !important;
    border:1px solid rgba(215,255,66,.32) !important;
    background:rgba(215,255,66,.08) !important;
    color:#efffc4 !important;
    font-weight:800 !important;
    transition:all .25s ease !important;
}
.stButton > button:hover {
    transform:translateY(-2px) scale(1.01);
    background:rgba(215,255,66,.16) !important;
    box-shadow:0 12px 35px rgba(215,255,66,.10);
}
div[data-testid="stFileUploader"] {
    border:1px dashed rgba(255,255,255,.16);
    border-radius:20px;
    padding:10px;
    background:rgba(255,255,255,.02);
}
@keyframes heroIn { from {opacity:0; transform:translateY(18px) scale(.985)} to {opacity:1;transform:none} }
@keyframes rise { from {opacity:0; transform:translateY(20px)} to {opacity:1;transform:none} }
@keyframes pulseIn { from {opacity:0; transform:scale(.97)} to {opacity:1;transform:scale(1)} }
@keyframes orbit { from {transform:rotate(0deg)} to {transform:rotate(360deg)} }
</style>
""", unsafe_allow_html=True)


def money(x):
    return f"₹{x:,.0f}"

def days(x):
    return f"{x/8:,.2f} d"

def path_html(paths, limit=5):
    if not paths:
        return "<span class='path-pill'>No critical path detected</span>"
    out = []
    for i, p in enumerate(paths[:limit], 1):
        out.append(f"<span class='path-pill path-critical'>CP{i}: {p}</span>")
    return "".join(out)



def render_cinematic_engine(result, normal_cpm, project, cost_engine, speed):
    """Browser-native cinematic animation: animated Gantt, CPM scan, cost meters and path migration."""
    # Rebuild the schedule state after every accepted crash so the browser can animate real data.
    snapshots = []
    current_durations = {t["task_id"]: float(t.get("duration_hr") or 0.0) for t in project.tasks}
    cpm_engine_local = CPMEngine()

    def snapshot(label, step_no, crash_activity=None, step=None):
        c = cpm_engine_local.analyze(current_durations, project.relationships)
        rows = []
        for aid, a in c.activities.items():
            rows.append({
                "id": aid,
                "name": str(aid),
                "start": float(a.es_hr),
                "duration": float(a.duration_hr),
                "critical": bool(a.critical),
            })
        snapshots.append({
            "label": label,
            "step": step_no,
            "crash": crash_activity or "",
            "duration": float(c.project_duration_hr),
            "critical": list(c.critical_activities),
            "paths": list(c.critical_paths),
            "rows": rows,
            "cost": float(step.total_cost_after if step else result.initial_total_cost),
            "crash_cost": float(step.cumulative_crash_cost if step else 0.0),
        })

    snapshot("BASELINE", 0)
    for i, step in enumerate(result.steps, 1):
        m = cost_engine.crash_models.get(step.activity_id)
        if m and m.slope_per_hr > 0:
            delta_hr = step.incremental_cost / m.slope_per_hr
        else:
            delta_hr = 1.0
        current_durations[step.activity_id] = max(0.0, current_durations[step.activity_id] - delta_hr)
        snapshot("CRASH", i, step.activity_id, step)

    # Keep all activities, but order critical/crashed activities first for a strong visual hierarchy.
    base_rows = snapshots[0]["rows"] if snapshots else []
    crash_ids = [s["crash"] for s in snapshots if s["crash"]]
    base_critical = set(snapshots[0]["critical"] if snapshots else [])
    ordered = sorted(base_rows, key=lambda r: (r["id"] not in crash_ids, r["id"] not in base_critical, r["start"], r["id"]))
    # Limit visual rows on small screens while retaining every crashed/critical activity.
    keep = ordered[:34]
    keep_ids = {r["id"] for r in keep}
    for r in ordered:
        if r["id"] in crash_ids and r["id"] not in keep_ids:
            keep.append(r); keep_ids.add(r["id"])

    payload = {
        "snapshots": snapshots,
        "activities": keep,
        "normal_days": result.initial_duration_hr / 8,
        "final_days": result.final_duration_hr / 8,
        "target_days": result.target_duration_hr / 8,
        "normal_cost": result.initial_total_cost,
        "final_cost": result.final_total_cost,
        "crash_spend": result.crash_cost,
        "speed": float(speed),
    }
    data = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")

    html = f"""
<!doctype html><html><head><meta charset='utf-8'>
<style>
*{{box-sizing:border-box}} body{{margin:0;background:#050608;color:#f6f7f8;font-family:Inter,Arial,sans-serif;overflow:hidden}}
.engine{{height:860px;position:relative;overflow:hidden;border:1px solid #20252b;border-radius:28px;background:
 radial-gradient(circle at 70% 12%,rgba(215,255,66,.12),transparent 23%),
 radial-gradient(circle at 10% 90%,rgba(83,164,255,.10),transparent 28%),#07090c;box-shadow:0 30px 100px #000}}
.scan{{position:absolute;inset:0;pointer-events:none;background:linear-gradient(90deg,transparent,rgba(215,255,66,.035),transparent);transform:translateX(-100%);animation:scan 7s linear infinite}}
.noise{{position:absolute;inset:0;opacity:.04;pointer-events:none;background-image:radial-gradient(#fff .6px,transparent .6px);background-size:5px 5px}}
.boot{{position:absolute;inset:0;z-index:10;background:#050608;display:flex;align-items:center;justify-content:center;transition:opacity .9s ease,visibility .9s}}
.boot.hide{{opacity:0;visibility:hidden;pointer-events:none}}
.boot-inner{{width:min(760px,90%);font-family:monospace}}
.boot-logo{{font-size:clamp(44px,8vw,96px);font-weight:900;letter-spacing:-.08em;color:#d7ff42;line-height:.8}}
.boot-line{{height:2px;background:#1e242a;margin:28px 0;overflow:hidden}} .boot-line i{{display:block;width:0;height:100%;background:#d7ff42;animation:load 2.2s cubic-bezier(.7,0,.2,1) forwards}}
.boot-status{{display:flex;justify-content:space-between;color:#75808b;font-size:12px;letter-spacing:.15em;text-transform:uppercase}}
.top{{height:92px;padding:24px 28px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #171b20}}
.eyebrow{{font:11px monospace;letter-spacing:.18em;color:#7d8792;text-transform:uppercase}}
.title{{font-size:26px;font-weight:850;letter-spacing:-.04em;margin-top:5px}} .title b{{color:#d7ff42}}
.live{{display:flex;gap:9px;align-items:center;font:11px monospace;color:#d7ff42;letter-spacing:.12em}} .dot{{width:8px;height:8px;border-radius:50%;background:#d7ff42;box-shadow:0 0 18px #d7ff42;animation:blink .8s infinite}}
.body{{display:grid;grid-template-columns:1.7fr .85fr;height:calc(100% - 92px)}}
.gantt{{padding:20px 24px 24px;border-right:1px solid #171b20;min-width:0}}
.g-head{{display:flex;justify-content:space-between;align-items:end;margin-bottom:14px}} .g-head h3{{margin:0;font-size:15px}} .phase{{font:10px monospace;color:#6e7782;letter-spacing:.1em}}
.timeline{{position:relative;height:610px;border:1px solid #1b2026;border-radius:18px;background:#080a0d;overflow:hidden}}
.grid{{position:absolute;inset:0;display:grid;grid-template-columns:repeat(10,1fr);pointer-events:none}} .grid i{{border-left:1px solid rgba(255,255,255,.055)}}
.rows{{position:absolute;inset:32px 12px 12px 12px;display:flex;flex-direction:column;gap:5px;overflow:hidden}}
.row{{position:relative;height:16px;display:flex;align-items:center}} .rlabel{{width:78px;flex:0 0 78px;font:9px monospace;color:#77818c;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}} .track{{height:11px;flex:1;position:relative;background:rgba(255,255,255,.018);border-radius:6px}}
.bar{{position:absolute;height:100%;min-width:3px;border-radius:6px;background:#52606d;box-shadow:0 0 0 rgba(215,255,66,0);transition:left .9s cubic-bezier(.2,.8,.2,1),width .9s cubic-bezier(.2,.8,.2,1),background .35s,box-shadow .35s,transform .35s}}
.bar.critical{{background:#ff6363;box-shadow:0 0 14px rgba(255,99,99,.35)}} .bar.crashed{{background:#d7ff42;color:#111;box-shadow:0 0 25px rgba(215,255,66,.5);transform:scaleY(1.55)}} .bar.changed{{animation:hit .75s ease}}
.now{{position:absolute;top:0;bottom:0;width:1px;background:#d7ff42;box-shadow:0 0 18px #d7ff42;left:0;z-index:5}}
.axis{{position:absolute;top:8px;left:90px;right:12px;height:16px;display:flex;justify-content:space-between;color:#505963;font:9px monospace}}
.side{{padding:22px;display:flex;flex-direction:column;gap:12px;min-width:0}}
.card{{border:1px solid #1b2026;border-radius:18px;background:linear-gradient(145deg,rgba(255,255,255,.045),rgba(255,255,255,.012));padding:17px;position:relative;overflow:hidden}}
.card h4{{margin:0 0 12px;font-size:11px;font-family:monospace;letter-spacing:.13em;color:#818b96;text-transform:uppercase}}
.big{{font-size:42px;font-weight:900;letter-spacing:-.07em;line-height:1}} .lime{{color:#d7ff42}}
.counter{{font:14px monospace;color:#c4ccd4;margin-top:6px}}
.formula{{font:11px monospace;line-height:1.8;color:#a9b2bd}} .formula strong{{color:#d7ff42}}
.cp{{display:flex;flex-wrap:wrap;gap:5px;max-height:74px;overflow:hidden}} .pill{{font:9px monospace;padding:5px 7px;border-radius:999px;background:rgba(255,99,99,.08);border:1px solid rgba(255,99,99,.2);color:#ffaaa5}}
.crash-name{{font-size:24px;font-weight:900;letter-spacing:-.04em;color:#d7ff42}} .crash-sub{{font:10px monospace;color:#7d8792;margin-top:3px}}
.console{{height:100px;overflow:hidden;font:10px monospace;line-height:1.65;color:#89939e;background:#050608;border:1px solid #161a1f;border-radius:12px;padding:10px}}
.progress{{height:3px;background:#15191e;border-radius:99px;overflow:hidden;margin-top:10px}} .progress i{{display:block;height:100%;width:0;background:#d7ff42;box-shadow:0 0 12px #d7ff42;transition:width .8s}}
.final{{position:absolute;inset:0;z-index:20;background:rgba(5,6,8,.96);display:flex;align-items:center;justify-content:center;opacity:0;visibility:hidden;transition:opacity .7s,visibility .7s}} .final.show{{opacity:1;visibility:visible}}
.final-box{{width:min(900px,90%);text-align:center}} .final-tag{{font:11px monospace;letter-spacing:.2em;color:#d7ff42}} .final h2{{font-size:clamp(45px,7vw,92px);letter-spacing:-.08em;line-height:.85;margin:18px 0}} .final-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:28px}} .final-m{{padding:18px;border:1px solid #252b31;border-radius:16px;background:#0b0d10}} .final-m b{{display:block;font-size:28px;margin-bottom:5px}} .final-m span{{font:9px monospace;color:#737d88;letter-spacing:.1em}}
@keyframes load{{to{{width:100%}}}} @keyframes scan{{to{{transform:translateX(100%)}}}} @keyframes blink{{50%{{opacity:.25}}}} @keyframes hit{{0%{{filter:brightness(1)}}35%{{filter:brightness(2.4)}}100%{{filter:brightness(1)}}}} 
@media(max-width:900px){{.body{{grid-template-columns:1fr}}.side{{display:none}}.gantt{{border-right:0}}}}
</style></head><body>
<div class='engine'>
<div class='noise'></div><div class='scan'></div>
<div class='boot' id='boot'><div class='boot-inner'><div class='eyebrow'>PRIMAVERA // DECISION ENGINE</div><div class='boot-logo'>CRASH<br>THE SCHEDULE.</div><div class='boot-line'><i></i></div><div class='boot-status'><span id='bootStatus'>INITIALIZING CPM CORE</span><span>LIVE</span></div></div></div>
<div class='top'><div><div class='eyebrow'>CINEMATIC CPM / TIME–COST SIMULATION</div><div class='title'>SCHEDULE <b>ACCELERATION</b> LAB</div></div><div class='live'><span class='dot'></span><span id='liveText'>ENGINE READY</span></div></div>
<div class='body'>
<div class='gantt'><div class='g-head'><h3>LIVE NETWORK / GANTT MORPH</h3><div class='phase' id='phase'>BASELINE CPM</div></div>
<div class='timeline'><div class='grid'>""" + "".join("<i></i>" for _ in range(10)) + f"""</div><div class='axis' id='axis'></div><div class='now' id='now'></div><div class='rows' id='rows'></div></div></div>
<div class='side'>
<div class='card'><h4>PROJECT FINISH</h4><div class='big' id='days'>{payload['normal_days']:.2f}d</div><div class='counter' id='saved'>0.00d saved</div><div class='progress'><i id='prog'></i></div></div>
<div class='card'><h4>ACTIVE CRASH DECISION</h4><div class='crash-name' id='crash'>BASELINE</div><div class='crash-sub' id='crashSub'>No acceleration applied</div><div style='height:12px'></div><div class='formula' id='formula'>Cost Slope = (Crash Cost − Normal Cost) / (Normal Duration − Crash Duration)<br><strong>Waiting for optimizer…</strong></div></div>
<div class='card'><h4>CRITICAL PATH MIGRATION</h4><div class='cp' id='cp'></div></div>
<div class='card'><h4>COST ENGINE</h4><div class='big lime' id='cost'>₹0</div><div class='counter' id='costSub'>cumulative crash spend</div></div>
<div class='console' id='console'></div>
</div></div>
<div class='final' id='final'><div class='final-box'><div class='final-tag'>OPTIMIZATION COMPLETE</div><h2>TIME <span style='color:#d7ff42'>SAVED.</span></h2><div style='color:#8d96a3'>Critical path recalculated after every accepted crash.</div><div class='final-grid'><div class='final-m'><b id='fBefore'>—</b><span>BASELINE</span></div><div class='final-m'><b id='fAfter'>—</b><span>FINAL</span></div><div class='final-m'><b id='fSave'>—</b><span>TIME SAVED</span></div></div></div></div>
</div>
<script>
const D={data};
const snaps=D.snapshots; const activities=D.activities;
const rowsEl=document.getElementById('rows'); const maxDur=Math.max(...snaps.map(s=>s.duration),1);
const rowEls={{}};
activities.forEach(a=>{{const r=document.createElement('div');r.className='row';r.innerHTML=`<div class="rlabel">${{a.id}}</div><div class="track"><div class="bar" id="bar-${{a.id.replace(/[^a-zA-Z0-9_-]/g,'_')}}"></div></div>`;rowsEl.appendChild(r);rowEls[a.id]=r.querySelector('.bar')}});
const axis=document.getElementById('axis'); for(let i=0;i<=10;i++){{const s=document.createElement('span');s.textContent=(maxDur/8*i/10).toFixed(0)+'d';axis.appendChild(s)}}
const boot=document.getElementById('boot'); const status=document.getElementById('bootStatus');
setTimeout(()=>status.textContent='PARSING TASK / TASKPRED',650);setTimeout(()=>status.textContent='BUILDING NETWORK GRAPH',1250);setTimeout(()=>status.textContent='CALCULATING CRITICAL PATH',1850);setTimeout(()=>boot.classList.add('hide'),2450);
function money(x){{return '₹'+Math.round(x).toLocaleString('en-IN')}}
function render(s,idx){{
 const scale=maxDur; document.getElementById('phase').textContent=idx===0?'BASELINE CPM':`CRASH ITERATION ${{String(s.step).padStart(3,'0')}}`;
 document.getElementById('liveText').textContent=idx===0?'NETWORK LOCKED':`CRASHING ${{s.crash}}`;
 document.getElementById('days').textContent=(s.duration/8).toFixed(2)+'d';
 document.getElementById('saved').textContent=((snaps[0].duration-s.duration)/8).toFixed(2)+'d saved';
 document.getElementById('prog').style.width=(idx/(snaps.length-1||1)*100)+'%';
 document.getElementById('cost').textContent=money(s.crash_cost);
 const cp=document.getElementById('cp');cp.innerHTML='';(s.critical||[]).slice(0,8).forEach(x=>{{const p=document.createElement('span');p.className='pill';p.textContent=x;cp.appendChild(p)}});
 document.getElementById('crash').textContent=idx===0?'BASELINE':s.crash;
 document.getElementById('crashSub').textContent=idx===0?'No acceleration applied':'Critical activity selected by lowest feasible cost slope';
 if(idx>0){{const prev=snaps[idx-1];const before=prev.duration/8;const after=s.duration/8;const step=s.step;document.getElementById('formula').innerHTML=`Cost Slope → lowest feasible critical candidate<br><strong>${{s.crash}}</strong> : ${{before.toFixed(2)}}d → ${{after.toFixed(2)}}d<br>Incremental crash spend: <strong>${{money(s.cost-prev.cost)}}</strong>`}}
 document.getElementById('console').innerHTML=(idx===0?'$ boot_engine<br>$ parse_xer<br>$ run_cpm<br>$ status: BASELINE LOCKED':`$ trial_crash ${{s.crash}} -1h<br>$ rerun_cpm<br>$ project_finish → ${{(s.duration/8).toFixed(2)}}d<br>$ critical_path_migration → DETECTED<br>$ status: ACCEPTED`);
 const critical=new Set(s.critical||[]);
 s.rows.forEach(a=>{{const b=rowEls[a.id]; if(!b)return; const left=(a.start/scale*100); const width=(a.duration/scale*100); b.style.left=left+'%'; b.style.width=width+'%'; b.classList.toggle('critical',critical.has(a.id)); b.classList.toggle('crashed',a.id===s.crash); if(a.id===s.crash){{b.classList.remove('changed');void b.offsetWidth;b.classList.add('changed')}}}});
 document.getElementById('now').style.left=Math.min(100,idx/(snaps.length-1||1)*100)+'%';
}}
let idx=0; render(snaps[0],0);
const interval=Math.max(850,1300/(D.speed||.75));
function next(){{if(idx<snaps.length-1){{idx++;render(snaps[idx],idx)}}else{{clearInterval(timer);setTimeout(()=>{{document.getElementById('fBefore').textContent=D.normal_days.toFixed(2)+'d';document.getElementById('fAfter').textContent=D.final_days.toFixed(2)+'d';document.getElementById('fSave').textContent=(D.normal_days-D.final_days).toFixed(2)+'d';document.getElementById('final').classList.add('show')}},900)}}}}
const timer=setInterval(next,interval);
</script></body></html>"""
    components.html(html, height=900, scrolling=False)

def section(title, subtitle=""):
    st.markdown(
        f"<div class='section'><div class='section-title'>{title}</div>"
        f"<div class='section-sub'>{subtitle}</div></div>",
        unsafe_allow_html=True
    )

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<div class="hero">
  <div class="eyebrow">PRIMAVERA P6 × CPM × TIME–COST OPTIMIZATION</div>
  <h1>CRASH<br>THE SCHEDULE.</h1>
  <p>
    A cinematic decision-support interface that reads your Primavera XER,
    reconstructs the network, calculates CPM, tests crash candidates,
    re-runs the critical path after every move, and exposes the economics
    of accelerating a construction project.
  </p>
  <div class="hero-badge">◉ LIVE CALCULATION MODE</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.markdown("### CONTROL DECK")
xer_file = st.sidebar.file_uploader("01 / Primavera XER", type=["xer"])
csv_file = st.sidebar.file_uploader("02 / Crash cost model", type=["csv"])
indirect_day = st.sidebar.number_input(
    "Indirect cost / working day (₹)", min_value=0.0, value=80000.0, step=5000.0
)
target_days = st.sidebar.number_input(
    "Target project duration (days)", min_value=0.0, value=0.0, step=1.0
)
speed = st.sidebar.slider("Animation speed", 0.2, 2.0, 0.75, 0.05)
st.sidebar.caption("Tip: set target days to a value below the baseline to watch the optimizer work.")

if not xer_file:
    section("01 — Upload the schedule", "Drop the native Primavera XER first. The rest of the system activates after parsing.")
    st.info("Upload an XER and a crash CSV from the left control deck.")
    st.stop()

tmp_dir = Path(".runtime_uploads")
tmp_dir.mkdir(exist_ok=True)
xer_path = tmp_dir / xer_file.name
xer_path.write_bytes(xer_file.getbuffer())

try:
    project = XERReader().read(xer_path)
except Exception as e:
    st.error(f"XER parsing failed: {e}")
    st.stop()

section("02 — The schedule is now a network", "The XER is decoded into activities, relationships, calendars and resource records.")

cpm_engine = CPMEngine()
durations = {t["task_id"]: float(t.get("duration_hr") or 0.0) for t in project.tasks}
relationships = project.relationships

normal_cpm = cpm_engine.analyze(durations, relationships)

c1, c2, c3, c4 = st.columns(4)
for col, label, value, delta in [
    (c1, "ACTIVITIES", len(project.tasks), "parsed from TASK"),
    (c2, "RELATIONSHIPS", len(relationships), "TASKPRED edges"),
    (c3, "NORMAL DURATION", days(normal_cpm.project_duration_hr), "baseline CPM"),
    (c4, "CRITICAL ACTIVITIES", len(normal_cpm.critical_activities), "float ≈ 0"),
]:
    with col:
        st.markdown(
            f"<div class='glass metric'><div class='label'>{label}</div>"
            f"<div class='value'>{value}</div><div class='delta'>{delta}</div></div>",
            unsafe_allow_html=True
        )

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

section("03 — Baseline critical path", "This is the schedule before a single hour is crashed.")
st.markdown(
    f"<div class='glass'><div class='kicker'>NORMAL NETWORK</div>"
    f"<div style='margin-top:14px'>{path_html(normal_cpm.critical_paths)}</div></div>",
    unsafe_allow_html=True
)

if not csv_file:
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    section("04 — Load the crash model", "The crash CSV tells the optimizer what acceleration is physically/economically available.")
    st.info("Upload the matching crash CSV to unlock the animated crashing laboratory.")
    st.stop()

csv_path = tmp_dir / csv_file.name
csv_path.write_bytes(csv_file.getbuffer())

try:
    cost_engine = CostEngine.from_csv(project, csv_path).enrich_from_p6()
except Exception as e:
    st.error(f"Crash CSV parsing failed: {e}")
    st.stop()

section("04 — Cost slope laboratory", "Every candidate gets a measurable price for one unit of acceleration.")
slope_df = pd.DataFrame(cost_engine.slope_table())
if not slope_df.empty:
    slope_df["normal_duration_days"] = slope_df["normal_duration_hr"] / 8
    slope_df["crash_duration_days"] = slope_df["crash_duration_hr"] / 8
    slope_df["cost_slope_per_day"] = slope_df["cost_slope_per_8hr_day"]
    show_cols = [
        "activity_id", "normal_duration_days", "crash_duration_days",
        "normal_cost", "crash_cost", "cost_slope_per_day", "crashable"
    ]
    st.dataframe(slope_df[show_cols].sort_values(["crashable", "cost_slope_per_day"], ascending=[False, True]),
                 use_container_width=True, hide_index=True)

# Target default: make it a little below baseline so demo is useful.
if target_days <= 0:
    target_days_effective = max(1.0, normal_cpm.project_duration_hr / 8 - 10)
else:
    target_days_effective = target_days

section("05 — Choose the finish line", "The optimizer will stop once the target is reached, or when no feasible critical crash remains.")
a, b, c = st.columns(3)
a.metric("Baseline", f"{normal_cpm.project_duration_hr/8:.1f} days")
b.metric("Target", f"{target_days_effective:.1f} days")
c.metric("Acceleration required", f"{max(0, normal_cpm.project_duration_hr/8-target_days_effective):.1f} days")

run = st.button("▶  START CINEMATIC CRASH SIMULATION", use_container_width=True)

if run:
    target_hr = target_days_effective * 8
    optimizer = CrashOptimizer(
        durations,
        relationships,
        cost_engine.crash_models,
        indirect_cost_per_hr=indirect_day / 8.0
    )
    result = optimizer.run(target_hr)

    section("06 — Live crash simulation", "Each frame below is one optimizer decision: candidate → cost slope → trial CPM → accepted crash → new network.")

    stage = st.empty()
    progress = st.progress(0)
    total_steps = max(1, len(result.steps))

    # Opening sequence
    opening = [
        ("BOOT", "Reading Primavera network…", "XER → TASK → TASKPRED → CPM"),
        ("CPM", "Finding the normal critical path…", f"{normal_cpm.project_duration_hr/8:.2f} working days"),
        ("COST", "Loading acceleration economics…", f"{len(slope_df)} crash models"),
    ]
    for i, (tag, title, detail) in enumerate(opening):
        stage.markdown(
            f"""<div class='step-card'>
              <div style='display:flex;gap:16px;align-items:center'>
                <div class='step-no'>{i+1}</div>
                <div><div class='kicker'>{tag}</div><h2 style='margin:4px 0'>{title}</h2>
                <div style='color:#9ba5b2'>{detail}</div></div>
              </div>
            </div>""", unsafe_allow_html=True)
        time.sleep(0.55 / speed)

    # Animate actual optimizer steps
    if result.steps:
        for idx, step in enumerate(result.steps):
            before_d = step.project_duration_hr / 8
            after_d = step.after_duration_hr / 8
            reduction_d = step.reduction_hr / 8
            slope = step.incremental_cost / max(step.reduction_hr, 1e-9)

            before_paths = " | ".join(step.critical_paths_before[:2]) or "—"
            after_paths = " | ".join(step.critical_paths_after[:2]) or "—"

            html = f"""
            <div class='step-card'>
              <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:20px'>
                <div>
                  <div class='kicker'>OPTIMIZER ITERATION {step.iteration:03d}</div>
                  <h2 style='margin:6px 0 2px'>Crash <span style='color:#d7ff42'>{step.activity_id}</span></h2>
                  <div style='color:#9ba5b2'>Lowest-slope feasible critical activity</div>
                </div>
                <div class='step-no'>{idx+1}</div>
              </div>

              <div class='formula'>
                Cost Slope = (Crash Cost − Normal Cost) / (Normal Duration − Crash Duration)
                <br><br>
                Trial decision → <b>{money(step.incremental_cost)}</b> for
                <b>{reduction_d:.2f} day</b> project reduction
                <br>
                Effective slope ≈ <b>{money(slope)} / day saved</b>
              </div>

              <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px'>
                <div class='glass'>
                  <div class='kicker'>BEFORE</div>
                  <div style='font-size:2rem;font-weight:900'>{before_d:.2f} d</div>
                  <div style='color:#8d96a3'>Total cost {money(step.total_cost_before)}</div>
                </div>
                <div class='glass'>
                  <div class='kicker'>AFTER</div>
                  <div style='font-size:2rem;font-weight:900;color:#d7ff42'>{after_d:.2f} d</div>
                  <div style='color:#8d96a3'>Total cost {money(step.total_cost_after)}</div>
                </div>
                <div class='glass'>
                  <div class='kicker'>MOVE</div>
                  <div style='font-size:2rem;font-weight:900'>{reduction_d:.2f} d</div>
                  <div style='color:#8d96a3'>Crash spend {money(step.incremental_cost)}</div>
                </div>
              </div>

              <div style='margin-top:18px'>
                <div class='kicker'>CRITICAL PATH — BEFORE</div>
                <div style='margin:8px 0'>{before_paths}</div>
                <div class='kicker'>CRITICAL PATH — AFTER</div>
                <div style='margin:8px 0;color:#d7ff42'>{after_paths}</div>
              </div>

              <div class='console'>
                $ trial_crash {step.activity_id} -1h<br>
                $ rerun_cpm<br>
                $ project_finish: {before_d:.2f}d → {after_d:.2f}d<br>
                $ critical_path_changed: {step.critical_path_changed}<br>
                $ status: ACCEPTED
              </div>
            </div>
            """
            stage.markdown(html, unsafe_allow_html=True)
            progress.progress((idx + 1) / total_steps)
            time.sleep(0.16 / speed)

    else:
        stage.markdown(
            "<div class='step-card'><h2>No feasible crash sequence</h2>"
            "<div style='color:#9ba5b2'>The target is already met or no critical crash candidate can reduce project finish.</div></div>",
            unsafe_allow_html=True
        )

    # REAL BROWSER CINEMATIC ENGINE
    section("07 — Cinematic schedule morph", "This is a browser-native animation: the Gantt bars physically shrink, critical activities glow, the finish counter moves, and the critical path migrates after every accepted crash.")
    render_cinematic_engine(result, normal_cpm, project, cost_engine, speed)

    # FINAL RESULT
    time.sleep(0.4)
    section("07 — The new schedule", "The final CPM is calculated again after all accepted crashes.")
    before_days = result.initial_duration_hr / 8
    after_days = result.final_duration_hr / 8
    saved_days = before_days - after_days

    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        (m1, "BEFORE", f"{before_days:.2f} d", "normal schedule"),
        (m2, "AFTER", f"{after_days:.2f} d", "crashed schedule"),
        (m3, "TIME SAVED", f"{saved_days:.2f} d", "schedule acceleration"),
        (m4, "CRASH SPEND", money(result.crash_cost), "additional direct cost"),
    ]
    for col, label, value, sub in metrics:
        with col:
            st.markdown(
                f"<div class='glass metric'><div class='label'>{label}</div>"
                f"<div class='value'>{value}</div><div class='delta'>{sub}</div></div>",
                unsafe_allow_html=True
            )

    section("08 — Critical path migration", "The most important visual proof: what was critical before, and what is critical now.")
    left, right = st.columns(2)
    with left:
        st.markdown(
            f"<div class='glass'><div class='kicker'>BEFORE CRASHING</div>"
            f"<div style='margin-top:14px'>{path_html(normal_cpm.critical_paths)}</div></div>",
            unsafe_allow_html=True
        )
    with right:
        st.markdown(
            f"<div class='glass'><div class='kicker'>AFTER CRASHING</div>"
            f"<div style='margin-top:14px'>{path_html(result.final_cpm.critical_paths)}</div></div>",
            unsafe_allow_html=True
        )

    section("09 — Time–cost trade-off", "Crash cost rises as the schedule accelerates. Indirect cost falls as the project gets shorter.")
    if result.steps:
        curve = pd.DataFrame([{
            "iteration": 0,
            "duration_days": result.initial_duration_hr/8,
            "direct_cost": result.initial_direct_cost,
            "indirect_cost": result.initial_indirect_cost,
            "total_cost": result.initial_total_cost,
        }] + [{
            "iteration": s.iteration,
            "duration_days": s.after_duration_hr/8,
            "direct_cost": s.direct_cost_after,
            "indirect_cost": s.indirect_cost_after,
            "total_cost": s.total_cost_after,
        } for s in result.steps])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=curve.duration_days, y=curve.total_cost,
            mode="lines+markers", name="Total Project Cost",
            line=dict(width=4)
        ))
        fig.add_trace(go.Scatter(
            x=[before_days, after_days],
            y=[result.initial_total_cost, result.final_total_cost],
            mode="markers", name="Before / After",
            marker=dict(size=13)
        ))
        fig.update_layout(
            template="plotly_dark",
            height=480,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Project Duration (working days)",
            yaxis_title="Total Cost (₹)",
            margin=dict(l=20,r=20,t=30,b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        step_df = pd.DataFrame([{
            "Step": s.iteration,
            "Activity": s.activity_id,
            "Before (days)": s.project_duration_hr/8,
            "After (days)": s.after_duration_hr/8,
            "Time saved (days)": s.reduction_hr/8,
            "Crash cost": s.incremental_cost,
            "Cumulative crash cost": s.cumulative_crash_cost,
            "Critical path changed": s.critical_path_changed,
        } for s in result.steps])
        st.dataframe(step_df, use_container_width=True, hide_index=True)

    section("10 — Cost verdict", "This is the economic decision, not just the fastest schedule.")
    x1, x2, x3, x4 = st.columns(4)
    verdicts = [
        (x1, "DIRECT COST", money(result.final_direct_cost), f"+{money(result.crash_cost)} crash spend"),
        (x2, "INDIRECT SAVING", money(result.indirect_cost_saving), "from shorter duration"),
        (x3, "NET SAVING", money(result.net_saving), "positive = economically better"),
        (x4, "FINAL CRITICAL ACTIVITIES", str(len(result.final_cpm.critical_activities)), "after optimization"),
    ]
    for col, label, value, sub in verdicts:
        with col:
            st.markdown(
                f"<div class='glass metric'><div class='label'>{label}</div>"
                f"<div class='value'>{value}</div><div class='delta'>{sub}</div></div>",
                unsafe_allow_html=True
            )

    if result.net_saving > 0:
        st.success("OPTIMUM DIRECTION: the accelerated schedule is economically better under the supplied indirect-cost assumption.")
    elif result.net_saving < 0:
        st.warning("ECONOMIC SIGNAL: the time saving costs more than the indirect cost recovered under the supplied assumption.")
    else:
        st.info("ECONOMIC SIGNAL: crashing is cost-neutral under the supplied assumption.")

    section("11 — Final CPM", "Every activity is recalculated after crashing.")
    final_rows = []
    for aid, a in result.final_cpm.activities.items():
        final_rows.append({
            "Activity": aid,
            "Duration (days)": a.duration_hr/8,
            "ES (days)": a.es_hr/8,
            "EF (days)": a.ef_hr/8,
            "LS (days)": a.ls_hr/8,
            "LF (days)": a.lf_hr/8,
            "Float (days)": a.total_float_hr/8,
            "Critical": a.critical,
        })
    st.dataframe(pd.DataFrame(final_rows), use_container_width=True, hide_index=True)

    st.caption("Research prototype note: durations are currently normalized to an 8-hour working day. Full P6 calendar exceptions, resource leveling and exact MILP optimization are future production upgrades.")
else:
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='glass'><div class='kicker'>READY</div>"
        "<h2 style='margin:8px 0'>The network is loaded.</h2>"
        "<div style='color:#9ba5b2'>Press START CINEMATIC CRASH SIMULATION to watch the optimizer make each decision.</div></div>",
        unsafe_allow_html=True
    )
