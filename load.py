import boto3
import pandas as pd
import io
from constants import BUCKET_NAME


def load(df, filename):
    # Create a buffer to hold the CSV data
    csv_buffer = io.StringIO()

    # Write the DataFrame to the buffer in CSV format
    df.to_csv(csv_buffer, index=False)

    # Create an S3 client
    s3_client = boto3.client('s3')

    # Upload the CSV data from the buffer to S3
    s3_client.put_object(Bucket=BUCKET_NAME, Key=filename,
                         Body=csv_buffer.getvalue())
    return
