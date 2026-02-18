import re
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient

# ---------------- DB ----------------
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

funds_col = db.fund_master
map_col = db.scheme_benchmark_map

# ---------------- HELPERS ----------------
def normalize(name: str) -> str:
    name = name.lower()
    name = re.sub(r"direct|regular|growth|plan|option|idcw|dividend", "", name)
    name = re.sub(r"[^a-z0-9 ]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()

# ---------------- LOAD FUND-LEVEL BENCHMARKS ----------------
fund_benchmark = {}

for row in map_col.find({ "source": "CRISIL" }):
    key = normalize(row["scheme_name"])
    fund_benchmark[key] = row["benchmark"]

print("Loaded fund-level benchmarks:", len(fund_benchmark))

# ---------------- PROPAGATE TO ALL PLANS ----------------
inserted = 0

for fund in funds_col.find({}, { "scheme_code": 1, "scheme_name": 1 }):
    key = normalize(fund["scheme_name"])

    if key not in fund_benchmark:
        continue

    map_col.update_one(
        { "scheme_code": fund["scheme_code"] },
        {
            "$set": {
                "scheme_name": fund["scheme_name"],
                "benchmark": fund_benchmark[key],
                "source": "CRISIL_PROPAGATED"
            }
        },
        upsert=True
    )
    inserted += 1

print("✅ Propagated benchmark to plan-level scheme_codes")
print("Inserted / Updated:", inserted)
print("Total mappings:", map_col.count_documents({}))
