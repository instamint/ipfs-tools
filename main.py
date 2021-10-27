import os, copy, json, sys
import urllib
from pathlib import Path
import requests
from dotenv import load_dotenv
import pandas
import shutil

# Base Configurations
INPUT_FILE = 'test.csv'
OUTPUT_FILE = 'output_test.csv'
META_DATA_TEMPLATE_FILE = 'metadata_template.json'
OUTPUT_DIRECTORY = './output/'
WALLET_ADDRESS = "0x6FCA0F70BcC4a86786c79414F8E84BD542F7c250"
INFURA_IPFS_API_ADD_URL = "https://ipfs.infura.io:5001/api/v0/add"
IPFS_BASE_URL = "https://ipfs.io/ipfs/"

# Remove output directory if exists. Else create one.
if os.path.exists(OUTPUT_DIRECTORY):
    shutil.rmtree(OUTPUT_DIRECTORY)
    os.makedirs(OUTPUT_DIRECTORY)
else:
    os.makedirs(OUTPUT_DIRECTORY)

# Read IPFS credentials from .env
load_dotenv()
try:
    INFURA_IPFS_PROJECT_ID= os.environ['INFURA_IPFS_PROJECT_ID']
    INFURA_IPFS_PROJECT_SECRET= os.environ['INFURA_IPFS_PROJECT_SECRET']
except KeyError as e:
    print(f"'{e.args[0]}'s  Environment variable is not properly set. Aborting")
    sys.exit(1)

with open(META_DATA_TEMPLATE_FILE) as f:
  json_template = json.load(f)

df = pandas.read_csv(INPUT_FILE)

image_list = df.to_dict(orient='records')
for image in image_list:
    image["Instagram Username"] = image["Instagram ID"]
    image_url = image["WasabiURL"]
    image_name =urllib.parse.urlparse(image_url).path.rstrip('/').split('/')[-1]
    image_path = OUTPUT_DIRECTORY + image_name
    r = requests.get(image_url)
    with open(image_path, "wb") as f:
        f.write(r.content)

    image_files = {
        image_name: open(image_path, "rb"),
    }
    response = requests.post(INFURA_IPFS_API_ADD_URL, files=image_files, auth=(INFURA_IPFS_PROJECT_ID,INFURA_IPFS_PROJECT_SECRET))
    ipfs_image_data = response.json()
    image["Image IPFS CID"] = ipfs_image_data["Hash"]
    image["Image IPFS URL"] = IPFS_BASE_URL + ipfs_image_data["Hash"]

    # Generate metadata json from metadata template
    metadata_json = copy.deepcopy(json_template)
    metadata_json["name"] = image_name
    metadata_json["description"] = image_name
    metadata_json["external_url"] = IPFS_BASE_URL + ipfs_image_data["Hash"]
    metadata_json["instagram_username"] = image["Instagram ID"]
    metadata_json["instagram_share_url"] = image["Instagram Pic Share URL"]
    metadata_json["instagram_direct_link"] = image["Instagram Direct Link"]
    metadata_json["image_ipfs_cid"] = ipfs_image_data["Hash"]
    metadata_json["contract_address"] = WALLET_ADDRESS
    metadata_json["vintage_date"]=image["Vintage Date"]
    metadata_json["token_id"] = image["ID"]

    metadata_json_file_name = Path(image_path).stem + ".json"
    metadata_json_file_path = OUTPUT_DIRECTORY + metadata_json_file_name
    with open(metadata_json_file_path, 'w') as fp:
        json.dump(metadata_json, fp, default=str)

    json_files = {
        metadata_json_file_name: open(metadata_json_file_path, "rb"),
    }

    response = requests.post(INFURA_IPFS_API_ADD_URL, files=json_files, auth=(INFURA_IPFS_PROJECT_ID,INFURA_IPFS_PROJECT_SECRET))
    ipfs_metadata_data = response.json()
    image["Metadata CID"] = ipfs_metadata_data["Hash"]
    image["Metadata IPFS URL"] = IPFS_BASE_URL + ipfs_metadata_data["Hash"]
    image["Contract Address"] = WALLET_ADDRESS
    image["Token ID"] = image["ID"]

#Write image_list dictionary to csv
colnames = ['ID',
 'Instagram Username',
 'Instagram Pic Share URL',
 'Instagram Direct Link',
 'WasabiURL',
 'Vintage Date',
 'Image IPFS CID',
 'Image IPFS URL',
 'Metadata CID',
 'Metadata IPFS URL',
 'Contract Address',
 'Token ID']
output_df = pandas.DataFrame(image_list, columns=colnames)
output_df.to_csv(OUTPUT_FILE, index=False)