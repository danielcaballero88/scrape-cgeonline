#!/bin/bash
set -e

# Load env vars
source .env

echo $DEPL_FILES

# Project base path to reference files.
BASE_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Delete the current script and requirements files
echo "Deleting remote files."
gcloud compute ssh \
    --zone $DEPL_ZONE \
    $DEPL_INSTANCE \
    --project $DEPL_PROJECT \
    --command="cd $DEPL_REMOTE_PATH && rm -rf $DEPL_FILES"

# Send the current files
echo "Sending new files."
rm -rf temp
mkdir temp
tar cf temp/temp.tar $DEPL_FILES

gcloud compute scp \
    --zone $DEPL_ZONE \
    --project $DEPL_PROJECT \
    --recurse "$BASE_PATH/temp/temp.tar" \
    "$DEPL_INSTANCE:$DEPL_REMOTE_PATH/"

gcloud compute ssh \
    --zone $DEPL_ZONE \
    $DEPL_INSTANCE  \
    --project $DEPL_PROJECT \
    --command="cd $DEPL_REMOTE_PATH && tar xf temp.tar"

# Install the latest requirements
echo "Installing requirements."
gcloud compute ssh \
    --zone $DEPL_ZONE \
    $DEPL_INSTANCE \
    --project $DEPL_PROJECT \
    --command="cd $DEPL_REMOTE_PATH && . .venv/bin/activate && pip install -r requirements.txt"
