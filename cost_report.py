#!/usr/bin/env python3
"""Kickbacks Cost & Model Report – detailed per-query view.

The Kickbacks proxy writes a *ledger* file (ledger.jsonl) where each line is a JSON
object with the following (relevant) fields:
    {
        "ts": "2026-06-13T14:09:20.916313",
        "q": 1,
        "model_actual": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "model_claude": "claude-sonnet-4",
        "free": true,
        "input_tokens": 22,
        "output_tokens": 17,
        "thinking_ms": 4384,
        "cost_usd": 0.0
    }

The script provides:
  * A **total summary** – number of queries, total input/output tokens and total
    USD cost.
  * A **detailed table** (one line per query) showing timestamp, model used and
    cost (plus token counts).
  * A **per‑model breakdown** (queries, tokens, total cost, % of total cost).

Optional arguments:
  --date YYYY‑MM‑DD   Restrict the report to a single day (matches the `ts`
                       prefix).
  --csv PATH          Write the detailed per‑query table to a CSV file.

When you switch to a paid model the field ``cost_usd`` will contain the real
amount spent and the report will automatically reflect it – no code changes are
required.
"""
import json, os, sys, argparse
from collections import defaultdict

LEDGER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.jsonl')

if not os.path.exists(LEDGER_PATH):
    sys.stderr.write(f"[!] Ledger file not found at {LEDGER_PATH}\n")
    sys.exit(1)

parser = argparse.ArgumentParser(description='Kickbacks cost & model report')
parser.add_argument('--date', help='Filter entries by date (YYYY-MM-DD)')
parser.add_argument('--csv', help='Path to write detailed CSV output')
args = parser.parse_args()

entries = []
with open(LEDGER_PATH) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Apply date filter if requested
        if args.date and not obj.get('ts','').startswith(args.date):
            continue
        entries.append(obj)

if not entries:
    print('No entries match the given criteria.')
    sys.exit(0)

# ------- Global aggregates -------------------------------------------------
total_queries = len(entries)
total_input = sum(e.get('input_tokens', 0) for e in entries)
total_output = sum(e.get('output_tokens', 0) for e in entries)
total_cost = sum(e.get('cost_usd', 0.0) for e in entries)

# Helper formatters
def fmt_usd(v):
    return f"${v:.6f}" if abs(v) < 1 else f"${v:,.2f}"

def fmt_num(n):
    return f"{n:,}"

print('=== Kickbacks Cost & Model Report ===')
print(f'🔢 Queries processed : {fmt_num(total_queries)}')
print(f'📥 Input tokens      : {fmt_num(total_input)}')
print(f'📤 Output tokens     : {fmt_num(total_output)}')
print(f'💰 Total USD cost    : {fmt_usd(total_cost)}')
print()

# ------- Detailed per‑query table ----------------------------------------
header = ['#', 'timestamp', 'model_actual', 'cost_usd', 'input', 'output']
rows = []
for idx, e in enumerate(entries, start=1):
    rows.append([
        str(idx),
        e.get('ts',''),
        e.get('model_actual','unknown'),
        fmt_usd(e.get('cost_usd',0.0)),
        fmt_num(e.get('input_tokens',0)),
        fmt_num(e.get('output_tokens',0))
    ])

# Print table to stdout (aligned columns)
col_widths = [max(len(row[i]) for row in ([header] + rows)) for i in range(len(header))]
row_fmt = '  '.join('{:<%d}' % w for w in col_widths)
print(row_fmt.format(*header))
print('-' * (sum(col_widths) + 2 * (len(header)-1)))
for r in rows:
    print(row_fmt.format(*r))
print()

# If CSV requested, write it
if args.csv:
    try:
        import csv
        with open(args.csv, 'w', newline='') as cf:
            writer = csv.writer(cf)
            writer.writerow(header)
            for r in rows:
                writer.writerow(r)
        print(f'✅ Detailed CSV written to {args.csv}')
    except Exception as exc:
        sys.stderr.write(f'⚠️ Failed to write CSV: {exc}\n')

# ------- Per‑model breakdown --------------------------------------------
model_stats = defaultdict(lambda: {'q':0, 'in':0, 'out':0, 'cost':0.0})
for e in entries:
    model = e.get('model_actual', 'unknown')
    stats = model_stats[model]
    stats['q']   += 1
    stats['in']  += e.get('input_tokens', 0)
    stats['out'] += e.get('output_tokens', 0)
    stats['cost']+= e.get('cost_usd', 0.0)

print('🧾 Breakdown by model:')
for model, st in sorted(model_stats.items(), key=lambda kv: -kv[1]['cost']):
    pct = (st['cost'] / total_cost * 100) if total_cost else 0.0
    print(f'  {model:45s} – {fmt_num(st["q"])} q, {fmt_num(st["in"])}+{fmt_num(st["out"])} tok, {fmt_usd(st["cost"])} ({pct:.1f}%)')

print('\nNote: Free models report $0.0 cost. When you switch to a paid model the same script will show the real spend without any code changes.')
