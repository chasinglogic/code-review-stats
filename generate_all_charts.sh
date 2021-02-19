#!/usr/bin/env bash

source env/bin/activate

if [[ -z $SKIP_DOWNLOAD ]]; then
  python ./download_all_data.py
fi

python ./transform_data.py

python ./visualize_data.py -f data/backend/transformed.json data/backend_report.html
python ./visualize_data.py -f data/frontend/transformed.json data/frontend_report.html
python ./visualize_data.py -f data/ta/transformed.json data/ta_report.html
