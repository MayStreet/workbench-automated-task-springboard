# MayStreet Analytics Workbench Automated Task Springboard

## Welcome

Welcome to the Automated Task Springboard.

This Springboard will talk you through how to create an automated task which will, when triggered via a HTTP
request, retrieve a file from S3, run it against the Data Lake, and then write out another file.

## Prerequisites

- An external AWS account with a pre-created S3 bucket.
- Credentials (an AWS access key and secret key) that have read and write access to the above bucket.

## Preparing your Workbench instance.

1. You will need to create a Dask cluster before you can run this sample; to do so, please follow the short video
here:

![images/provisioning-cluster.gif](/images/provisioning-cluster.gif)

2. You will then need to create a simple web-triggered job using the cluster you've just created:

![images/creating-job.gif](/images/creating-job.gif)

## Running the job.

1. Ensure you have updated the bucket ID, the access key and the secret key inside the _[augment.py](augment.py)_ file.
2. Create a file named '20-apr-2022.csv' with the following content inside that bucket:

| Product | Feed | Requested Date |
| ------- | ---- | -------------- |
| AAPL | bats_edga | 12/01/2022 |
| V | bats_edga | 13/01/2022 |
| V | bats_edga | 13/01/2022 |
| VRSN | bats_edga | 14/01/2022 |
| NOTHING | bats_false | 14/01/2022 |

(the file is also in this Springboard so you can easily just drop that in.)

3. Copy the job URL as show in the above image, and then customise it to add in the filename inside the bucket; the
command should look something like the following (with a different Job ID)
```
curl -H 'Content-Type: application/json' -X POST --data '{ "jobId": "698db01b-ed95-45c7-b686-b018a7059ae6", "data": {"filename":"20-apr-2022.csv" } }' https://wb-api.shared-dev.maystreet.com/api/dask-jobs/trigger
```
4. Wait, and you should see the file being generated in the S3 repository.
