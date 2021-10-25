import os, copy, json, sys
import urllib
from pathlib import Path
import requests
from dotenv import load_dotenv
import pandas

import shutil

output_directory = './output'
if os.path.exists(output_directory):
    shutil.rmtree(output_directory)
    os.makedirs(output_directory)
else:
    os.makedirs(output_directory)

load_dotenv()
try:
    infura_ipfs_project_id= os.environ['INFURA_IPFS_PROJECT_ID']
    infura_ipfs_project_secret= os.environ['INFURA_IPFS_PROJECT_SECRET']
except KeyError as e:
    print(f"'{e.args[0]}'s  Environment variable is not properly set. Aborting")
    sys.exit(1)

with open('metadata_template.json') as f:
  json_template = json.load(f)

df = pandas.read_csv('input.csv', index_col='ID', parse_dates=['Vintage Date'])
#wasabi_images = df["WasabiURL"]

image_list = df.values.tolist()

for image in image_list:
    image_url = image[4]
    image_name =urllib.parse.urlparse(image_url).path.rstrip('/').split('/')[-1]
    image_path = "./output/" + image_name
    r = requests.get(image_url)
    with open(image_path, "wb") as f:
        f.write(r.content)

    image_files = {
        image_name: image_path,
    }
    response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=image_files, auth=(infura_ipfs_project_id,infura_ipfs_project_secret))
    ipfs_image_data = response.json()
    image.append(ipfs_image_data["Hash"])
    image.append("https://ipfs.io/ipfs/" + ipfs_image_data["Hash"])

    metadata_json = copy.deepcopy(json_template)
    metadata_json["name"] = image_name
    metadata_json["description"] = image_name
    # 'name', 'description', 'external_url', 'instagram_username', 'instagram_share_url',
    # 'instagram_direct_link', 'image_ipfs_cid', 'contract_address', 'vintage_date', 'token_id'
    metadata_json["external_url"] = "https://ipfs.io/ipfs/" + ipfs_image_data["Hash"]
    metadata_json["instagram_username"] = image[1]
    metadata_json["instagram_share_url"] = image[2]
    metadata_json["instagram_direct_link"] = image[3]
    metadata_json["image_ipfs_cid"] = ipfs_image_data["Hash"]
    metadata_json["contract_address"]
    metadata_json["vintage_date"]=image[5]
    metadata_json["token_id"] = image[0]

    metadata_json_file_name = Path(image_path).stem + ".json"
    metadata_json_file_path = "./output/" + metadata_json_file_name
    with open(metadata_json_file_path, 'w') as fp:
        json.dump(metadata_json, fp, default=str)
    with open(metadata_json_file_path, 'w') as fp:
        json.dump(metadata_json, fp, default=str)

    json_files = {
        metadata_json_file_name: metadata_json_file_path,
    }

    response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=json_files, auth=(infura_ipfs_project_id,infura_ipfs_project_secret))
    ipfs_metadata_data = response.json()
    image.append(ipfs_metadata_data["Hash"])
    image.append("https://ipfs.io/ipfs/" + ipfs_metadata_data["Hash"])
    image.append(ipfs_image_data["Hash"])
    image.append(image[0])
