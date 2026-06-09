from typing import List, Callable, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from core.config import settings


class BaseChunker:
    def split_documents(self, documents: List[Document]) -> List[Document]:
        raise NotImplementedError

    def split_text(self, text: str) -> List[str]:
        raise NotImplementedError


class LocalChunker(BaseChunker):
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        length_function: Optional[Callable] = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self._length_function = length_function

    def _default_length(self, text: str) -> int:
        return len(text) // 4

    @property
    def length_function(self) -> Callable:
        return self._length_function or self._default_length

    def split_documents(self, documents: List[Document]) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self.length_function,
            separators=["\n\n", "\n", "။", "၊", " ", ""],
        )
        return splitter.split_documents(documents)

    def split_text(self, text: str) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self.length_function,
            separators=["\n\n", "\n", "။", "၊", " ", ""],
        )
        return splitter.split_text(text)


class CloudChunker(BaseChunker):
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

    def split_documents(self, documents: List[Document]) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", "။", "၊", " ", ""],
        )
        return splitter.split_documents(documents)

    def split_text(self, text: str) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", "။", "၊", " ", ""],
        )
        return splitter.split_text(text)


def get_chunker(mode: str = "local") -> BaseChunker:
    if mode == "cloud":
        return CloudChunker()
    return LocalChunker()
