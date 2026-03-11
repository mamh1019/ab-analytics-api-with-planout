#!/bin/bash
pkill -f uvicorn
PROJECT_LOCAL_PATH=`pwd -P`
source ${PROJECT_LOCAL_PATH}/venv/bin/activate

echo "check pip packages.."
pip3 install -r ${PROJECT_LOCAL_PATH}/requirements.txt
pip3 freeze > ./requirements.txt


cp ./.env.local ./.env

${PROJECT_LOCAL_PATH}/venv/bin/uvicorn app.main:app --reload --host=0.0.0.0 --port 8001