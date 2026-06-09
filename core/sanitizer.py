import re


def strict_unicode_sanitizer(text: str) -> str:
    text = re.sub(r'[\u200c\u200d]', '', text)
    text = re.sub(r'\s*။\s*', '။ ', text)
    text = re.sub(r'\s*၊\s*', '၊ ', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\n+', '\n\n', text)
    return text.strip()


def sanitize_documents(docs: list) -> list:
    for doc in docs:
        doc.page_content = strict_unicode_sanitizer(doc.page_content)
    return docs
