"""worldmap — an old sea chart of the world from Natural Earth coastlines (public domain, data/world_land_50m.geojson),
in the same style as the reel 7 East Asia chart: parchment land with a shaded coast and an ink coastline, a teal sea
lighter along the shore with ripple lines following the coast, and little wave marks out at sea.  Mercator, from the
Caribbean to Japan and from Scotland to the Cape of Good Hope (every place the name 'Japan' passed through).
chart_xy(lon, lat) gives the chart pixel of a place."""
import json
import os

import cv2
import numpy as np

from engine import HERE, INK, StrokeSet, noise, spline, stroke

K = 24.0                                  # chart pixels per degree of longitude
LON0, LON1 = -98.0, 152.0
LAT1, LAT0 = 63.0, -40.0
SWEEP = ((0, 0.3), (0.3, 1), (1, 0.2))


def _merc(lat):
    return np.degrees(np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)))


def chart_xy(lon, lat):
    return np.array([(lon - LON0) * K, (_merc(LAT1) - _merc(lat)) * K], np.float32)


def size():
    return int((LON1 - LON0) * K), int(chart_xy(0, LAT0)[1])


def world_chart():
    w, h = size()
    gj = json.load(open(os.path.join(HERE, 'data', 'world_land_50m.geojson')))
    land = np.zeros((h, w), np.uint8)
    for f in gj['features']:
        g = f['geometry']
        polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        for poly in polys:
            ring = np.array(poly[0], np.float64)
            if ring[:, 0].max() < LON0 - 5 or ring[:, 0].min() > LON1 + 5:
                continue
            lat = np.clip(ring[:, 1], -80, 84)
            pts = np.stack([(ring[:, 0] - LON0) * K, (_merc(LAT1) - _merc(lat)) * K], 1)
            cv2.fillPoly(land, [np.round(pts * 4).astype(np.int32)], 1, lineType=cv2.LINE_AA, shift=2)
            for hole in poly[1:]:
                hr = np.array(hole, np.float64)
                hp = np.stack([(hr[:, 0] - LON0) * K, (_merc(LAT1) - _merc(np.clip(hr[:, 1], -80, 84))) * K], 1)
                cv2.fillPoly(land, [np.round(hp * 4).astype(np.int32)], 0, lineType=cv2.LINE_AA, shift=2)
    L = land.astype(np.float32)
    dsea = cv2.distanceTransform((1 - land).astype(np.uint8), cv2.DIST_L2, 5)
    dland = cv2.distanceTransform(land, cv2.DIST_L2, 5)
    nz = noise(h, w, 220, 4, 6)
    sea_c = np.array([0.42, 0.57, 0.59], np.float32)
    deep_c = np.array([0.31, 0.46, 0.50], np.float32)
    coast_c = np.array([0.63, 0.73, 0.71], np.float32)
    s_mix = np.clip(dsea / 300, 0, 1)[..., None]
    sea = sea_c * (1 - s_mix) + deep_c * s_mix
    band = np.exp(-dsea / 12)[..., None]
    sea = sea * (1 - band * 0.6) + coast_c * band * 0.6
    sea *= (0.93 + 0.1 * nz)[..., None]
    rip = np.zeros((h, w), np.float32)
    for d0 in (18, 36):
        rip = np.maximum(rip, np.exp(-((dsea - d0) / 1.2) ** 2) * (dsea > 0))
    sea *= (1 - 0.2 * rip)[..., None]
    land_c = np.array([0.90, 0.84, 0.70], np.float32)
    lnd = land_c * (0.95 + 0.07 * nz)[..., None] * (1 - 0.1 * np.exp(-dland / 9))[..., None]
    img = sea * (1 - L[..., None]) + lnd * L[..., None]
    line = np.clip(np.exp(-(dsea / 1.3) ** 2) * (dsea > 0) + np.exp(-(dland / 0.9) ** 2) * (dland > 0), 0, 1) * 0.85
    ink = line
    rng = np.random.default_rng(5)
    wv = StrokeSet(w, h)
    n = 0
    while n < 260:
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        if dsea[int(y), int(x)] < 50:
            continue
        s = rng.uniform(12, 20)
        wv.add(stroke(w, h, spline([(x - s, y), (x - s * 0.4, y - s * 0.3), (x + s * 0.2, y), (x + s * 0.8, y - s * 0.3)], 6), 1.6,
                      ink=0.5, dry=0.5, profile=SWEEP, seed=400 + n), 0, 1)
        n += 1
    ink = np.maximum(ink, wv.render(9) * 0.55)
    img *= (1 - ink[..., None] * (1 - INK))
    return {'rgb': img.astype(np.float16), 'land': land}
