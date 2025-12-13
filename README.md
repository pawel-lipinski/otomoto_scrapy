\# Otomoto Car Data Scraper



A simple, batch-based web scraper built with Python and Scrapy to collect car listing data from \[Otomoto.pl](https://www.otomoto.pl).



This project uses a \*\*three-tier architecture\*\* designed for stability, long-running execution, and ban avoidance.



\## Project Structure



The system is divided into three distinct scripts:



1\.  \*\*`run\_continuous\_otomoto\_v1.py` (The Supervisor)\*\*

&nbsp;   \* \*\*Role:\*\* The entry point. It runs an infinite loop to ensure scraping continues even if a batch fails.

&nbsp;   \* \*\*Features:\*\* Handles delays between batches and monitors the exit codes of the manager.



2\.  \*\*`main\_batch\_v1.py` (The Manager)\*\*

&nbsp;   \* \*\*Role:\*\* Manages the state of the scraping job.

&nbsp;   \* \*\*Features:\*\*

&nbsp;       \* Reads/Writes `checkpoint\_otomoto.txt` to remember the last scraped page.

&nbsp;       \* Calculates the page range for the current batch (e.g., Page 100-200) based on `BATCH\_SIZE`.

&nbsp;       \* Generates unique filenames (timestamps) for CSV outputs in the `batches\_otomoto/` folder.

&nbsp;       \* Handles "Soft Bans" (empty pages) and "Hard Bans" (429 errors).



3\.  \*\*`otomoto\_spider\_batch\_v1.py` (The Worker)\*\*

&nbsp;   \* \*\*Role:\*\* The actual Scrapy spider.

&nbsp;   \* \*\*Features:\*\*

&nbsp;       \* Fetches car details (Mileage, Price, Engine, VIN, etc.).

&nbsp;       \* Extracts phone numbers via AJAX requests.

&nbsp;       \* Uses `scrapy-fake-useragent` to rotate headers.



---



\## Installation



1\.  \*\*Clone the repository\*\* (or extract the files to a folder).

2\.  \*\*Set up a Virtual Environment\*\* (Recommended):

&nbsp;   ```bash

&nbsp;   python -m venv venv

&nbsp;   # Windows:

&nbsp;   venv\\Scripts\\activate

&nbsp;   # Mac/Linux:

&nbsp;   source venv/bin/activate

&nbsp;   ```

3\.  \*\*Install Dependencies:\*\*

&nbsp;   ```bash

&nbsp;   pip install -r requirements.txt

&nbsp;   ```



---



\## Configuration



\### Adjusting Batch Settings

Open `main\_batch\_v1.py` to change the scraping behavior:



\* \*\*`BATCH\_SIZE = 100`\*\*: How many pages to scrape in one go before saving a file and restarting the process.

\* \*\*`TOTAL\_PAGES\_LIMIT = 8000`\*\*: The scraper will stop completely when this page number is reached.



\### Adjusting Speed/Delays

Open `run\_continuous\_otomoto\_v1.py`:

\* \*\*`PAUSE\_BETWEEN\_BATCHES`\*\*: Time to wait (in minutes) between batches (default is set via env var or defaults to 0).



---



\## Usage



To start the scraper, run the \*\*Supervisor\*\* script:



```bash

python run\_continuous\_otomoto\_v1.py

