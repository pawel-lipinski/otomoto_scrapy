# Otomoto Car Data Scraper

A batch-based web scraper built with Python and Scrapy to collect car listing data from [Otomoto.pl](https://www.otomoto.pl).

This project uses a **three-tier architecture** designed for stability, resilience during long-running jobs, and ban avoidance.

## Project Structure

The system is divided into three distinct scripts:


1.  **`run_continuous_otomoto_v1.py` (Supervisor)**
    > The main entry point. It runs an infinite loop to ensure scraping continues even if a batch fails. It also manages delays between batches and monitors the exit codes of the Manager process.

2.  **`main_batch_v1.py` (Manager)**
    > Manages the state of the scraping job. It reads and writes the last scraped page to `checkpoint_otomoto.txt`, calculates the page range for the next batch, and launches the Scrapy spider. It also handles ban detection.

3.  **`otomoto_spider_batch_v1.py` (Worker)**
    > The Scrapy spider that performs the actual scraping. It extracts car details (Mileage, Price, model, brand etc.), fetches phone numbers via AJAX requests, and rotates user agents to avoid detection.

## How It Works

1.  The **Supervisor** script is executed.
2.  It calls the **Manager** script, which determines the range of pages to scrape (e.g., pages 1-100).
3.  The **Manager** then executes the **Worker** (Scrapy spider) to scrape the data for that page range.
4.  The scraped data is saved to a timestamped CSV file in the `batches_otomoto/` directory.
5.  The **Manager** updates the `checkpoint_otomoto.txt` file with the last successfully scraped page number.
6.  The process repeats, with the **Supervisor** adding a configurable delay between each batch.

---

## Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/your-username/otomoto-scraper.git
    cd otomoto-scraper
    ```

2.  **Set up a Virtual Environment** (Recommended)
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

---

## Configuration

All settings can be adjusted by editing the Python scripts.

#### In `main_batch_v1.py`:
*   `BATCH_SIZE = 100`: The number of pages to scrape in a single batch.
*   `TOTAL_PAGES_LIMIT = 8000`: The scraper will stop completely after this page number is reached.

#### In `run_continuous_otomoto_v1.py`:
*   `PAUSE_BETWEEN_BATCHES`: The time to wait (in minutes) between batches. This can be set via an environment variable or defaults to `0`.

---

## Usage

To start the scraper, run the **Supervisor** script from your terminal:
```bash
python run_continuous_otomoto_v1.py
