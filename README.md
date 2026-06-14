# Kickbacks Multi‑Instance Setup

This directory contains everything you need to run multiple `intd‑v2.js` workers in parallel, monitor them, and generate cost/revenue reports.

## Contents

- `intd‑v2.js` – the worker script (reads `intd-config.json` and `model_config.json`).
- `intd-config.json` – timing configuration (think, coffee‑break, pause, long‑pause).
- `model_config.json` – default and paid model identifiers.
- `run_intd_instances.sh` – Bash helper to launch **N** instances simultaneously (default 5). Use `./run_intd_instances.sh 7` for 7 instances.
- `cost_report.py` – detailed per‑query report (timestamp, model, cost, token counts). Supports `--date YYYY‑MM‑DD` and `--csv path`.
- `current_cost_report.py` – quick snapshot of total queries, tokens, USD cost, estimated ad revenue and earnings.

## How to use

```bash
# Make scripts executable
chmod +x run_intd_instances.sh cost_report.py current_cost_report.py

# Launch 5 workers (default)
./run_intd_instances.sh 5

# Check that they are running
ps aux | grep '[i]ntd‑v2.js'

# View logs (example for worker 1)
 tail -f /tmp/intd-1.log

# Generate a detailed report for today
python3 cost_report.py --date $(date -u +%F) --csv daily_report.csv

# Get a quick snapshot
python3 current_cost_report.py
```

Feel free to modify `intd-config.json` or `model_config.json` to adjust timings or switch to paid models. When you are ready, you can push this directory to a GitHub repository of your choice.
