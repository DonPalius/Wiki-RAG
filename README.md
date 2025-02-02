```markdown
# Wiki-RAG

Wiki-RAG is a Retrieval-Augmented Generation (RAG) system designed to enhance the process of querying and generating responses based on the Italian Wikipedia. By combining advanced retrieval techniques with state-of-the-art natural language generation, Wiki-RAG provides precise, contextually relevant answers for Italian-language queries.

## Features

- **Retrieval-Augmented Generation:** Leverages both document retrieval and language generation to produce coherent and informative responses.
- **Italian Wikipedia Focus:** Tailored to work with Italian-language content, ensuring culturally and contextually accurate results.
- **Scalable and Efficient:** Optimized for quick retrieval and smooth integration with various applications.

## Project Structure

- `requirements.txt`  
  Lists all the dependencies required for the project.
- `app.py`  
  Streamlit interface for interacting with the Wiki-RAG system.
- `prompt.py`  
  Contains the prompts used for querying.
- `ModelQuery.py`  
  Handles local model queries via LLM Studio.
- `VectorStore.py`  
  Initializes and populates the vector stores for documents and keywords.
- `search.py`  
  Provides functionalities for search, retrieval, and re-ranking.
- `wiki_dump.py`  
  Manages downloading, preprocessing, and parsing of Wikipedia data.
- `test.ipynb`  
  A Jupyter Notebook for testing and debugging the system.
- `README.md`  
  Detailed instructions for setting up and running the project.

## How It Works

1. **Query Input:**  
   Users submit a query in Italian via the Streamlit interface or command line.
2. **Information Retrieval:**  
   The system searches Italian Wikipedia using separate vector stores:
   - A **document vector store** for detailed text chunks.
   - A **keyword vector store** for title-based retrieval.
3. **Content Generation:**  
   The retrieved data is passed to a language model that generates a human-like, comprehensive response.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-repo/wiki-rag.git
   cd wiki-rag
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**  
   Create a `.env` file in the project root with the following content:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

### Running the Streamlit Application

Launch the user interface with:
```bash
streamlit run app.py
```

## Wikipedia Dump Configuration

The project is set up to optionally download and process a Wikipedia dump. Update the following configuration variables as needed:

- **DUMP_URL:**  
  `https://dumps.wikimedia.org/itwiki/latest/itwiki-latest-pages-articles-multistream-index1.txt-p1p316052.bz2`
- **DUMP_FILE:**  
  `Data/itwiki-latest-pages-articles.xml.bz2`  
  *(Change this to the local path of your dump file.)*
- **OUTPUT_DIR:**  
  `Data`  
  *(Change this to your desired output directory.)*
- **BASE_DIR:**  
  `Data`

## Future Improvements (TODO)

- **Wikipedia Dump Pipeline:**  
  Integrate a full pipeline to download the Wikipedia dump and update the vector stores (using ChromaDB) by adding or modifying documents.
- **Enhanced UI:**  
  Add a chat history feature for better user interaction.
- **Improved Text Processing:**  
  Refine the splitting and chunking of Wikipedia articles for more accurate retrieval.

```