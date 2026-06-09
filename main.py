"""
Myanmar-English Bilingual RAG Pipeline
This module implements a Retrieval-Augmented Generation system for Myanmar and English text.
"""

import re
import os
import time
from typing import List, Optional
from dotenv import load_dotenv

# LangChain imports
from langchain_cohere import CohereEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

# Qdrant imports
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# Load environment variables from .env file
load_dotenv()

# Configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "myanmar_english_knowledge_corp"

# LLM Configuration
LLM_API_BASE = os.getenv("LLM_API_BASE", "http://localhost:8000")
LLM_API_KEY = os.getenv("LLM_API_KEY", "sk-default-key")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
USE_CUSTOM_LLM = os.getenv("USE_CUSTOM_LLM", "false").lower() == "true"

# Validate API key
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY not found in environment variables. Please set it in .env file.")

print("[OK] Configuration loaded successfully")


def calculated_cohere_token_metric(text: str) -> int:
    """
    Returns exact token count for text using Cohere's tokenizer.
    This ensures accurate chunk sizes relative to the Cohere Embed model.
    """
    if not text.strip():
        return 0
    try:
        import cohere
        client = cohere.ClientV2(api_key=COHERE_API_KEY)
        response = client.tokenize(text=text, model="embed-multilingual-v3.0")
        return len(response.tokens)
    except Exception as e:
        print(f"Warning: Could not tokenize with Cohere: {e}")
        # Fallback: approximate 1 token ~ 4 characters for multilingual text
        return len(text) // 4


def strict_unicode_sanitizer(text: str) -> str:
    """
    Cleans structural noise and normalizes Burmese Unicode text without fracturing
    compound Burmese characters.
    
    Handles:
    - Zero-width non-joiners/joiners that cause token inflation
    - Burmese punctuation standardization (Pyaat-thone / Shone)
    - Excessive whitespace
    """
    # Strip dangerous zero-width non-joiners/joiners which cause token inflation
    text = re.sub(r'[\u200c\u200d]', '', text)
    
    # Standardize consecutive Burmese punctuation markers
    # Pyaat-thone (။)
    text = re.sub(r'\s*။\s*', '။ ', text)
    # Shone (၊)
    text = re.sub(r'\s*၊\s*', '၊ ', text)
    
    # Collapse multiple whitespace lines down to logical bounds
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\n+', '\n\n', text)
    
    return text.strip()


def load_and_sanitize_documents(file_path: str) -> List:
    """
    Loads PDF documents and sanitizes the text content.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of documents with sanitized content
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    try:
        loader = PyPDFLoader(file_path)
        raw_docs = loader.load()
        
        # Sanitize each document
        for doc in raw_docs:
            doc.page_content = strict_unicode_sanitizer(doc.page_content)
        
        print(f"[OK] Loaded {len(raw_docs)} pages from {file_path}")
        return raw_docs
    
    except Exception as e:
        print(f"[ERR] Error loading PDF: {e}")
        raise


def initialize_qdrant_collection() -> QdrantClient:
    """
    Initializes connection to Qdrant and creates collection if it doesn't exist.
    
    Returns:
        QdrantClient instance
    """
    try:
        client = QdrantClient(url=QDRANT_URL)
        
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if COLLECTION_NAME in collection_names:
            print(f"Deleting existing collection: {COLLECTION_NAME}")
            client.delete_collection(collection_name=COLLECTION_NAME)
        
        print(f"Creating collection: {COLLECTION_NAME}")
        
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=qmodels.VectorParams(
                size=1024,  # Cohere multilingual-v3.0 dimension
                distance=qmodels.Distance.COSINE
            )
        )
        
        # Build a full-text lexical index inside the payload for BM25 search
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="page_content",
            field_schema=qmodels.TextIndexParams(
                type=qmodels.TextIndexType.TEXT,
                tokenizer=qmodels.TokenizerType.MULTILINGUAL
            )
        )
        print("[OK] Collection created with multilingual text indexing")
        
        return client
    
    except Exception as e:
        print(f"[ERR] Error initializing Qdrant: {e}")
        print(f"  Make sure Qdrant is running at {QDRANT_URL}")
        raise


def create_rag_pipeline(vector_store: QdrantVectorStore):
    """
    Creates the RAG pipeline with retrieval and generation chains.
    
    Args:
        vector_store: QdrantVectorStore instance
        
    Returns:
        RAG application system (retrieval + generation chain)
    """
    
    # System prompt for bilingual generation
    bilingual_prompt_template = """You are an expert bilingual knowledge engine serving users in Myanmar and English.

