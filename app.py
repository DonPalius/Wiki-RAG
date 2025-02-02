import itertools
import ast
import streamlit as st
from search import Search
from prompt import *
from VectorStore import VectorStore
from ModelQuery import ModelQuery
import wikipedia_dump_processor as wp
from dotenv import load_dotenv
import os
load_dotenv()
print(os.getenv("DUMP_FILE"))
def download_and_process_dump():
    """
    Main function to download, extract, parse, and chunk the Wikipedia dump.
    Returns the processed DataFrame.
    """
    # Define your Wikipedia dump parameters (adjust as needed)
    DUMP_URL = "https://dumps.wikimedia.org/itwiki/latest/itwiki-latest-pages-articles1.xml-p1p316052.bz2"
    DUMP_FILE = "Data/itwiki-latest-pages-articles1.xml-p1p316052.bz2"    # Change this to your local dump file path
    OUTPUT_DIR = "Data"         # Change this to your desired output directory
    BASE_DIR = OUTPUT_DIR                       # Assuming the extracted files reside in the output directory

    # Ensure the output directory exists
    # os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Initialize processor and execute processing steps
    processor = wp.WikipediaDumpProcessor(DUMP_URL, DUMP_FILE, OUTPUT_DIR, BASE_DIR)
    processor.download_dump()
    processor.extract_dump()
    df = processor.parse_extracted_files().head(1)
    # Assumes that the article text is stored in the 'text' column. Adjust if necessary.
    df = processor.chunk_dataframe_text(df, 'text')
    return df.head(5)

# Initialize session state for the LLM if not already done.
if 'llm' not in st.session_state:
    st.session_state.llm = ModelQuery("http://127.0.0.1:1234/v1/chat/completions", "meta-llama-3.1-8b-instruct")

# -------------------------------------------------------------------
# Always initialize the vector stores (document and keyword) even if no dump is downloaded.
# -------------------------------------------------------------------
if 'vector_store_doc' not in st.session_state or 'vector_store_keywords' not in st.session_state:
    try:
        # Create a single VectorStore instance so we can extract both collections.
        vs = VectorStore(
            doc_collection_name="wikipedia_docs",
            keyword_collection_name="wikipedia_keywords",
            data_path="Wikipedia.csv",  # Provide the path if the CSV exists; otherwise, set to None
            reset=False
        )
    except Exception as e:
        vs = VectorStore(
            doc_collection_name="wikipedia_docs",
            keyword_collection_name="wikipedia_keywords",
            reset=False
        )
    st.session_state.vector_store_doc = vs.doc_collection
    st.session_state.vector_store_keywords = vs.keyword_collection

# Initialize search objects if they do not exist
if 'search_docs' not in st.session_state:
    st.session_state.search_docs = Search(st.session_state.vector_store_doc)
if 'search_keywords' not in st.session_state:
    st.session_state.search_keywords = Search(st.session_state.vector_store_keywords)

# -------------------------------------------------------------------
# Button to Download and Process Wikipedia Dump and Update Vector Stores
# -------------------------------------------------------------------
st.header("Aggiorna Vector Store da Wikipedia Dump")
if st.button("Scarica e carica dump Wikipedia"):
    with st.spinner("Elaborazione del dump in corso..."):
        df = download_and_process_dump()
        # Reinitialize vector stores with reset enabled to ensure a fresh update.
        vs = VectorStore(
            doc_collection_name="wikipedia_docs",
            keyword_collection_name="wikipedia_keywords",
            data_path="Wikipedia.csv",
            reset=True
        )
        # Update session state with the separate vector stores.
        st.session_state.vector_store_doc = vs.doc_collection
        st.session_state.vector_store_keywords = vs.keyword_collection
        # Process both document chunks and keywords using the same instance.
        df_final = vs.process_all(chunked_docs=df, use_openai_embedding=False)
        # Update the session state search objects with the new collections.
        st.session_state.search_docs = Search(st.session_state.vector_store_doc)
        st.session_state.search_keywords = Search(st.session_state.vector_store_keywords)
    st.success("Dump Wikipedia processato e Vector Stores aggiornati con successo!")

# -------------------------------------------------------------------
#  Q&A UI Section
# -------------------------------------------------------------------
st.title("Domande sui Giochi Olimpici")
st.write("Fai una domanda sui Giochi Olimpici per ottenere una risposta.")

# Text input for user questions
user_question = st.text_area("Inserisci la tua domanda:", height=100)

# Button to generate the answer
generate_button = st.button("Genera Risposta")

# Answer placeholder
answer_placeholder = st.empty()

def process_query(question):
    with st.spinner("Recuperando informazioni rilevanti..."):
        # Use the document vector store for semantic retrieval.
        semantic_results = st.session_state.search_docs.semantic_retrieve(question)
        print(semantic_results)
        # Flatten and reverse the document lists to preserve original order.
        semantic_docs = list(itertools.chain(*semantic_results['documents']))[::-1]
        context = " ".join(semantic_docs)
        # Debug: Count tokens using tiktoken
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        encoded_text = encoding.encode(context)
        print("Numero di token:", len(encoded_text))
    with st.spinner("Generando risposta..."):
        answer = st.session_state.llm.query_local_model(
            query=question,
            context=context,
            prompt=answer_prompt
        )
        return answer, semantic_docs

if user_question and generate_button:
    answer, semantic_docs = process_query(user_question)

    # Check for fallback condition
    if answer == "Non posso rispondere.":
        st.warning("La risposta non è stata soddisfacente. Generando nuove query...")
        new_queries = st.session_state.llm.query_local_model(
            query=user_question,
            context="",
            prompt=rewriting_prompt
        )
        new_queries = ast.literal_eval(new_queries)
        print(new_queries)
        
        if isinstance(new_queries, list):
            all_documents = []
            for new_query in new_queries:
                semantic_results = st.session_state.search_docs.semantic_retrieve(new_query)
                semantic_docs = list(itertools.chain(*semantic_results['documents']))[::-1]
                all_documents.append(semantic_docs)
            # Re-rank using RRF (Ranked Retrieval Fusion)
            combined_results = st.session_state.search_docs.rrf(all_documents)
            duck_result = st.session_state.search_docs.duckduckgo_retrieve(user_question)
            context = duck_result + " " + " ".join(combined_results)
            answer = st.session_state.llm.query_local_model(
                query=user_question,
                context=context,
                prompt=fallback_prompt
            )
            st.write("## Risposta")
            st.write(answer)
            with st.expander("Visualizza Contesto di Origine"):
                for idx, result in enumerate(combined_results, start=1):
                    st.write(f"Fonte {idx}:", result)
                    st.write("---")
        else:
            st.error("Impossibile generare nuove query.")
    else:
        st.write("## Risposta")
        st.write(answer)
        with st.expander("Visualizza Contesto di Origine"):
            for idx, result in enumerate(semantic_docs[:3], start=1):
                st.write(f"Fonte {idx}:", result)
                st.write("---")

if generate_button:
    st.success("Elaborazione completata!")
else:
    st.info("Scrivi una domanda e clicca 'Genera Risposta' per iniziare.")
