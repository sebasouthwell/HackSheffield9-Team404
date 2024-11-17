from ai_hallucination_lib import *
from databricks_langchain import DatabricksVectorSearch
from databricks_langchain import DatabricksEmbeddings
from databricks.vector_search.client import VectorSearchClient

loadDotEnv()
from langchain_core.documents import Document
# Read all files in ../copyright_free_books
import os
import json


def read_files():
    documents = []
    for filename in os.listdir("copyright_free_books"):
        with open(f"copyright_free_books/{filename}", "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
            # Split every file by every fifth newline
            lines = [lines[i:i+5] for i in range(0, len(lines), 5)]
            for line in lines:
                # Join the list of lines into a single string
                page_content = "".join(line)
                documents.append(Document(page_content=page_content, metadata={"source": filename}))
    return documents, [i+1 for i in range(len(documents))]

embeddings = DatabricksEmbeddings(endpoint="databricks-bge-large-en")

client = VectorSearchClient()

index = client.create_direct_access_index(
  endpoint_name="hs9",
  index_name="hacksheffield9.default.gutenberg",
  primary_key="id",
  embedding_dimension=1024,
  embedding_vector_column="text_vector",
  schema={
    "id": "int",
    "document_content": "string",
    "field3": "float",
    "text_vector": "array<float>"}
)



vector_store = DatabricksVectorSearch(
    endpoint="hs9",
    index_name="hacksheffield9.default.gutenberg",
    embedding=embeddings,
    # The column name in the index that contains the text data to be embedded
    text_column="document_content", 
)

docs, ids = read_files()

try:
    vector_store.add_documents(documents=docs, ids=ids)
    print(vector_store)
except requests.exceptions.SSLError as e:
    print(f"SSL error occurred: {e}")
