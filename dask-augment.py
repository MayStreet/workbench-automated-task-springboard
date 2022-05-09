from importlib import reload
import os
import sys

import logging
logging.basicConfig(level=logging.INFO)

import maystreet_data

# Allow to import modules from shared home folder
os.chdir('/home/workbench')
sys.path.append('/home/workbench')

# Ensures boto3 library is installed
try:
    import boto3
except ImportError:
    client = maystreet_data.current_job().client
    client.run(lambda: os.system("pip install boto3"))

import augment
# Ensure this is a fresh module version, and not one cached by the Dask cluster
reload(augment)

# Grab arguments from web request
# Example invocation:
# curl -H 'Content-Type: application/json' -X POST --data '{ "jobId": "...", "data": {"filename": "20-apr-2022.csv" }}' https://wb-api.shared-dev.maystreet.com/api/dask-jobs/trigger
file_name = job_arguments['filename'] # type: ignore

augment.run_process(file_name)
