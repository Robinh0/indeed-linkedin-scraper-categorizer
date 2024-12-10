from datetime import datetime
import json
import platform
from etl.extract import IndeedExtractor, LinkedInExtractor
from etl.load import Loader
from etl.transform import Transformer
import os
from dotenv import load_dotenv


class ETLRunner:
    def __init__(self):
        pass

    def run(self, filename, aws_download_link):
        # Step 1: Extract job links
        print("Starting extraction of job links and job description.")
        if 'indeed.com' in os.getenv('URL'):
            extractor = IndeedExtractor()
        if 'linkedin.com' in os.getenv('URL'):
            extractor = LinkedInExtractor()

        df = extractor.run_scraper()

        # Step 2: Transform data
        print("Starting transformation of job data...")
        transformer = Transformer()
        df = transformer.transform(df=df)

        # Step 3: Loading the results to the AWS S3 bucket
        print("Starting load process to AWS S3.")
        loader = Loader()
        loader.load(df, filename)

        print(
            f"ETL process completed successfully. The results can be downloaded at {aws_download_link}")
        return


def handler(event, context):
    load_dotenv()
    print(f"Event: {event}")
    print(f"Context: {context}")
    if platform.system() != "Windows":
        message = event['Records'][0]['Sns']['Message']
        print(f'message: {message}')
        json_data = json.loads(message)
        print(f'json_data: {json_data}')

        max_pages_to_scrape = json_data.get('max_pages_to_scrape')
        nr_items_per_page = json_data.get('nr_items_per_page')
        url = json_data.get('URL')
        filename = json_data.get('filename')
        aws_download_link = json_data.get('aws_download_link')

        print(f'max_pages_to_scrape: {max_pages_to_scrape}')
        print(f'URL: {url}')
        print(f'filename: {filename}')
        print(f'aws_download_link: {aws_download_link}')

        os.environ['MAX_PAGES_TO_SCRAPE'] = str(
            max_pages_to_scrape)
        os.environ['NR_ITEMS_PER_PAGE'] = str(nr_items_per_page)
        os.environ['URL'] = str(url)
        os.environ['FILENAME'] = str(filename)
        os.environ['AWS_DOWNLOAD_LINK'] = str(aws_download_link)

        print("Updated environment variables:")
    if platform.system() == "Windows":
        filename = f'indeed_scraped_enriched_local_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        os.environ['MAX_PAGES_TO_SCRAPE'] = "1"
        os.environ['NR_ITEMS_PER_PAGE'] = "10"
        # os.environ['URL'] = "https://nl.indeed.com/jobs?q=python+developer&l=Randstad"
        os.environ['URL'] = "https://www.linkedin.com/jobs/search/?currentJobId=4084206092&distance=25&f_E=2&f_T=9%2C25201%2C24&geoId=90010383&keywords=python&origin=JOBS_HOME_SEARCH_CARDS"
        os.environ['FILENAME'] = filename
        os.environ[
            'AWS_DOWNLOAD_LINK'] = f'http://indeed-scrapy.s3.amazonaws.com/{filename}'

    # # Print all environment variables
    # for key, value in os.environ.items():
    #     print(f"{key}={value}")

    etl_runner = ETLRunner()
    etl_runner.run(filename=os.getenv('FILENAME'),
                   aws_download_link=os.getenv('AWS_DOWNLOAD_LINK'))

    if platform.system() != "Windows":
        return {"statusCode": 200, "download_link": aws_download_link}


if platform.system() == "Windows":
    handler(None, None)
