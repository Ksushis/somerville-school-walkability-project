"""
Fetches clean MA town boundaries from MassGIS ArcGIS REST service.
Run: python3 fetch_boundaries_v2.py
Outputs: boundaries_v2.json — upload to Claude
"""
import urllib.request, urllib.parse, json

TOWNS = ["SOMERVILLE", "MEDFORD", "ARLINGTON", "CAMBRIDGE", "EVERETT", "MALDEN"]

# MassGIS town survey boundaries — authoritative MA source
url = (
    "https://arcgisserver.digital.mass.gov/arcgisserver/rest/services/AGOL/"
    "Towns_survey_polys/MapServer/0/query"
    "?where=TOWN+IN+('" + "','".join(TOWNS) + "')"
    "&outFields=TOWN"
    "&outSR=4326"
    "&f=geojson"
)

print("Fetching from MassGIS...")
try:
    req = urllib.request.Request(url, headers={"User-Agent": "somerville-school-map/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read())
    features = data.get("features", [])
    print(f"Got {len(features)} features from MassGIS")
    with open("boundaries_v2.json", "w") as f:
        json.dump(data, f)
    print("Upload boundaries_v2.json to Claude")
except Exception as e:
    print(f"MassGIS failed: {e}")
    print("Trying Census TIGER...")
    # Fallback: Census cartographic boundary shapefiles via their API
    url2 = (
        "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/"
        "Places_CouSub_ConCity_SubMCD/MapServer/4/query"
        "?where=NAME+IN+('" + "','".join(t.title() for t in TOWNS) + "')+AND+STATE='25'"
        "&outFields=NAME"
        "&outSR=4326"
        "&f=geojson"
    )
    req2 = urllib.request.Request(url2, headers={"User-Agent": "somerville-school-map/1.0"})
    with urllib.request.urlopen(req2, timeout=20) as r:
        data2 = json.loads(r.read())
    features2 = data2.get("features", [])
    print(f"Got {len(features2)} features from Census TIGER")
    with open("boundaries_v2.json", "w") as f:
        json.dump(data2, f)
    print("Upload boundaries_v2.json to Claude")
