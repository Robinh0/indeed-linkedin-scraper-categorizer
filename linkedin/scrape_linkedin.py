import requests
import os
import json
from dotenv import load_dotenv
import pandas as pd

headers = {
    'cookie': f'JSESSIONID={os.getenv("JSESSIONID")}; li_at={os.getenv("LI_AT")}',
    'csrf-token': f'{os.getenv("JSESSIONID")}'
}


def get_linkedin_ids():
    start_counter = 0
    job_ids = []
    # URL to scrape python jobs in amsterdam specifically, can change later.
    url = "https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-216&q=jobSearch&query=(currentJobId:4036488959,origin:JOBS_HOME_SEARCH_CARDS,keywords:python,locationUnion:(geoId:90010383),selectedFilters:(distance:List(25),experience:List(2),title:List(9,25201,24)),spellCorrectionEnabled:true)&count=100"
    response = requests.request("GET", url, headers=headers)
    count = response.json()['paging']['total']
    for element in response.json()['elements']:
        id = element['jobCardUnion']['jobPostingCard']['preDashNormalizedJobPostingUrn'].split(
            "fs_normalized_jobPosting:")[1]
        job_ids.append(id)
    return job_ids


def get_linkedin_descriptions():
    job_ids = get_linkedin_ids()
    descriptions = []
    for enum, item in enumerate(job_ids):
        try:
            individual_url = f"https://www.linkedin.com/voyager/api/jobs/jobPostings/{item}"
            response = requests.request(
                "GET", individual_url, headers=headers)
            # print(response.text)
            response_json = response.json()
            response.raise_for_status()
            # with open('job_response.json', 'w') as file:
            #     json.dump(response_json, file, indent=4)
            description = response_json['description']['text']
            descriptions.append(description)
            print(description)
        except:
            continue
        finally:
            if enum == 10:
                break
    df = pd.DataFrame(descriptions, columns=['description'])
    df["title"] = None
    df["url"] = None
    df["company_name"] = None
    df["location"] = None
    df["salary"] = None
    df["html_content"] = None
    df.to_csv('Descriptions.csv')
    return df
