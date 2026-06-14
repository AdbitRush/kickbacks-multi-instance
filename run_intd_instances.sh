#!/usr/bin/env bash
# ---------------------------------------------------------------
# run_intd_instances.sh – start multiple isolated intd‑v2.js processes
# ---------------------------------------------------------------
# Usage: ./run_intd_instances.sh [NUMBER]
#   NUMBER – how many instances to start (default: 5)
# ---------------------------------------------------------------

NUM=${1:-5}
SCRIPT_DIR="/root/Kick_Ai/scripts"
INTD="intd-v2.js"

if [[ ! -f "$SCRIPT_DIR/$INTD" ]]; then
  echo "[!] Could not find $SCRIPT_DIR/$INTD – aborting"
  exit 1
fi

echo "Launching $NUM intd‑v2 instances..."
for i in $(seq 1 $NUM); do
  LOGFILE="/tmp/intd-${i}.log"
  echo "  • Instance $i → $LOGFILE"
  # Set INSTANCE_ID so that intd‑v2.js writes to its own log/ledger
  INSTANCE_ID=$i nohup node "$SCRIPT_DIR/$INTD" > "$LOGFILE" 2>&1 &
  # Small pause to avoid race‑condition when spawning many processes quickly
  sleep 0.5
done

echo "All instances launched. Use 'ps aux | grep intd‑v2' to verify, or tail the logs:";
for i in $(seq 1 $NUM); do echo "  tail -f /tmp/intd-${i}.log &"; done
