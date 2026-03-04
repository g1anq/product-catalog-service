"""
GraphQL package.

This package contains all GraphQL-related code including types,
queries, mutations, and schema definition.
"""

from app.graphql.schema import schema
from app.graphql.router import graphql_router

__all__ = ["schema", "graphql_router"]
