"""Hybrid semantic search over the `tool_search` Qdrant index.

Ported from search-eval (`src/search_eval/retrieval/`), where the method was designed
and evaluated (MRR@10 0.628 vs 0.264 for the keyword `/search`). Keep the two in sync:
a change to the fusion or a retriever should be evaluated there first.
"""
