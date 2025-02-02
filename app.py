import itertools
import ast
import streamlit as st
from search import Search
from prompt import *
from VectorStore import VectorStore
from ModelQuery import ModelQuery
import wikipedia_dump_processor as wp
import pandas as pd
def download_and_process_dump():
    """
    Main function to download, extract, parse, and chunk the Wikipedia dump.
    Returns the processed DataFrame.
    """
    # Define your Wikipedia dump parameters (adjust as needed)
    DUMP_URL = "https://dumps.wikimedia.org/itwiki/latest/itwiki-latest-pages-articles-multistream-index1.txt-p1p316052.bz2"
    DUMP_FILE = "/home/palius/Desktop/GITHUB/Wiki-RAG/Data/itwiki-latest-pages-articles.xml.bz2"    # Change this to your local dump file path
    OUTPUT_DIR = "/home/palius/Desktop/GITHUB/Wiki-RAG/Data"         # Change this to your desired output directory
    BASE_DIR = OUTPUT_DIR                         # Assuming the extracted files reside in the output directory

    # Ensure the output directory exists
    # os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Initialize processor and execute processing steps
    processor = wp.WikipediaDumpProcessor(DUMP_URL, DUMP_FILE, OUTPUT_DIR, BASE_DIR)
    processor.download_dump()
    processor.extract_dump()
    df = processor.parse_extracted_files()
    # Assumes that the article text is stored in the 'text' column. Adjust if necessary.
    df = processor.chunk_dataframe_text(df, 'text')
    return df.head(1)

# Initialize session state for the LLM if not already done.
if 'llm' not in st.session_state:
    st.session_state.llm = ModelQuery("http://127.0.0.1:1234/v1/chat/completions", "meta-llama-3.1-8b-instruct")

# -------------------------------------------------------------------
# Button to Download and Process Wikipedia Dump and Update Vector Store
# -------------------------------------------------------------------
st.header("Aggiorna Vector Store da Wikipedia Dump")
if st.button("Scarica e carica dump Wikipedia"):
    with st.spinner("Elaborazione del dump in corso..."):
        # Import the helper function from your processing module.
        # processor = wp.WikipediaDumpProcessor()
        # df = download_and_process_dump()
        df = pd.read_csv('/home/palius/Desktop/GITHUB/Wiki-RAG/Data/Wikipedia.csv').head(1)
        # Create a new VectorStore with reset enabled using the generated CSV
        vector_store = VectorStore(
            doc_collection_name="wikipedia_docs",
            keyword_collection_name="wikipedia_keywords",
            data_path="/home/palius/Desktop/GITHUB/Wiki-RAG/Data/Wikipedia.csv",
            reset=True
        )
        # Process both document chunks and keywords
        df_final = vector_store.process_all(chunked_docs=df)
        # Update the session state with the new vector store and search object.
        st.session_state.vector_store = vector_store
        st.session_state.search = Search(vector_store.chroma_collection)
    st.success("Dump Wikipedia processato e Vector Store aggiornato con successo!")

# -------------------------------------------------------------------
# Existing Q&A UI Section
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
        semantic_results = st.session_state.search.semantic_retrieve(question)
        print("Recuperando informazioni rilevanti")
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
                semantic_results = st.session_state.search.semantic_retrieve(new_query)
                semantic_docs = list(itertools.chain(*semantic_results['documents']))[::-1]
                all_documents.append(semantic_docs)
            # Re-rank using RRF (Ranked Retrieval Fusion)
            combined_results = st.session_state.search.rrf(all_documents)
            duck_result = st.session_state.search.duckduckgo_retrieve(user_question)
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

with st.expander("Esempi di domande che puoi fare"):
    st.write("""
    - Quale città ospitò i primi Giochi Olimpici estivi dell'età moderna?
    - Quante volte i Giochi Olimpici estivi sono stati ospitati in Francia?
    - Chi è l'ultima vincitrice dei 100 metri piani?
    - L'arrampicata sportiva è uno sport olimpico?
    - Quale è il numero medio di ori olimpici per edizione per l'Italia?
    """)

if generate_button:
    st.success("Elaborazione completata!")
else:
    st.info("Scrivi una domanda e clicca 'Genera Risposta' per iniziare.")
