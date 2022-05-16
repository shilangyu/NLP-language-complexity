import csv
from typing import Dict, List
from os import mkdir
from os.path import exists
from re import finditer
import pandas as pd
from tqdm import tqdm

"""
DEBUG mode uses a tiny csv file (tiny.csv) for the purposes of testing.
"""
DEBUG = False
"""
WARN mode prints the raw text message every time an error (missing ''') is found.
In addition, a bonus file is created that contains raw text message that caused the error.
"""
WARN = False


REGULAR_FILE_NAME = "issues.csv.gz"             ## File name of the scrapped dataset
DEBUG_FILE_NAME   = "tiny.csv"                  ## File name of the tiny dataset used in DEBUG mode
DELIMETER         = ","                         ## CSV delimeter symbol. It will also be used in the generated CSVs
OUTPUT_DIR        = "output"                    ## Directory where to store generated CSVs
REMOVE_CHARACTERS = ["\\n", "\\t", "\\r"]       ## These characteds will be removed from the text
REPLACE_RM_CHARS  = " "                         ## This symbol replaces the removed characters
IGNORE_LANGUAGES  = ["language"]                ## Programming languages with this name are ignored. (For some reason entry 163k-ish has 'language' langauge)
WARN_CSV_NAME     = "warns"                     ## CSV with caught errors will have this name (do not add .csv)
DEBUG_LINE        = "======================"    ## DEBUG and WARN decorative line seaparator

# ================= CODE STARTS HERE ====================================================
warnings = 0


class DataEntry:
    """This class stores processed entries and important data.
    Additionally, it contains a header used in all CSV generated files.
    """
    author: str
    text: str

    def __init__(self, author: str, text: str):
        self.author = author
        self.text = text

    def csv_row(self) -> list[str]:
        return [self.author, self.text]

    @staticmethod
    def csv_header() -> list[str]:
        return ["author", "text"]


def process_text(raw_text: str) -> [str, bool]:
    global warnings

    # Finds indexes of the ``` symbols in the text. Output format is a list of tuples - idx of the first and last ` - symbol
    indexes = [(m.start(0), m.end(0)) for m in finditer("```", raw_text)]
    text_warning = False

    # If odd number of ``` symbols is found, print a warning and append additional index at the end
    if not len(indexes) % 2 == 0:
        warnings += 1

        if WARN:
            print(f"[WARN][```] was found odd number of times.\n{DEBUG_LINE}\n {raw_text} \n{DEBUG_LINE}")
            text_warning = True

        indexes.append((0, len(raw_text) - 1))

    # If warning is found, a deep copy instead of reference assignment occurs, to store original raw data
    if not text_warning:
        text = raw_text
    else:
        text = "%s" % raw_text

    offset = 0
    # Pairwise remove data between two ``` symbols
    for i in range(len(indexes)//2):
        idx1 = indexes[2*i][0] - offset
        idx2 = indexes[2*i+1][1] - offset
        offset += idx2 - idx1
        text = f"{text[:idx1]} {text[idx2:]}"

    # Remove unwanted characters.
    for symbol in REMOVE_CHARACTERS:
        text = text.replace(symbol, REPLACE_RM_CHARS)

    return text, text_warning


def main():
    global warnings

    filename = DEBUG_FILE_NAME if DEBUG else REGULAR_FILE_NAME
    print(f"[INFO] Reading file {filename}...")
    data = pd.read_csv(filename, sep=DELIMETER, names=["author", "language", "raw_text"], header=0)
    data = data.fillna("")

    # This dictionary stores processed data
    data_dict: Dict[str, List[DataEntry]] = {}

    if WARN:
        data_dict[WARN_CSV_NAME] = []

    # Process each entry and save it to the dict
    for i, row in tqdm(data.iterrows(), desc='[INFO] Processing data segment', total=len(data)):
        author = row["author"]
        language = row["language"]
        raw_text = row["raw_text"]

        text, text_warning = process_text(raw_text)
        entry = DataEntry(author, text)

        if language in IGNORE_LANGUAGES:
            continue

        if language in data_dict.keys():
            data_dict[language].append(entry)
        else:
            data_dict[language] = [entry]

        if text_warning:
            raw_entry = DataEntry(author, raw_text)
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

        print(f"[INFO] File [{key}.csv] successfully created.")


if __name__ == "__main__":
    main()
