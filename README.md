# Flexweb image scraper
This tool scrapes all images of the "Tijdlijn" of Flexkids/Flexweb.

Example output:
```
(.env) ted@laptopted ~/flexweb-scraper % python fetch.py
Fetched post 0-20 of 57
Fetched post 20-40 of 57
Fetched post 40-60 of 57
100%|██████████████████████████████████████████████████████████████████████████| 36/36 [00:00<00:00, 14969.26it/s]
(.env) ted@laptopted ~/flexweb-scraper % 
```
## Quickstart:
### Using virtualenv
```
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
SESSID = 'hexstring here' BASE_URL='https://organizationname.flexkids.nl' KIND_ID=number python fetch.py
```
### Using Docker
```
cp env.example my-env.txt
# Now fill in the my-env.txt with proper values
docker build . -t flexweb-scraper
mkdir output
docker run -t --env-file my-env.txt -v $(pwd)/output:/app/output flexweb-scraper
```