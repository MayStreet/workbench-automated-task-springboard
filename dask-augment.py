from importlib import reload

import augment
# Ensure this is a fresh module version, and not one cached by the Dask cluster
reload(augment)

# Grab arguments from web request
# Example invocation:
# curl -H 'Content-Type: application/json' -X POST --data '{ "jobId": "...", "data": {"filename": "20-apr-2022.csv" }}' https://wb-api.maystreet.com/api/dask-jobs/trigger

file_name = job_arguments['filename'] # type: ignore

augment.run_process(file_name)
