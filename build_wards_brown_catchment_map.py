"""
CURRENT PROXIMITY SCHOOL ASSIGNMENT WITH WARD BOUNDARIES
=========================================================
All 7 zones shown with zone color (no reassignment). Ward boundaries on top.
Run: python3 build_wards_brown_catchment_map.py
Output: wards_brown_catchment_map.html
"""
import json, statistics

INPUT_ZONES  = "seven_zone_with_status.json"
INPUT_WARDS  = "wards.geojson"
INPUT_BOUNDS = "boundaries.json"
OUTPUT_FILE  = "wards_brown_catchment_map.html"

SCHOOLS = [
    {"name": "Brown School",                            "grades": "K-5",  "lat": 42.397302, "lon": -71.114010, "address": "201 Willow Avenue",      "key": "Brown"},
    {"name": "Kennedy School",                          "grades": "K-8",  "lat": 42.389388, "lon": -71.115523, "address": "5 Cherry Street",         "key": "Kennedy"},
    {"name": "West Somerville Neighborhood School",     "grades": "PK-8", "lat": 42.406166, "lon": -71.126467, "address": "177 Powder House Blvd",   "key": "WestSomerville"},
    {"name": "Winter Hill Community Innovation School", "grades": "PK-8", "lat": 42.391667, "lon": -71.098797, "address": "115 Sycamore Street",     "key": "WinterHill"},
    {"name": "Healey School",                          "grades": "PK-8", "lat": 42.397530, "lon": -71.095360, "address": "5 Meacham Street",        "key": "Healey"},
    {"name": "Argenziano School",                      "grades": "PK-8", "lat": 42.379030, "lon": -71.098674, "address": "290 Washington Street",   "key": "Argenziano"},
    {"name": "East Somerville Community School",       "grades": "K-8",  "lat": 42.389744, "lon": -71.084723, "address": "50 Cross Street",         "key": "EastSomerville"},
]
OTHER_SCHOOLS = [
    {"name": "Edgerly (Winter Hill Temporary Location)", "grades": "PK-8 (temporary site)",
     "lat": 42.38798214035693, "lon": -71.08728780221357, "address": "33 Cross Street"},
    {"name": "SHS / Next Wave", "grades": "",
     "lat": 42.386971, "lon": -71.096151, "address": "81 Highland Ave / 153 School St"},
    {"name": "Capuano", "grades": "PK-K",
     "lat": 42.383074494377055, "lon": -71.08728791692477, "address": "150 Glen Street"},
]

ZONE_TO_KEY = {
    "Brown":          "Brown",
    "Kennedy":        "Kennedy",
    "West":           "WestSomerville",
    "Winter Hill":    "WinterHill",
    "Healey":         "Healey",
    "Argenziano":     "Argenziano",
    "East Somerville":"EastSomerville",
}
COLOR = {
    "Brown":          {"dark": "#7c3aed", "light": "#ddd6fe"},   # purple
    "Kennedy":        {"dark": "#92400e", "light": "#fcd34d"},
    "WestSomerville": {"dark": "#1e3a8a", "light": "#93c5fd"},
    "WinterHill":     {"dark": "#065f46", "light": "#6ee7b7"},
    "Healey":         {"dark": "#991b1b", "light": "#fca5a5"},
    "Argenziano":     {"dark": "#155e75", "light": "#67e8f9"},
    "EastSomerville": {"dark": "#9d174d", "light": "#f9a8d4"},
}
DISPLAY_NAME = {
    "Brown":          "Brown",
    "Kennedy":        "Kennedy",
    "WestSomerville": "West Somerville",
    "WinterHill":     "Winter Hill",
    "Healey":         "Healey",
    "Argenziano":     "Argenziano",
    "EastSomerville": "East Somerville",
}


def polygon_centroid(coords):
    lats = [c[1] for c in coords[0]]
    lons = [c[0] for c in coords[0]]
    return statistics.mean(lats), statistics.mean(lons)


def main():
    with open(INPUT_ZONES)  as f: zones  = json.load(f)
    with open(INPUT_WARDS)  as f: wards  = json.load(f)
    with open(INPUT_BOUNDS) as f: bounds = json.load(f)

    ward_labels = []
    for feat in wards["features"]:
        lat, lon = polygon_centroid(feat["geometry"]["coordinates"])
        ward_labels.append({"ward": feat["properties"]["ward"], "lat": lat, "lon": lon})

    map_points = []
    for pt in zones:
        sk = ZONE_TO_KEY.get(pt["zone"])
        if not sk:
            continue
        wm = pt.get("walk_min_adj", pt.get("walk_min", "?"))
        map_points.append({
            "lat": pt["lat"], "lon": pt["lon"],
            "school_key": sk,
            "popup": (f"<div style='font-weight:600;font-size:14px;margin-bottom:4px'>"
                      f"{pt['street']} {pt.get('num','')}</div>"
                      f"<div><span style='background:#e2e8f0;padding:1px 6px;border-radius:10px;font-size:11px'>"
                      f"{pt['zone']} zone</span></div>"
                      f"<div style='margin-top:4px'><strong>{wm} min</strong> walk to {DISPLAY_NAME[sk]}</div>"),
        })

    print(f"{len(map_points)} points")

    # legend
    legend_items = ""
    for s in SCHOOLS:
        c = COLOR[s["key"]]
        dn = DISPLAY_NAME[s["key"]]
        legend_items += (f'<div class="leg-group">'
                         f'<div class="dot" style="background:{c["light"]}"></div>'
                         f'<span>{dn} zone</span></div>')

    somerville_coords = json.dumps(bounds["Somerville"])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Current Proximity School Assignment with Ward Boundaries</title>
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
          font-size:10px;flex-shrink:0;}}
