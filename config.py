from tokens import azure_openai_endpoint, azure_openai_key
from openai import AsyncAzureOpenAI, AzureOpenAI
from agents import set_tracing_disabled, ModelProvider, OpenAIChatCompletionsModel, Model, RunConfig, OpenAIResponsesModel

model_name = "o1"

async_client = AsyncAzureOpenAI(base_url=azure_openai_endpoint, api_key=azure_openai_key, api_version="2024-12-01-preview")
sync_client = AzureOpenAI(base_url=azure_openai_endpoint, api_key=azure_openai_key, api_version="2024-12-01-preview")
set_tracing_disabled(disabled=True)

class CustomModelProvider(ModelProvider):
    def get_model(self, model_name: str | None) -> Model:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=async_client)

class SyncCustomModelProvider(ModelProvider):
    def get_model(self, model_name: str | None) -> Model:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=sync_client)

#CUSTOM_MODEL_PROVIDER = CustomModelProvider()

run_config_model = RunConfig(model_provider = CustomModelProvider())
sync_run_config_model = RunConfig(model_provider = SyncCustomModelProvider())

model_to_use = OpenAIChatCompletionsModel(model = model_name, openai_client=async_client)
sync_model_to_use = OpenAIChatCompletionsModel(model = model_name, openai_client=sync_client)