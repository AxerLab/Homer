"""In-memory store for iterative LLM agent chat histories.

This module provides a minimal abstraction for persisting chat histories
produced during slide regeneration iterations. The histories originate from
`pydantic-ai` agent runs (see https://ai.pydantic.dev/message-history/).

For now, the storage is purely in-memory and therefore ephemeral. It is
designed so that it can be swapped with a persistent backend in the future
without affecting callers.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from hashlib import sha1
from threading import Lock
from typing import Dict, List, Optional, Sequence

from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter


@dataclass(frozen=True)
class IterationMemoryKey:
	"""Identifier for a single slide iteration session."""

	original_prompt_hash: str
	slide_index: int


@dataclass
class IterationMemoryEntry:
	"""Stored metadata for a regeneration attempt."""

	edit_prompt: str
	messages: List[ModelMessage] = field(default_factory=list)

	def messages_json(self) -> bytes:
		"""Return the stored messages serialized to JSON bytes."""

		return ModelMessagesTypeAdapter.dump_json(self.messages)


class IterationMemory:
	"""Thread-safe, non-persistent store for slide iteration chat histories."""

	def __init__(self) -> None:
		self._storage: Dict[IterationMemoryKey, List[IterationMemoryEntry]] = {}
		self._lock = Lock()

	@staticmethod
	def _build_key(original_prompt: str, slide_index: int) -> IterationMemoryKey:
		"""Create a deterministic key for identifying a slide iteration session."""

		prompt_hash = sha1(original_prompt.encode("utf-8")).hexdigest()
		return IterationMemoryKey(original_prompt_hash=prompt_hash, slide_index=slide_index)

	def record_iteration(
		self,
		*,
		original_prompt: str,
		slide_index: int,
		edit_prompt: str,
		messages: Optional[Sequence[ModelMessage]],
	) -> None:
		"""Append a chat history for a slide iteration.

		Args:
			original_prompt: The initial presentation generation prompt.
			slide_index: Index of the slide being regenerated.
			edit_prompt: User instructions for the regeneration.
			messages: Message sequence as returned by ``AgentRunResult.new_messages``.
		"""

		validated_messages = (
			ModelMessagesTypeAdapter.validate_python(list(messages))
			if messages is not None
			else []
		)
		entry = IterationMemoryEntry(edit_prompt=edit_prompt, messages=deepcopy(validated_messages))

		with self._lock:
			key = self._build_key(original_prompt, slide_index)
			self._storage.setdefault(key, []).append(entry)

	def get_entries(self, *, original_prompt: str, slide_index: int) -> List[IterationMemoryEntry]:
		"""Retrieve stored entries for a slide iteration session."""

		key = self._build_key(original_prompt, slide_index)
		with self._lock:
			return deepcopy(self._storage.get(key, []))

	def get_history(self, *, original_prompt: str, slide_index: int) -> List[ModelMessage]:
		"""Return the flattened message history for a slide iteration session."""

		messages: List[ModelMessage] = []
		for entry in self.get_entries(original_prompt=original_prompt, slide_index=slide_index):
			messages.extend(deepcopy(entry.messages))
		return messages

	def get_latest(
		self, *, original_prompt: str, slide_index: int
	) -> Optional[IterationMemoryEntry]:
		"""Return the most recent chat history entry for a session, if any."""

		entries = self.get_entries(original_prompt=original_prompt, slide_index=slide_index)
		return entries[-1] if entries else None

	def clear(self, *, original_prompt: Optional[str] = None, slide_index: Optional[int] = None) -> None:
		"""Clear histories.

		If both ``original_prompt`` and ``slide_index`` are provided, the specific
		session is cleared. Otherwise the entire store is reset.
		"""

		with self._lock:
			if original_prompt is None and slide_index is None:
				self._storage.clear()
				return

			if original_prompt is None or slide_index is None:
				raise ValueError("Both original_prompt and slide_index are required to clear a session.")

			key = self._build_key(original_prompt, slide_index)
			self._storage.pop(key, None)


iteration_memory = IterationMemory()
"""Shared singleton instance for convenience."""
