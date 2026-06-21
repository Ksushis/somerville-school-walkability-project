"""
2x2 QUADRANT: WINTER HILL'S REAL DISPLACEMENT vs. BROWN'S PROPOSED DISPLACEMENT
====================================================================================
  Upper left:  Winter Hill walking to OWN school (if it were open)
  Upper right: Winter Hill ACTUALLY walking to Edgerly (real, current displacement)
  Lower left:  Brown walking to OWN school (if it stays open)
  Lower right: Brown walking to Winter Hill under the PROPOSED redistricting

Same column = same school's before/after. Same row = same kind of
comparison (baseline on top, displaced on bottom). All four panes share
one color scale and pan/zoom in sync.

This does NOT call any API and does NOT need Claude.

USAGE:
  Place this script in the same folder as:
    - winterhill_vs_edgerly_export.json
    - brown_own_export.json
    - proposed_state_export.json
  Run: python3 build_quadrant_comparison.py
  Output: current_and_planned_displacement_comparison.html
"""
import json

WH_EDGERLY_FILE = "winterhill_vs_edgerly_export.json"
BROWN_OWN_FILE = "brown_own_export.json"
BROWN_PROPOSED_FILE = "proposed_state_export.json"
OUTPUT_FILE = "current_and_planned_displacement_comparison.html"

SHARED_MAX = 35

SCHOOLS = {
    "brown": {"name": "Brown School", "lat": 42.397302, "lon": -71.114010, "address": "201 Willow Avenue"},
    "winterhill": {"name": "Winter Hill Community Innovation School", "lat": 42.391667, "lon": -71.098797, "address": "115 Sycamore Street"},
    "edgerly": {"name": "Edgerly (Winter Hill Temporary Location)", "lat": 42.38798214035693, "lon": -71.08728780221357, "address": "33 Cross Street"},
}


