"""Lokaler Hilfsdienst fuer Pipeline-CRM.html: Grundstueck (Flurstueck) anhand von
Koordinaten ermitteln und Laenge/Breite ueber die minimal umschliessende
Rechteck-Flaeche berechnen.

Datenquelle: offener INSPIRE-WFS "Flurstuecke/Grundstuecke ALKIS" des Landes
Hessen (Datenlizenz Deutschland - Zero 2.0), bereitgestellt vom HVBG.

Start:   python grundstueck_service.py
Aufruf:  GET http://127.0.0.1:5001/grundstueck?lat=50.68&lng=8.69

Nur Python-Standardbibliothek noetig, kein pip install erforderlich.
"""

import json
import math
import urllib.request
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

WFS_URL = "https://inspire-hessen.de/ows/services/org.2.07247d95-adc7-4c7d-9c7a-ed17af855317_wfs"
NS = {
    'wfs': 'http://www.opengis.net/wfs/2.0',
    'gml': 'http://www.opengis.net/gml/3.2',
    'cp': 'http://inspire.ec.europa.eu/schemas/cp/4.0',
}

BORIS_WFS_URL = "https://www.gds.hessen.de/wfs2/boris/cgi-bin/brw/2024/wfs"
BORIS_NS = {
    'wfs': 'http://www.opengis.net/wfs/2.0',
    'gml': 'http://www.opengis.net/gml/3.2',
    'boris': 'http://www.adv-online.de/namespaces/adv/brm/2.1',
}
# Nutzungsart-Kuerzel laut BORIS/ALKIS-Kodeliste (die gebraeuchlichsten)
BORIS_NUTZUNG = {
    'W': 'Wohnbaufläche', 'G': 'Gewerbefläche', 'M': 'Gemischte Baufläche',
    'L': 'Landwirtschaftsfläche', 'F': 'Forstwirtschaftsfläche', 'S': 'Fläche besonderer funktionaler Prägung',
}

PORT = 5001


def fetch_parcels(lat, lng, half_deg=0.0015):
    bbox = f"{lat-half_deg},{lng-half_deg},{lat+half_deg},{lng+half_deg},urn:ogc:def:crs:EPSG::4326"
    url = (
        f"{WFS_URL}?SERVICE=WFS&REQUEST=GetFeature&VERSION=2.0.0"
        f"&TYPENAMES=cp:CadastralParcel&BBOX={bbox}&COUNT=200"
    )
    with urllib.request.urlopen(url, timeout=15) as resp:
        xml_bytes = resp.read()
    root = ET.fromstring(xml_bytes)
    parcels = []
    for member in root.findall('wfs:member', NS):
        parcel_el = member.find('cp:CadastralParcel', NS)
        if parcel_el is None:
            continue
        pos_list_el = parcel_el.find('.//gml:posList', NS)
        if pos_list_el is None or not pos_list_el.text:
            continue
        nums = [float(n) for n in pos_list_el.text.split()]
        coords = list(zip(nums[0::2], nums[1::2]))  # (lat, lon) Paare
        area_el = parcel_el.find('cp:areaValue', NS)
        area = float(area_el.text) if area_el is not None and area_el.text else None
        label_el = parcel_el.find('cp:label', NS)
        ref_el = parcel_el.find('cp:nationalCadastralReference', NS)
        parcels.append({
            'coords': coords,
            'area_official': area,
            'label': label_el.text if label_el is not None else None,
            'ref': ref_el.text if ref_el is not None else None,
        })
    return parcels


