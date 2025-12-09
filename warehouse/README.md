# Database/Warehouse Module

This module provides a hybrid ORM-based data warehouse supporting SQLite and Snowflake backends.

## Quick Start for New Developers

### Basic Testing (Works Out-of-Box):
```bash
cd /your/project/root
pip install -r new_requirements.txt
PYTHONPATH=. python warehouse/test_warehouse.py --complete
```

This will:
- Create a SQLite database (yearlong_warehouse.db)
- Load sample retail data
- Run query tests
- Demonstrate warehouse functionality

### Data Ingestion:
```bash
# Load your own data (requires data files)
PYTHONPATH=. python -m warehouse.data_ingestion

# Or specify custom paths:
manager = DataIngestionManager()
manager.load_retail_data("/path/to/your/data.parquet")
```

### Unit Tests:
```bash
PYTHONPATH=. python -m pytest tests/unit/ -v
```

## Database Backend Support

- SQLite (Default): Local development/testing
- Snowflake: Production data warehouse

## Import Notes

Modules use relative imports. Run with PYTHONPATH=. when calling modules directly:

```bash
# Works
PYTHONPATH=. python warehouse/db_setup.py

# Fails with import errors  
python warehouse/db_setup.py
```

## Project Structure
```
warehouse/
├── __init__.py          # Package exports
├── db_setup.py          # Database connection & hybrid logic
├── models.py            # SQLAlchemy ORM models (facts/dimensions)
├── query_wrapper.py     # Query API wrapper
├── data_ingestion.py    # ETL pipeline
├── test_warehouse.py    # Integration tests
└── README.md           # This file
```

## Troubleshooting

- Import errors: Use PYTHONPATH=.
- Missing data: Code auto-falls back to retail_data_sample.parquet
- Large data files: Excluded from repo (.gitignore) - provide your own
- Database backends: Default is SQLite; set SNOWFLAKE_* env vars for Snowflake

## Data Schema

The warehouse uses a classical star schema:

- Metrics: Sales, Quantity, Returns, etc.
- Dimensions: Sites, Commands, Products (hierarchical attributes)
- Facts: Actual measurements with foreign key relationships
