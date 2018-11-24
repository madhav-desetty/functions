# mercator tile grid 
This is a simple python Google Cloud function that burns a tile grid or grid union for a specific zoom level in  Web Mercator CRS, given an arbitary polygon in geojson format using [mercantile](https://github.com/mapbox/mercantile) and [supermercado](https://github.com/mapbox/supermercado) libraries 

# Deployment
```
git clone https://github.com/madhav-desetty/functions.git
cd functions/merctilegrid
gcloud functions deploy merctilegrid --runtime python37 --trigger-http
git clone https://github.com/madhav-desetty/functionsl.git
gcloud functions describe merctilegrid
```
It should look like this:
```
https://GCP_REGION-PROJECT_ID.cloudfunctions.net/merctilegrid 
```


# Usage
```
curl -X POST -H "Content-Type: application/json" -d 
{
  "aoi": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": {},
        "geometry": {
          "type": "Polygon",
          "coordinates": [
            [
              [
                -91.31561279296875,
                33.114549382824535
              ],
              [
                -90.68939208984375,
                33.114549382824535
              ],
              [
                -90.68939208984375,
                33.57343808567733
              ],
              [
                -91.31561279296875,
                33.57343808567733
              ],
              [
                -91.31561279296875,
                33.114549382824535
              ]
            ]
          ]
        }
      }
    ]
  },
  "zoom": 10,
  "op": "union"
}
https://GCP_REGION-PROJECT_ID.cloudfunctions.net/merctilegrid | geojsonio
```