Carefully evaluate the following context extracts to answer the incoming user query. The texts are raw, verified Unicode segments containing cross-lingual knowledge entries.

CRITICAL GENERATION INSTRUCTIONS:
1. You must respond to the user utilizing the exact language, script, and writing style of their question.
2. If the query is written in Burmese Unicode, your entire thought structure and final output must be in pure Burmese Unicode.
3. If the query is in English, respond entirely in English.
4. If the answer cannot be confidently verified inside the provided context documents, state directly that you do not possess sufficient data to answer.

Context:
{context}

User Question: {input}
System Verified Output:"""
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_template(bilingual_prompt_template)
    
    # Initialize LLM - use custom endpoint if configured
    if USE_CUSTOM_LLM and LLM_API_BASE and LLM_API_BASE != "http://localhost:8000":
        print(f"[OK] Using custom OpenAI-compatible LLM at {LLM_API_BASE}")
        llm_engine = ChatOpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_API_BASE,
            model=LLM_MODEL,
            temperature=0.3,
        )
    else:
        print("[OK] Using OpenAI-compatible endpoint (default config)")
        llm_engine = ChatOpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_API_BASE,
            model=LLM_MODEL,
            temperature=0.3,
        )
    
    # Create retriever from vector store
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    # Create a simple RAG chain using RunnablePassthrough
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm_engine
    )
    
    print("[OK] RAG pipeline created successfully")
    return rag_chain


def main():
    """
    Main execution function for the RAG pipeline.
    """
    try:
        print("\n" + "="*60)
        print("Myanmar-English Bilingual RAG Pipeline")
        print("="*60 + "\n")
        
        # Step 1: Initialize embeddings
        print("1. Initializing Cohere Embeddings (multilingual-v3.0)...")
        embeddings_engine = CohereEmbeddings(
            model="embed-multilingual-v3.0",
            cohere_api_key=COHERE_API_KEY
        )
        print("[OK] Embeddings engine initialized")
        
        # Step 2: Initialize Qdrant
        print("\n2. Initializing Qdrant vector database...")
        qdrant_client = initialize_qdrant_collection()
        print("[OK] Qdrant initialized")
        
        # Step 3: Create vector store
        print("\n3. Creating vector store...")
        vector_store = QdrantVectorStore(
            client=qdrant_client,
            collection_name=COLLECTION_NAME,
            embedding=embeddings_engine
        )
        print("[OK] Vector store created")
        
        # Step 4: Load documents (you need to provide PDF files)
        print("\n4. Loading and processing documents...")
        
        # Create data directory if it doesn't exist
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"[OK] Created {data_dir} directory. Please add PDF files here.")
        
        # Check for PDF files
        pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"[WARN] No PDF files found in {data_dir}/ directory")
            print("To use this pipeline, add PDF files to the data/ directory")
            
            # Create sample data for testing
            # create_sample_data()
        else:
            # Process PDF files
            all_docs = []
            for pdf_file in pdf_files:
                file_path = os.path.join(data_dir, pdf_file)
                docs = load_and_sanitize_documents(file_path)
                all_docs.extend(docs)
            
            # Add documents to vector store
            print("\n5. Chunking and embedding documents...")
            
            # Initialize text splitter with Cohere token awareness
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=350,  # Tokens (not characters)
                chunk_overlap=35,  # 10% overlap
                length_function=calculated_cohere_token_metric,
                separators=["\n\n", "\n", "။", "၊", " ", ""]
            )
            
            # Split documents
            chunks = text_splitter.split_documents(all_docs)
            print(f"[OK] Created {len(chunks)} chunks from {len(all_docs)} documents")
            
            # Add to vector store
            vector_store.add_documents(chunks)
            print("[OK] Documents added to vector store")
        
        # Step 5: Create RAG pipeline
        print("\n6. Setting up RAG pipeline...")
        rag_pipeline = create_rag_pipeline(vector_store)
        
        # Step 6: Start interactive query loop
        print("\n7. RAG Pipeline ready for queries!")
        interactive_query_loop(rag_pipeline)
        
    except Exception as e:
        print(f"\n[ERR] Error in main: {e}")
        raise


def query_rag_pipeline(rag_pipeline, query_text: str, max_retries: int = 3, retry_delay: int = 2) -> Optional[str]:
    """
    Queries the RAG pipeline with error handling and retry logic.
    
    Args:
        rag_pipeline: The RAG chain to query
        query_text: The user's question
        max_retries: Number of times to retry on failure
        retry_delay: Delay in seconds between retries
        
    Returns:
        The LLM response or error message
    """
    
    for attempt in range(max_retries):
        try:
            print("\n[Processing] Retrieving documents...")
            result = rag_pipeline.invoke(query_text)
            
            # Extract content from result
            if hasattr(result, 'content'):
                response = result.content
            elif isinstance(result, dict) and 'content' in result:
                response = result['content']
            elif isinstance(result, str):
                response = result
            else:
                response = str(result)
            
            print("\n[OK] Response received")
            return response
            
        except Exception as e:
            error_msg = str(e)
            attempt_num = attempt + 1
            
            print(f"\n[WARN] Attempt {attempt_num}/{max_retries} failed")
            print(f"       Error: {error_msg[:100]}...")
            
            # Check if it's a connection error
            if "connection" in error_msg.lower() or "refused" in error_msg.lower():
                print(f"       Is your LLM endpoint running at {LLM_API_BASE}?")
                if attempt < max_retries - 1:
                    print(f"       Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
            # Check if it's an API key error
            elif "unauthorized" in error_msg.lower() or "api_key" in error_msg.lower():
                print("       Check your LLM_API_KEY in .env file")
                return None
            # Other errors - retry
            elif attempt < max_retries - 1:
                print(f"       Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    print(f"\n[ERR] Failed after {max_retries} attempts")
    return None


def interactive_query_loop(rag_pipeline):
    """
    Interactive query loop for the RAG pipeline.
    Users can ask questions until they type 'exit' or 'quit'.
    
    Args:
        rag_pipeline: The RAG chain to query
    """
    
    print("\n" + "="*60)
    print("INTERACTIVE RAG QUERY MODE")
    print("="*60)
    print("\nYou can now ask questions about the documents.")
    print("Supports Myanmar (Burmese) and English queries.")
    print("Type 'exit' or 'quit' to stop.\n")
    
    query_count = 0
    
    while True:
        try:
            # Get user query
            user_query = input("\n> Your Question: ").strip()
            
            # Check for exit commands
            if user_query.lower() in ['exit', 'quit', 'bye']:
                print("\n[OK] Thank you for using the RAG pipeline. Goodbye!")
                break
            
            # Skip empty queries
            if not user_query:
                print("[WARN] Please enter a question.")
                continue
            
            query_count += 1
            print(f"\n[Query #{query_count}] {user_query}")
            print("-" * 60)
            
            # Query the pipeline
            response = query_rag_pipeline(rag_pipeline, user_query)
            
            if response:
                print("\n[Answer]:")
                print(response)
                print("-" * 60)
            else:
                print("\n[ERR] Could not generate response. Check your LLM endpoint configuration.")
                print(f"      Expected endpoint at: {LLM_API_BASE}")
                print(f"      Model: {LLM_MODEL}")
        
        except KeyboardInterrupt:
            print("\n\n[OK] Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERR] Unexpected error: {e}")
            print("      Please check your configuration.")



    """
    Creates sample data directory with instructions.
    """
    print("\n" + "="*60)
    print("SAMPLE DATA SETUP REQUIRED")
    print("="*60)
    print("\nTo run this RAG pipeline, you need to add PDF files with Myanmar and/or English text.")
    print("\nSteps:")
    print("1. Create a 'data/' directory in the project root (already created)")
    print("2. Add PDF files containing Myanmar and/or English text")
    print("3. Run the pipeline again")
    print("\nExample PDF files:")
    print("  - data/myanmar_text.pdf")
    print("  - data/english_text.pdf")
    print("  - data/bilingual_content.pdf")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
