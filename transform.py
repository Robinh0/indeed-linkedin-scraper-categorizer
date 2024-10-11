import pandas as pd
import os
import json
import time
import threading
from dotenv import load_dotenv
from openai import OpenAI
from extract import SEARCH_TERM

# Load environment variables
load_dotenv()

# Constants
FILENAME = f'results/{SEARCH_TERM}_extraction'
OUTPUT_FILENAME = f'results/{SEARCH_TERM}_result.csv'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize API client
client = OpenAI(api_key=OPENAI_API_KEY)

COLUMNS = [
    "backend_frameworks",
    "company_industry",
    "company_name",
    "company_size",
    "company_type",
    "frontend_frameworks",
    "has_django",
    "has_python",
    "is_data_engineer",
    "is_fullstack",
    "is_sustainability_focused",
    "location",
    "seniority_level",
    "years_of_experience",
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
                "description": "What frontend frameworks are mentioned, if any? Return exactly the frontend_frameworks json key",
            },
            "backend_frameworks": {
                "type": "string",
                "description": "What backend frameworks are mentioned, if any? Return exactly the backend_frameworks json key",
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
                "type": "integer",
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
            "company_name": {
                "type": "string",
                "description": "What is the name of the company, if mentioned in the job post? Return exactly the company_name json key",
            },
            "company_size": {
                "type": "integer",
                "description": "If the company name is mentioned, what is the estimated company size in FTE? Return exactly the company_size json key",
            },
        },
    },
    "required": COLUMNS
}]


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
        # Extracting and parsing the response
        response_content = response.choices[0].message.function_call.arguments
        return json.loads(response_content)
    except Exception as e:
        print(f"Error categorizing text: {e}")
        return {}


def process_row(index: int, row: pd.Series, df: pd.DataFrame) -> None:
    """
    Processes a single row in the DataFrame and updates it with categorized information.

    Args:
        index (int): The index of the row being processed.
        row (pd.Series): The row data to process.
        df (pd.DataFrame): The DataFrame being updated with categorized information.

    Returns:
        None
    """
    text = row['Description']
    res = categorize_text(text=text, function_context=FUNCTION_CONTEXT)

    if res.get('has_python') is None:
        df.at[index, 'enriched_with_chatgpt'] = "empty_response_from_openai_api"
        return

    print(f"ChatGPT categorisation for index {index}:\n{res}")

    for column in COLUMNS:
        df.at[index, column] = res.get(column, None)


def transform() -> None:
    """
    Main function to load data, process it, and output results.

    Returns:
        None
    """
    df = pd.read_csv(f"{FILENAME}.csv", on_bad_lines='skip')
    # Initialize columns in DataFrame
    for col in COLUMNS:
        df[col] = None

    threads = []

    for index, row in df.iterrows():
        print(f"Processing row {index}")
        thread = threading.Thread(target=process_row, args=(index, row, df))
        threads.append(thread)
        thread.start()

        time.sleep(0.3)  # Adding a delay between starting each thread

        # Join threads in batches of 10
        if index % 10 == 0 and index != 0:
            for thread in threads:
                thread.join()
            threads = []
            df.fillna('unknown', inplace=True)
            df.to_csv(OUTPUT_FILENAME, index=False)

    # Join any remaining threads
    for thread in threads:
        thread.join()

    # Move the 'description' column to the back
    # Get all columns except 'description'
    cols = [col for col in df.columns if col not in ['URL', 'Description']]
    cols.append('URL')
    cols.append('Description')

    df = df[cols]  # Reorder the DataFrame

    # Final output
    df.fillna('unknown', inplace=True)
    df.to_csv(OUTPUT_FILENAME, index=False)
    print(df)


if __name__ == "__main__":
    transform()
