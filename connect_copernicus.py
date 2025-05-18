from dotenv import load_dotenv
import os
from sentinelhub import SHConfig, SentinelHubSession, BBox, CRS, bbox_to_dimensions, SentinelHubRequest, DataCollection, MimeType, SentinelHubDownloadClient, DownloadRequest
import numpy as np
import rasterio

load_dotenv()

config = SHConfig()

config.sh_client_id  = os.getenv("SH_CLIENT_ID")
config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")
config.sh_base_url   = os.getenv("SH_BASE_URL")
config.sh_auth_base_url = os.getenv("SH_AUTH_BASE_URL")
#config.sh_token_url  = os.getenv("SH_TOKEN_URL")
config.instance_id   = os.getenv("INSTANCE_ID")

print("Instance ID:      ", config.instance_id)
print("Client ID:        ", config.sh_client_id[:8], "…")
print("Token URL:        ", config.sh_token_url)
print("Base URL:",  config.sh_base_url)

# Try requesting a token
session = SentinelHubSession(config=config)
#token = session.get_session_token()
#print("Access token OK, expires in:", token["expires_in"], "seconds")

'''bbox = BBox(bbox=[26.02, 44.42, 26.15, 44.50], crs=CRS.WGS84)
# 10 m resolution
resolution = 10  
size = bbox_to_dimensions(bbox, resolution=resolution)

# 3) Write an Evalscript for NDVI (Sentinel-2 L2A)
evalscript_ndvi = """
//VERSION=3
function setup() {
  return {
    input: ["B04","B08"],
    output: {bands:1, sampleType: "FLOAT32"}
  }
}
function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi];
}
"""

request = SentinelHubRequest(
    evalscript=evalscript_ndvi,
    input_data=[SentinelHubRequest.input_data(
        DataCollection.SENTINEL2_L2A, 
        time_interval=('2025-05-01','2025-05-02')
    )],
    responses=[SentinelHubRequest.output_response('default', MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
    data_folder='data/ndvi'           # where to cache tiles & metadata
)

ndvi_data = request.get_data()

arr = ndvi_data[0]
print("NDVI array shape:", arr.shape)
print("NDVI stats:", np.nanmin(arr), np.nanmax(arr), np.nanmean(arr))

output_path = './data/ndvi_bucharest.tif'
with rasterio.open(
    output_path, 'w',
    driver='GTiff',
    height=arr.shape[0],
    width=arr.shape[1],
    count=1,
    dtype=arr.dtype,
    crs=bbox.crs.pyproj_crs(),
    transform=rasterio.transform.from_bounds(*bbox.bounds, arr.shape[1], arr.shape[0])
) as dst:
    dst.write(arr, 1)

print(f"Saved NDVI GeoTIFF → {output_path}")'''