.leg-group {{display:flex;align-items:center;gap:4px;border-right:1px solid #e5e5e5;padding-right:8px;}}
.leg-group:last-child {{border-right:none;}}
.dot {{width:10px;height:10px;border-radius:50%;flex-shrink:0;}}
.ward-swatch {{width:28px;height:3px;background:#1e3a8a;border-radius:2px;}}
</style>
</head>
<body>
<div id="header">
  <h1>Current Proximity School Assignment with Ward Boundaries</h1>
  <p>{len(map_points)} addresses &middot; dot color = current school zone assignment &middot; ward boundaries overlaid</p>
</div>
<div id="map"></div>
<div id="legend">
  {legend_items}
  <div class="leg-group">
    <svg width="12" height="12" viewBox="0 0 24 24"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="#94a3b8" stroke="#475569" stroke-width="1.5"/></svg>
    <span>Other schools</span>
  </div>
  <div class="leg-group"><div class="ward-swatch"></div><span>Ward boundary</span></div>
</div>
<script>
const mapPoints = {json.dumps(map_points)};
const schools = {json.dumps(SCHOOLS)};
const colors = {json.dumps(COLOR)};
const otherSchools = {json.dumps(OTHER_SCHOOLS)};
const wardsGeoJSON = {json.dumps(wards)};
const wardLabels = {json.dumps(ward_labels)};
const somervilleCoords = {somerville_coords};

const map = L.map('map').setView([42.392, -71.103], 13);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO', maxZoom: 19
}}).addTo(map);

function starIcon(fill, stroke, size) {{
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'" viewBox="0 0 24 24">' +
    '<polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" ' +
    'fill="'+fill+'" stroke="'+stroke+'" stroke-width="1.5"/></svg>';
  return L.divIcon({{html:svg, className:'', iconAnchor:[size/2,size/2], iconSize:[size,size]}});
}}

// all zone dots — no border, light fill, uniform style
mapPoints.forEach(p => {{
  const c = colors[p.school_key];
  L.circleMarker([p.lat, p.lon], {{
    radius: 4, fillColor: c.light, color: 'transparent', weight: 0, fillOpacity: 0.55
  }}).addTo(map).bindPopup(p.popup);
}});

// school stars
schools.forEach(s => {{
  const c = colors[s.key];
  L.marker([s.lat, s.lon], {{icon: starIcon(c.light, c.dark, 26), zIndexOffset: 1000}})
    .addTo(map).bindPopup('<strong>'+s.name+'</strong>'+(s.grades?' ('+s.grades+')':'')+'<br>'+s.address);
  const sn = s.name.replace(' Community Innovation School','').replace(' Neighborhood School','').replace(' Community School','');
  L.marker([s.lat, s.lon], {{
    icon: L.divIcon({{html:'<div style="font-size:11px;font-weight:600;white-space:nowrap;margin-left:15px;margin-top:-6px;color:#1a1a18;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff">'+sn+'</div>',className:'',iconAnchor:[0,6]}}),
    zIndexOffset: 999, interactive: false
  }}).addTo(map);
}});

// other schools (gray stars)
otherSchools.forEach(s => {{
  L.marker([s.lat, s.lon], {{icon: starIcon('#94a3b8','#475569',20), zIndexOffset:1000}})
    .addTo(map).bindPopup('<strong>'+s.name+'</strong>'+(s.grades?' ('+s.grades+')':'')+'<br>'+s.address);
}});

// ward boundaries — wards 1,2,3,7 navy+gray fill; wards 4,5,6 gray border only
const shadedWards = new Set([1,2,3,7]);
const grayWards = new Set([4,5,6]);
L.geoJSON(wardsGeoJSON, {{
  style: function(feature) {{
    const w = feature.properties.ward;
    if (shadedWards.has(w))
      return {{color:'#1e3a8a', weight:2, opacity:0.75, fill:true, fillColor:'#6b7280', fillOpacity:0.18}};
    if (grayWards.has(w))
      return {{color:'#9ca3af', weight:2, opacity:0.75, fill:false}};
    return {{color:'#1e3a8a', weight:2, opacity:0.75, fill:false}};
  }}
}}).addTo(map);

// ward labels
wardLabels.forEach(w => {{
  L.marker([w.lat, w.lon], {{
    icon: L.divIcon({{
      html: '<div style="font-size:12px;font-weight:700;color:#1e3a8a;text-shadow:0 0 4px #fff,0 0 4px #fff,0 0 4px #fff,0 0 4px #fff;white-space:nowrap">Ward '+w.ward+'</div>',
      className: '', iconAnchor: [24, 8]
    }}),
    zIndexOffset: 2000, interactive: false
  }}).addTo(map);
}});

// Somerville border — last
L.geoJSON({{type:"Feature",geometry:{{type:"MultiLineString",coordinates:somervilleCoords}}}},
  {{style:{{color:"#6366f1",weight:2.5,opacity:0.9,fill:false}}}}).addTo(map);
</script>
</body>
</html>"""

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"Saved {OUTPUT_FILE} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
