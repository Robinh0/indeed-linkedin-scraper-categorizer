import pandas as pd
import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import re
from openai import OpenAI
import json
import time
import threading
import chardet


def categorize_text(text, function_context):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": text},
        ],
        functions=function_context,
        function_call={"name": "choose_from_options"}
    )

    # # Assuming response object has a 'status_code' attribute
    # status_code = response.status_code
    # print(f"Status Code: {status_code}")

    response = response.choices[0].message.function_call.arguments

    return json.loads(response)


def process_row(index, row, df):
    """
    Handler function to process the rows and updates the values in the dataframe.
    """
    text = row['Description']
    res = categorize_text(text=text, function_context=FUNCTION_CONTEXT)
    # if res.get('error', None):
    #     repeat = True
    #     while repeat:
    #         time.sleep(1)
    #         res = categorize_text(cleaned_text)
    #         print(f"Res: {res}, sleeping for 1 second.")
    #         if not res.get('error', None):
    #             print("Res is now true for {url}. Continuiing!")
    #             repeat = False

    if res.get('has_python', None) is None:
        df.at[index, 'enriched_with_chatgpt'] = "empty_response_from_openai_api"
        return

    print(f"ChatGPT categorisation for the index {index}:\n{res}")
    # if pd.isna(row['has_python']):
    df.at[index, 'company_industry'] = res['company_industry']
    df.at[index, 'company_type'] = res['company_type']
    df.at[index, 'enriched_with_chatgpt'] = True
    df.at[index, 'has_django'] = res['has_django']
    df.at[index, 'has_python'] = res['has_python']
    df.at[index, 'is_data_engineer'] = res['is_data_engineer']
    df.at[index, 'is_fullstack'] = res['is_fullstack']
    df.at[index, 'is_sustainability_focused'] = res['is_sustainability_focused']
    df.at[index, 'seniority_level'] = res['seniority_level']
    df.at[index, 'years_of_experience'] = res['years_of_experience']
    df.at[index, 'location'] = res['location']
    df.at[index, 'has_frontent_mentioned'] = res['has_frontent_mentioned']
    return


# Load environment variables
load_dotenv()

filename = 'df_with_description'

# Initialize API keys and client
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)


FUNCTION_CONTEXT = [{
    "name": "choose_from_options",
    "description": "Analyse the job post and choose the correct category from the provided options. Please do not include the text from the recruiters signature in your analysis, this can be at the end of the text prompt.",
    "parameters": {
        "type": "object",
        "properties": {
            "has_python": {
                "type": "string",
                "description": "Is Python specifically mentioned as a requirement for this job post? Return exactly the has_python json key",
                "enum": ['True', 'False']
            },
            "has_django": {
                "type": "string",
                "description": "Is Django specifically mentioned as a requirement for this job post? Return exactly the has_django json key",
                "enum": ['True', 'False']
            },
            "is_fullstack": {
                "type": "string",
                "description": "Is this a fullstack role with React, Angular or Vue? Return exactly the is_fullstack json key",
                "enum": ['True', 'False']
            },
            "has_frontent_mentioned": {
                "type": "string",
                "description": "Is frontend mentioned in this job role? For example with javascript, typescript, react, angular or vue? Return exactly the has_frontent_mentioned json key",
                "enum": ['True', 'False']
            },
            "company_type": {
                "type": "string",
                "description": "Is this a consultancy or an in house job position? Return exactly the company_type json key",
                "enum": ['in_house', 'consultancy']
            },
            "seniority_level": {
                "type": "string",
                "description": "Is this a junior, medior or a senior job position? Return exactly the seniority_level json key",
                "enum": ['junior', 'medior/junior', 'medior', 'medior/senior', 'senior']
            },
            "years_of_experience": {
                "type": "string",
                "description": "How many years of experience is required for this job role as a number? Return exactly the years_of_experience json key",
            },
            "is_data_engineer": {
                "type": "string",
                "description": "Is this role a data engineering role? Return exactly the is_data_engineer json key",
                "enum": ['True', 'False']
            },
            "is_sustainability_focused": {
                "type": "string",
                "description": "Is job post specifically oriented towards sustainability and making an impact on the planet and reducing footprint? Return exactly the is_sustainability_focused json key",
                "enum": ['True', 'False']
            },
            "company_industry": {
                "type": "string",
                "description": "What is the company industry? Return exactly the company_industry json key",
            },
            "location": {
                "type": "string",
                "description": "What is the location of the company in the job post? Return exactly the location json key",
            },
        },
    },
    "required": ["has_python", "has_django", "is_fullstack" "company_type", "seniority_level", "years_of_experience", "is_data_engineer", "is_sustainability_focused", "company_industry", "location"]
}
]

df = pd.read_csv(f"{filename}.csv", on_bad_lines='skip')
df['company_industry'] = None
df['company_type'] = None
df['enriched_with_chatgpt'] = False
df['has_django'] = None
df['has_python'] = None
df['is_data_engineer'] = None
df['is_fullstack'] = None
df['is_sustainability_focused'] = None
df['seniority_level'] = None
df['years_of_experience'] = None
df['location'] = None
df['has_frontent_mentioned'] = None

# session = requests.Session()
threads = []

for index, row in df.iterrows():
    print(f"Processing row {index}")
    thread = threading.Thread(
        target=process_row, args=(index, row, df))
    threads.append(thread)
    thread.start()

    time.sleep(0.3)  # Adding a delay between starting each thread

    if index % 10 == 0 and index != 0:
        for thread in threads:
            thread.join()
        threads = []
        df.fillna('unknown', inplace=True)
        df.to_csv(f"{filename}_result.csv", index=False)

        # if index == 20:
        #     raise

for thread in threads:
    thread.join()

df.to_csv(f"{filename}_result.csv", index=False)

print()
print(df)
