"""
Snowflake-Compatible Data Warehouse Package
Provides ORM-based access to live Snowflake data for fast querying and LLM integration.
"""

from .db_setup import HybridDataWarehouse, YearlongDataWarehouse, create_session
from .models import Base, Metric, Dimension, Fact, FactDimension
# Import query functions for easy access
from .query_wrapper import create_session as query_create_session, query_facts, convert_jargons

__version__ = "2.1.0"  # Updated with proper star schema design
__all__ = [
    'HybridDataWarehouse',
    'YearlongDataWarehouse',  # Backward compatibility alias
    'create_session',
    'query_create_session',
    'query_facts',
    'convert_jargons',
    'Base',
    'Metric',
    'Dimension',
    'Fact',
    'FactDimension'
]
