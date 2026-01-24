"""LLM and Embedding adapters for RAG service"""

import os
from typing import List, Optional

import httpx
import numpy as np
from huggingface_hub import AsyncInferenceClient

from lightrag.utils import EmbeddingFunc

from .config import rag_config

# Portkey configuration
PORTKEY_GATEWAY_URL = "https://api.portkey.ai/v1/chat/completions"
PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY", "")
PORTKEY_CONFIG_ID = os.getenv("PORTKEY_CONFIG_ID", "")


def _get_portkey_headers() -> dict:
    if not PORTKEY_API_KEY:
        raise ValueError("PORTKEY_API_KEY environment variable is required")
    if not PORTKEY_CONFIG_ID:
        raise ValueError("PORTKEY_CONFIG_ID environment variable is required")
    return {
        "Content-Type": "application/json",
        "x-portkey-api-key": PORTKEY_API_KEY,
        "x-portkey-config": PORTKEY_CONFIG_ID,
    }


async def portkey_complete(
    prompt: str,
    system_prompt: Optional[str] = None,
    history_messages: Optional[List[dict]] = None,
    **kwargs,
) -> str:
    """Complete text using Portkey gateway"""
    headers = _get_portkey_headers()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            PORTKEY_GATEWAY_URL,
            headers=headers,
            json={
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4096),
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def portkey_vision_complete(
    prompt: str,
    system_prompt: Optional[str] = None,
    history_messages: Optional[List[dict]] = None,
    image_data: Optional[str] = None,
    messages: Optional[List[dict]] = None,
    **kwargs,
) -> str:
    """Complete text with vision using Portkey gateway"""
    headers = _get_portkey_headers()

    if messages:
        request_messages = messages
    elif image_data:
        request_messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ],
            }
        ]
    else:
        return await portkey_complete(prompt, system_prompt, history_messages, **kwargs)

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            PORTKEY_GATEWAY_URL,
            headers=headers,
            json={
                "messages": request_messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4096),
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def hf_embedding_func(texts: List[str]) -> np.ndarray:
    """Generate embeddings using HuggingFace Inference API"""
    if not texts:
        return np.array([])

    client = AsyncInferenceClient(
        provider="hf-inference",
        api_key=rag_config.hf_api_token or os.environ.get("HF_TOKEN"),
    )

    embeddings = []
    for text in texts:
        result = await client.feature_extraction(
            text,
            model=rag_config.embedding_model,
        )
        embeddings.append(result)

    return np.array(embeddings, dtype=np.float32)


def get_embedding_func() -> EmbeddingFunc:
    """Get the embedding function for RAGAnything"""
    return EmbeddingFunc(
        embedding_dim=rag_config.embedding_dim,
        max_token_size=512,
        func=hf_embedding_func,
    )


def get_llm_model_func():
    """Get the LLM function for RAGAnything"""
    return portkey_complete


def get_vision_model_func():
    """Get the vision model function for RAGAnything"""
    return portkey_vision_complete
