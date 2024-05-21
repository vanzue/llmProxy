from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

class AzureOpenAIClientSingleton:
    _instance = None
    _client = None

    def __new__(cls, api_key = None, endpoint=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialize_client(api_key,endpoint)
        return cls._instance

    @classmethod
    def _initialize_client(cls, api_key, endpoint):
        if cls._client is None:
            cls._client = AzureOpenAI(
                api_key = api_key,
                azure_endpoint=endpoint,
                api_version="2024-02-01",
            )


    @classmethod
    def get_client(cls):
        if cls._client is None:
            raise ValueError("Client not initialized. Call AzureOpenAIClientSingleton(api_key, endpoint) first.")
        return cls._client
