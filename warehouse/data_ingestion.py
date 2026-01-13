"""
Data Ingestion Module for Year-long Data Warehouse
Processes and loads data from various sources into the SQLite warehouse.
"""

import pandas as pd
import dask.dataframe as dd
import os
import json
import sys
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from .db_setup import YearlongDataWarehouse
import logging

# Add parent directory to path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionManager:
