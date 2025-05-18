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

print(token['access_token'])

resp = oauth.get("https://sh.dataspace.copernicus.eu/configuration/v1/wms/instances")
print(resp.content)

#print(resp)
instances = resp.json()#["instances"]
instance_id = instances[0]["id"]
#print(instances)
# pick the first one, or filter by name
#instance_id = instances[0]["id"]
print("Using instance:", instance_id)

#process_url = "https://sh.dataspace.copernicus.eu/api/v1/process"

evalscript = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B04",
        "dataMask"
      ]
    }],
    output: [
      {
        id: "output_B04",
        bands: 1,
        sampleType: "FLOAT32"
      },
      {
        id: "dataMask",
        bands: 1
      }]
  }
}
function evaluatePixel(samples) {
    return {
        output_B04: [samples.B04],
        dataMask: [samples.dataMask]
        }
}
"""

stats_request = {
  "input": {
    "bounds": {
      "bbox": [414315, 4958219, 414859, 4958819],
    "properties": {
        "crs": "http://www.opengis.net/def/crs/EPSG/0/32633"
        }
    },
    "data": [
      {
        "type": "sentinel-2-l2a",
        "dataFilter": {
            "mosaickingOrder": "leastRecent"
        },
      }
    ]
  },
  "aggregation": {
    "timeRange": {
            "from": "2020-07-04T00:00:00Z",
            "to": "2020-07-05T00:00:00Z"
      },
    "aggregationInterval": {
        "of": "P1D"
    },
    "evalscript": evalscript,
    "resx": 10,
    "resy": 10
  }
}

headers = {
  "Content-Type": "application/json",
  "Accept": "application/json",
  "Authorization": f"Bearer {token['access_token']}"
}

url = "https://services.sentinel-hub.com/api/v1/statistics"
response = oauth.request("POST", url=url , headers=headers, json=stats_request)
#response = oauth.request("POST", url=url , json=stats_request)
sh_statistics = response.json()
print(sh_statistics)