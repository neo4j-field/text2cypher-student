import pytest
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langsmith import Client


@pytest.fixture(scope="session")
def llm_openai_gpt_4o() -> ChatOpenAI:
    return ChatOpenAI(model="gpt-4o", temperature=0)


@pytest.fixture(scope="session")
def embedder_openai_text_embedding_ada_002() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model="text-embedding-ada-002")


@pytest.fixture(scope="session")
def langsmith_client() -> Client:
    return Client()
