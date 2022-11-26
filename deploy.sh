#!/bin/bash
set -e

# Delete the current script and requirements files
echo "Deleting remote files."
REMOTE_PATH="/home/dancab/scripts/scrape-cgeonline"
gcloud compute ssh --zone "us-central1-a" "dc-free-vm"  --project "dc-2022-369305" \
--command="cd $REMOTE_PATH && rm -f requirements.txt scrape_cgeonline.py gmail_api_helper.py"

# Send the current files
echo "Sending new files."
tar cf temp.tar scrape_cgeonline.py requirements.txt gmail_api_helper.py

gcloud compute scp --zone "us-central1-a" --project "dc-2022-369305" \
--recurse "$PWD/temp.tar" "dc-free-vm:$REMOTE_PATH/"

gcloud compute ssh --zone "us-central1-a" "dc-free-vm"  --project "dc-2022-369305" \
--command="cd $REMOTE_PATH && tar xf temp.tar"

# Install the latest requirements
echo "Installing requirements."
gcloud compute ssh --zone "us-central1-a" "dc-free-vm"  --project "dc-2022-369305" \
--command="cd $REMOTE_PATH && . .venv/bin/activate && pip install -r requirements.txt"