def _point_to_segment_dist2(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return (px - ax) ** 2 + (py - ay) ** 2
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    cx, cy = ax + t * dx, ay + t * dy
    return (px - cx) ** 2 + (py - cy) ** 2


def point_to_polygon_dist2(lat, lng, coords):
    """Kuerzeste Distanz^2 (in Grad) vom Punkt zu einer Kante des Polygons.
    Wichtig: Abstand zur naechsten KANTE, nicht zum naechsten Eckpunkt --
    ein langes Polygon (z.B. Bahnstrecke) hat sonst einen zufaellig nahen
    Eckpunkt, obwohl der Punkt weit von der eigentlichen Flaeche entfernt ist."""
    best = None
    n = len(coords)
    for i in range(n):
        lat1, lon1 = coords[i]
        lat2, lon2 = coords[(i + 1) % n]
        d2 = _point_to_segment_dist2(lng, lat, lon1, lat1, lon2, lat2)
        if best is None or d2 < best:
            best = d2
    return best if best is not None else float('inf')


def fetch_bodenrichtwertzonen(lat, lng, half_deg=0.004):
    bbox = f"{lat-half_deg},{lng-half_deg},{lat+half_deg},{lng+half_deg},urn:ogc:def:crs:EPSG::4326"
    url = (
        f"{BORIS_WFS_URL}?SERVICE=WFS&REQUEST=GetFeature&VERSION=2.0.0"
        f"&TYPENAMES=boris:BR_BodenrichtwertZonal&BBOX={bbox}"
        f"&SRSNAME=urn:ogc:def:crs:EPSG::4326&COUNT=200"
    )
    with urllib.request.urlopen(url, timeout=15) as resp:
        xml_bytes = resp.read()
    root = ET.fromstring(xml_bytes)
    zonen = []
    for member in root.findall('wfs:member', BORIS_NS):
        zone_el = member.find('boris:BR_BodenrichtwertZonal', BORIS_NS)
        if zone_el is None:
            continue
        pos_list_el = zone_el.find('.//gml:posList', BORIS_NS)
        if pos_list_el is None or not pos_list_el.text:
            continue
        nums = [float(n) for n in pos_list_el.text.split()]
        coords = list(zip(nums[0::2], nums[1::2]))  # (lat, lon) Paare
        wert_el = zone_el.find('boris:bodenrichtwert', BORIS_NS)
        wert = float(wert_el.text) if wert_el is not None and wert_el.text else None
        stichtag_el = zone_el.find('boris:stichtag', BORIS_NS)
        nutzung_el = zone_el.find('.//boris:art', BORIS_NS)
        entwicklung_el = zone_el.find('boris:entwicklungszustand', BORIS_NS)
        gemarkung_el = zone_el.find('.//boris:BR_Gemarkung/boris:name', BORIS_NS)
        nummer_el = zone_el.find('boris:bodenrichtwertNummer', BORIS_NS)
        zonen.append({
            'coords': coords,
            'bodenrichtwert': wert,
            'stichtag': stichtag_el.text if stichtag_el is not None else None,
            'nutzung': nutzung_el.text if nutzung_el is not None else None,
            'entwicklungszustand': entwicklung_el.text if entwicklung_el is not None else None,
            'gemarkung': gemarkung_el.text if gemarkung_el is not None else None,
            'nummer': nummer_el.text if nummer_el is not None else None,
        })
    return zonen


def find_bodenrichtwert(lat, lng):
    zonen = fetch_bodenrichtwertzonen(lat, lng)
    if not zonen:
        return None
    containing = [z for z in zonen if z['bodenrichtwert'] is not None and point_in_polygon(lat, lng, z['coords'])]
    if containing:
        zone = containing[0]
    else:
        mit_wert = [z for z in zonen if z['bodenrichtwert'] is not None]
        if not mit_wert:
            return None
        zone = min(mit_wert, key=lambda z: point_to_polygon_dist2(lat, lng, z['coords']))
    return {
        'bodenrichtwert_eur_m2': zone['bodenrichtwert'],
        'bodenrichtwert_stichtag': zone['stichtag'],
        'bodenrichtwert_nutzung': BORIS_NUTZUNG.get(zone['nutzung'], zone['nutzung']),
        'bodenrichtwert_gemarkung': zone['gemarkung'],
        'bodenrichtwert_nummer': zone['nummer'],
    }


def point_in_polygon(lat, lng, coords):
    x, y = lng, lat
    inside = False
    n = len(coords)
    j = n - 1
    for i in range(n):
        yi, xi = coords[i]
        yj, xj = coords[j]
        if (yi > y) != (yj > y):
            x_intersect = (xj - xi) * (y - yi) / ((yj - yi) or 1e-15) + xi
            if x < x_intersect:
                inside = not inside
        j = i
    return inside


def to_local_xy(coords, lat0, lng0):
    m_per_deg_lat = 111320.0
    m_per_deg_lng = 111320.0 * math.cos(math.radians(lat0))
    return [((lon - lng0) * m_per_deg_lng, (lat - lat0) * m_per_deg_lat) for lat, lon in coords]


def convex_hull(points):
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def min_bounding_rectangle(points_xy):
    """Rotating-calipers: kleinste umschliessende Rechteck-Flaeche ueber die
    konvexe Huelle. Liefert (Seite1_m, Seite2_m)."""
    hull = convex_hull(points_xy)
    n = len(hull)
    if n < 3:
        xs = [p[0] for p in points_xy]
        ys = [p[1] for p in points_xy]
        return max(xs) - min(xs), max(ys) - min(ys)
    best_area = None
    best_dims = (0.0, 0.0)
    for i in range(n):
        x1, y1 = hull[i]
        x2, y2 = hull[(i + 1) % n]
        edge_angle = math.atan2(y2 - y1, x2 - x1)
        c, s = math.cos(-edge_angle), math.sin(-edge_angle)
        rotated = [(px*c - py*s, px*s + py*c) for px, py in hull]
        xs = [p[0] for p in rotated]
        ys = [p[1] for p in rotated]
        w = max(xs) - min(xs)
        h = max(ys) - min(ys)
        area = w * h
        if best_area is None or area < best_area:
            best_area = area
            best_dims = (w, h)
    return best_dims


def polygon_area_shoelace(points_xy):
    area = 0.0
    n = len(points_xy)
    for i in range(n):
        x1, y1 = points_xy[i]
        x2, y2 = points_xy[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def find_grundstueck(lat, lng):
    parcels = fetch_parcels(lat, lng)
    if not parcels:
        parcels = fetch_parcels(lat, lng, half_deg=0.004)
    if not parcels:
        return None

    containing = [p for p in parcels if point_in_polygon(lat, lng, p['coords'])]
    if containing:
        chosen = min(containing, key=lambda p: p['area_official'] or float('inf'))
    else:
        chosen = min(parcels, key=lambda p: point_to_polygon_dist2(lat, lng, p['coords']))

    xy = to_local_xy(chosen['coords'], lat, lng)
    side_a, side_b = min_bounding_rectangle(xy)
    length, width = (side_a, side_b) if side_a >= side_b else (side_b, side_a)
    area_calc = polygon_area_shoelace(xy)
    area_qm = chosen['area_official'] if chosen['area_official'] is not None else area_calc

    result = {
        'ok': True,
        'label': chosen['label'],
        'nationalCadastralReference': chosen['ref'],
        'area_qm': round(area_qm, 1),
        'length_m': round(length, 2),
        'width_m': round(width, 2),
        'polygon': [[c[0], c[1]] for c in chosen['coords']],
    }

    try:
        brw = find_bodenrichtwert(lat, lng)
    except Exception as exc:
        brw = None
        print(f"Bodenrichtwert-Abfrage fehlgeschlagen: {exc}")
    if brw:
        result.update(brw)

    return result


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            self._send_json({'ok': True, 'usage': '/grundstueck?lat=..&lng=..'})
            return
        if parsed.path != '/grundstueck':
            self._send_json({'ok': False, 'error': 'Unbekannter Endpunkt. Nutze /grundstueck?lat=..&lng=..'}, 404)
            return
        qs = parse_qs(parsed.query)
        try:
            lat = float(qs['lat'][0])
            lng = float(qs['lng'][0])
        except (KeyError, ValueError, IndexError):
            self._send_json({'ok': False, 'error': 'Parameter lat und lng erforderlich (Dezimalgrad).'}, 400)
            return
        try:
            result = find_grundstueck(lat, lng)
        except Exception as exc:
            self._send_json({'ok': False, 'error': f'Abfrage beim Geoportal Hessen fehlgeschlagen: {exc}'}, 502)
            return
        if result is None:
            self._send_json({'ok': False, 'error': 'Kein Flurstück an dieser Position gefunden.'}, 404)
            return
        self._send_json(result)

    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    print(f"Grundstücks-Dienst läuft auf http://127.0.0.1:{PORT}/grundstueck?lat=..&lng=..")
    print("Wird von Pipeline-CRM.html über den Button 'Grundstück automatisch erfassen' aufgerufen.")
    print("Beenden mit Strg+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
