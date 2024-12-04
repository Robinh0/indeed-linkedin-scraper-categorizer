import pandas as pd
import os
import json
import time
import threading
from openai import OpenAI

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

COLUMNS = [
    "location",
    "programming_languages",
    "backend_frameworks",
    "frontend_frameworks",
    "seniority_level",
    "company_type",
    "years_of_experience",
    "company_industry",
    "company_size",
    "has_django",
    "has_python",
    "is_fullstack",
    "is_sustainability_focused",
]

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
            "frontend_frameworks": {
                "type": "string",
                "description": "What frontend frameworks are mentioned? Return all that are mentioned. Return exactly the frontend_frameworks json key",
            },
            "backend_frameworks": {
                "type": "string",
                "description": "What backend frameworks are mentioned? Return all that are mentioned. Return exactly the backend_frameworks json key",
            },
            "programming_languages": {
                "type": "string",
                "description": "What programming languages are mentioned? Return all that are mentioned. Return exactly the programming_languages json key",
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
            "company_size": {
                "type": "integer",
                "description": "If the company name is mentioned, what is the estimated company size in FTE? Return exactly the company_size json key",
            },
        },
    },
    "required": COLUMNS
}]

# Global dictionary to store results and a lock for thread safety
results = {}


def categorize_text(text: str, function_context: list) -> dict:
    """
    Categorizes the text using OpenAI's chat completion API.

    Args:
        text (str): The text to categorize.
        function_context (list): The function context for the API call.

    Returns:
        dict: A dictionary containing the categorized information.
    """
    try:
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
        response_content = response.choices[0].message.function_call.arguments
        return json.loads(response_content)
    except Exception as e:
        print(f"Error categorizing text: {e}")
        return {}


def process_row(index: int, row: pd.Series, results: dict) -> None:
    """
    Processes a single row in the DataFrame and stores it in a shared dictionary.

    Args:
        index (int): The index of the row being processed.
        row (pd.Series): The row data to process.
        results (dict): Dictionary to store processed row data.

    Returns:
        None
    """
    res = categorize_text(text=row['description'],
                          function_context=FUNCTION_CONTEXT)

    if res.get('has_python') is None:
        results[index] = {
            'enriched_with_chatgpt': "empty_response_from_openai_api"}
        return

    print(f"ChatGPT categorisation for index {index}:\n{res}")

    # Store processed data in the results dictionary
    results[index] = {col: res.get(col, None) for col in COLUMNS}
    return


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main function to load data, process it, and output results.

    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    for col in COLUMNS:
        df[col] = None

    threads = []

    for index, row in df.iterrows():
        print(f"Processing row {index}")
        thread = threading.Thread(
            target=process_row, args=(index, row, results))
        threads.append(thread)
        thread.start()

        time.sleep(0.3)

        if index % 50 == 0 and index != 0:
            for thread in threads:
                thread.join()
            threads = []

            # Update the DataFrame outside of threads, unpack the row and the processed_row as
            # dictionaries, and then update the rows from processed_rows dict.
            for idx, processed_row in results.items():
                df.loc[idx] = {**df.loc[idx], **processed_row}

            df.fillna('unknown', inplace=True)
            results.clear()

    for thread in threads:
        thread.join()

    for idx, processed_row in results.items():
        df.loc[idx] = {**df.loc[idx], **processed_row}

    cols = [col for col in df.columns if col not in [
        'url', 'description', 'html_content']]
    cols.extend(['url', 'description', 'html_content'])
    df = df[cols]

    df.fillna('unknown', inplace=True)
    print(df)
    return df
