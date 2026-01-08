import os
from typing import List, Optional
import numpy as np
from huggingface_hub import AsyncInferenceClient

from lightrag.utils import EmbeddingFunc

from .config import rag_config
from ..llm import portkey_complete, portkey_vision_complete


async def hf_embedding_func(texts: List[str]) -> np.ndarray:
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
    return EmbeddingFunc(
        embedding_dim=rag_config.embedding_dim,
        max_token_size=512,
        func=hf_embedding_func,
    )


def get_llm_model_func():
    return portkey_complete


def get_vision_model_func():
    return portkey_vision_complete
