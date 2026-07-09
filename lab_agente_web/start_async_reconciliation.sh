#!/bin/bash
# Start script for Async Reconciliation Architecture V2

# Navigate to the lab_agente_web directory
cd /home/teco/work_out/lab_agente_web

# Activate virtual environment if needed
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run the Async Reconciliation V2
python3 async_reconciliation_v2.py

# Check exit status
exit_status=$?
if [ $exit_status -eq 0 ]; then
    echo "Async Reconciliation V2 completed successfully"
else
    echo "Async Reconciliation V2 failed with exit status $exit_status"
fi