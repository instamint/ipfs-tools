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