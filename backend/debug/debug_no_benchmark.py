import pandas as pd
import re
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

fund_map_col = db["fund_benchmark_map"]

def canon(name):
    name = name.lower()
    for t in ["direct","regular","growth","plan","option","fund","idcw","dividend","mf"]:
        name = name.replace(t,"")
    name = re.sub(r"[^a-z0-9 ]+"," ",name)
    return " ".join(name.split())

df = pd.read_csv("skipped_score_business_cycle.csv")

print("\n---- CANONICAL KEYS YOU SHOULD OVERRIDE ----\n")

for _, r in df.iterrows():
    if r["reason"] == "NO_BENCHMARK":
        print(canon(r["scheme_name"]).replace(" ",""))
