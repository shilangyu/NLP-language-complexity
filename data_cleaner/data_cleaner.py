from typing import Dict, List
from os import mkdir
from os.path import exists
import pandas as pd


DEBUG = True
DELIMETER = ","
OUTPUT_DIR = "output"

class DataEntry:
    author: str
    text: str

    def __init__(self, author:str, text:str):
        self.author = author
        self.text = text

    def __str__(self) -> str:
        return DELIMETER.join([self.author, self.text]) + "\n"
    
    @staticmethod
    def header() -> str:
        return DELIMETER.join(["author","text"]) + "\n"

def main():

    def processText(raw_text:str) -> str:
        return raw_text

    filename = "tiny.csv" if DEBUG else "issues.csv"
    data = pd.read_csv(filename, sep=DELIMETER, names = ["author","language","raw_text"], header=0)

    data_dict:Dict[str, List[DataEntry]] = {}

    for _, row in data.iterrows():
        author   = row["author"]
        language = row["language"]
        raw_text = row["raw_text"]

        text = processText(raw_text)
        entry = DataEntry(author,text)

        if language in data.keys():
            data_dict[language].append(entry)
        else:
            data_dict[language] = [entry]
    

    if not exists(OUTPUT_DIR):
        mkdir(OUTPUT_DIR)


    for key, vals in data_dict.items():
        file = open(f"{OUTPUT_DIR}/{key}.csv",mode='w')
        file.write(DataEntry.header())
        for entry in vals:
            file.write(str(entry))
        file.close()


if __name__ == "__main__":
    main()
