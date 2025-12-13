import os
import time
import subprocess
import sys
import random
from datetime import datetime

# === CONFIGURATION ===
BATCH_SIZE = 100                 
TOTAL_PAGES_LIMIT = 8000        
CHECKPOINT_FILE = 'checkpoint_otomoto.txt' 
BATCH_FOLDER_NAME = 'batches_otomoto'

# --- PATH FIX: Force folder to be next to this script ---
# Get the directory where main_batch_v1.py is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Create the full path for the checkpoint and batch folder
CHECKPOINT_PATH = os.path.join(SCRIPT_DIR, CHECKPOINT_FILE)
BATCH_FOLDER_PATH = os.path.join(SCRIPT_DIR, BATCH_FOLDER_NAME)

# Create batch folder if not exists
os.makedirs(BATCH_FOLDER_PATH, exist_ok=True)

def load_checkpoint():
    """Reads the last starting page from a file."""
    if os.path.exists(CHECKPOINT_PATH):
        try:
            with open(CHECKPOINT_PATH, 'r') as f:
                val = int(f.read().strip())
                return val if val > 0 else 1
        except:
            return 1
    return 1

def save_checkpoint(page_num):
    """Saves the next starting page to a file."""
    with open(CHECKPOINT_PATH, 'w') as f:
        f.write(str(page_num))

def run_manager():
    print("="*60)
    print(" OTOMOTO SMART MANAGER (SINGLE BATCH)")
    print(" Features:")
    print(" 1. Auto-Resume from Checkpoint")
    print(" 2. Individual Batch Files")
    print(" 3. Ban Protection")
    print("="*60)

    # --- PATH FIX for Worker Script ---
    spider_script = os.path.join(SCRIPT_DIR, 'otomoto_spider_batch_v1.py')

    if not os.path.exists(spider_script):
        print(f"CRITICAL ERROR: Cannot find worker script at: {spider_script}")
        return

    # 1. Load checkpoint
    start_page = load_checkpoint()
    
    # === CRITICAL FIX HERE ===
    # If we are past the limit, exit with code 99 (Signal for "Totally Done")
    if start_page > TOTAL_PAGES_LIMIT:
        print(f">>> Limit reached ({TOTAL_PAGES_LIMIT} pages). Job finished.")
        sys.exit(99)  # <--- CHANGED FROM 0 TO 99

    end_page = start_page + BATCH_SIZE - 1
    if end_page > TOTAL_PAGES_LIMIT: 
        end_page = TOTAL_PAGES_LIMIT

    # 2. Prepare Unique Filename (Using absolute path)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(BATCH_FOLDER_PATH, f"otomoto_{start_page}_{end_page}_{timestamp}.csv")

    print(f"\n>>> [MANAGER] Starting Batch: Pages {start_page} - {end_page}")
    print(f">>> Saving to: {output_file}")

    try:
        # 3. Run the Spider
        subprocess.check_call([sys.executable, spider_script, str(start_page), str(end_page), output_file])
        
        # --- SUCCESS (Exit Code 0) ---
        print(f">>> [SUCCESS] Batch {start_page}-{end_page} completed.")
        
        # Save checkpoint for the NEXT run
        save_checkpoint(end_page + 1)
        
    except subprocess.CalledProcessError as e:
        # --- ERROR HANDLING ---
        
        if e.returncode == 429:
            # HARD BAN (429)
            print(f"\n!!! [429 ERROR DETECTED] !!!")
            print(f"Server says: Too Many Requests.")
            print(f"Holding execution for 2 minutes before exiting...")
            time.sleep(120) 
            sys.exit(429)
        
        elif e.returncode == 5:
            # SOFT BAN (Empty Pages)
            wait_time = random.randint(120, 240)
            print(f"\n!!! [SOFT BAN DETECTED] !!!")
            print(f"Spider found 0 items. Cooling down for {wait_time} seconds...")
            time.sleep(wait_time)
            sys.exit(5)
        
        else:
            # UNKNOWN ERROR
            print(f">>> [ERROR] Script crashed with code {e.returncode}.")
            sys.exit(e.returncode)
    
    except KeyboardInterrupt:
        print("\n>>> Interrupted by user.")
        sys.exit(1)

if __name__ == "__main__":
    run_manager()