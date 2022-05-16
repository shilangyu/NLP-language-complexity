import csv
import re
from multiprocessing import Pool
from os import mkdir
from os.path import exists
from typing import Optional, Any

import attr
import langdetect
import pandas as pd
from langdetect import DetectorFactory, LangDetectException
from mistletoe import Document
from mistletoe.block_token import BlockToken, CodeFence, List, Heading
from mistletoe.span_token import SpanToken, Image, Link
from tqdm import tqdm

# Make langdetect deterministic
DetectorFactory.seed = 0

"""
DEBUG mode uses a tiny csv file (tiny.csv) for the purposes of testing.
"""
DEBUG = False
"""
WARN mode prints the raw text message every time an error (missing ''') is found.
In addition, a bonus file is created that contains raw text message that caused the error.
"""
WARN = False

# File name of the scrapped dataset
REGULAR_FILE_NAME = "issues.csv"

# File name of the tiny dataset used in DEBUG mode
DEBUG_FILE_NAME = "tiny.csv"

# Directory where to store generated CSVs
OUTPUT_DIR = "output"

# These characters will be removed from the text
REMOVE_PATTERN = re.compile(r'('
                            r'#\w\S*|'  # hashtags
                            r'```.*|'  # partial code blocks
                            r'\w+://\S+'  # simple urls
                            r')')

# Whitespace replacement must be done AFTER REMOVE_PATTERN is complete
WHITESPACE_PATTERN = re.compile(r'\s+')

# Programming languages with this name are ignored. (For some reason entry 163k-ish has 'language' langauge)
IGNORE_PROGRAMMING_LANGUAGES = ["language"]

# CSV with caught errors will have this name (do not add .csv)
WARN_CSV_NAME = "warns"

# DEBUG and WARN decorative line separator
DEBUG_LINE = "======================"

ONLY_HUMAN_LANGUAGES = {'en'}

# ================= CODE STARTS HERE ====================================================
warnings = 0


@attr.s(slots=True, kw_only=True, auto_attribs=True)
class DataEntry:
    """This class stores processed entries and important data.
    Additionally, it contains a header used in all CSV generated files.
    """
    author: str
    programming_language: str
    human_language: str
    raw_text: str
    text: str
    text_warning: bool

    @staticmethod
    def csv_header() -> list[str]:
        return ["author", "text"]

    def csv_row(self) -> list[str]:
        return [self.author, self.text]


def process_markdown(token: SpanToken | BlockToken) -> str:
    # ignore some tokens
    if isinstance(token, (CodeFence, Heading, List, Image, Link)):
        return ''

    if hasattr(token, 'children'):
        return ' '.join(map(process_markdown, token.children))

    if hasattr(token, 'content'):
        return token.content

    return ''


def process_raw_text(raw_text: str) -> [str, bool]:
    global warnings

    text = process_markdown(Document(raw_text))

    # remove unwanted patterns
    text = re.sub(REMOVE_PATTERN, ' ', text)
    text = re.sub(WHITESPACE_PATTERN, ' ', text)

    text_warning = False

    return text.strip(), text_warning


def detect_human_language(text: str) -> Optional[str]:
    if not text:
        return None

    try:
        return langdetect.detect(text)
    except LangDetectException:
        return None


def process_entry(args: tuple[Any, dict]) -> Optional[DataEntry]:
    idx = args[0]
    row = args[1]

    author = row["author"]
    programming_language = row["language"]
    raw_text = row["raw_text"]

    if programming_language in IGNORE_PROGRAMMING_LANGUAGES:
        return None

    text, text_warning = process_raw_text(raw_text)

    # naive and quick english check (emojis break it!)
    if not text.isascii():
        return None

    human_language = detect_human_language(text)

    if human_language not in ONLY_HUMAN_LANGUAGES:
        return None

    return DataEntry(
        author=author,
        programming_language=programming_language,
        human_language=human_language,
        raw_text=raw_text,
        text=text,
        text_warning=text_warning
    )


def main():
    global warnings

    filename = DEBUG_FILE_NAME if DEBUG else REGULAR_FILE_NAME
    print(f"[INFO] Reading file {filename}...")
    data = pd.read_csv(filename, names=["author", "language", "raw_text"], header=0)
    data = data.fillna("")

    # This dictionary stores processed data
    data_dict: dict[str, list[DataEntry]] = {}

    if WARN:
        data_dict[WARN_CSV_NAME] = []

    # Process each entry and save it to the dict
    with Pool() as pool:
        for entry in tqdm(
                pool.imap_unordered(process_entry, data.iterrows(), chunksize=16),
                desc='[INFO] Processing data segment',
                total=len(data)):
            if not entry:
                continue

            assert isinstance(entry, DataEntry)

            if entry.programming_language in data_dict:
                data_dict[entry.programming_language].append(entry)
            else:
                data_dict[entry.programming_language] = [entry]

            if entry.text_warning:
                data_dict[WARN_CSV_NAME].append(entry)

    print(f"\n[INFO] Process finished with {warnings} warnings. Saving outputs to [{OUTPUT_DIR}] directory.")

    # Create output folder
    if not exists(OUTPUT_DIR):
        mkdir(OUTPUT_DIR)

    # Create all CSV files
    for key, vals in data_dict.items():
        with open(f"{OUTPUT_DIR}/{key}.csv", mode='w') as f:
            writer = csv.writer(f)
            writer.writerow(DataEntry.csv_header())

            for val in vals:
                writer.writerow(val.csv_row())

        print(f"[INFO] File [{key}.csv] created with ({len(vals)}) entries")


if __name__ == "__main__":
    main()
