

import os
import logging
import csv
from tempfile import gettempdir
from pathlib import Path
from datetime import datetime, date, time

import boto3
import json

import maystreet_data

def get_data(feed, product, date_time):
    # UK/EU/everywhere else in the entire world date format
    parsed_date = datetime.strptime(date_time, '%d/%m/%Y')

    query_text = f"""
    SELECT 
        side, 
        MAX(price) 
    FROM 
        "prod_lake.p_mst_data_lake".mt_trade
    WHERE 
        f = '{feed}'
        AND y = '{parsed_date.year}'
        AND m = '{str(parsed_date.month).zfill(2)}'
        AND d = '{str(parsed_date.day).zfill(2)}'
        AND product = '{product}'
        AND side IS NOT NULL
    GROUP BY 
        side
    """

    logging.debug(query_text)

    records_iter = maystreet_data.query(
        maystreet_data.DataSource.DATA_LAKE,
        query_text,
    )

    return {
        record['side']: record['EXPR$1']
        for record in records_iter
    }


def run_process(file_name):
    logging.info(f'using filename: {file_name}')

    bucket_name = '<<BUCKET NAME>>'

    temp_directory = gettempdir()

    boto3.set_stream_logger('', logging.DEBUG)

    session = boto3.Session(
        aws_access_key_id='<<AWS ACCESS KEY ID>>',
        aws_secret_access_key='<<AWS SECRET ACCESS KEY>>',
        region_name='us-east-1'
    )

    logging.info('created session... %s, %s', session.get_credentials(), session.region_name)

    path = Path(file_name)
    output_file_name = f"{path.stem}-output{path.suffix}"

    bucket_destination = os.path.join(temp_directory, 's3-file.csv')
    output_file = os.path.join(temp_directory, output_file_name)

    logging.info("downloading from %s to %s...", file_name, bucket_destination)
    logging.info("will upload from %s to %s...", output_file, output_file_name)

    s3 = session.resource('s3')
    s3.Bucket(bucket_name).download_file(file_name, bucket_destination)

    with open(bucket_destination) as csv_file, open(output_file, 'w') as csv_output_file:
        line_writer = csv.writer(csv_output_file)
        line_writer.writerow(['Product', 'Feed', 'Date/Time', 'Ask', 'Bid', 'Error'])
        line_reader = csv.reader(csv_file)
        next(line_reader, None)
        for row in line_reader:
            product = row[0]
            feed = row[1]
            date_time = row[2]

            logging.info('getting data for %s on %s at %s...', product, feed, date_time)

            try:
                response_data = get_data(feed, product, date_time)
                logging.info(response_data)
                line_writer.writerow([product.upper(), feed.upper(), date_time, response_data['Ask'], response_data['Bid'], ''])
            except Exception as ex:
                line_writer.writerow([product.upper(), feed.upper(), date_time, '', '', str(ex)])

    s3.Bucket(bucket_name).upload_file(output_file, output_file_name)

    logging.info('done!')
