import mercantile 
import logging
from supermercado import edge_finder, uniontiles, burntiles, super_utils as sutils
import json

import numpy as np
import io
import rasterio
from flask import make_response, jsonify
from rasterio import Affine

def compute_grid(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    if request_json:    
        gjson = request_json.get('aoi')
        zoom = request_json.get('zoom')
        op = request_json.get('op')
        if op == 'union':
         	return compute_grid_union(gjson,zoom)
        elif op == 'burn':
            return compute_grid_burn(gjson,zoom)
        else: 
            return make_response(jsonify({'error': 'Invalid Op specified in the JSON body'}), 400)
    else:
        return make_response(jsonify({'error': 'Invalid JSON body'}), 400)
   

def compute_grid_burn(geojson,zoom):
    features = [f for f in sutils.filter_polygons(geojson)]
    tile_indices = burntiles.burn(geojson["features"], zoom)
    features = [] 
    col_xs = []
    col_ys = []

    for tindex in tile_indices:
        feature = mercantile.feature(tindex)
        bbox = feature['bbox']
        w, s, e, n = bbox
        col_xs.extend([w, e])
        col_ys.extend([s, n])
        features.append(feature)

    bbox = [min(col_xs), min(col_ys), max(col_xs), max(col_ys)]
    return json.dumps({
                'type': 'FeatureCollection',
                'bbox': bbox, 'features': features}) 

def compute_grid_union(geojson,zoom):
    features = [f for f in sutils.filter_polygons(geojson)]
    tiles = burntiles.burn(geojson["features"], zoom)
    xmin, xmax, ymin, ymax = sutils.get_range(tiles)
    zoom = sutils.get_zoom(tiles)
    burn = sutils.burnXYZs(tiles, xmin, xmax, ymin, ymax, 0)
    nw = mercantile.xy(*mercantile.ul(xmin, ymin, zoom))
    se = mercantile.xy(*mercantile.ul(xmax + 1, ymax + 1, zoom))
    aff = Affine(((se[0] - nw[0]) / float(xmax - xmin + 1)), 0.0, nw[0],
        0.0, -((nw[1] - se[1]) / float(ymax - ymin + 1)), nw[1])
    unprojecter = sutils.Unprojecter()
    unionedTiles = [
        {
            'geometry': unprojecter.unproject(feature),
            'properties': {},
            'type': 'Feature'
        } for feature, shapes in rasterio.features.shapes(np.asarray(np.flipud(np.rot90(burn)).astype(np.uint8), order='C'), transform=aff) if shapes == 1
    ]
    
    ufeatures = []
    for u in unionedTiles:
        ufeatures.append(u)
        
    return json.dumps({
        'type': 'FeatureCollection',
         'features': ufeatures}) 