from openai import OpenAI
import os
import json


class OpenAIAPIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def openai_api_categorizer(self, text: str, function_context: list) -> dict:
        """
        Categorizes the text using OpenAI's chat completion API.

        Args:
            text (str): The text to categorize.
            function_context (list): The function context for the API call.

        Returns:
            dict: A dictionary containing the categorized information.
        """
        try:
            response = self.client.chat.completions.create(
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
