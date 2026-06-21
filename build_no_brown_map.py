"""
NO-BROWN SCENARIO MAP
======================
Shows what happens if Brown School closes and its students are reassigned
to their closest remaining school (by straight-line distance).

Dot encoding:
  Solid filled dot   = current zone student (non-Brown)
  Outlined dot       = reassigned Brown student (lighter fill, bold border)
                       border + fill color = their new school

Majority of Brown points (~226/266) flow to Kennedy.

USAGE:
  python3 build_no_brown_map.py
  Output: no_brown_scenario_map.html
"""
import json
from collections import Counter

INPUT_ZONES        = "seven_zone_with_status.json"
INPUT_PROX         = "proximity_analysis.json"
WALK_KENNEDY       = "samples_walk_to_kennedy.json"
WALK_WEST          = "samples_walk_to_west.json"
WALK_WINTERHILL    = "brown_to_winterhill_walks.json"
WALK_HEALEY        = "brown_to_healey_walks.json"
OUTPUT_FILE        = "no_brown_scenario_map.html"

SCHOOLS = [
    {"name": "Kennedy School",                          "grades": "K-8",  "lat": 42.389388, "lon": -71.115523, "address": "5 Cherry Street",        "key": "Kennedy"},
    {"name": "West Somerville Neighborhood School",     "grades": "PK-8", "lat": 42.406166, "lon": -71.126467, "address": "177 Powder House Blvd",   "key": "WestSomerville"},
    {"name": "Winter Hill Community Innovation School", "grades": "PK-8", "lat": 42.391667, "lon": -71.098797, "address": "115 Sycamore Street",     "key": "WinterHill"},
    {"name": "Healey School",                          "grades": "PK-8", "lat": 42.397530, "lon": -71.095360, "address": "5 Meacham Street",        "key": "Healey"},
    {"name": "Argenziano School",                      "grades": "PK-8", "lat": 42.379030, "lon": -71.098674, "address": "290 Washington Street",   "key": "Argenziano"},
    {"name": "East Somerville Community School",       "grades": "K-8",  "lat": 42.389744, "lon": -71.084723, "address": "50 Cross Street",         "key": "EastSomerville"},
]

# Brown shown as ghost/closed marker
BROWN_SCHOOL = {"name": "Brown School (closed in scenario)", "lat": 42.397302, "lon": -71.114010, "address": "201 Willow Avenue"}

OTHER_SCHOOLS = [
    {"name": "Edgerly (Winter Hill Temporary Location)", "grades": "PK-8 (temporary site)",
     "lat": 42.38798214035693, "lon": -71.08728780221357, "address": "33 Cross Street"},
    {"name": "SHS / Next Wave", "grades": "",
     "lat": 42.386971, "lon": -71.096151, "address": "81 Highland Ave / 153 School St"},
    {"name": "Capuano", "grades": "PK-K",
     "lat": 42.383074494377055, "lon": -71.08728791692477, "address": "150 Glen Street"},
]

# zone key in seven_zone_with_status -> school key in proximity
ZONE_TO_KEY = {
    "Kennedy":        "Kennedy",
    "West":           "WestSomerville",
    "Winter Hill":    "WinterHill",
    "Healey":         "Healey",
    "Argenziano":     "Argenziano",
    "East Somerville":"EastSomerville",
}

SCHOOL_KEYS = [s["key"] for s in SCHOOLS]

COLOR = {
    "Kennedy":        {"dark": "#92400e", "light": "#fcd34d"},
    "WestSomerville": {"dark": "#1e3a8a", "light": "#93c5fd"},
    "WinterHill":     {"dark": "#065f46", "light": "#6ee7b7"},
    "Healey":         {"dark": "#991b1b", "light": "#fca5a5"},
    "Argenziano":     {"dark": "#155e75", "light": "#67e8f9"},
    "EastSomerville": {"dark": "#9d174d", "light": "#f9a8d4"},
}

DISPLAY_NAME = {
    "Kennedy":        "Kennedy",
    "WestSomerville": "West Somerville",
    "WinterHill":     "Winter Hill",
    "Healey":         "Healey",
    "Argenziano":     "Argenziano",
    "EastSomerville": "East Somerville",
}


def load_walk_index(path):
    with open(path) as f:
        data = json.load(f)
    return {p["address"]: p for p in data}


