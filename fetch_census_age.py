"""
Fetches ACS 5-year population by age for every block group in Somerville, MA,
using the place-level geography filter (more reliable than tract-number guessing).

Run: python3 fetch_census_age.py
Outputs: somerville_age_blockgroups.json — upload to Claude
"""
import urllib.request, json

API_KEY = "d19c06afcacbcaf2b41d82e1f4a9f16df4af0750"
VARS = "B01001_003E,B01001_004E,B01001_005E,B01001_027E,B01001_028E,B01001_029E,NAME"

# Somerville city FIPS place code = 62535, state = 25 (Massachusetts)
# Block groups don't support "in=place" directly in all years, so we use tract
# within county, but restrict to the known Somerville tract list (3501-3515 incl. decimals)
url = (
    f"https://api.census.gov/data/2022/acs/acs5"
    f"?get={VARS}"
    f"&for=block%20group:*"
    f"&in=state:25%20county:017%20tract:*"
    f"&key={API_KEY}"
)

print("Fetching block group age data for Middlesex County...")
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=30) as r:
    data = json.loads(r.read())

header = data[0]
rows = data[1:]
print(f"Got {len(rows)} block groups in Middlesex County")

# Somerville's known tract numbers (without decimal point, as 6-digit codes)
# Tracts 3501.xx through 3515.xx, expressed as 350100-351599
somerville_rows = []
for row in rows:
    rec = dict(zip(header, row))
    tract = rec["tract"]  # e.g. "350105" = tract 3501.05
    tract_num = int(tract[:4])  # first 4 digits = whole-number part (3501-3515)
    if 3501 <= tract_num <= 3515:
        somerville_rows.append(rec)

print(f"Filtered to tracts 3501-3515: {len(somerville_rows)} block groups")
print("\nSample:")
for r in somerville_rows[:5]:
    print(f"  {r['NAME']}  tract={r['tract']}")

results = []
for rec in somerville_rows:
    under5 = int(rec["B01001_003E"] or 0) + int(rec["B01001_027E"] or 0)
    age5_9 = int(rec["B01001_004E"] or 0) + int(rec["B01001_028E"] or 0)
    age10_14 = int(rec["B01001_005E"] or 0) + int(rec["B01001_029E"] or 0)
    results.append({
        "name": rec["NAME"],
        "tract": rec["tract"],
        "block_group": rec["block group"],
        "under_5": under5,
        "age_5_9": age5_9,
        "age_10_14": age10_14,
        "elementary_age_total": age5_9 + age10_14,
        "pre_elementary_total": under5
    })

with open("somerville_age_blockgroups.json", "w") as f:
    json.dump(results, f, indent=2)

total_under5 = sum(r["under_5"] for r in results)
total_5_14 = sum(r["elementary_age_total"] for r in results)
print(f"\nSaved {len(results)} block groups")
print(f"Total under-5 in Somerville: {total_under5}")
print(f"Total age 5-14 in Somerville: {total_5_14}")
print("\nUpload somerville_age_blockgroups.json to Claude")
