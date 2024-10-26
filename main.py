from extract import extract
from load import load
from transform import transform
import os
from dotenv import load_dotenv
import threading
from datetime import datetime


def run_etl(filename, aws_download_link):
    # Step 1: Extract job links
    print("Starting extraction of job links and job description.")
    df = extract()

    # Step 2: Transform data
    print("Starting transformation of job data...")
    df = transform(df)

    # Step 3: Loading the results to the AWS S3 bucket
    print("Starting load process to AWS S3.")
    load(df, filename)

    print(
        f"ETL process completed successfully. The results can be downloaded at {aws_download_link}")
    return


def handler(event, context):
    load_dotenv()
    try:
        print(event)
        max_pages_to_scrape = event.get('max_pages_to_scrape')
        indeed_url = event.get('indeed_url')

        # Check if both parameters are provided
        if max_pages_to_scrape is not None or indeed_url is not None:
            # Override current environment variables
            os.environ['MAX_PAGES_TO_SCRAPE'] = str(
                max_pages_to_scrape)
            os.environ['INDEED_URL'] = str(indeed_url)

            # Log the new environment variables
            print("Updated environment variables:")
            print(f"MAX_PAGES_TO_SCRAPE: {os.environ['MAX_PAGES_TO_SCRAPE']}")
            print(f"INDEED_URL: {os.environ['INDEED_URL']}")
    except:
        print("No event message located.")

    filename = f'indeed_scraped_enriched_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    aws_download_link = f'http://indeed-scrapy.s3.amazonaws.com/{filename}'

    # Start ETL in a new thread
    etl_thread = threading.Thread(
        target=run_etl, args=(filename, aws_download_link))
    etl_thread.start()

    return {"statusCode": 200, "download_link": aws_download_link}
