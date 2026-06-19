"""
Fetches block group polygon geometries (GeoJSON) for Somerville, MA
from the Census TIGERweb REST service, matched to the age data tracts.

Run: python3 fetch_blockgroup_geometry.py
Outputs: somerville_blockgroup_geometry.json — upload to Claude
"""
import urllib.request, urllib.parse, json

# Somerville's known tracts (without decimal)
TRACTS = [
    "350105","350106","350107","350108","350109",
    "350201","350202","350300","350400","350500","350600",
    "350701","350702","350800","350900",
    "351001","351002","351101","351102","351203","351204",
    "351300","351403","351404","351500"
]

# Census TIGERweb REST API — block groups layer
BASE = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/1/query"

results = []
for tract in TRACTS:
    where = f"STATE='25' AND COUNTY='017' AND TRACT='{tract}'"
    params = {
        "where": where,
        "outFields": "STATE,COUNTY,TRACT,BLKGRP,GEOID",
        "outSR": "4326",
        "f": "geojson"
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    print(f"Fetching tract {tract}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "somerville-school-map/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        features = data.get("features", [])
        print(f"  Got {len(features)} block groups")
        for f in features:
            results.append(f)
    except Exception as e:
        print(f"  ERROR: {e}")

print(f"\nTotal features: {len(results)}")

output = {"type": "FeatureCollection", "features": results}
with open("somerville_blockgroup_geometry.json", "w") as f:
    json.dump(output, f)

print("Saved to somerville_blockgroup_geometry.json")
print("Upload to Claude")
