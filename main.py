import argparse
import json
from pathlib import Path
from engine import XERReader, CPMEngine, CostEngine, CrashOptimizer
from engine.report import activities_dataframe, relationships_dataframe

def main():
    p = argparse.ArgumentParser()
    p.add_argument("xer", help="Path to Primavera P6 .XER")
    p.add_argument("--target-days", type=float, default=None)
    p.add_argument("--indirect-cost-per-day", type=float, default=0.0)
    p.add_argument("--crash-csv", default=None)
    args = p.parse_args()

    project = XERReader().read(args.xer)
    durations = {t["task_id"]: float(t.get("duration_hr") or 0) for t in project.tasks}
    cpm = CPMEngine().analyze(durations, project.relationships)

    print("\nPROJECT")
    print(project.project.get("proj_short_name") or project.project.get("proj_name"))
    print(f"Activities: {len(project.tasks)}")
    print(f"Relationships: {len(project.relationships)}")
    print(f"Project duration: {cpm.project_duration_hr/8:.2f} working days")
    print(f"Critical activities: {len(cpm.critical_activities)}")

    print("\nCRITICAL PATH(S)")
    for path in cpm.critical_paths[:20]:
        print(" -> ".join(path))

    if args.crash_csv:
        cost = CostEngine.from_csv(project, args.crash_csv).enrich_from_p6()
        target = args.target_days
        if target is None:
            target = cpm.project_duration_hr / 8 - 10
        opt = CrashOptimizer(
            durations,
            project.relationships,
            cost.crash_models,
            args.indirect_cost_per_day / 8
        ).run(target * 8)
        print("\nOPTIMIZATION")
        print(f"Initial: {opt.initial_duration_hr/8:.2f} days")
        print(f"Final:   {opt.final_duration_hr/8:.2f} days")
        print(f"Crash cost: {opt.final_direct_cost-opt.initial_direct_cost:,.2f}")
        print(f"Indirect saving: {opt.indirect_cost_saving:,.2f}")
        print(f"Net saving: {opt.net_saving:,.2f}")

if __name__ == "__main__":
    main()
