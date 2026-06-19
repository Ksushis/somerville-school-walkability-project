"""
Patches Benton Road 1-54 with corrected coordinate and re-routes
to both Kennedy and Winter Hill.
Run: python3 fetch_kennedy_benton_patch.py
Outputs: kennedy_walk_to_winterhill.json (updated) — upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
KENNEDY = [-71.115523, 42.389388]
WINTERHILL = [-71.098797, 42.391667]

NEW_LAT, NEW_LON = 42.38904591431922, -71.1054925776143
STREET = "Benton Road 1-54"

def ors_walk(dest, lon, lat):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], dest], "units": "mi"}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": ORS_KEY, "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    feature = data["features"][0]
    return (
        round(feature["properties"]["summary"]["distance"], 2),
        round(feature["properties"]["summary"]["duration"] / 60, 1)
    )

existing = json.load(open("kennedy_walk_to_winterhill.json"))
idx = next(i for i, d in enumerate(existing) if d["street"] == STREET)

print("Re-routing " + STREET + " from corrected coordinate...")
k_dist, k_mins = ors_walk(KENNEDY, NEW_LON, NEW_LAT)
time.sleep(2)
wh_dist, wh_mins = ors_walk(WINTERHILL, NEW_LON, NEW_LAT)

k_adj = math.ceil(k_mins * 1.13)
wh_adj = math.ceil(wh_mins * 1.13)

existing[idx]["lat"] = NEW_LAT
existing[idx]["lon"] = NEW_LON
existing[idx]["walk_mi"] = k_dist
existing[idx]["walk_min"] = k_mins
existing[idx]["walk_min_adj"] = k_adj
existing[idx]["wh_walk_mi"] = wh_dist
existing[idx]["wh_walk_min"] = wh_mins
existing[idx]["wh_walk_min_adj"] = wh_adj

print("  To Kennedy: " + str(k_dist) + " mi (" + str(k_adj) + " min)")
print("  To Winter Hill: " + str(wh_dist) + " mi (" + str(wh_adj) + " min)")

with open("kennedy_walk_to_winterhill.json", "w") as f:
    json.dump(existing, f, indent=2)

print("\nDone. Upload kennedy_walk_to_winterhill.json to Claude")
