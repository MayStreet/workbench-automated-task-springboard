import csv
import logging
import os
from datetime import date, datetime
from pathlib import Path
from tempfile import gettempdir

import boto3
import maystreet_data

# Change these values to your bucket / AWS account.
# Set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY to None if the bucket is an Analytics Workbench shared resource.
BUCKET_NAME = "<<BUCKET NAME>>"
AWS_ACCESS_KEY_ID = "<<AWS_ACCESS_KEY_ID>>"
AWS_SECRET_ACCESS_KEY = "<<AWS_SECRET_ACCESS_KEY>>"


def get_max_price_by_side(feed: str, product: str, day: date):
    query_text = f"""
    SELECT
        side,
        MAX(price) AS max_price
    FROM
        "prod_lake.p_mst_data_lake".mt_trade
    WHERE
        f = '{feed}'
        AND dt = '{day.isoformat()}'
        AND product = '{product}'
        AND side IS NOT NULL
    GROUP BY
        side
    """

    records_iter = maystreet_data.query(
        maystreet_data.DataSource.DATA_LAKE,
        query_text,
    )

    return {record["side"]: record["max_price"] for record in records_iter}


def run_process(source_remote_path):
    logging.info(f"using remote path: {source_remote_path}")

    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name="us-east-1",
    )
    bucket = session.resource("s3").Bucket(BUCKET_NAME)

    filename_path = Path(source_remote_path)
    destination_remote_path = f"{filename_path.stem}-output{filename_path.suffix}"

    temp_directory = gettempdir()
    source_local_path = os.path.join(temp_directory, "s3-file.csv")
    destination_local_path = os.path.join(temp_directory, destination_remote_path)

    logging.info(f"downloading from {source_remote_path} to {source_local_path}...")
    logging.info(
        f"will upload from {destination_local_path} to {destination_remote_path}...",
    )

    bucket.download_file(source_remote_path, source_local_path)

    with open(source_local_path) as source_csv, open(
        destination_local_path, "w"
    ) as destination_csv:
        source_reader = csv.reader(source_csv)
        destination_writer = csv.writer(destination_csv)

        next(source_reader, None)  # skip header

        destination_writer.writerow(
            ["Product", "Feed", "Date/Time", "Ask", "Bid", "Error"]
        )

        for product, feed, csv_day in source_reader:
            # dates in the CSV are in day/month/year format
            day = datetime.strptime(csv_day, "%d/%m/%Y").date()

            logging.info(f"fetching prices for {product} on {feed} at {day}")

            try:
                prices = get_max_price_by_side(feed, product, day)
                destination_writer.writerow(
                    [
                        product.upper(),
                        feed.upper(),
                        csv_day,
                        prices["Ask"],
                        prices["Bid"],
                        "",
                    ]
                )
            except Exception as ex:
                destination_writer.writerow(
                    [product.upper(), feed.upper(), csv_day, "", "", str(ex)]
                )

    bucket.upload_file(destination_local_path, destination_remote_path)

    logging.info("done!")
