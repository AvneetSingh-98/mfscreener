import pandas as pd
import re
from datetime import datetime
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

fund_master = db["fund_master"]
fund_master_v2 = db["fund_master_v2"]

CATEGORY_SCORE_COLLECTION = {
    "Banking & Financial Services": "score_banking_financial_services",
    "Healthcare": "score_healthcare",
    "Infrastructure": "score_infrastructure",
    "Consumption": "score_consumption",
    "Business Cycle": "score_business_cycle",
    "ESG": "score_esg",
    "Technology": "score_technology",
    "Quant": "score_quant_multifactor"
}

print("Loading fund key master...")
factsheet = pd.read_excel("Factsheet_Fund_Key.xlsx")

factsheet = factsheet.dropna(subset=["fund_key","amc","asset_class"])

factsheet["amc_norm"] = factsheet["amc"].str.lower().str.strip()
factsheet["asset_class_norm"] = factsheet["asset_class"].str.lower().str.strip()
factsheet["fund_key"] = factsheet["fund_key"].astype(str)
factsheet["fund_key_norm"] = factsheet["fund_key"].str.lower()

def normalize_text(x):
    x = x.lower()
    x = re.sub(r"[^a-z ]"," ",x)
    return " ".join(x.split())

def normalize_category(cat):

    c = cat.lower()

    if "bank" in c and ("psu" in c or "financial" in c):
        return "banking & financial services"

    if "health" in c or "pharma" in c:
        return "healthcare"

    if "infra" in c:
        return "infrastructure"

    if "consum" in c:
        return "consumption"

    if "business" in c:
        return "business cycle"

    if "esg" in c:
        return "esg"

    if "tech" in c or "digital" in c:
        return "technology"

    if "quant" in c:
        return "quant"

    return c


mapped = 0
unmapped = []

for category, score_coll_name in CATEGORY_SCORE_COLLECTION.items():

    print("\nProcessing:", category)

    score_col = db[score_coll_name]
    asset_class_norm = normalize_category(category)

    for doc in score_col.find({"phase3a_status":"eligible"}):

        scheme_code = doc["scheme_code"]

        fm = fund_master.find_one({"scheme_code":scheme_code})
        if not fm:
            continue

        scheme_name_norm = normalize_text(fm["scheme_name"])
        amc_norm = fm["amc"].lower().strip()

        # STEP 1: Filter factsheet by AMC + Asset Class
        possible = factsheet[
            (factsheet["amc_norm"]==amc_norm) &
            (factsheet["asset_class_norm"]==asset_class_norm)
        ]

        if len(possible)==0:
            unmapped.append(fm["scheme_name"])
            continue

        # STEP 2: If only one fund exists → assign directly
        if len(possible)==1:
            fund_key = possible.iloc[0]["fund_key"]

        else:
            # STEP 3: Token match with scheme name
            best_match=None
            for _,row in possible.iterrows():
                fk=row["fund_key_norm"]
                tokens=fk.split("_")[1:]
                if any(t in scheme_name_norm for t in tokens):
                    best_match=row
                    break

            if best_match is None:
                unmapped.append(fm["scheme_name"])
                continue

            fund_key=best_match["fund_key"]

        fund_master_v2.update_one(
            {"scheme_code":scheme_code},
            {"$set":{
                "scheme_code":scheme_code,
                "scheme_name":fm["scheme_name"],
                "amc":fm["amc"],
                "category":category,
                "fund_key":fund_key,
                "updated_at":datetime.utcnow()
            }},
            upsert=True
        )

        mapped+=1


print("\n====================")
print("Mapped:",mapped)
print("Unmapped:",len(unmapped))

if unmapped:
    pd.DataFrame(unmapped,columns=["scheme_name"]).to_csv(
        "unmatched_thematic_mapping.csv",index=False
    )
