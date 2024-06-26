from typing import Any, Callable, List, Tuple

from langchain_core.documents import Document

from langchain.retrievers.multi_vector import MultiVectorRetriever, SearchType
from langchain.storage import InMemoryStore
from tests.unit_tests.indexes.test_indexing import InMemoryVectorStore


class InMemoryVectorstoreWithSearch(InMemoryVectorStore):
    @staticmethod
    def _identity_fn(score: float) -> float:
        return score

    def _select_relevance_score_fn(self) -> Callable[[float], float]:
        return self._identity_fn

    def similarity_search(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> List[Document]:
        res = self.store.get(query)
        if res is None:
            return []
        return [res]

    def similarity_search_with_score(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> List[Tuple[Document, float]]:
        res = self.store.get(query)
        if res is None:
            return []
        return [(res, 0.8)]


def test_multi_vector_retriever_initialization() -> None:
    vectorstore = InMemoryVectorstoreWithSearch()
    retriever = MultiVectorRetriever(  # type: ignore[call-arg]
        vectorstore=vectorstore, docstore=InMemoryStore(), doc_id="doc_id"
    )
    documents = [Document(page_content="test document", metadata={"doc_id": "1"})]
    retriever.vectorstore.add_documents(documents, ids=["1"])
    retriever.docstore.mset(list(zip(["1"], documents)))
    results = retriever.invoke("1")
    assert len(results) > 0
    assert results[0].page_content == "test document"


def test_multi_vector_retriever_similarity_search_with_score() -> None:
    documents = [Document(page_content="test document", metadata={"doc_id": "1"})]

    ## score_threshold = 0.5
    vectorstore = InMemoryVectorstoreWithSearch()
    retriever = MultiVectorRetriever(  # type: ignore[call-arg]
        vectorstore=vectorstore,
        docstore=InMemoryStore(),
        doc_id="doc_id",
        search_kwargs={"score_threshold": 0.5},
        search_type=SearchType.similarity_score_threshold,
    )
    retriever.vectorstore.add_documents(documents, ids=["1"])
    retriever.docstore.mset(list(zip(["1"], documents)))
    results = retriever.invoke("1")
    assert len(results) > 0
    assert results[0].page_content == "test document"

    ## score_threshold = 0.5
    vectorstore = InMemoryVectorstoreWithSearch()
    retriever = MultiVectorRetriever(  # type: ignore[call-arg]
        vectorstore=vectorstore,
        docstore=InMemoryStore(),
        doc_id="doc_id",
        search_kwargs={"score_threshold": 0.9},
        search_type=SearchType.similarity_score_threshold,
    )
    retriever.vectorstore.add_documents(documents, ids=["1"])
    retriever.docstore.mset(list(zip(["1"], documents)))
    results = retriever.invoke("1")
    assert len(results) == 0


async def test_multi_vector_retriever_initialization_async() -> None:
    vectorstore = InMemoryVectorstoreWithSearch()
    retriever = MultiVectorRetriever(  # type: ignore[call-arg]
        vectorstore=vectorstore, docstore=InMemoryStore(), doc_id="doc_id"
    )
    documents = [Document(page_content="test document", metadata={"doc_id": "1"})]
    await retriever.vectorstore.aadd_documents(documents, ids=["1"])
    await retriever.docstore.amset(list(zip(["1"], documents)))
    results = await retriever.ainvoke("1")
    assert len(results) > 0
    assert results[0].page_content == "test document"
