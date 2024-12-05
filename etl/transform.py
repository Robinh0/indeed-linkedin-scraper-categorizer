import pandas as pd
import time
import threading
from constants.constants_transform import COLUMNS, FUNCTION_CONTEXT
from services.openai_api_service import OpenAIAPIService


class Transformer():
    def __init__(self):
        self.results = {}
        self.openai_service = OpenAIAPIService()

    def process_row(self, index: int, row: pd.Series, results: dict) -> None:
        """
        Processes a single row in the DataFrame and stores it in a shared dictionary.

        Args:
            index (int): The index of the row being processed.
            row (pd.Series): The row data to process.
            results (dict): Dictionary to store processed row data.

        Returns:
            None
        """
        res = self.openai_service.openai_api_categorizer(text=row['description'],
                                                         function_context=FUNCTION_CONTEXT)

        if res.get('has_python') is None:
            results[index] = {
                'enriched_with_chatgpt': "empty_response_from_openai_api"}
            return

        print(f"ChatGPT categorisation for index {index}:\n{res}")

        # Store processed data in the results dictionary
        results[index] = {col: res.get(col, None) for col in COLUMNS}
        return

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
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
                target=self.process_row, args=(index, row, self.results))
            threads.append(thread)
            thread.start()

            time.sleep(0.3)

            if index % 50 == 0 and index != 0:
                for thread in threads:
                    thread.join()
                threads = []

                # Update the DataFrame outside of threads, unpack the row and the processed_row as
                # dictionaries, and then update the rows from processed_rows dict.
                for idx, processed_row in self.results.items():
                    df.loc[idx] = {**df.loc[idx], **processed_row}

                df.fillna('unknown', inplace=True)
                self.results.clear()

        for thread in threads:
            thread.join()

        for idx, processed_row in self.results.items():
            df.loc[idx] = {**df.loc[idx], **processed_row}

        cols = [col for col in df.columns if col not in [
            'url', 'description', 'html_content']]
        cols.extend(['url', 'description', 'html_content'])
        df = df[cols]

        df.fillna('unknown', inplace=True)
        print(df)
        return df
