# Wiki-RAG

Wiki-RAG is a Retrieval-Augmented Generation (RAG) system designed to enhance the process of querying and generating responses based on the Italian Wikipedia. By combining advanced retrieval techniques with state-of-the-art natural language generation, Wiki-RAG provides precise, contextually relevant answers for Italian-language queries.

## Features

- **Retrieval-Augmented Generation:** Combines document retrieval and language generation to produce coherent, informative responses.
- **Italian Wikipedia Focus:** Tailored for Italian-language content to ensure culturally and contextually accurate results.
- **Dual Vector Store:** Utilizes two vector stores:
  - **Document Vector Store:** For semantic search over chunked document texts.
  - **Keyword Vector Store:** For title-based retrieval.
- **Local LLM Integration:** Interfaces with a local language model (e.g., `meta-llama-3.1-8b-instruct`) via LM Studio.

## Project Structure

- `requirements.txt`  
  Lists all dependencies required for the project.
- `app.py`  
  Streamlit interface for interacting with the Wiki-RAG system.
- `prompt.py`  
  Contains prompts for querying.
- `ModelQuery.py`  
  Handles local model queries via LM Studio.
- `VectorStore.py`  
  Manages initialization and population of vector stores for documents and keywords.
- `search.py`  
  Provides search, retrieval, and re-ranking functionalities.
- `wiki_dump.py`  
  Handles downloading, preprocessing, and parsing of the Wikipedia dump.
- `wikipedia_dump_processor.py`  
  Contains the `WikipediaDumpProcessor` class for dump extraction and processing (uses WikiExtractor).
- `README.md`  
  This file – detailed instructions for setup and usage.

## How It Works

1. **Query Input:**  
   Users submit an Italian query via the Streamlit interface.
2. **Information Retrieval:**  
   The system uses two vector stores:
   - **Document Vector Store:** Retrieves relevant document chunks.
   - **Keyword Vector Store:** Retrieves articles based on titles.
3. **Response Generation:**  
   Retrieved content is passed to a local LLM (via LM Studio) to generate a comprehensive answer.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone git@github.com:DonPalius/Wiki-RAG.git
   cd Wiki-RAG
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**  
   Create a `.env` file in the project root with the following content (update paths as needed):
   ```env
   OPENAI_API_KEY=your_openai_api_key
   DUMP_FILE=Data/itwiki-latest-pages-articles1.xml-p1p316052.bz2
   OUTPUT_DIR=Data
   BASE_DIR=Data
   ```

## Wikipedia Dump Configuration

Wiki-RAG is set up to optionally download and process a Wikipedia dump using WikiExtractor. Update these configuration variables in your environment or code (current version) as needed:

- **DUMP_URL:**  
  `https://dumps.wikimedia.org/itwiki/latest/itwiki-latest-pages-articles1.xml-p1p316052.bz2`
- **DUMP_FILE:**  
  The local path to your downloaded dump file (e.g., `Data/itwiki-latest-pages-articles1.xml-p1p316052.bz2`).
- **OUTPUT_DIR:**  
  The directory where extracted files and CSV outputs will be stored (e.g., `Data`).
- **BASE_DIR:**  
  The base directory for extracted files (usually the same as OUTPUT_DIR).

The `WikipediaDumpProcessor` class in `wikipedia_dump_processor.py` handles:
- **Downloading:** Checks if the dump exists locally; if not, downloads it.
- **Extraction:** Uses WikiExtractor to convert the dump into JSON files.
- **Parsing and Chunking:** Converts JSON files to a Pandas DataFrame, splits article text into smaller chunks, and saves the results in `Wikipedia.csv`.

## LM Studio & Local LLM Setup

Wiki-RAG uses LM Studio to interface with a local language model. For example, to use the `meta-llama-3.1-8b-instruct` model:

1. **Download and Install LM Studio:**
   - Visit [LM Studio](https://lmstudio.ai/) and install the application.

2. **Download the Model:**
   - Within LM Studio, locate and download the `meta-llama-3.1-8b-instruct` model.

3. **Start the LM Studio Local Server:**
   - Launch LM Studio and load the model. The default endpoint is typically:
     ```
     http://127.0.0.1:1234/v1/chat/completions
     ```

4. **Configure the Model Query:**
   - In `app.py`, the local model is initialized as follows:
     ```python
     if 'llm' not in st.session_state:
         st.session_state.llm = ModelQuery("http://127.0.0.1:1234/v1/chat/completions", "meta-llama-3.1-8b-instruct")
     ```

## Running the Application

### Launching the Streamlit UI

Run the Streamlit interface with:
```bash
streamlit run app.py
```

### Updating the Vector Stores

In the UI, click the **"Scarica e carica dump Wikipedia"** button to:
- Download and process the Wikipedia dump.
- Parse, chunk, and update both the document and keyword vector stores.
- The updated data is stored in `Wikipedia.csv` and loaded into ChromaDB-backed collections.

## Future Improvements

- **Wikipedia Dump Pipeline v2:**  
  Download the full dump of italian wikipedia, split in multiple vector and load it only after we find a match in the keyword vectorstore.

- **Enhanced UI:**  
  Implement a chat history feature for improved user interaction.
- **Improved Text Processing:**  
  Further refine article chunking for better retrieval accuracy.

## Additional Notes

- **VectorStore:**  
  The `VectorStore` class in `VectorStore.py` manages two separate collections:
  - **Document Collection (`wikipedia_docs`):** Stores individual text chunks.
  - **Keyword Collection (`wikipedia_keywords`):** Stores article titles with associated chunk IDs.
  
- **Search Functionality:**  
  The `Search` class (in `search.py`) provides methods for semantic retrieval (from document chunks) and keyword-based retrieval.

By following these instructions, you'll have a fully functional Wiki-RAG system that integrates both document and keyword vector stores, and communicates with a local LLM via LM Studio.
