# NLP language complexity data cleaner

A data cleaner that removes unneccesary text, such as code blocks, unneccessary signs, ect.

### Installation

Before running, make sure you have a python ver 3 environment ready, and run (Windows)

> python -m pip install -r requirements.txt

or, alternatively, on Mac/Linux:

> python3 -m pip install -r requirements.txt

Download the scrapped data, or scrap it using the scrapper

(Pre-scraped data link: [Data Link](https://drive.google.com/uc?export=download&id=1BrTQHTMAvPC54rGmWMs0e_ATTgRD1NFz))

Place the scrapped csv file in the main catalog of the data cleaner (same place of this README)

Navigate to this folder in console and run

> python data_cleaner.py

> python3 data_cleaner.py

### Solution description

Program analyzes the csv file and extracts 4 output files (one for a given language) with cleaned data.
