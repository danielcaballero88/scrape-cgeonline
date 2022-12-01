#!/bin/bash
set -e

# Project base path to reference files.
BASE_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Delete the current script and requirements files
echo "Deleting remote files."
REMOTE_PATH="/home/dancab/scripts/scrape-cgeonline"
gcloud compute ssh --zone "us-central1-a" "dc-free-vm"  --project "dc-2022-369305" \
--command="cd $REMOTE_PATH && rm -rf requirements.txt src main.py"

# Send the current files
echo "Sending new files."
tar cf temp/temp.tar requirements.txt src main.py

gcloud compute scp --zone "us-central1-a" --project "dc-2022-369305" \
--recurse "$BASE_PATH/temp/temp.tar" "dc-free-vm:$REMOTE_PATH/"

gcloud compute ssh --zone "us-central1-a" "dc-free-vm"  --project "dc-2022-369305" \
--command="cd $REMOTE_PATH && tar xf temp.tar"

# Install the latest requirements
echo "Installing requirements."
gcloud compute ssh --zone "us-central1-a" "dc-free-vm"  --project "dc-2022-369305" \
--command="cd $REMOTE_PATH && . .venv/bin/activate && pip install -r requirements.txt"
