# instamint-ipfs-tools
## Running Locally


```shell

git clone git@github.com:jamiels/instamint-ipfs-tools.git
cd instamint-ipfs-tools
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/production.txt
```
Create .env file
```
INFURA_IPFS_PROJECT_ID=<Project ID>
INFURA_IPFS_PROJECT_SECRET=<Project Secret>
```

Run main.py
```shell
source .venv/bin/activate
python main.py
```