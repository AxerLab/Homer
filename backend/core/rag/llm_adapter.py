import asyncio
from typing import List, Optional
import numpy as np
import httpx

from lightrag.utils import EmbeddingFunc

from .config import rag_config

HF_INFERENCE_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction"


async def hf_embedding_func(texts: List[str]) -> np.ndarray:
    if not texts:
        return np.array([])

    url = f"{HF_INFERENCE_URL}/{rag_config.embedding_model}"
    headers = {"Content-Type": "application/json"}
    if rag_config.hf_api_token:
        headers["Authorization"] = f"Bearer {rag_config.hf_api_token}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            headers=headers,
            json={"inputs": texts, "options": {"wait_for_model": True}},
        )
        response.raise_for_status()
        result = response.json()

        # Handle different response formats
        # TEI returns list of embeddings directly or nested
        if isinstance(result, list) and len(result) > 0:
            # If nested (token-level), mean pool
            if isinstance(result[0], list) and isinstance(result[0][0], list):
                embeddings = [np.mean(emb, axis=0) for emb in result]
            else:
                embeddings = result
        else:
            embeddings = result

    return np.array(embeddings, dtype=np.float32)


def get_embedding_func() -> EmbeddingFunc:
    return EmbeddingFunc(
        embedding_dim=rag_config.embedding_dim,
        max_token_size=512,
        func=hf_embedding_func,
    )


async def groq_complete_func(
    prompt: str,
    system_prompt: Optional[str] = None,
    history_messages: Optional[List[dict]] = None,
    **kwargs,
) -> str:
    if not rag_config.groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {rag_config.groq_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": rag_config.groq_model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4096),
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def get_llm_model_func():
    return groq_complete_func


def get_vision_model_func():
    async def vision_func(
        prompt: str,
        system_prompt: Optional[str] = None,
        history_messages: Optional[List[dict]] = None,
        image_data: Optional[str] = None,
        messages: Optional[List[dict]] = None,
        **kwargs,
    ) -> str:
        if not rag_config.groq_api_key:
            raise ValueError("GROQ_API_KEY required for vision model")

        if messages:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {rag_config.groq_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama-3.2-90b-vision-preview",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 4096,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

        if image_data:
            msg = {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ],
            }
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {rag_config.groq_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama-3.2-90b-vision-preview",
                        "messages": [msg],
                        "temperature": 0.7,
                        "max_tokens": 4096,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

        return await groq_complete_func(
            prompt, system_prompt, history_messages, **kwargs
        )

    return vision_func
