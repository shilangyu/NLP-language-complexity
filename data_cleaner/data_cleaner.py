from typing import Dict, List
from os import mkdir
from os.path import exists
from re import finditer
import pandas as pd


"""
DEBUG mode uses a tiny csv file (tiny.csv) for the purposes of testing.
"""
DEBUG = False
"""
WARN mode prints the raw text message every time an error (missing ''') is found.
In addition, a bonus file is created that contains raw text message that caused the error.
"""
WARN  = False


REGULAR_FILE_NAME = "issues.csv"                ## File name of the scrapped dataset
DEBUG_FILE_NAME   = "tiny.csv"                  ## File name of the tiny dataset used in DEBUG mode
DELIMETER         = ","                         ## CSV delimeter symbol. It will also be used in the generated CSVs
OUTPUT_DIR        = "output"                    ## Directory where to store generated CSVs
REMOVE_CHARACTERS = ["\\n","\\t","\\r"]         ## These characteds will be removed from the text
REPLACE_RM_CHARS  = " "                         ## This symbol replaces the removed characters
IGNORE_LANGUAGES  = ["language"]                ## Programming languages with this name are ignored. (For some reason entry 163k-ish has 'language' langauge)
WARN_CSV_NAME     = "warns"                     ## CSV with caught errors will have this name (do not add .csv) 
DEBUG_LINE        = "======================"    ## DEBUG and WARN decorative line seaparator

# ================= CODE STARTS HERE ====================================================
warnings = 0

class DataEntry:
    """This class stores processed entries and important data.
    Additionaly, it contains a header used in all CSV generated files.
    """
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
        global warnings
        # Finds indexes of the ``` symbols in the text. Output format is a list of tuples - idx of the first and last ` - symbol
        indexes = [(m.start(0), m.end(0)) for m in finditer("```", raw_text)]
        w = False
        
        # If odd number of ``` symbols is found, print a warning and append additional index at the end
        if not len(indexes)%2 == 0:
            warnings += 1
            if WARN:
                print(f"[WARN][```] was found odd number of times.\n{DEBUG_LINE}\n {raw_text} \n{DEBUG_LINE}")
                w = True
            indexes.append((0,len(raw_text)-1))

        ## If warning is found, a deep copy instead of reference assignment occurs, to store original raw data
        if not w: 
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
            
        return text,w

    global warnings
    filename = DEBUG_FILE_NAME if DEBUG else REGULAR_FILE_NAME
    print(f"[INFO] Reading file {filename}...")
    data = pd.read_csv(filename, sep=DELIMETER, names = ["author","language","raw_text"], header=0)
    data = data.fillna("")

    # This dictionary stores processed data
    data_dict:Dict[str, List[DataEntry]] = {}
    if WARN:
        data_dict[WARN_CSV_NAME] = []
    
    l  = len(data)
    
    # Process each entry and save it to the dict
    for i, row in data.iterrows():
        print(f"\r[INFO] Processing data segment {i}\{l}...",end="")
        author   = row["author"]
        language = row["language"]
        raw_text = row["raw_text"]

        text,w = processText(raw_text)
        entry = DataEntry(author,text)

        if language in IGNORE_LANGUAGES:
            continue
            
        if language in data_dict.keys():
            data_dict[language].append(entry)
        else:
            data_dict[language] = [entry]
            
        if w:
            raw_entry = DataEntry(author,raw_text)
            data_dict[WARN_CSV_NAME].append(entry)

    print(f"\n[INFO] Process finished with {warnings} warnings. Saving outputs to [{OUTPUT_DIR}] directory.")

    # Create output folder
    if not exists(OUTPUT_DIR):
        mkdir(OUTPUT_DIR)

    # Create all CSV files
    for key, vals in data_dict.items():
        file = open(f"{OUTPUT_DIR}/{key}.csv",mode='w')
        file.write(DataEntry.header())
        for entry in vals:
            file.write(str(entry))
        file.close()
        print(f"[INFO] File [{key}.csv] succesfully created.")



if __name__ == "__main__":
    main()