def main():
    with open(INPUT_ZONES) as f: zones = json.load(f)

    # walk-distance lookups keyed by address
    walk = {
        "Kennedy":        load_walk_index(WALK_KENNEDY),
        "WestSomerville": load_walk_index(WALK_WEST),
        "WinterHill":     load_walk_index(WALK_WINTERHILL),
        "Healey":         load_walk_index(WALK_HEALEY),
    }

    map_points = []

    for pt in zones:
        zone = pt["zone"]

        if zone == "Brown":
            addr = pt["address"]
            # pick closest by walk_min_adj; fall back to whichever keys exist
            dists = {}
            for sk, idx in walk.items():
                rec = idx.get(addr)
                if rec and rec.get("walk_min_adj") is not None:
                    dists[sk] = rec["walk_min_adj"]
            if not dists:
                continue
            new_school = min(dists, key=dists.get)
            walk_min   = dists[new_school]
            walk_mi    = walk[new_school].get(addr, {}).get("walk_mi", "?")
            map_points.append({
                "lat":        pt["lat"],
                "lon":        pt["lon"],
                "address":    addr,
                "school_key": new_school,
                "is_brown":   True,
                "label":      f"{pt['street']} {pt.get('num','')}",
                "popup_extra": f"<div style='color:#7c3aed;margin-top:4px'>Formerly Brown zone</div>"
                               f"<div>Reassigned → {DISPLAY_NAME[new_school]}</div>"
                               f"<div style='color:#444;font-size:11px'>{walk_mi} mi · {walk_min} min walk</div>",
            })
        else:
            sk = ZONE_TO_KEY.get(zone)
            if not sk:
                continue
            map_points.append({
                "lat":        pt["lat"],
                "lon":        pt["lon"],
                "address":    pt["address"],
                "school_key": sk,
                "is_brown":   False,
                "label":      f"{pt['street']} {pt.get('num','')}",
                "popup_extra": f"<div style='color:#555;margin-top:4px'>"
                               f"Walk: {pt.get('walk_min_adj', pt.get('walk_min','?'))} min to {DISPLAY_NAME[sk]}</div>",
            })

    brown_dest = Counter(p["school_key"] for p in map_points if p["is_brown"])
    total_brown = sum(brown_dest.values())
    print(f"Loaded {len(zones)} zone points → {len(map_points)} mapped")
    print(f"Brown reassignment ({total_brown} pts): {dict(brown_dest)}")

    html = build_html(map_points, total_brown, brown_dest)
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"Saved {OUTPUT_FILE} ({len(html):,} bytes)")


