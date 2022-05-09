from typing import Dict, List
from os import mkdir
from os.path import exists
from re import finditer
import pandas as pd

DEBUG = True

REGULAR_FILE_NAME = "issues.csv"
DEBUG_FILE_NAME   = "tiny.csv"
DELIMETER         = ","
OUTPUT_DIR        = "output"
DEBUG_LINE        = "======================"

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
        indexes = [(m.start(0), m.end(0)) for m in finditer("```", raw_text)]
        
        if not len(indexes) in [0,2]:
            raise ValueError(f"[```] was found more than once.\n{DEBUG_LINE}\n {raw_text} \n{DEBUG_LINE}")
            
        text = raw_text
        if not len(indexes) == 0:
            str1 = raw_text[:indexes[0][0]]
            str2 = raw_text[indexes[1][1]:]
            text = f"{str1} {str2}"
            
        return text

    filename = DEBUG_FILE_NAME if DEBUG else REGULAR_FILE_NAME
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