def main():
    try:
        with open(WH_EDGERLY_FILE) as f:
            wh_data = json.load(f)
        with open(BROWN_OWN_FILE) as f:
            brown_own = json.load(f)
        with open(BROWN_PROPOSED_FILE) as f:
            proposed = json.load(f)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    brown_proposed = [d for d in proposed if d.get("zone") == "Brown (proposed -> Winter Hill)"]
    print(f"Winter Hill: {len(wh_data)}, Brown own: {len(brown_own)}, Brown proposed: {len(brown_proposed)}")

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Winter Hill's Current Displacement vs. Brown's Proposed Displacement</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<style>
* {box-sizing:border-box;margin:0;padding:0;}
body {font-family:system-ui,sans-serif;background:#f5f4f0;display:flex;flex-direction:column;height:100vh;}
#header {padding:10px 18px 6px;background:#fff;border-bottom:1px solid #e0dfd8;flex-shrink:0;}
#header h1 {font-size:15px;font-weight:600;margin-bottom:2px;}
#header p {font-size:12px;color:#666;}
#grid {flex:1;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;}
.quad {position:relative;border:1px solid #e0dfd8;display:flex;flex-direction:column;}
.quad-title {padding:6px 10px;background:#f8f8f6;font-size:11px;font-weight:600;text-align:center;border-bottom:1px solid #e0dfd8;}
.quad-map {flex:1;}
#legend {display:flex;align-items:center;justify-content:center;gap:14px;flex-wrap:wrap;padding:7px 18px;background:#fff;border-top:1px solid #e0dfd8;font-size:11px;flex-shrink:0;}
.grad-bar {width:140px;height:8px;border-radius:4px;background:linear-gradient(to right,#22c55e,#86efac,#fde047,#fb923c,#ef4444);}
</style>
</head>
<body>
<div id="header">
  <h1>Winter Hill's Current Displacement (to Edgerly) vs. Brown's Proposed Displacement (to Winter Hill)</h1>
  <p>Same column = same school, before (top) and after (bottom) displacement &middot; same 0-""" + str(SHARED_MAX) + """ min color scale throughout</p>
</div>
<div id="grid">
  <div class="quad">
    <div class="quad-title">Winter Hill -- walking to OWN school</div>
    <div id="map-tl" class="quad-map"></div>
  </div>
  <div class="quad">
    <div class="quad-title">Brown -- walking to OWN school</div>
    <div id="map-tr" class="quad-map"></div>
  </div>
  <div class="quad">
    <div class="quad-title">Winter Hill -- CURRENT walk to Edgerly (Winter Hill temporary location)</div>
    <div id="map-bl" class="quad-map"></div>
  </div>
  <div class="quad">
    <div class="quad-title">Brown -- PROPOSED walk to Winter Hill (permanent future)</div>
    <div id="map-br" class="quad-map"></div>
  </div>
</div>
<div id="legend">
  <span style="font-size:11px">0 min</span><div class="grad-bar"></div><span style="font-size:11px">""" + str(SHARED_MAX) + """ min</span>
</div>
<script>
const whData = """ + json.dumps(wh_data) + """;
const brownOwn = """ + json.dumps(brown_own) + """;
const brownProposed = """ + json.dumps(brown_proposed) + """;
const schools = """ + json.dumps(SCHOOLS) + """;

const MIN_MIN = 0, MAX_MIN = """ + str(SHARED_MAX) + """;
const STOPS = [[0,[34,197,94]],[0.3,[134,239,172]],[0.55,[253,224,71]],[0.75,[251,146,60]],[1.0,[239,68,68]]];
function lerpColor(t) {
  t = Math.max(0, Math.min(1, t));
  let i = 0;
  while (i < STOPS.length - 2 && t > STOPS[i+1][0]) i++;
  const [t0,c0]=STOPS[i],[t1,c1]=STOPS[i+1],f=(t-t0)/(t1-t0);
  return "rgb("+Math.round(c0[0]+f*(c1[0]-c0[0]))+","+Math.round(c0[1]+f*(c1[1]-c0[1]))+","+Math.round(c0[2]+f*(c1[2]-c0[2]))+")";
}
function walkColor(mins) { return lerpColor((mins-MIN_MIN)/(MAX_MIN-MIN_MIN)); }
function starIcon(fill,stroke,size) {
  const svg='<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'" viewBox="0 0 24 24"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="'+fill+'" stroke="'+stroke+'" stroke-width="1.5"/></svg>';
  return L.divIcon({html:svg,className:'',iconAnchor:[size/2,size/2],iconSize:[size,size]});
}

function makeMap(id, center) {
  const map = L.map(id, {zoomControl:true}).setView(center,13);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{
    attribution:'&copy; OSM &copy; CARTO', maxZoom:19
  }).addTo(map);
  return map;
}

function plotPoints(map, points, valueKey, destMarker, destFill, destStroke) {
  points.forEach(p => {
    const v = p[valueKey];
    if (!v) return;
    L.circleMarker([p.lat, p.lon], {radius:5, fillColor:walkColor(v), color:'#fff', weight:1, fillOpacity:0.9})
      .addTo(map).bindPopup('<div style="font-weight:600">' + p.street + '</div><div>' + v + ' min</div>');
  });
  if (destMarker) {
    L.marker([destMarker.lat, destMarker.lon], {icon:starIcon(destFill||'#facc15',destStroke||'#a16207',24), zIndexOffset:1000})
      .addTo(map).bindPopup('<strong>' + destMarker.name + '</strong><br>' + destMarker.address);
  }
}

const center = [42.394,-71.100];
const mapTL = makeMap('map-tl', center);
plotPoints(mapTL, whData, 'walk_min_own_school', schools.winterhill);

const mapTR = makeMap('map-tr', center);
plotPoints(mapTR, brownOwn, 'walk_min_adj', schools.brown, '#a855f7', '#7e22ce');

const mapBL = makeMap('map-bl', center);
plotPoints(mapBL, whData, 'walk_min_edgerly', schools.edgerly);
L.marker([schools.winterhill.lat, schools.winterhill.lon], {icon:starIcon('#a855f7','#7e22ce',20), zIndexOffset:999})
  .addTo(mapBL).bindPopup('<strong>' + schools.winterhill.name + ' (current site)</strong><br>' + schools.winterhill.address);

const mapBR = makeMap('map-br', center);
plotPoints(mapBR, brownProposed, 'walk_min_adj', schools.winterhill);
L.marker([schools.brown.lat, schools.brown.lon], {icon:starIcon('#a855f7','#7e22ce',20), zIndexOffset:999})
  .addTo(mapBR).bindPopup('<strong>' + schools.brown.name + ' (current site)</strong><br>' + schools.brown.address);

let syncing = false;
const allMaps = [mapTL, mapTR, mapBL, mapBR];
allMaps.forEach(source => {
  source.on('move', function() {
    if (syncing) return;
    syncing = true;
    allMaps.forEach(target => { if (target !== source) target.setView(source.getCenter(), source.getZoom(), {animate:false}); });
    syncing = false;
  });
});
</script>
</body>
</html>"""

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"\nSaved {OUTPUT_FILE} ({len(html):,} bytes)")
    print("Open it directly in your browser.")


if __name__ == "__main__":
    main()
