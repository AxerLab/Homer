"""In-memory store for global presentation generation chat histories.

This module provides a minimal abstraction for persisting chat histories
produced during full presentation generation. The histories originate from
`pydantic-ai` agent runs (see https://ai.pydantic.dev/message-history/).

Unlike `iteration_memory`, this store maintains histories for entire presentation
generations rather than individual slide iterations. For now, the storage is
purely in-memory and therefore ephemeral. It is designed so that it can be
swapped with a persistent backend in the future without affecting callers.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from hashlib import sha1
from threading import Lock
from typing import Dict, List, Optional, Sequence

from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter


@dataclass(frozen=True)
class GlobalMemoryKey:
	"""Identifier for a single presentation generation session."""

	prompt_hash: str


@dataclass
class GlobalMemoryEntry:
	"""Stored metadata for a presentation generation attempt."""

	user_prompt: str
	messages: List[ModelMessage] = field(default_factory=list)

	def messages_json(self) -> bytes:
		"""Return the stored messages serialized to JSON bytes."""

		return ModelMessagesTypeAdapter.dump_json(self.messages)


class GlobalMemory:
	"""Thread-safe, non-persistent store for presentation generation chat histories."""

	def __init__(self) -> None:
		self._storage: Dict[GlobalMemoryKey, List[GlobalMemoryEntry]] = {}
		self._lock = Lock()

	@staticmethod
	def _build_key(prompt: str) -> GlobalMemoryKey:
		"""Create a deterministic key for identifying a presentation generation session."""

		prompt_hash = sha1(prompt.encode("utf-8")).hexdigest()
		return GlobalMemoryKey(prompt_hash=prompt_hash)

	def record_generation(
		self,
		*,
		user_prompt: str,
		messages: Optional[Sequence[ModelMessage]],
	) -> None:
		"""Append a chat history for a presentation generation.

		Args:
			user_prompt: The user's presentation generation prompt.
			messages: Message sequence as returned by ``AgentRunResult.new_messages``.
		"""

		validated_messages = (
			ModelMessagesTypeAdapter.validate_python(list(messages))
			if messages is not None
			else []
		)
		entry = GlobalMemoryEntry(user_prompt=user_prompt, messages=deepcopy(validated_messages))

		with self._lock:
			key = self._build_key(user_prompt)
			self._storage.setdefault(key, []).append(entry)

	def get_entries(self, *, user_prompt: str) -> List[GlobalMemoryEntry]:
		"""Retrieve stored entries for a presentation generation session."""

		key = self._build_key(user_prompt)
		with self._lock:
			return deepcopy(self._storage.get(key, []))

	def get_history(self, *, user_prompt: str) -> List[ModelMessage]:
		"""Return the flattened message history for a presentation generation session."""

		messages: List[ModelMessage] = []
		for entry in self.get_entries(user_prompt=user_prompt):
			messages.extend(deepcopy(entry.messages))
		return messages

	def get_latest(self, *, user_prompt: str) -> Optional[GlobalMemoryEntry]:
		"""Return the most recent chat history entry for a session, if any."""

		entries = self.get_entries(user_prompt=user_prompt)
		return entries[-1] if entries else None

	def clear(self, *, user_prompt: Optional[str] = None) -> None:
		"""Clear histories.

		If ``user_prompt`` is provided, only that specific session is cleared.
		Otherwise the entire store is reset.
		"""

		with self._lock:
			if user_prompt is None:
				self._storage.clear()
				return

			key = self._build_key(user_prompt)
			self._storage.pop(key, None)


global_memory = GlobalMemory()
"""Shared singleton instance for convenience."""
