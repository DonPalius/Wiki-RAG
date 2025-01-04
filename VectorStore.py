
from uuid import uuid4
import chromadb
from tqdm import tqdm
class VectorStore:
    """
    Class for managing a vector store using ChromaDB.
    This class handles loading, creating, and interacting with the vector store.
    """

    def __init__(self, collection_name, reset=False):
        self.collection_name = collection_name
        self.chroma_client = chromadb.PersistentClient()
        self.chroma_collection = self.load_vectors_store(reset)

    def load_vectors_store(self, reset):
        """
        Loads or resets the ChromaDB vector store for fast retrieval based on vector similarity.
        """
        if reset:
            try:
                self.chroma_client.delete_collection(name=self.collection_name)
            except Exception as e:
                print(f"No collection found to delete: {e}")

        chroma_collection = self.chroma_client.get_or_create_collection(self.collection_name)
        print("Vector store loaded.\n")
        # try:
        #     print(chroma_collection.peek(1))
        # except Exception as e:
        #     print(f"Error while peeking into the collection: {e}")

        return chroma_collection

    def create_vector_store(self, chunked_docs):
        """
        Populates the ChromaDB vector store with document chunks, including metadata such as
        document titles and chunk paths.
        """
        for doc in tqdm(chunked_docs, desc="Processing Documents", unit="document"):
            title = doc['title']
            url = doc['url']
            chunk_ids = []
            documents = []
            metadatas = []

            for path, content in doc['chunked_text']:
                chunk_id = str(uuid4())
                chunk_ids.append(chunk_id)
                documents.append(content)
                metadatas.append({"Title": title, "Paragraph": path})

            self.chroma_collection.add(
                ids=chunk_ids,
                documents=documents,
                metadatas=metadatas,
            )
