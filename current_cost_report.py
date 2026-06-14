#!/usr/bin/env python3
"""Quick current cost & revenue snapshot for Kickbacks.

Usage:
    python3 /root/kickbacks-proxy/current_cost_report.py

The script reads the ledger (ledger.jsonl) and prints:
  • Total number of queries
  • Total input / output tokens
  • Total USD cost (sum of the `cost_usd` field)
  • Estimated revenue based on CPM $0.20 (every 5 s of thinking = 1 impression)
  • Your 50 % earnings split
  • Per‑model breakdown (queries, tokens, cost, % of total cost)

If you later switch to a paid model the `cost_usd` field will be filled by the
proxy and the numbers will reflect the real spend automatically.
"""
import json, os, sys
from collections import defaultdict

LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.jsonl')
if not os.path.exists(LEDGER):
    sys.stderr.write(f"[!] Ledger not found at {LEDGER}\n")
    sys.exit(1)

entries = []
with open(LEDGER) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue

if not entries:
    print('No entries in ledger.')
    sys.exit(0)

# Global aggregates
total_q   = len(entries)
total_in  = sum(e.get('input_tokens', 0) for e in entries)
total_out = sum(e.get('output_tokens', 0) for e in entries)
total_cost = sum(e.get('cost_usd', 0.0) for e in entries)
total_think_ms = sum(e.get('thinking_ms', 0) for e in entries)

# Revenue assumptions – CPM $0.20, 5 s per impression, 50 % split
CPM_USD = 0.20
impressions = total_think_ms / 5000.0
revenue_usd = impressions * (CPM_USD / 1000.0)
earnings_usd = revenue_usd * 0.5

def fmt_usd(v):
    return f"${v:.6f}" if abs(v) < 1 else f"${v:,.2f}"

def fmt_num(n):
    return f"{n:,}"

print('=== Kickbacks – Current Cost & Revenue Snapshot ===')
print(f'🔢 Queries processed : {fmt_num(total_q)}')
print(f'📥 Input tokens      : {fmt_num(total_in)}')
print(f'📤 Output tokens     : {fmt_num(total_out)}')
print(f'💰 Total USD cost    : {fmt_usd(total_cost)}')
print(f'💸 Estimated revenue : {fmt_usd(revenue_usd)}')
print(f'💰 ½‑split earnings  : {fmt_usd(earnings_usd)}')
print()

# Per‑model breakdown
model_stats = defaultdict(lambda: {'q':0,'in':0,'out':0,'cost':0.0})
for e in entries:
    model = e.get('model_actual', 'unknown')
    st = model_stats[model]
    st['q']   += 1
    st['in']  += e.get('input_tokens', 0)
    st['out'] += e.get('output_tokens', 0)
    st['cost']+= e.get('cost_usd', 0.0)

print('🧾 Breakdown by model:')
for model, st in sorted(model_stats.items(), key=lambda kv: -kv[1]['cost']):
    pct = (st['cost'] / total_cost * 100) if total_cost else 0.0
    print(f'  {model:45s} – {fmt_num(st["q"])} q, {fmt_num(st["in"])}+{fmt_num(st["out"])} tok, {fmt_usd(st["cost"])} ({pct:.1f}%)')

print('\nNote: Free models report $0.0 cost. When you switch to a paid model the same script will\nshow the real spend automatically.')
