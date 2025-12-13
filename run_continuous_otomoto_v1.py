# run_continuous_otomoto.py
# Fixed to find main_batch_v1.py regardless of execution directory

import os
import time
import subprocess
from datetime import datetime
import sys

# === CONFIGURATION ===
PAUSE_BETWEEN_BATCHES = int(os.getenv('PAUSE_MINUTES', '0'))
MAX_BATCHES_PER_RUN = int(os.getenv('MAX_BATCHES', '8800'))

def run_single_batch():
    """Executes a single scraping batch"""
    print(f"{datetime.now().strftime('%H:%M:%S')} - Starting Otomoto batch...")
    
    # --- PATH FIX ---
    # Determine the folder where THIS script (run_continuous) is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to main_batch_v1.py
    manager_script = os.path.join(current_dir, 'main_batch_v1.py')

    # Verify file exists before running
    if not os.path.exists(manager_script):
        print(f"CRITICAL ERROR: Could not find {manager_script}")
        print("Make sure main_batch_v1.py is in the same folder as this script.")
        return False
    
    try:
        # Run using the absolute path
        result = subprocess.run([sys.executable, manager_script], 
                               text=True)
        
        if result.returncode == 0:
            print(" Batch completed successfully")
            return True
        
        # === CRITICAL FIX HERE ===
        # If we see code 99, it means the job is totally finished.
        elif result.returncode == 99:
            print(">>> ALL PAGES SCRAPED. Stopping continuous loop.")
            sys.exit(0) # Stop the whole script
            
        else:
            print(f" Batch finished with exit code: {result.returncode}")
            return False
            
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f" Execution error: {e}")
        return False

def main():
    """Main continuous scraping loop"""
    print("="*60)
    print(" OTOMOTO CONTINUOUS SCRAPER")
    print("="*60)
    
    batch_count = 0
    
    try:
        while batch_count < MAX_BATCHES_PER_RUN:
            
            # Run batch
            success = run_single_batch()
            batch_count += 1
            
            if not success:
                print("Batch error detected. Waiting 10 seconds before retry...")
                time.sleep(10)
            
            # Pause between batches logic
            if PAUSE_BETWEEN_BATCHES > 0:
                print(f" Pause {PAUSE_BETWEEN_BATCHES} minutes before next batch...")
                time.sleep(PAUSE_BETWEEN_BATCHES * 60)
                
    except KeyboardInterrupt:
        print("\n  Interrupted by user")

if __name__ == "__main__":
    main()