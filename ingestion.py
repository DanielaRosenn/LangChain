import os
import sys
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from openai import embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import ReadTheDocsLoader
from bs4 import BeautifulSoup

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def ingest_docs():
    loader = ReadTheDocsLoader("C:/Users/DanielaRosenstein/Desktop/LangChain/documentation-helper/langchain-docs",
                               encoding="utf8")
    raw_documents = loader.load()

    print(f"loaded {len(raw_documents)} documents")

    # Reduce chunk size to ensure individual chunks aren't too large
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    documents = text_splitter.split_documents(raw_documents)

    for doc in documents:
        new_url = doc.metadata["source"]
        new_url = new_url.replace("langchain-docs", "https:/")
        doc.metadata.update({"source": new_url})

    print(f"Going to add {len(documents)} documents to Pinecone in batches")

    # Process documents in batches to avoid hitting Pinecone's size limit
    batch_size = 50  # Adjust this based on your document sizes

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        print(
            f"Processing batch {i // batch_size + 1}/{(len(documents) + batch_size - 1) // batch_size} ({len(batch)} documents)")

        try:
            # Create vector store with the first batch or add to existing
            if i == 0:
                vector_store = PineconeVectorStore.from_documents(
                    batch, embeddings, index_name="langchain-doc-index"
                )
            else:
                vector_store.add_documents(batch)
            print(f"Successfully processed batch {i // batch_size + 1}")

        except Exception as e:
            print(f"Error processing batch {i // batch_size + 1}: {e}")
            # If batch fails, try smaller sub-batches
            smaller_batch_size = 10
            for j in range(0, len(batch), smaller_batch_size):
                sub_batch = batch[j:j + smaller_batch_size]
                try:
                    if i == 0 and j == 0:
                        vector_store = PineconeVectorStore.from_documents(
                            sub_batch, embeddings, index_name="langchain-doc-index"
                        )
                    else:
                        vector_store.add_documents(sub_batch)
                    print(f"Successfully processed sub-batch {j // smaller_batch_size + 1}")
                except Exception as sub_e:
                    print(f"Error processing sub-batch {j // smaller_batch_size + 1}: {sub_e}")
                    continue

    print("*** Loading to vectorstore done")


if __name__ == '__main__':
    ingest_docs()