def build_html(map_points, total_brown, brown_dest):
    kennedy_count = brown_dest.get("Kennedy", 0)

    legend_items = ""
    for s in SCHOOLS:
        c = COLOR[s["key"]]
        dn = DISPLAY_NAME[s["key"]]
        legend_items += f"""
  <div class="leg-group">
    <div class="dot" style="background:{c['dark']};border:1px solid {c['dark']}"></div>
    <span>{dn} (current)</span>
  </div>
  <div class="leg-group">
    <div class="dot" style="background:{c['light']};border:2.5px solid {c['dark']}"></div>
    <span>{dn} (ex-Brown)</span>
  </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Somerville — No Brown Scenario</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<style>
* {{box-sizing:border-box;margin:0;padding:0;}}
body {{font-family:system-ui,sans-serif;background:#f5f4f0;display:flex;flex-direction:column;height:100vh;}}
#header {{padding:12px 18px 8px;background:#fff;border-bottom:1px solid #e0dfd8;flex-shrink:0;}}
#header h1 {{font-size:15px;font-weight:600;margin-bottom:2px;}}
#header p {{font-size:12px;color:#666;}}
#map {{flex:1;}}
#legend {{display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;
          padding:8px 18px;background:#fff;border-top:1px solid #e0dfd8;
          font-size:10px;flex-shrink:0;max-height:110px;overflow-y:auto;}}
.leg-group {{display:flex;align-items:center;gap:4px;border-right:1px solid #e5e5e5;padding-right:8px;}}
.leg-group:last-child {{border-right:none;}}
.dot {{width:10px;height:10px;border-radius:50%;flex-shrink:0;}}
.leg-section {{font-size:10px;font-weight:600;color:#444;padding-right:6px;border-right:2px solid #ccc;}}
</style>
</head>
<body>
<div id="header">
  <h1>Somerville — What If Brown School Closed?</h1>
  <p>{total_brown} Brown zone addresses reassigned to nearest school &nbsp;·&nbsp;
     {kennedy_count} of {total_brown} ({kennedy_count*100//total_brown}%) → Kennedy &nbsp;·&nbsp;
     Solid dot = current zone &nbsp;·&nbsp; Outlined dot = reassigned Brown student</p>
</div>
<div id="map"></div>
<div id="legend">
  <span class="leg-section">Current zone</span>
  <span class="leg-section">Ex-Brown reassigned</span>
  {legend_items}
  <div class="leg-group">
    <div class="dot" style="background:#d1d5db;border:2px dashed #6b7280"></div>
    <span>Brown (closed)</span>
  </div>
</div>
<script>
const mapPoints = {json.dumps(map_points)};
const schools   = {json.dumps(SCHOOLS)};
const colors    = {json.dumps(COLOR)};
const brownSchool = {json.dumps(BROWN_SCHOOL)};
const displayName = {json.dumps(DISPLAY_NAME)};
const otherSchools = {json.dumps(OTHER_SCHOOLS)};

const map = L.map('map').setView([42.392, -71.103], 13);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO', maxZoom: 19
}}).addTo(map);

async function addSomervilleBorder() {{
  try {{
    const url = "https://nominatim.openstreetmap.org/search?q=" +
      encodeURIComponent("Somerville, Massachusetts, USA") +
      "&polygon_geojson=1&format=json&limit=1";
    const resp = await fetch(url, {{headers:{{"User-Agent":"somerville-school-map/1.0"}}}});
    const data = await resp.json();
    if (data.length && data[0].geojson) {{
      L.geoJSON(data[0].geojson, {{style:{{color:"#6366f1",weight:2.5,opacity:0.9,fill:false}}}}).addTo(map);
    }}
  }} catch(e) {{ console.warn('Border fetch failed', e); }}
}}
addSomervilleBorder();

function starIcon(fill, stroke, size) {{
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'" viewBox="0 0 24 24">' +
    '<polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" ' +
    'fill="'+fill+'" stroke="'+stroke+'" stroke-width="1.5"/></svg>';
  return L.divIcon({{html:svg, className:'', iconAnchor:[size/2,size/2], iconSize:[size,size]}});
}}

// draw current-zone (non-Brown) points first, then ex-Brown on top
const current = mapPoints.filter(p => !p.is_brown);
const exBrown  = mapPoints.filter(p =>  p.is_brown);

current.forEach(p => {{
  const c = colors[p.school_key];
  L.circleMarker([p.lat, p.lon], {{
    radius: 3.5, fillColor: c.light, color: c.dark, weight: 0.8, fillOpacity: 0.45
  }}).addTo(map).bindPopup(
    '<div style="font-weight:600;font-size:14px;margin-bottom:4px">' + p.label + '</div>' +
    '<div>Zone: <strong>' + displayName[p.school_key] + '</strong></div>' + p.popup_extra
  );
}});

exBrown.forEach(p => {{
  const c = colors[p.school_key];
  L.circleMarker([p.lat, p.lon], {{
    radius: 4, fillColor: c.light, color: c.dark, weight: 2, fillOpacity: 0.95
  }}).addTo(map).bindPopup(
    '<div style="font-weight:600;font-size:14px;margin-bottom:4px">' + p.label + '</div>' +
    p.popup_extra
  );
}});

// active schools — star markers
schools.forEach(s => {{
  const c = colors[s.key];
  L.marker([s.lat, s.lon], {{icon: starIcon(c.dark, '#000', 26), zIndexOffset: 1000}})
    .addTo(map)
    .bindPopup('<strong>' + s.name + '</strong>' + (s.grades ? ' (' + s.grades + ')' : '') + '<br>' + s.address);
  const shortName = s.name
    .replace(' Community Innovation School','')
    .replace(' Neighborhood School','')
    .replace(' Community School','');
  L.marker([s.lat, s.lon], {{
    icon: L.divIcon({{
      html: '<div style="font-size:11px;font-weight:600;white-space:nowrap;margin-left:15px;margin-top:-6px;' +
            'color:#1a1a18;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff">' + shortName + '</div>',
      className:'', iconAnchor:[0,6]
    }}),
    zIndexOffset: 999, interactive: false
  }}).addTo(map);
}});

// Brown — ghost/closed marker
L.marker([brownSchool.lat, brownSchool.lon], {{
  icon: starIcon('#d1d5db', '#9ca3af', 26), zIndexOffset: 1000, opacity: 0.5
}}).addTo(map)
  .bindPopup('<strong>' + brownSchool.name + '</strong><br>' + brownSchool.address);
L.marker([brownSchool.lat, brownSchool.lon], {{
  icon: L.divIcon({{
    html: '<div style="font-size:11px;font-weight:600;white-space:nowrap;margin-left:15px;margin-top:-6px;' +
          'color:#9ca3af;text-shadow:0 0 3px #fff,0 0 3px #fff">Brown (closed)</div>',
    className:'', iconAnchor:[0,6]
  }}),
  zIndexOffset: 999, interactive: false
}}).addTo(map);

// other reference schools
otherSchools.forEach(s => {{
  L.marker([s.lat, s.lon], {{icon: starIcon('#94a3b8','#475569',20), zIndexOffset:1000}})
    .addTo(map)
    .bindPopup('<strong>' + s.name + '</strong>' + (s.grades ? ' (' + s.grades + ')' : '') + '<br>' + s.address);
}});
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()
