from duckduckgo_search import DDGS
class Search:
    """
    Search class for RAG (Retrieval-Augmented Generation) application.
    This class provides methods for document retrieval using semantic search with vector
    embeddings, and a Reciprocal Rank Fusion (RRF) algorithm to combine results from multiple rankers.
    """
    
    def __init__(self, db):
        """
        Initializes the Search class with a Retriever instance.
        
        Parameters:
        -----------
        retriever : Retriever
            The Retriever instance containing BM25 and vector search methods.
        """
        self.db = db



    def semantic_retrieve(self, query, n_results=10):
        """
        Retrieves top documents based on semantic similarity using vector embeddings.
        
        Parameters:
        -----------
        query : str
            The search query.
        n_results : int, optional
            Number of top results to retrieve (default: 10).
        
        Returns:
        --------
        list
            Top n documents ranked by semantic similarity.
        """
        query_args = {
            "query_texts": query,
            "n_results": n_results,
            "include": ['documents', 'metadatas', 'distances', 'uris']
        }
        return self.db.query(**query_args)
    
    def duckduckgo_retrieve(self, query):
        """
        Retrieves search results from DuckDuckGo for the given query.
        
        Parameters:
        -----------
        query : str
            The search query.
        max_results : int, optional
            Maximum number of results to retrieve (default: 10).
        
        Returns:
        --------
        list
            A list of search results from DuckDuckGo.
                """
        results = DDGS().text(query, max_results=3)
        ans = []
        for i in results:
            ans.append(f"[{i['title']}],{i['body']}")


        
        return ' '.join(ans)


    def rrf(self, results_list, k=10, c=60):
        """
        Generalized Reciprocal Rank Fusion (RRF) for combining results from multiple rankers.
        
        Parameters:
        -----------
        results_list : list of lists
            A list where each inner list contains ranked documents from a classifier.
        k : int, optional
            Number of top results to return (default: 10).
        c : int, optional
            Constant to prevent division by small numbers, typically 60 (default: 60).
            
        Returns:
        --------
        list
            Top k documents ranked by their combined RRF scores.
        """
        scores = {}
        
        # Aggregate scores from each ranker's results
        for classifier_results in results_list:
            for idx, doc in enumerate(classifier_results):
                scores[doc] = scores.get(doc, 0) + 1 / (idx + c)
        
        # Sort documents by RRF score in descending order
        sorted_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
        # Return the top k ranked documents
        return [doc[0] for doc in sorted_results[:k]]
