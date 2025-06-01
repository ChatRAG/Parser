import cohere
import os

API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(API_KEY)


def embed_text(text, model="embed-multilingual-v3.0", input_type="search_query"):
    response = co.embed(
        texts=[text],
        model=model,
        input_type=input_type,
        embedding_types=["float"]
    )
    return response.embeddings.float_[0]
