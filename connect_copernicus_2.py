from dotenv import load_dotenv
import os
from sentinelhub import SHConfig, SentinelHubSession, BBox, CRS, bbox_to_dimensions, SentinelHubRequest, DataCollection, MimeType, SentinelHubDownloadClient, DownloadRequest
import numpy as np
import rasterio
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import rasterio
import matplotlib.pyplot as plt
import numpy as np

load_dotenv()

config = SHConfig()

client_id  = os.getenv("SH_CLIENT_ID")
client_secret = os.getenv("SH_CLIENT_SECRET")

client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)

token = oauth.fetch_token(token_url='https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
                          client_secret=client_secret, include_client_id=True)

resp = oauth.get("https://sh.dataspace.copernicus.eu/configuration/v1/wms/instances")
print(resp.content)

##############################################################################################

# after fetching the token…
resp = oauth.get("https://sh.dataspace.copernicus.eu/configuration/v1/wms/instances")
#print(resp)
instances = resp.json()#["instances"]
instance_id = instances[0]["id"]
#print(instances)
# pick the first one, or filter by name
#instance_id = instances[0]["id"]
print("Using instance:", instance_id)

process_url = "https://sh.dataspace.copernicus.eu/api/v1/process"

# 1) Define an NDVI evalscript
evalscript_ndvi = """
//VERSION=3
function setup() {
  return { input: ["B04","B08"], output: { bands:1, sampleType:"UINT16" } };
}
function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  // scale to 0–65535 for UINT16
  return [ Math.round((ndvi + 1) * 32767.5) ];
}
"""

# 2) Build the JSON payload
payload = {
  "input": {
    "bounds": { "bbox": [26.018784, 44.389409, 26.187698, 44.488495] },
    "data": [{
      "type": "sentinel-2-l2a",
      "dataFilter": {
        "timeRange": { "from": "2025-05-01T00:00:00Z", "to": "2025-05-02T23:59:59Z" }
      }
    }]
  },
  "evalscript": evalscript_ndvi,
  "output": {
    "responses": [{
      "identifier": "default",
      "format": { "type": "image/tiff" }
    }]
  }
}

proc_resp = oauth.post(process_url, json=payload)
proc_resp.raise_for_status()

# 3) Save the GeoTIFF
with open("./data/bucharest_ndvi.tif", "wb") as f:
    f.write(proc_resp.content)

print("Saved NDVI GeoTIFF → bucharest_ndvi.tif")

with rasterio.open("./data/bucharest_ndvi.tif") as src:
    ndvi = src.read(1)  # Read first band

ndvi = ndvi.astype("float32")
ndvi[ndvi == 0] = np.nan
ndvi[ndvi == 65535] = np.nan
ndvi = (ndvi / 32767.5) - 1  # rescale to -1 to 1 if needed

# Visualize
plt.imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1)
plt.colorbar(label="NDVI")
plt.title("NDVI - Bucharest")
plt.axis("off")
plt.show()
