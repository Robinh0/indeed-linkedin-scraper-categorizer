import boto3
import pandas as pd
import io
from constants.constants import BUCKET_NAME

BUCKET_NAME = 'indeed-scrapy'


class Loader():
    def __init__(self):
        self.bucket_name = BUCKET_NAME

    def load(self, df, filename):
        # Create a buffer to hold the CSV data
        csv_buffer = io.StringIO()

        # Write the DataFrame to the buffer in CSV format
        df.to_csv(csv_buffer, index=False)

        # Create an S3 client
        s3_client = boto3.client('s3')

        # Upload the CSV data from the buffer to S3
        s3_client.put_object(Bucket=self.bucket_name, Key=filename,
                             Body=csv_buffer.getvalue())
        return
