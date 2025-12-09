"""
Data Ingestion Module for Year-long Data Warehouse
Processes and loads data from various sources into the SQLite warehouse.
"""

import dask.dataframe as dd
import os
import sys
from datetime import datetime
from typing import Optional
from sqlalchemy import text
try:
    from .db_setup import YearlongDataWarehouse
except ImportError:
    # Allow running as standalone script
    from warehouse.db_setup import YearlongDataWarehouse
import logging

# Add parent directory to path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionManager:
    """
    Handles data ingestion from various sources into the data warehouse.

    Supports loading retail sales data and creating the necessary dimension
    and fact records for analytics and querying.
    """

    def __init__(self, warehouse: Optional[YearlongDataWarehouse] = None):
        """
        Initialize the data ingestion manager.

        Args:
            warehouse: Pre-existing warehouse connection, or None to auto-create
        """
        self.warehouse = warehouse or YearlongDataWarehouse()
        logger.info("DataIngestionManager initialized")

    def load_retail_data(self, data_path: Optional[str] = None) -> bool:
        """
        Load retail sales data from parquet/csv files into the warehouse.

        Args:
            data_path: Path to data file, or None to auto-detect

        Returns:
            True if successful, False otherwise
        """
        try:
            if data_path is None:
                # Auto-detect data file
                potential_paths = [
                    "data/rawdata/MCCS_RetailData.parquet",
                    "data/convertedcsv/MCCS_RetailData.csv",
                    "retail_data_sample.parquet"
                ]

                for path in potential_paths:
                    if os.path.exists(path):
                        data_path = path
                        break
                else:
                    logger.error("No retail data file found")
                    return False

            logger.info(f"Loading data from: {data_path}")

            # Load data using Dask for memory efficiency
            if data_path.endswith('.parquet'):
                df = dd.read_parquet(data_path)
            elif data_path.endswith('.csv'):
                df = dd.read_csv(data_path)
            else:
                logger.error(f"Unsupported file format: {data_path}")
                return False

            # Process data
            success = self._process_retail_data(df)
            if success:
                logger.info("Retail data loading completed successfully")
            return success

        except Exception as e:
            logger.error(f"Failed to load retail data: {e}")
            return False

    def _process_retail_data(self, df: dd.DataFrame) -> bool:
        """
        Process and load retail data into warehouse tables.

        Args:
            df: Dask dataframe with retail data

        Returns:
            True if successful
        """
        try:
            # Extract unique site information for dimensions
            site_info = df[['SITE_ID', 'SITE_NAME', 'COMMAND_NAME']].drop_duplicates()
            site_data = site_info.compute()  # Convert to pandas for processing

            # Create site dimensions
            dimension_ids = {}
            for _, row in site_data.iterrows():
                site_id = str(row['SITE_ID'])
                dimension_id = self.warehouse.get_dimension_id(
                    dimension_type='site',
                    dimension_code=site_id,
                    dimension_name=row['SITE_NAME'],
                    metadata={
                        'command_name': row['COMMAND_NAME'],
                        'store_format': 'MAIN STORE' if 'MAIN' in row['SITE_NAME'] else 'MARINE MART'
                    }
                )

                if dimension_id:
                    dimension_ids[site_id] = dimension_id
                    logger.info(f"Created dimension for site {site_id}")
                else:
                    logger.error(f"Failed to create dimension for site {site_id}")
                    return False

            # Process fact data by date periods
            processed_count = 0
            total_count = 0

            # Get unique dates for processing
            dates = df['SALE_DATE'].drop_duplicates().compute()

            for sale_date in dates:
                try:
                    # Filter data for this date
                    daily_data = df[df['SALE_DATE'] == sale_date].compute()

                    # Parse the date from string format (MM/DD/YY)
                    if isinstance(sale_date, str):
                        try:
                            parsed_date = datetime.strptime(sale_date, '%m/%d/%y')
                        except ValueError:
                            # Try YY/MM/DD format
                            try:
                                parsed_date = datetime.strptime(sale_date, '%y/%m/%d')
                            except ValueError:
                                logger.error(f"Unable to parse date format: {sale_date}")
                                continue
                    else:
                        parsed_date = sale_date

                    # Aggregate by site for the day
                    for site_id, site_data_group in daily_data.groupby('SITE_ID'):
                        total_sales = site_data_group['EXTENSION_AMOUNT'].sum()
                        total_quantity = site_data_group['QTY'].sum()
                        total_returns = site_data_group['RETURN_IND'].eq('Y').sum()

                        dim_ids = [dimension_ids[str(site_id)]]

                        # Insert total sales fact for this day
                        self.warehouse.insert_fact(
                            metric_id=1,  # Total Sales
                            dimension_ids=dim_ids,
                            period_type=1,  # Daily
                            period_start=parsed_date.strftime('%Y%m%d'),
                            period_end=parsed_date.strftime('%Y%m%d'),
                            period_key=parsed_date.strftime('%Y-%m-%d'),
                            value=float(total_sales),
                            count=int(total_quantity)
                        )

                        # Insert returns data
                        if total_returns > 0:
                            self.warehouse.insert_fact(
                                metric_id=3,  # Total Returns
                                dimension_ids=dim_ids,
                                period_type=1,  # Daily
                                period_start=parsed_date.strftime('%Y%m%d'),
                                period_end=parsed_date.strftime('%Y%m%d'),
                                period_key=parsed_date.strftime('%Y-%m-%d'),
                                value=float(total_returns),
                                count=int(total_returns)
                            )

                    processed_count += 1
                    total_count += len(daily_data)

                    if processed_count % 10 == 0:
                        logger.info(f"Processed {processed_count} dates, {total_count} transactions")

                except Exception as e:
                    logger.error(f"Failed to process date {sale_date}: {e}")
                    continue

            logger.info(f"Successfully processed {processed_count} dates with {total_count} transactions")
            return True

        except Exception as e:
            logger.error(f"Failed to process retail data: {e}")
            return False

    def create_date_dimensions(self) -> bool:
        """
        Create dimension records for date hierarchies.

        Returns:
            True if successful
        """
        try:
            # This could be expanded to create date dimension tables
            # For now, we rely on period-based facts
            logger.info("Date dimensions handled through period-based facts")
            return True
        except Exception as e:
            logger.error(f"Failed to create date dimensions: {e}")
            return False

    def validate_data_integrity(self) -> bool:
        """
        Perform basic data integrity checks on loaded data.

        Returns:
            True if data appears consistent
        """
        try:
            with self.warehouse.get_session() as session:
                # Check that we have some basic metrics and dimensions
                metric_count = session.execute(text("SELECT COUNT(*) FROM metrics")).scalar()
                dimension_count = session.execute(text("SELECT COUNT(*) FROM dimensions")).scalar()
                fact_count = session.execute(text("SELECT COUNT(*) FROM facts")).scalar()

                logger.info(f"Data integrity check: {metric_count} metrics, {dimension_count} dimensions, {fact_count} facts")

                # Basic validation
                if metric_count == 0:
                    logger.warning("No metrics found - data may not be properly loaded")
                    return False

                if dimension_count == 0:
                    logger.warning("No dimensions found - data may not be properly loaded")
                    return False

                if fact_count == 0:
                    logger.warning("No facts found - data may not be properly loaded")
                    return False

                return True

        except Exception as e:
            logger.error(f"Data integrity check failed: {e}")
            return False

    def close(self):
        """Close warehouse connections."""
        if self.warehouse:
            self.warehouse.close()


def main():
    """Main function to run data ingestion."""
    logger.info("Starting data ingestion process...")

    try:
        manager = DataIngestionManager()

        # Load retail data
        if manager.load_retail_data():
            logger.info("Data loading successful")

            # Validate integrity
            if manager.validate_data_integrity():
                logger.info("Data integrity validation passed")
                logger.info("Data ingestion completed successfully!")
                return True
            else:
                logger.error("Data integrity validation failed")
                return False
        else:
            logger.error("Data loading failed")
            return False

    except Exception as e:
        logger.error(f"Data ingestion failed with error: {e}")
        return False
    finally:
        try:
            manager.close()
        except:
            pass


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
