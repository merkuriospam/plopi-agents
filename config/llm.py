import os
from dotenv import load_dotenv

load_dotenv()

def _get_api_key(provider: str) -> str:
    """
    Obtiene la API key, primero buscando una clave genérica,
    luego una específica del proveedor
    """
    # Intentar clave genérica primero
    api_key = os.getenv("LLM_API_KEY")
    if api_key:
        return api_key
    
    # Fallback a claves específicas del proveedor
    provider_keys = {
        "groq": "GROQ_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "azure": "AZURE_API_KEY",
    }
    
    key_name = provider_keys.get(provider)
    if key_name:
        return os.getenv(key_name)
    
    return None

def get_llm():
    """
    Factory function para obtener la instancia correcta del LLM
    basada en la configuración en .env
    """
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=model, api_key=_get_api_key(provider))
    
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, api_key=_get_api_key(provider))
    
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model, api_key=_get_api_key(provider))
    
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = _get_api_key(provider)
        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
    
    elif provider == "azure":
        from langchain_openai import AzureChatOpenAI
        return AzureChatOpenAI(
            model=model,
            azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
            api_version=os.getenv("AZURE_API_VERSION", "2024-02-15-preview")
        )
    
    else:
        raise ValueError(f"Proveedor LLM no soportado: {provider}")
