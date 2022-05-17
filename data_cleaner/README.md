# NLP language complexity data cleaner

A data cleaner that removes unnecessary text, such as code blocks, unnecessary signs, ect.

### Installation

Before running, make sure you have (Pipenv)[https://pipenv.pypa.io/en/latest/] installed, then install dependencies with

```sh
pipenv install
```

Download the scrapped data, or scrap it using the scrapper

(Pre-scraped data link: [Data Link](https://drive.google.com/uc?export=download&id=1BrTQHTMAvPC54rGmWMs0e_ATTgRD1NFz))

Place the scrapped csv file in the main catalog of the data cleaner (same place of this README)

Navigate to this folder in console and execute the script:

```sh
pipenv run python data_cleaner.py
```

### Solution description

Program analyzes the csv file and extracts 4 output files (one for a given language) with cleaned data.

`tiny.csv` is used for debug, it contains a small data sample from the original file.

#### Text processing procedure:

1. Parse markdown and strip selected tokens *(CodeFence, Heading, List, Image, Link)*.
2. Use regex to remove additional raw text patterns *(hashtags, partial code blocks, urls)*.
3. Remove unnecessary whitespace *(new line, double space, leading, trailing)*.
4. Drop entry if contains non-ASCII characters.
5. Drop entry if `langdetect` determines it to be non-english.
