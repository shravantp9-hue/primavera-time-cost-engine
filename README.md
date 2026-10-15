# Primavera P6 XER Time–Cost Optimization Engine

A Python engine for:

XER -> project database -> CPM/network -> cost database -> cost slope ->
time–cost trade-off -> project crashing -> resource utilization -> dashboard.

## Important engineering limitation

A normal Primavera XER export contains schedule, relationship, calendar and
resource/cost information, but it does NOT inherently contain a "crash cost"
and "crash duration" for every activity. Therefore the engine separates:

1. P6 baseline data:
   - planned duration
   - planned cost
   - resources
   - relationships
   - calendars

2. Crash model:
   - normal duration/cost
   - crash duration/cost
   - indirect cost/day
   - optional mandatory/forbidden crash limits

You can supply the crash model in `data/crash_plan.csv`.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

CLI:

```bash
python main.py "C:/path/project.xer"
```

Run tests:

```bash
pytest -q
```

## Crash-plan CSV

Columns:

activity_id,normal_duration_hr,crash_duration_hr,normal_cost,crash_cost,crashable

If omitted for an activity, the engine uses the P6 planned duration and
planned resource cost as the normal values and treats it as non-crashable.

Example:

```csv
activity_id,normal_duration_hr,crash_duration_hr,normal_cost,crash_cost,crashable
A100,40,32,80000,92000,1
A110,80,64,150000,180000,1
A120,24,24,40000,40000,0
```

## Architecture

PRIMAVERA P6 (.XER)
        |
        v
XER FILE READER
        |
        v
PROJECT DATABASE
        |
        +------------------+
        v                  v
CPM / NETWORK        COST DATABASE
        |                  |
        +--------+---------+
                 v
        TIME-COST ANALYSIS
                 |
                 v
        COST SLOPE ENGINE
                 |
                 v
        CRASHING ENGINE
                 |
                 v
        OPTIMIZATION ENGINE
                 |
                 v
        OPTIMAL PROJECT PLAN
                 |
                 v
             DASHBOARD

## Optimization modes

### Greedy cost-slope crashing
At every iteration:
1. Calculate CPM.
2. Find critical activities.
3. Find feasible crash candidates.
4. Choose the lowest incremental cost/day candidate.
5. Crash by the smallest useful amount.
6. Recalculate CPM.
7. Repeat.

The engine checks multiple critical paths. A candidate is only accepted if
the selected reduction actually reduces the project finish.

### Exact linear programming mode
The engine can formulate a continuous time-cost model using activity start
times and durations:

minimize:
    sum(crash_cost_slope_i * x_i) + indirect_cost_per_hour * project_finish

subject to relationship constraints and:
    0 <= x_i <= max_crash_i

This is an LP relaxation. For integer-day crashing, use the greedy method or
extend the model to MILP.

## XER compatibility

The reader uses the native `%T`, `%F`, `%R` record structure and retains
unknown tables rather than silently discarding them. The normalized engine
focuses on PROJECT, PROJWBS, TASK, TASKPRED, CALENDAR, RSRC and TASKRSRC.

Oracle's XER map identifies TASK as the activity table, TASKPRED as the
relationship table, CALENDAR as the calendar table, and TASKRSRC as resource
assignments. See:
https://docs.oracle.com/cd/G48897_01/English/Mapping_and_Schema/xer_import_export_data_map_project/97906.htm
https://docs.oracle.com/cd/F74773_01/English/Mapping_and_Schema/xer_import_export_data_map_project/97914.htm
https://docs.oracle.com/cd/F88966_01/English/Mapping_and_Schema/xer_import_export_data_map_project/97869.htm
https://docs.oracle.com/cd/F25599_01/English/Mapping_and_Schema/xer_import_export_data_map_project/97916.htm
