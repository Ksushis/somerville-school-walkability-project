"""
Routes the 7 corrected Beacon Street / School Street points to
Argenziano School (fixing the bad fallback-coordinate bug).

Run: python3 fetch_beacon_school_walks.py
Outputs: beacon_school_walks.json -- upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
ARGENZIANO = [-71.098674, 42.37903]

with open("beacon_school_to_route.json") as f:
    samples = json.load(f)

def ors_walk(lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], ARGENZIANO], "units": "mi"}).encode()
    for attempt in range(retries):
        try:
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
        except Exception as e:
            if "429" in str(e) and attempt < retries - 1:
                wait = 5 * (attempt + 1)
                print("    Rate limited, waiting " + str(wait) + "s...")
                time.sleep(wait)
            else:
                raise

results = []
print("Routing " + str(len(samples)) + " points to Argenziano...\n")
for i, s in enumerate(samples):
    dist, mins = ors_walk(s["lon"], s["lat"])
    adj = math.ceil(mins * 1.13)
    results.append({**s, "walk_mi": dist, "walk_min": mins, "walk_min_adj": adj})
    print(s["address"] + ": " + str(dist) + " mi (" + str(adj) + " min)")
    time.sleep(2)

with open("beacon_school_walks.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved. Upload beacon_school_walks.json to Claude")
