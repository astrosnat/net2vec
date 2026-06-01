from net2vec.config.settings import Settings
from net2vec.embeddings.client import EmbeddingClient
from net2vec.embeddings.factory import create_embedding_client, create_embedding_service


class FakeClient(EmbeddingClient):
    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


def test_factory_selects_local_client() -> None:
    settings = _settings(provider="local")

    client = create_embedding_client(settings, local_factory=FakeClient)

    assert isinstance(client, FakeClient)


def test_factory_selects_openai_client_with_api_key() -> None:
    captured = {}
    settings = _settings(provider="openai", api_key="sk-test")

    def openai_factory(api_key: str | None) -> EmbeddingClient:
        captured["api_key"] = api_key
        return FakeClient()

    client = create_embedding_client(settings, openai_factory=openai_factory)

    assert isinstance(client, FakeClient)
    assert captured == {"api_key": "sk-test"}


def test_factory_creates_embedding_service() -> None:
    settings = _settings(provider="local")

    service = create_embedding_service(settings)

    assert service.model == "fake-model"
    assert service.dimensions == 3


def _settings(provider: str, api_key: str | None = None) -> Settings:
    return Settings(
        database_url="postgresql+psycopg://net2vec:net2vec@localhost:5432/net2vec",
        openai_api_key=api_key,
        embedding_provider=provider,
        embedding_model="fake-model",
        embedding_dimensions=3,
        api_host="127.0.0.1",
        api_port=8000,
        mcp_url="http://127.0.0.1:8001/mcp",
    )
