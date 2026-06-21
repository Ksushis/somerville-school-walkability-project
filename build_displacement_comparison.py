"""
WINTER HILL'S REAL DISPLACEMENT vs. BROWN'S PROPOSED DISPLACEMENT
=====================================================================
Builds a three-pane comparison:
  1. Winter Hill students walking to their OWN school (if it were open)
  2. Winter Hill students ACTUALLY walking to Edgerly right now (real,
     current displacement)
  3. Brown students walking to Winter Hill under the PROPOSED
     redistricting (future, permanent displacement)

The argument: Winter Hill's current Edgerly displacement is a real-world
preview of what Brown's catchment would experience permanently if
reassigned. If Edgerly's walk times are comparable to or worse than
Brown's proposed walk times, that's direct evidence the proposal would
create a hardship Winter Hill is already living through.

This does NOT call any API and does NOT need Claude.

USAGE:
  Place this script in the same folder as:
    - winterhill_vs_edgerly_export.json
    - proposed_state_export.json (Brown -> Winter Hill data, already used
      for the side-by-side map)
  Run: python3 build_displacement_comparison.py
  Output: winterhill_displacement_vs_brown_proposed.html
"""
import json

WH_EDGERLY_FILE = "winterhill_vs_edgerly_export.json"
BROWN_PROPOSED_FILE = "proposed_state_export.json"
OUTPUT_FILE = "winterhill_displacement_vs_brown_proposed.html"

SHARED_MAX = 35

SCHOOLS = [
    {"name": "Brown School", "lat": 42.397302, "lon": -71.114010, "address": "201 Willow Avenue"},
    {"name": "Winter Hill Community Innovation School", "lat": 42.391667, "lon": -71.098797, "address": "115 Sycamore Street"},
]
EDGERLY = {"name": "Edgerly (Winter Hill Temporary Location)", "lat": 42.38798214035693,
           "lon": -71.08728780221357, "address": "33 Cross Street"}


def main():
    try:
        with open(WH_EDGERLY_FILE) as f:
            wh_data = json.load(f)
        with open(BROWN_PROPOSED_FILE) as f:
            proposed = json.load(f)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    brown_proposed = [d for d in proposed if d.get("zone") == "Brown (proposed -> Winter Hill)"]
    print(f"Winter Hill addresses: {len(wh_data)}")
    print(f"Brown (proposed) addresses: {len(brown_proposed)}")

    max_own = max((d["walk_min_own_school"] for d in wh_data if d.get("walk_min_own_school")), default=0)
    max_edgerly = max((d["walk_min_edgerly"] for d in wh_data if d.get("walk_min_edgerly")), default=0)
    max_brown = max((d["walk_min_adj"] for d in brown_proposed if d.get("walk_min_adj")), default=0)
    print(f"Max walk -- Own school: {max_own} min, Edgerly (current): {max_edgerly} min, Brown proposed: {max_brown} min")

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
#maps {flex:1;display:flex;}
.map-pane {flex:1;display:flex;flex-direction:column;border-right:1px solid #e0dfd8;}
.map-pane:last-child {border-right:none;}
.pane-title {padding:6px 10px;background:#f8f8f6;font-size:11px;font-weight:600;text-align:center;border-bottom:1px solid #e0dfd8;}
.pane-map {flex:1;}
#legend {display:flex;align-items:center;justify-content:center;gap:14px;flex-wrap:wrap;padding:7px 18px;background:#fff;border-top:1px solid #e0dfd8;font-size:11px;flex-shrink:0;}
.leg {display:flex;align-items:center;gap:5px;}
.grad-bar {width:140px;height:8px;border-radius:4px;background:linear-gradient(to right,#22c55e,#86efac,#fde047,#fb923c,#ef4444);}
</style>
</head>
<body>
<div id="header">
  <h1>Winter Hill's Current Real Displacement (to Edgerly) vs. Brown's Proposed Permanent Displacement (to Winter Hill)</h1>
  <p>Same 0-""" + str(SHARED_MAX) + """ min color scale across all three panes &middot; Winter Hill's present-day Edgerly walk is a real-world preview of what the Brown redistricting proposal would create permanently</p>
</div>
<div id="maps">
  <div class="map-pane">
    <div class="pane-title">Winter Hill -- walking to OWN school (baseline)</div>
    <div id="map-1" class="pane-map"></div>
  </div>
  <div class="map-pane">
    <div class="pane-title">Winter Hill -- ACTUALLY walking to Edgerly (current reality)</div>
    <div id="map-2" class="pane-map"></div>
  </div>
  <div class="map-pane">
    <div class="pane-title">Brown -- PROPOSED to walk to Winter Hill (permanent future)</div>
    <div id="map-3" class="pane-map"></div>
  </div>
</div>
<div id="legend">
  <span style="font-size:11px">0 min</span><div class="grad-bar"></div><span style="font-size:11px">""" + str(SHARED_MAX) + """ min</span>
</div>
<script>
const whData = """ + json.dumps(wh_data) + """;
const brownProposed = """ + json.dumps(brown_proposed) + """;
const schools = """ + json.dumps(SCHOOLS) + """;
const edgerly = """ + json.dumps(EDGERLY) + """;

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

function makeMap(id) {
  const map = L.map(id, {zoomControl:true}).setView([42.394,-71.100],13);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{
    attribution:'&copy; OSM &copy; CARTO', maxZoom:19
  }).addTo(map);
  return map;
}

function plotPoints(map, points, valueKey, destMarker) {
  points.forEach(p => {
    const v = p[valueKey];
    if (!v) return;
    L.circleMarker([p.lat, p.lon], {radius:5, fillColor:walkColor(v), color:'#fff', weight:1, fillOpacity:0.9})
      .addTo(map).bindPopup('<div style="font-weight:600">' + p.street + '</div><div>' + v + ' min</div>');
  });
  if (destMarker) {
    L.marker([destMarker.lat, destMarker.lon], {icon:starIcon('#facc15','#a16207',24), zIndexOffset:1000})
      .addTo(map).bindPopup('<strong>' + destMarker.name + '</strong><br>' + destMarker.address);
  }
}

const map1 = makeMap('map-1');
plotPoints(map1, whData, 'walk_min_own_school', schools[1]);

const map2 = makeMap('map-2');
plotPoints(map2, whData, 'walk_min_edgerly', edgerly);

const map3 = makeMap('map-3');
plotPoints(map3, brownProposed, 'walk_min_adj', schools[1]);
L.marker([schools[0].lat, schools[0].lon], {icon:starIcon('#a855f7','#7e22ce',24), zIndexOffset:1000})
  .addTo(map3).bindPopup('<strong>' + schools[0].name + ' (current site)</strong><br>' + schools[0].address);

let syncing = false;
function syncAll(maps) {
  maps.forEach(source => {
    source.on('move', function() {
      if (syncing) return;
      syncing = true;
      maps.forEach(target => { if (target !== source) target.setView(source.getCenter(), source.getZoom(), {animate:false}); });
      syncing = false;
    });
  });
}
syncAll([map1, map2, map3]);
</script>
</body>
</html>"""

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"\nSaved {OUTPUT_FILE} ({len(html):,} bytes)")
    print("Open it directly in your browser.")


if __name__ == "__main__":
    main()
