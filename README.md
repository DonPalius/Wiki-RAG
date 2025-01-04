# Wiki-RAG

Wiki-RAG is a Retrieval-Augmented Generation (RAG) system designed to enhance the process of querying and generating responses based on the Italian Wikipedia. This system integrates advanced retrieval techniques with natural language generation capabilities to provide precise and contextually relevant answers.

## Features

- **Retrieval-Augmented Generation:** Combines retrieval of relevant information with natural language generation to produce coherent and informative responses.
- **Focused on Italian Wikipedia:** Specially designed to work with Italian-language content, offering accurate and culturally relevant results.
- **Scalable and Efficient:** Optimized for quick retrieval and seamless integration with various applications.

## Project Structure

- `requirements.txt`: Contains all the dependencies required for the project.
- `app.py`: Streamlit interface for interacting with the Wiki-RAG system.
- `prompt.py`: Class containing the prompts used for querying.
- `ModelQuery.py`: Class for making local model queries using LLM Studio.
- `VectorStore.py`: Class for initializing and populating the vector store.
- `search.py`: Contains functionalities for search and re-ranking.
- `wiki_dump.py`: Handles the dumping and preprocessing of Wikipedia data.
- `test.ipynb`: Jupyter Notebook for testing and debugging the system.
- `README.md`: Detailed instructions for setting up and running the project.

## How It Works

1. **Query Input:** Users submit a query in Italian.
2. **Information Retrieval:** The system searches the Italian Wikipedia for the most relevant documents using the vector store.
3. **Content Generation:** Using the retrieved data, the system generates a detailed, human-like response.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/wiki-rag.git
   cd wiki-rag
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the Italian Wikipedia dataset or API integration as specified in the documentation.

## TODO
- Integrate the pipeline to download the wikipedia dump and integrate it in chromadb by adding or modifying the changed documents.
- Improve the UI by adding a chat history feature.
- Improve the split and chunk of the wikipedia dump.

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

Or execute a query directly:
```bash
python wiki_rag.py --query "Che cos'è la teoria della relatività?"
```

The system will retrieve relevant information from Italian Wikipedia and generate a comprehensive response.

## Use Cases

- **Academic Research:** Quickly gather summarized and accurate information for educational purposes.
- **Customer Support:** Answer customer inquiries in Italian with relevant Wikipedia-backed content.
- **Content Creation:** Assist writers and journalists by providing concise and verified information.



