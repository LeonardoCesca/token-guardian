from app.providers.sources.anthropic import list_models as list_anthropic_models
from app.providers.sources.google import list_models as list_google_models
from app.providers.sources.openai import list_models as list_openai_models
from app.providers.sources.openrouter import list_models as list_openrouter_models


PROVIDER_ADAPTERS = {
    "anthropic": list_anthropic_models,
    "google": list_google_models,
    "openai": list_openai_models,
    "openrouter": list_openrouter_models,
}
