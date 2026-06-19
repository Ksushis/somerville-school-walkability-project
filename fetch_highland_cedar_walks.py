"""
Walking distances for the 22 Highland Avenue / Cedar Street points.
Kennedy-zoned points (Highland 182-402, Cedar 1-105) get routed to BOTH
Kennedy and Winter Hill. Winter Hill-zoned points (Highland 154-217) get
routed to Winter Hill only.
Run: python3 fetch_highland_cedar_walks.py
Outputs: highland_cedar_walks.json — upload to Claude
"""
import urllib.request, json, time, math, csv

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
KENNEDY = [-71.115523, 42.389388]
WINTERHILL = [-71.098797, 42.391667]

samples = []
with open("highland_cedar_to_geocode_geocodio_b50308175c0f74ef29faad8fd4ae099c32d3f88c.csv") as f:
    for row in csv.DictReader(f):
        samples.append({
            "address": row["address"],
            "street":  row["street"],
            "num":     row["num"],
            "school":  row["school"],
            "range_note": row["range_note"],
            "lat":     float(row["Geocodio Latitude"]),
            "lon":     float(row["Geocodio Longitude"]),
        })

def ors_walk(dest, lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], dest], "units": "mi"}).encode()
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
print("Routing " + str(len(samples)) + " points...\n")
for i, s in enumerate(samples):
    try:
        wh_dist, wh_mins = ors_walk(WINTERHILL, s["lon"], s["lat"])
        wh_adj = math.ceil(wh_mins * 1.13)
        entry = {**s, "wh_walk_mi": wh_dist, "wh_walk_min": wh_mins, "wh_walk_min_adj": wh_adj}

        if s["school"] == "KENNEDY":
            time.sleep(2)
            k_dist, k_mins = ors_walk(KENNEDY, s["lon"], s["lat"])
            k_adj = math.ceil(k_mins * 1.13)
            entry.update({"kennedy_walk_mi": k_dist, "kennedy_walk_min": k_mins, "kennedy_walk_min_adj": k_adj})
            print("[" + str(i+1).rjust(2) + "/" + str(len(samples)) + "] " + s["street"] + " " + s["num"] + ": Kennedy=" + str(k_adj) + "min, WH=" + str(wh_adj) + "min")
        else:
            print("[" + str(i+1).rjust(2) + "/" + str(len(samples)) + "] " + s["street"] + " " + s["num"] + " (WH zone): WH=" + str(wh_adj) + "min")

        results.append(entry)
    except Exception as e:
        print("[" + str(i+1).rjust(2) + "/" + str(len(samples)) + "] " + s["street"] + " " + s["num"] + ": ERROR " + str(e))
        results.append({**s, "wh_walk_mi": None})
    time.sleep(2)

with open("highland_cedar_walks.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nDone. Upload highland_cedar_walks.json to Claude")
