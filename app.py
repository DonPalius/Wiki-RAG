import itertools
from search import Search
import streamlit as st
from prompt import *
import ast
from VectorStore import VectorStore
from ModelQuery import ModelQuery

# Initialize session state for vector_store and Search if not already done
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = VectorStore(collection_name="olympics")
    st.session_state.search = Search(st.session_state.vector_store.chroma_collection)
    st.session_state.llm = ModelQuery("http://127.0.0.1:1234/v1/chat/completions", "meta-llama-3.1-8b-instruct")

# Streamlit UI
st.title("Domande sui Giochi Olimpici")
st.write("Fai una domanda sui Giochi Olimpici per ottenere una risposta.")

# Text input for user questions
user_question = st.text_area("Inserisci la tua domanda:", height=100)

# Add a button to generate the answer
generate_button = st.button("Genera Risposta")

# Initialize answer placeholder
answer_placeholder = st.empty()

def process_query(question):
    with st.spinner("Recuperando informazioni rilevanti..."):
        semantic_results = st.session_state.search.semantic_retrieve(question)
        print("Recuperando informazioni rilevanti")

        semantic_docs = list(itertools.chain(*semantic_results['documents']))[::-1]
        context = " ".join(semantic_docs)

        # Debug: Token counting
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

        # Generate new queries based on the prompt
        new_queries = st.session_state.llm.query_local_model(
            query=user_question,
            context="",
            prompt=rewriting_prompt
        )
        new_queries = ast.literal_eval(new_queries)
        print(new_queries)
        
        # If new_queries is a list of queries, iterate through each and get results
        if isinstance(new_queries, list):
            all_documents = []
            for new_query in new_queries:
                semantic_results = st.session_state.search.semantic_retrieve(new_query)
                # Reverse the documents list to maintain original order
                semantic_docs = list(itertools.chain(*semantic_results['documents']))[::-1]
                all_documents.append(semantic_docs)
            # Re-rank using RRF (Ranked Retrieval Fusion)
            combined_results = st.session_state.search.rrf(all_documents)

            # Generate answer from combined results
            duck_result = st.session_state.search.duckduckgo_retrieve(user_question)
            context = duck_result + " ".join(combined_results)
            answer = st.session_state.llm.query_local_model(
                query=user_question,
                context=context,
                prompt=fallback_prompt
            )

            # Display the new answer
            st.write("## Risposta")
            st.write(answer)

            # Optionally show the context used
            with st.expander("Visualizza Contesto di Origine"):
                for idx, result in enumerate(combined_results[:], start=1):
                    st.write(f"Fonte {idx}:", result)
                    st.write("---")
        else:
            st.error("Impossibile generare nuove query.")
    else:
        # Display the original answer
        st.write("## Risposta")
        st.write(answer)

        # Optionally show the context used
        with st.expander("Visualizza Contesto di Origine"):
            for idx, result in enumerate(semantic_docs[:3], start=1):
                st.write(f"Fonte {idx}:", result)
                st.write("---")

# Add example questions to help users
with st.expander("Esempi di domande che puoi fare"):
    st.write("""
    - Quale città ospitò i primi Giochi Olimpici estivi dell'età moderna?
    - Quante volte i Giochi Olimpici estivi sono stati ospitati in Francia?
    - Chi è l'ultima vincitrice dei 100 metri piani?
    - L'arrampicata sportiva è uno sport olimpico?
    - Quale è il numero medio di ori olimpici per edizione per l'Italia?
    """)

# Add a status indicator
if generate_button:
    st.success("Elaborazione completata!")
else:
    st.info("Scrivi una domanda e clicca 'Genera Risposta' per iniziare.")