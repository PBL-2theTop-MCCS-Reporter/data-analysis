"""
Hybrid ORM Data Warehouse
Supports both SQLite (development) and Snowflake (production) using SQLAlchemy ORM.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from .models import Base, Metric, Dimension, Fact, FactDimension

logger = logging.getLogger(__name__)

class HybridDataWarehouse:
    """
    ORM-based data warehouse supporting both SQLite and Snowflake.

    Automatically detects database type based on connection string or environment variables:
    - SQLite: For development/testing (uses local .db files)
    - Snowflake: For production (queries live enterprise data)
    """

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize warehouse connection for SQLite or Snowflake.

        Args:
            connection_string: Database connection string. If None, auto-detects based on environment.
                              SQLite: Path ending in '.db' or 'sqlite:///'
                              Snowflake: 'snowflake://' URL or uses SNOWFLAKE_* env vars
        """
        self.db_type = "sqlite"  # Default to SQLite for development

        if connection_string is None:
            # Auto-detect based on environment variables
            snowflake_account = os.getenv('SNOWFLAKE_ACCOUNT')
            snowflake_user = os.getenv('SNOWFLAKE_USER')
            snowflake_password = os.getenv('SNOWFLAKE_PASSWORD')

            if all([snowflake_account, snowflake_user, snowflake_password]):
                # Snowflake credentials found - use Snowflake
                self.db_type = "snowflake"
                warehouse_env = os.getenv('SNOWFLAKE_WAREHOUSE', 'default_warehouse')
                database = os.getenv('SNOWFLAKE_DATABASE', 'default_database')
                schema = os.getenv('SNOWFLAKE_SCHEMA', 'default_schema')
                connection_string = f"snowflake://{snowflake_user}:{snowflake_password}@{snowflake_account}/{database}/{schema}?warehouse={warehouse_env}"
            else:
                # No Snowflake credentials - use SQLite
                self.db_type = "sqlite"
                connection_string = "sqlite:///yearlong_warehouse.db"

        elif connection_string.startswith('snowflake://'):
            self.db_type = "snowflake"
        elif connection_string.endswith('.db'):
            # Convert bare .db path to proper SQLAlchemy URL with absolute path
            self.db_type = "sqlite"
            abs_path = os.path.abspath(connection_string)
            connection_string = f"sqlite:///{abs_path}"
        elif 'sqlite://' in connection_string:
            self.db_type = "sqlite"

        try:
            logger.info(f"Initializing {self.db_type.upper()} data warehouse...")
            self.engine = create_engine(connection_string, echo=False)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            # Test connection
            if self.db_type == "snowflake":
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                # SQLite connection is automatically tested by engine creation

            # Create tables if they don't exist
            if not self._tables_exist():
                logger.info(f"Creating tables in {self.db_type.upper()}...")
                Base.metadata.create_all(bind=self.engine)

                # Initialize default metrics if database is empty
                self._initialize_default_metrics()

            logger.info(f"Connected to {self.db_type.upper()} data warehouse")

        except Exception as e:
            # Clean up any partially initialized state
            self.engine = None
            self.SessionLocal = None
            raise ValueError(f"Failed to connect to {self.db_type.upper()}: {e}")

    def _tables_exist(self) -> bool:
        """Check if required tables exist in the database."""
        if self.engine is None:
            return False
        try:
            # Get table names using database-specific methods
            if self.db_type == "snowflake":
                with self.engine.connect() as conn:
                    result = conn.execute(text("SHOW TABLES"))
                    existing_tables = {row[1] for row in result}  # table names are in second column
            else:  # SQLite
                with self.engine.connect() as conn:
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                    existing_tables = {row[0] for row in result}  # table names are in first column

            required_tables = {'metrics', 'dimensions', 'facts', 'fact_dimensions'}
            return required_tables.issubset(existing_tables)
        except Exception:
            return False

    def _initialize_default_metrics(self):
        """Initialize default metrics in the database during setup."""
        with self.get_session() as session:
            try:
                # Check if metrics already exist
                existing_count = session.query(Metric).count()
                if existing_count > 0:
                    return

                # Initialize default metrics
                default_metrics = [
                    (1, "Total Sales", "Total sales revenue in dollars", "numeric"),
                    (2, "Total Quantity", "Total quantity sold", "numeric"),
                    (3, "Total Returns", "Total return transactions", "numeric"),
                    (4, "Return Rate", "Percentage of returns", "percentage"),
                    (5, "Net Sales", "Sales after returns", "numeric"),
                    (6, "Email Opens", "Number of email opens", "numeric"),
                    (7, "Email Clicks", "Number of email clicks", "numeric"),
                    (8, "Social Media Engagement", "Social media engagement metrics", "numeric"),
                    (9, "Social Media Followers", "Total social media followers", "numeric")
                ]

                for metric_id, name, desc, data_type in default_metrics:
                    metric = Metric(
                        metric_id=metric_id,
                        metric_name=name,
                        metric_desc=desc,
                        data_type=data_type
                    )
                    session.add(metric)

                session.commit()
                logger.info("Initialized default metrics in database")

            except Exception as e:
                session.rollback()
                logger.error(f"Failed to initialize default metrics: {e}")

    def get_session(self) -> Session:
        """Get a new database session."""
        if self.SessionLocal is None:
            raise RuntimeError("Database connection not established. Unable to create session.")
        return self.SessionLocal()

    def get_dimension_id(self, dimension_type: str, dimension_code: str,
                        dimension_name: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """
        Get dimension ID by type and code. Creates dimension if it doesn't exist.

        Note: In production with live Snowflake data, dimensions should already exist.
        This method is primarily for development/testing.
        """
        with self.get_session() as session:
            # Try to find existing dimension
            dimension = session.query(Dimension).filter(
                Dimension.dimension_type == dimension_type,
                Dimension.dimension_code == dimension_code
            ).first()

            if dimension:
                return dimension.id  # type: ignore[attr-defined]

            # Create new dimension (development/testing only)
            metadata_str = json.dumps(metadata) if metadata else None
            new_dimension = Dimension(
                dimension_type=dimension_type,
                dimension_code=dimension_code,
                dimension_name=dimension_name,
                dimension_metadata=metadata_str
            )

            try:
                session.add(new_dimension)
                session.commit()
                session.refresh(new_dimension)
                logger.info(f"Created new dimension: {dimension_code}")
                return new_dimension.id  # type: ignore[attr-defined]
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to create dimension: {e}")
                return None

    def insert_fact(self, metric_id: int, dimension_ids: List[int], period_type: int,
                   period_start: str, period_end: str, period_key: str, value: float, count: int) -> bool:
        """
        Insert a fact record with proper many-to-many relationships.

        Note: In production, facts are typically loaded via ETL pipelines.
        This method is primarily for development/testing.
        """
        with self.get_session() as session:
            try:
                # Create the fact record
                fact = Fact(
                    metric_id=metric_id,
                    period_type=period_type,
                    period_start=period_start,
                    period_end=period_end,
                    period_key=period_key,
                    value=value,
                    count=count
                )

                session.add(fact)
                session.flush()  # Get the fact ID without committing

                # Create many-to-many relationships
                for dimension_id in dimension_ids:
                    fact_dimension = FactDimension(
                        fact_id=fact.id,
                        dimension_id=dimension_id
                    )
                    session.add(fact_dimension)

                session.commit()
                logger.debug(f"Inserted fact: metric_id={metric_id}, value={value}, dimensions={dimension_ids}")
                return True

            except Exception as e:
                session.rollback()
                logger.error(f"Failed to insert fact: {e}")
                return False

    def query_facts(self, session: Session, metric_ids: List[int], group_names: List[str],
                   period_levels: List[int], exact_date: str) -> Dict[str, Any]:
        """
        Query facts table for aggregated data using proper star schema relationships.

        This method queries live data using SQLAlchemy ORM relationships.
        """
        try:
            # Build query using proper ORM relationships
            query = session.query(
                Fact,
                Metric,
                Dimension
            ).join(Metric, Fact.metric_id == Metric.metric_id)\
             .join(FactDimension, Fact.id == FactDimension.fact_id)\
             .join(Dimension, FactDimension.dimension_id == Dimension.id)

            # Apply filters
            query = query.filter(
                Fact.metric_id.in_(metric_ids),
                Fact.period_type.in_(period_levels),
                Fact.period_start <= exact_date,
                Fact.period_end >= exact_date
            )

            # Filter by dimension codes if specified
            if group_names:
                query = query.filter(
                    Dimension.dimension_code.in_(group_names),
                    Dimension.dimension_type == 'site'
                )

            results = query.all()

            # Format results to match existing API structure
            formatted_results = {}
            for fact, metric, dimension in results:
                # Parse dimension metadata
                dimension_details = {
                    'site_id': dimension.dimension_code,
                    'site_name': dimension.dimension_name,
                }
                if dimension.dimension_metadata:
                    try:
                        dimension_details.update(json.loads(dimension.dimension_metadata))
                    except:
                        pass

                # Group by metric for the expected format
                metric_key = str(fact.metric_id)
                if metric_key not in formatted_results:
                    formatted_results[metric_key] = []

                # Check if we already have this fact to avoid duplicates
                existing_fact = next(
                    (f for f in formatted_results[metric_key]
                     if f['period_key'] == fact.period_key and f['site_id'] == dimension_details['site_id']),
                    None
                )

                if existing_fact:
                    # Update existing fact with additional dimension info if needed
                    continue
                else:
                    # Add new formatted result
                    formatted_results[metric_key].append({
                        'metric_id': fact.metric_id,
                        'metric_name': metric.metric_name,
                        'metric_description': metric.metric_desc or '',
                        'site_id': dimension_details.get('site_id', ''),
                        'site_name': dimension_details.get('site_name', ''),
                        'command_name': dimension_details.get('command_name', ''),
                        'store_format': dimension_details.get('store_format', ''),
                        'period_key': fact.period_key,
                        'value': fact.value,
                        'count': fact.count
                    })

            return {'result': formatted_results}

        except Exception as e:
            logger.error(f"Query failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {'result': {}}

    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Snowflake connections closed")

    def __del__(self):
        """Ensure connections are closed."""
        self.close()


# Backward compatibility: aliases for existing code
SnowflakeDataWarehouse = HybridDataWarehouse  # For Snowflake-specific usage
YearlongDataWarehouse = HybridDataWarehouse   # For existing code


def create_session(connection_string: Optional[str] = None) -> Session:
    """
    Create a database session for the warehouse.

    Args:
        connection_string: Optional connection string. If None, auto-detects database type.

    Returns:
        SQLAlchemy session for database operations
    """
    warehouse = HybridDataWarehouse(connection_string)
    return warehouse.get_session()


if __name__ == '__main__':
    # Test the connection (auto-detects database type)
    try:
        warehouse = HybridDataWarehouse()
        print(f"✅ {warehouse.db_type.upper()} data warehouse connection successful!")
        warehouse.close()
    except Exception as e:
        print(f"❌ Failed to connect to data warehouse: {e}")
        if "SNOWFLAKE" in str(e):
            print("For Snowflake access, set SNOWFLAKE_* environment variables")
        else:
            print("For SQLite access, ensure the database file is accessible")
