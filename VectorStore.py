from uuid import uuid4
import chromadb
from tqdm import tqdm
import pandas as pd
import openai
import os
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
class VectorStore:
    """
    Class for managing vector stores using ChromaDB.
    Handles both document chunks and keyword-based (title) vector stores.
    """
    def __init__(self, doc_collection_name, keyword_collection_name, data_path=None, reset=False, openai_api_key=None):
        """
        Initialize VectorStore with separate collections for documents and keywords.
        
        Args:
            doc_collection_name (str): Name of the document chunks collection.
            keyword_collection_name (str): Name of the keywords collection.
            data_path (str, optional): Path to the DataFrame file.
            reset (bool): Whether to reset existing collections.
            openai_api_key (str, optional): Your OpenAI API key. If not provided, it will try to use the OPENAI_API_KEY environment variable.
        """
        load_dotenv()

        self.chroma_client = chromadb.PersistentClient()
        
        # Initialize OpenAI
        if openai_api_key:
            openai.api_key = openai_api_key
        else:
            openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            print("OpenAI API key is not set. Please provide one or set the OPENAI_API_KEY environment variable.")

        # Initialize document collection
        self.doc_collection_name = doc_collection_name
        self.doc_collection = self.load_vectors_store(doc_collection_name, reset)
        
        # Initialize keyword collection
        self.keyword_collection_name = keyword_collection_name
        self.keyword_collection = self.load_vectors_store(keyword_collection_name, reset)
        
        self.df = self.load_dataframe(data_path) if data_path else None

    def load_dataframe(self, path):
        """Load DataFrame from file based on file extension."""
        if path.endswith('.csv'):
            return pd.read_csv(path).head(1)
        elif path.endswith('.parquet'):
            return pd.read_parquet(path)
        elif path.endswith('.pickle') or path.endswith('.pkl'):
            return pd.read_pickle(path)
        else:
            raise ValueError(f"Unsupported file format for path: {path}")

    def load_vectors_store(self, collection_name, reset):
        """Load or reset a ChromaDB vector store collection."""
        if reset:
            try:
                self.chroma_client.delete_collection(name=collection_name)
            except Exception as e:
                print(f"No collection found to delete: {e}")
        
        collection = self.chroma_client.get_or_create_collection(collection_name)
        print(f"Vector store '{collection_name}' loaded.\n")
        return collection

    def get_openai_embedding(self, text: str):
        """
        Get the OpenAI embedding for a given text using the text-embedding-ada-002 model.
        """
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']

    def create_document_store(self, chunked_docs=None, use_openai_embedding=False):
        """
        Create vector store for document chunks and return DataFrame with chunk IDs.
        
        Args:
            chunked_docs: DataFrame or other data structure containing documents.
            use_openai_embedding (bool): Whether to compute OpenAI embeddings for each chunk.
        """
        print("Creating document store")
        # Use loaded DataFrame if no input provided
        if chunked_docs is None:
            if self.df is None:
                raise ValueError("No data provided and no DataFrame was loaded during initialization")
            df = self.df.copy()
        elif not isinstance(chunked_docs, pd.DataFrame):
            df = pd.DataFrame(chunked_docs)
        else:
            df = chunked_docs.copy()
        
        # Create new column for chunk IDs
        df['chunk_ids'] = None
        

        # for idx, doc in tqdm(df.iterrows(), desc="Processing Document Chunks", total=len(df)):
        for idx, doc in df.iterrows():
            print(doc['title'])
            title = doc['title']
            chunk_ids = []
            documents = []
            metadatas = []
            print(len(doc['chunked_text']))
            # Process each chunk in the document
            for content in tqdm(doc['chunked_text'], desc="Processing Chunks", leave=False):

                chunk_id = str(uuid4())
                chunk_ids.append(chunk_id)
                documents.append(content)
                metadatas.append({"Title": title})
            
            # Compute embeddings using OpenAI if enabled
            if use_openai_embedding:
                embeddings = [self.get_openai_embedding(text) for text in documents]
                self.doc_collection.add(
                    ids=chunk_ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
            else:
                self.doc_collection.add(
                    ids=chunk_ids,
                    documents=documents,
                    metadatas=metadatas,
                )
            
            # Store chunk IDs in DataFrame
            df.at[idx, 'chunk_ids'] = chunk_ids
        
        return df

    def create_keyword_store(self, df):
        """
        Create vector store for keywords based on titles and their chunk IDs.
        
        Args:
            df (pandas.DataFrame): DataFrame containing 'title' and 'chunk_ids' columns.
            
        Returns:
            pandas.DataFrame: Original DataFrame with keyword_id column added.
        """
        df = df.copy()
        df['keyword_id'] = None
        
        for idx, row in tqdm(df.iterrows(), desc="Processing Keywords", total=len(df)):
            # Generate unique ID for the keyword entry
            keyword_id = str(uuid4())
            
            # Add title as keyword to ChromaDB
            self.keyword_collection.add(
                ids=[keyword_id],
                documents=[row['title']],
                metadatas=[{
                    "Title": row['title'],
                    "chunk_ids": ",".join(row['chunk_ids'])  # Store associated chunk IDs in metadata
                }]
            )
            
            # Store keyword ID in DataFrame
            df.at[idx, 'keyword_id'] = keyword_id
        
        return df

    def process_all(self, chunked_docs=None, use_openai_embedding=False):
        """
        Process both document chunks and keywords in one go.
        
        Args:
            chunked_docs: DataFrame or other data structure containing documents.
            use_openai_embedding (bool): Whether to compute OpenAI embeddings for document chunks.
            
        Returns:
            tuple: (final_df, doc_collection, keyword_collection)
        """
        # First process documents to get chunk IDs (and optionally compute embeddings)
        df_with_chunks = self.create_document_store(chunked_docs, use_openai_embedding=use_openai_embedding)
        # Then process keywords using the chunk IDs
        final_df = self.create_keyword_store(df_with_chunks)
        
        # Return the final DataFrame along with both vector store objects.
        return final_df

