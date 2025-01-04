import requests
import json

class ModelQuery:
    def __init__(self, model_endpoint, model_name, temperature=0.2, max_tokens=-1):
        """
        Initializes the LocalModelQuerier with the model endpoint and parameters.

        :param model_endpoint: URL of the local model endpoint.
        :param model_name: Name of the model to query.
        :param temperature: Sampling temperature for the model (default: 0.2).
        :param max_tokens: Maximum number of tokens to generate (default: -1 for no limit).
        """
        self.model_endpoint = model_endpoint
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def query_local_model(self, query, context, prompt):
        """
        Queries a local language model endpoint for generating responses, using
        the query and context in the prompt.

        :param query: The question to be asked.
        :param context: Additional context to be included in the query.
        :param prompt: The system prompt for the model.
        :return: The model's response.
        """
        headers = {"Content-Type": "application/json"}
        user_message = f"Question: {query}"
        if context is not None:
            user_message += f"\nContext: {context}"
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        response = requests.post(self.model_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Failed to get response from model: {response.status_code} - {response.text}")

# Example usage:
# model_querier = LocalModelQuerier("http://127.0.0.1:1234/v1/chat/completions", "meta-llama-3.1-8b-instruct")
# response = model_querier.query_local_model("What is the capital of France?", None, "Provide concise answers.")
# print(response)
