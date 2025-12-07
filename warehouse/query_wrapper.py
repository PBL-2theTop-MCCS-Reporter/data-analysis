"""
Query Wrapper for Year-long Data Warehouse
Provides the same API interface as the user's existing warehouse system.
"""

from typing import List, Dict, Any, cast
from datetime import date
from .db_setup import YearlongDataWarehouse
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YearlongWarehouseSession:
    """Session wrapper to match existing query interface."""

    def __init__(self, db_path = None):
        if hasattr(db_path, 'get_session'):  # If it's a warehouse object
            self.warehouse: YearlongDataWarehouse = cast(YearlongDataWarehouse, db_path)
        elif db_path is None:
            # Use auto-detection
            self.warehouse = YearlongDataWarehouse()
        elif hasattr(db_path, 'startswith') and db_path.startswith('sqlite://'):
            self.warehouse = YearlongDataWarehouse(db_path)
        else:
            # For direct file paths, convert to proper SQLite URL
            import os
            db_path = os.path.abspath(db_path)  # Get absolute path
            self.warehouse = YearlongDataWarehouse(f"sqlite:///{db_path}")
        logger.info("Year-long warehouse session initialized")

    def query_facts(self, metric_ids: List[int], group_names: List[str],
                   period_levels: List[int], exact_date: date) -> Dict[str, Any]:
        """Query interface matching the user's existing system."""

        exact_date_str = exact_date.strftime('%Y%m%d')

        # Query the warehouse using session
        session = self.warehouse.get_session()
        df = self.warehouse.query_facts(
            session=session,
            metric_ids=metric_ids,
            group_names=group_names,
            period_levels=period_levels,
            exact_date=exact_date_str
        )

        # Format results to match existing structure
        result = {}

        if not df['result']:
            logger.warning("No data found for the given query parameters")
            return {'result': {}}

        # Process the results dictionary
        for metric_id_str, facts in df['result'].items():
            metric_id = int(metric_id_str)
            result[metric_id] = {
                'metadata': {
                    'metric_name': 'Total Sales',
                    'metric_desc': 'Total sales revenue'
                }
            }

            for fact in facts:
                site_id = fact.get('site_id', '')
                site_name = fact.get('site_name', '')
                command_name = fact.get('command_name', '')
                store_format = fact.get('store_format', '')
                period_key = fact.get('period_key', '')
                value = fact.get('value', 0)

                site_metadata = {}
                if command_name:
                    site_metadata['command_name'] = command_name
                if store_format:
                    site_metadata['store_format'] = store_format

                if site_id and site_id not in result[metric_id]:
                    result[metric_id][site_id] = {
                        'metadata': site_metadata,
                        'site_name': site_name,
                        period_key: value
                    }
                elif site_id:
                    result[metric_id][site_id][period_key] = value

        # Return in the expected format
        return {'result': result}

    def to_dataframe(self, query_result: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert query result dictionary to pandas DataFrame.

        Args:
            query_result: Result from query_facts method

        Returns:
            pandas DataFrame with flattened data
        """
        if not query_result.get('result'):
            logger.warning("No data in query result to convert to DataFrame")
            return pd.DataFrame()

        rows = []

        # Flatten the nested dictionary structure
        for metric_id, metric_data in query_result['result'].items():
            metric_metadata = metric_data.get('metadata', {})
            metric_name = metric_metadata.get('metric_name', f'Metric {metric_id}')
            metric_desc = metric_metadata.get('metric_desc', '')

            # Process each site within this metric
            for site_key, site_data in metric_data.items():
                if site_key == 'metadata':
                    continue  # Skip metric-level metadata

                site_id = site_key
                site_name = site_data.get('site_name', '')
                site_metadata = site_data.get('metadata', {})
                command_name = site_metadata.get('command_name', '')
                store_format = site_metadata.get('store_format', '')

                # Process each period within this site
                for period_key, value in site_data.items():
                    if period_key in ['site_name', 'metadata']:
                        continue  # Skip non-period data

                    # Create a row for this data point
                    row = {
                        'metric_id': int(metric_id),
                        'metric_name': metric_name,
                        'metric_description': metric_desc,
                        'site_id': site_id,
                        'site_name': site_name,
                        'command_name': command_name,
                        'store_format': store_format,
                        'period_key': period_key,
                        'value': float(value) if value is not None else 0.0,
                        'count': 1  # Default count, can be enhanced later
                    }
                    rows.append(row)

        # Create DataFrame from rows
        df = pd.DataFrame(rows)

        # Ensure proper data types
        df['metric_id'] = df['metric_id'].astype(int)
        df['value'] = df['value'].astype(float)

        logger.info(f"Converted query result to DataFrame with {len(df)} rows and {len(df.columns)} columns")
        return df

    def query_facts_as_dataframe(self, metric_ids: List[int], group_names: List[str],
                               period_levels: List[int], exact_date: date) -> pd.DataFrame:
        """
        Query facts and return results directly as pandas DataFrame.

        Args:
            metric_ids: List of metric IDs to query
            group_names: List of site IDs to filter by
            period_levels: List of period levels (1=daily, 2=monthly, 4=yearly)
            exact_date: Date to query for

        Returns:
            pandas DataFrame with query results
        """
        query_result = self.query_facts(metric_ids, group_names, period_levels, exact_date)
        return self.to_dataframe(query_result)

# Wrapper functions to match the user's existing interface
def convert_jargons(session: YearlongWarehouseSession, df: Dict[str, Any]) -> Dict[str, Any]:
    """Convert and format results (wrapper for compatibility)."""
    # This is a pass-through for now, but you can add formatting logic here
    return df

def query_facts(session: YearlongWarehouseSession, metric_ids: List[int],
               group_names: List[str], period_levels: List[int],
               exact_date: date) -> Dict[str, Any]:
    """Main query function to match existing interface."""
    return session.query_facts(
        metric_ids=metric_ids,
        group_names=group_names,
        period_levels=period_levels,
        exact_date=exact_date
    )

# Factory function for creating sessions
def create_session(db_path: str = 'yearlong_warehouse.db') -> YearlongWarehouseSession:
    """Create a new warehouse session."""
    return YearlongWarehouseSession(db_path)

# Sample usage examples
def demo_yearlong_warehouse():
    """Demo function showing how to use the yearlong warehouse."""

    # Create session
    session = create_session('yearlong_warehouse.db')

    # Example 1: What is the total sales of three locations for 2025
    print("=" * 60)
    print("Query: What is the total sales of three locations for 2025")
    result = query_facts(
        session=session,
        metric_ids=[1],  # Total Sales
        group_names=["1100", "5206", "2301"],  # Site IDs
        period_levels=[4],  # Yearly
        exact_date=date(2025, 1, 1)
    )

    logger.info(convert_jargons(session=session, df=result))

    # Example 2: What is the total sales of MCCS for Oct 2024
    print("=" * 60)
    print("Query: What is the total sales of MCCS for Oct 2024")
    result = query_facts(
        session=session,
        metric_ids=[1],
        group_names=["1100"],
        period_levels=[2],  # Monthly
        exact_date=date(2024, 10, 1)
    )

    logger.info(convert_jargons(session=session, df=result))

if __name__ == '__main__':
    demo_yearlong_warehouse()
