from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

class AzureOpenAIClientSingleton:
    _instance = None
    _client = None

    def __new__(cls, endpoint=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialize_client(endpoint)
        return cls._instance

    @classmethod
    def _initialize_client(cls, endpoint):
        if cls._client is None:
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

            cls._client = AzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,
                api_version="2024-02-01",
            )


    @classmethod
    def get_client(cls):
        if cls._client is None:
            raise ValueError("Client not initialized. Call AzureOpenAIClientSingleton(api_key, endpoint) first.")
        return cls._client
