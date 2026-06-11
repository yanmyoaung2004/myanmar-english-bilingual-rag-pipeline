from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from core.config import settings
from core.embeddings import EmbeddingStrategy
from core.retriever import get_retriever
from rag.prompts import BILINGUAL_PROMPT


def create_llm():
    if settings.use_custom_llm and settings.llm_api_base != "http://localhost:8000":
        return ChatOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_api_base,
            model=settings.llm_model,
            temperature=0.3,
        )
    return ChatOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_api_base,
        model=settings.llm_model,
        temperature=0.3,
    )


def build_rag_pipeline(
    embedding_strategy: Optional[EmbeddingStrategy] = None,
    top_k: Optional[int] = None,
):
    prompt = ChatPromptTemplate.from_template(BILINGUAL_PROMPT)
    llm = create_llm()
    retriever = get_retriever(embedding_strategy, top_k)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
    )
    return rag_chain
