"""
Walking distances from Healey zone streets to Healey School (5 Meacham St).
Run: python3 fetch_healey_walk.py
Outputs: healey_walk.json — upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
DEST = [-71.09536, 42.39753]  # Healey School — geocod.io rooftop

samples = [{"address": "Ash Avenue, Somerville MA 02144", "street": "Ash Avenue", "school": "HEALEY", "lat": 42.399052, "lon": -71.095018}, {"address": "Bailey Road, Somerville MA 02145", "street": "Bailey Road", "school": "HEALEY", "lat": 42.394745, "lon": -71.086748}, {"address": "Bond Street, Somerville MA 02145", "street": "Bond Street", "school": "HEALEY", "lat": 42.395626, "lon": -71.095584}, {"address": "Broadway 253-431, Somerville MA 02145", "street": "Broadway 253-431", "school": "HEALEY", "lat": 42.391046, "lon": -71.095146}, {"address": "Butler Drive, Somerville MA 02145", "street": "Butler Drive", "school": "HEALEY", "lat": 42.395263, "lon": -71.091361}, {"address": "Canal Lane, Somerville MA 02145", "street": "Canal Lane", "school": "HEALEY", "lat": 42.396735, "lon": -71.093939}, {"address": "Canal Street, Somerville MA 02145", "street": "Canal Street", "school": "HEALEY", "lat": 42.394328, "lon": -71.078314}, {"address": "Century Street, Somerville MA 02145", "street": "Century Street", "school": "HEALEY", "lat": 42.39676, "lon": -71.097141}, {"address": "Crest Hill Road, Somerville MA 02145", "street": "Crest Hill Road", "school": "HEALEY", "lat": 42.398884, "lon": -71.086896}, {"address": "Derby Street, Somerville MA 02145", "street": "Derby Street", "school": "HEALEY", "lat": 42.393174, "lon": -71.089013}, {"address": "Douglas Avenue, Somerville MA 02145", "street": "Douglas Avenue", "school": "HEALEY", "lat": 42.395455, "lon": -71.097233}, {"address": "East Albion Street, Somerville MA 02145", "street": "East Albion Street", "school": "HEALEY", "lat": 42.399056, "lon": -71.095515}, {"address": "Edgar Avenue, Somerville MA 02145", "street": "Edgar Avenue", "school": "HEALEY", "lat": 42.397176, "lon": -71.09602}, {"address": "Edgar Court, Somerville MA 02145", "street": "Edgar Court", "school": "HEALEY", "lat": 42.397157, "lon": -71.096393}, {"address": "Edgar Terrace, Somerville MA 02145", "street": "Edgar Terrace", "school": "HEALEY", "lat": 42.396653, "lon": -71.096657}, {"address": "Fellsway, Somerville MA 02145", "street": "Fellsway", "school": "HEALEY", "lat": 42.392732, "lon": -71.085793}, {"address": "Fellsway West, Somerville MA 02145", "street": "Fellsway West", "school": "HEALEY", "lat": 42.391287, "lon": -71.08968}, {"address": "Fenwick Street, Somerville MA 02145", "street": "Fenwick Street", "school": "HEALEY", "lat": 42.395271, "lon": -71.094873}, {"address": "Florence Terrace, Somerville MA 02145", "street": "Florence Terrace", "school": "HEALEY", "lat": 42.394631, "lon": -71.093035}, {"address": "Fremont Street, Somerville MA 02145", "street": "Fremont Street", "school": "HEALEY", "lat": 42.397026, "lon": -71.099094}, {"address": "Gov. Winthrop Road, Somerville MA 02145", "street": "Gov. Winthrop Road", "school": "HEALEY", "lat": 42.391046, "lon": -71.095146}, {"address": "Grant Street, Somerville MA 02145", "street": "Grant Street", "school": "HEALEY", "lat": 42.393641, "lon": -71.089013}, {"address": "Great River Road, Somerville MA 02145", "street": "Great River Road", "school": "HEALEY", "lat": 42.395924, "lon": -71.08064}, {"address": "Heath Street, Somerville MA 02145", "street": "Heath Street", "school": "HEALEY", "lat": 42.3945, "lon": -71.094361}, {"address": "Jaques Street, Somerville MA 02145", "street": "Jaques Street", "school": "HEALEY", "lat": 42.39263, "lon": -71.089757}, {"address": "Langmaid Avenue, Somerville MA 02145", "street": "Langmaid Avenue", "school": "HEALEY", "lat": 42.393492, "lon": -71.093676}, {"address": "Main Street, Somerville MA 02145", "street": "Main Street", "school": "HEALEY", "lat": 42.395725, "lon": -71.098121}, {"address": "Meacham Street, Somerville MA 02145", "street": "Meacham Street", "school": "HEALEY", "lat": 42.397439, "lon": -71.096154}, {"address": "Melville Road, Somerville MA 02145", "street": "Melville Road", "school": "HEALEY", "lat": 42.398482, "lon": -71.086283}, {"address": "Memorial Road, Somerville MA 02145", "street": "Memorial Road", "school": "HEALEY", "lat": 42.396036, "lon": -71.092222}, {"address": "Moreland Street, Somerville MA 02145", "street": "Moreland Street", "school": "HEALEY", "lat": 42.399495, "lon": -71.095611}, {"address": "Mystic Avenue 356-End, Somerville MA 02145", "street": "Mystic Avenue 356-End", "school": "HEALEY", "lat": 42.397417, "lon": -71.091917}, {"address": "Puritan Road, Somerville MA 02145", "street": "Puritan Road", "school": "HEALEY", "lat": 42.396268, "lon": -71.086467}, {"address": "Putnam Road, Somerville MA 02145", "street": "Putnam Road", "school": "HEALEY", "lat": 42.397089, "lon": -71.086423}, {"address": "River Road, Somerville MA 02145", "street": "River Road", "school": "HEALEY", "lat": 42.397515, "lon": -71.093069}, {"address": "Sewall Street, Somerville MA 02145", "street": "Sewall Street", "school": "HEALEY", "lat": 42.393276, "lon": -71.092064}, {"address": "Shore Drive, Somerville MA 02145", "street": "Shore Drive", "school": "HEALEY", "lat": 42.397864, "lon": -71.090344}, {"address": "Snow Terrace, Somerville MA 02145", "street": "Snow Terrace", "school": "HEALEY", "lat": 42.394773, "lon": -71.093345}, {"address": "Sydney Street, Somerville MA 02145", "street": "Sydney Street", "school": "HEALEY", "lat": 42.394161, "lon": -71.089084}, {"address": "Taylor Street, Somerville MA 02145", "street": "Taylor Street", "school": "HEALEY", "lat": 42.394792, "lon": -71.088972}, {"address": "Temple Road, Somerville MA 02145", "street": "Temple Road", "school": "HEALEY", "lat": 42.39807, "lon": -71.085647}, {"address": "Temple Street, Somerville MA 02145", "street": "Temple Street", "school": "HEALEY", "lat": 42.393008, "lon": -71.09302}, {"address": "Ten Hills Road, Somerville MA 02145", "street": "Ten Hills Road", "school": "HEALEY", "lat": 42.396074, "lon": -71.085687}, {"address": "Upland Park, Somerville MA 02145", "street": "Upland Park", "school": "HEALEY", "lat": 42.396847, "lon": -71.099456}, {"address": "Wheatland Street, Somerville MA 02145", "street": "Wheatland Street", "school": "HEALEY", "lat": 42.392666, "lon": -71.089075}, {"address": "Winter Hill Circle, Somerville MA 02145", "street": "Winter Hill Circle", "school": "HEALEY", "lat": 42.393833, "lon": -71.095099}]

def ors_walk(lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], DEST], "units": "mi"}).encode()
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
print("Routing " + str(len(samples)) + " streets to Healey School...\n")
for i, s in enumerate(samples):
    try:
        dist, mins = ors_walk(s["lon"], s["lat"])
        adj = math.ceil(mins * 1.13)
        results.append({**s, "walk_mi": dist, "walk_min": mins, "walk_min_adj": adj})
        print("[" + str(i+1).rjust(3) + "/" + str(len(samples)) + "] " + s["street"] + ": " + str(dist) + " mi (" + str(adj) + " min)")
    except Exception as e:
        print("[" + str(i+1).rjust(3) + "/" + str(len(samples)) + "] " + s["street"] + ": ERROR " + str(e))
        results.append({**s, "walk_mi": None, "walk_min": None, "walk_min_adj": None})
    time.sleep(3)

with open("healey_walk.json", "w") as f:
    json.dump(results, f, indent=2)

failed = [r for r in results if r["walk_mi"] is None]
print("\nDone. Failed: " + str(len(failed)))
print("Upload healey_walk.json to Claude")
