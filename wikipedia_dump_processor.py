import os
import sys
import json
import pandas as pd
from wikiextractor.WikiExtractor import main as wiki_extractor
import requests
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List 

class WikipediaDumpProcessor:
    max_chunk_size: int = 256
    chunk_overlap: int = 200
    headers_to_split_on: List[str] = None
    excluded_sections: List[str] = None

    def __init__(self, dump_url, dump_file, output_dir, base_dir):
        self.dump_url = dump_url
        self.dump_file = dump_file
        self.output_dir = output_dir
        self.base_dir = base_dir



        # Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.max_chunk_size, chunk_overlap=self.chunk_overlap
        )

    def download_dump(self):
        """Downloads the Wikipedia dump file from the specified URL."""
        if not os.path.exists(self.dump_file):
            print(f"Downloading dump from {self.dump_url}...")
            response = requests.get(self.dump_url, stream=True)
            with open(self.dump_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Dump downloaded to {self.dump_file}.")
        else:
            print(f"Dump file already exists at {self.dump_file}.")

    def extract_dump(self):
        """Extracts the Wikipedia dump into JSON files using WikiExtractor."""
        print(f"Extracting dump file {self.dump_file}...")
        sys.argv = [
            "WikiExtractor.py",  # Dummy script name
            self.dump_file,       # Path to Wikipedia dump
            "--json",            # Output in JSON format (optional)
            "--no-templates",    # Skip template content (optional)
            "--output", self.output_dir  # Output directory
        ]
        wiki_extractor()
        print(f"Extraction completed. Extracted files are in {self.output_dir}.")

    def parse_extracted_files(self):
        """Parses the extracted JSON files and converts them into a Pandas DataFrame."""
        print(f"Parsing extracted files from {self.base_dir}...")
        all_json_objects = []

        for root, _, files in os.walk(self.base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        for line in f:
                            try:
                                all_json_objects.append(json.loads(line))
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON in file: {file_path}")
                                print(f"Error: {e}")
                except Exception as e:
                    print(f"Error reading file: {file_path}")
                    print(f"Error: {e}")

        df = pd.DataFrame(all_json_objects)
        print("Parsing completed. Returning DataFrame.")
        return df

    def chunk_text(self, text: str) -> List[str]:
        """Splits text into smaller chunks based on the specified chunk size."""
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\[[\d+]\]', '', text)
        return self.text_splitter.split_text(text)

    def chunk_dataframe_text(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """Chunks the text in a specified column of a DataFrame and creates a new column with chunked text."""
        print(f"Chunking text in DataFrame column '{text_column}'...")
        df['chunked_text'] = df[text_column].apply(lambda x: self.chunk_text(x) if isinstance(x, str) else [])
        df[df['chunked_text'].map(len) > 0]
        df.to_csv('Data/Wikipedia.csv')
        print("Chunking completed. Returning updated DataFrame.")
        return df.head(1)



