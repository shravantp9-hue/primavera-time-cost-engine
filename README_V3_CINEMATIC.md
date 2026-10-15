# Primavera Time-Cost Engine — V3 REAL CINEMATIC UI

This version adds a **real browser-native cinematic animation layer**, not just CSS entrance effects.

## What actually animates

- Full-screen boot sequence: `INITIALIZING CPM CORE → PARSING TASK/TASKPRED → BUILDING NETWORK GRAPH → CALCULATING CRITICAL PATH`
- Animated Gantt/network bars using the actual CPM states from the optimizer
- Every accepted crash causes the affected activity bar to physically shrink/morph
- Critical activities glow red; the active crashed activity flashes lime
- Project finish counter updates after every crash
- Cumulative crash spend updates after every crash
- Critical path activity pills migrate after every CPM recalculation
- Moving vertical scan line shows the simulation progressing
- Live calculation console shows trial crash → CPM → project finish → path migration
- Final cinematic takeover shows baseline, final duration and time saved

The animation runs inside a browser component, so it is not dependent on Streamlit's text rerender speed.

## Run

```bash
cd C:\Users\ASUS\Desktop\primavera_time_cost_engine_v3_cinematic
.venv\Scripts\activate
streamlit run app.py
```

Upload:

- `CPWD_style_building_60_activity_demo.xer`
- `CPWD_DSR_crash_input_engine_compatible.csv`

Set a target duration below the baseline and press **START CINEMATIC CRASH SIMULATION**.

## Important

The CPWD-style dataset is an illustrative/research dataset, not an official CPWD-issued crashing dataset.

The calculation engine still uses the research-prototype assumptions documented in the main README, including 8-hour working-day normalization and a greedy cost-slope optimizer.
