"""
Fetches municipal boundary polygons from OpenStreetMap via Overpass API.
Run: python3 fetch_boundaries.py
Outputs: boundaries.json — upload to Claude
"""
import urllib.request, urllib.parse, json, time

def fetch_boundary(name):
    query = f"""
[out:json][timeout:30];
relation["name"="{name}"]["boundary"="administrative"]["admin_level"="8"];
out geom;
"""
    url = "https://overpass-api.de/api/interpreter"
    data = urllib.parse.urlencode({"data": query}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": "somerville-school-map/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.loads(r.read())
            break
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                wait = 15 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    # Filter to Massachusetts by checking coordinates are in roughly the right area
    elements = [e for e in result.get("elements", []) 
                if any(m.get("geometry") and any(42.0 < n["lat"] < 43.0 and -72.0 < n["lon"] < -70.5
                       for n in m["geometry"]) for m in e.get("members", []))]
    return elements

towns = ["Somerville", "Medford", "Arlington", "Cambridge", "Everett", "Malden"]
results = {}

for town in towns:
    print(f"Fetching {town}...")
    try:
        elements = fetch_boundary(town)
        if not elements:
            print(f"  No results")
            continue
        rel = elements[0]
        print(f"  Found relation id={rel['id']}, members={len(rel.get('members',[]))}")
        coords = []
        for member in rel.get("members", []):
            if member.get("role") == "outer" and "geometry" in member:
                ring = [[n["lon"], n["lat"]] for n in member["geometry"]]
                coords.append(ring)
        results[town] = coords
        print(f"  Got {len(coords)} rings, {sum(len(r) for r in coords)} total points")
        time.sleep(5)
    except Exception as e:
        print(f"  ERROR: {e}")

with open("boundaries.json", "w") as f:
    json.dump(results, f)

print(f"\nDone. Got boundaries for: {list(results.keys())}")
print("Upload boundaries.json to Claude")
