"""
AI Query Routing System

Routes queries to appropriate specialist models or general knowledge systems.
"""

from .query_router import QueryRouter, Domain

__all__ = ['QueryRouter', 'Domain']
