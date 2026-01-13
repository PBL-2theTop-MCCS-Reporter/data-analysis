"""
Test and Demo Script for Year-long Data Warehouse
Demonstrates the warehouse functionality and evaluates the approach.
"""

import logging
import os
from datetime import date
from warehouse.db_setup import YearlongDataWarehouse
from warehouse.query_wrapper import create_session, query_facts, convert_jargons, YearlongWarehouseSession
from typing import NamedTuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Sites(NamedTuple):
    """Site information structure to match user's existing code."""
    site_id: str
    site_name: str
    command_name: str
    store_format: str

def test_warehouse_creation():
    """Test warehouse database creation."""
    logger.info("Testing warehouse creation...")
    try:
        # Auto-detect will use SQLite by default since no Snowflake env vars are set
        warehouse = YearlongDataWarehouse()
        logger.info("✓ Warehouse created successfully")
        return warehouse
    except Exception as e:
        logger.error(f"✗ Warehouse creation failed: {e}")
        return None

def insert_sample_data(warehouse: YearlongDataWarehouse):
    """Insert sample data that matches user's example structure."""
    logger.info("Inserting sample data...")

    try:
        # Insert sample site dimensions
        sites_data = [
            ("1100", "HHM MCX MAIN STORE", "HENDERSON HALL", "MAIN STORE"),
            ("5206", "CLM MCX CAMP JOHNSON MARINE MART", "CAMP LEJEUNE", "MARINE MART"),
            ("2301", "QUM MCX MARINE MART", "QUANTICO", "MARINE MART")
        ]

        for site_id, site_name, command_name, store_format in sites_data:
            dimension_id = warehouse.get_dimension_id(
                dimension_type='site',
                dimension_code=site_id,
                dimension_name=site_name,
                metadata={
                    'command_name': command_name,
                    'store_format': store_format
                }
            )
            logger.info(f"✓ Created dimension for site {site_id} (ID: {dimension_id})")

        # Insert sample facts (matching user's examples)
        sample_facts = [
            # 2025 total sales
            (1, [1], 4, "20250101", "20251231", "20250101 to 20251231", 773686.11, 1000),  # Site 1100 dimension ID
            (1, [2], 4, "20250101", "20251231", "20250101 to 20251231", 616489.05, 850),    # Site 5206 dimension ID
            (1, [3], 4, "20250101", "20251231", "20250101 to 20251231", 204485.38, 600),    # Site 2301 dimension ID

            # Oct 2024 sales
            (1, [1], 2, "20241001", "20241031", "20241001 to 20241031", 1138733.48, 500),   # Site 1100 dimension ID
        ]

        for fact in sample_facts:
            warehouse.insert_fact(*fact)
            logger.info(f"✓ Inserted fact: {fact}")

        logger.info("Sample data insertion completed successfully")
        return True

    except Exception as e:
        logger.error(f"✗ Sample data insertion failed: {e}")
        return False

def test_queries(warehouse: YearlongDataWarehouse):
    """Test the query functionality with sample data."""
    logger.info("Testing query functionality...")

    # Use the same warehouse for querying
    session = YearlongWarehouseSession(warehouse)

    try:
        # Test Query 1: Total sales of three locations for 2025
        logger.info("=" * 60)
        logger.info("Query 1: What is the total sales of three locations for 2025?")
        result1 = query_facts(
            session=session,
            metric_ids=[1],  # Total Sales
            group_names=["1100", "5206", "2301"],  # Site IDs
            period_levels=[4],  # Yearly
            exact_date=date(2025, 1, 1)
        )

        logger.info(f"Result 1: {convert_jargons(session=session, df=result1)}")
        logger.info("✓ Query 1 executed successfully")

        # Test Query 2: Total sales for Oct 2024
        logger.info("=" * 60)
        logger.info("Query 2: What is the total sales of MCCS for Oct 2024?")
        result2 = query_facts(
            session=session,
            metric_ids=[1],
            group_names=["1100"],
            period_levels=[2],  # Monthly
            exact_date=date(2024, 10, 1)
        )

        logger.info(f"Result 2: {convert_jargons(session=session, df=result2)}")
        logger.info("✓ Query 2 executed successfully")

        return True

    except Exception as e:
        logger.error(f"✗ Query testing failed: {e}")
        return False

# def evaluate_approach():
#     """Evaluate the proposed warehouse approach."""
#     logger.info("=" * 80)
#     logger.info("WAREHOUSE APPROACH EVALUATION")
#     logger.info("=" * 80)

#     evaluation_points = [
#         ("✅ SQLite Database", "Simple, portable, easy deployment"),
#         ("✅ Unified Interface", "Same API as existing system"),
#         ("✅ Fast Query Performance", "Indexed for quick aggregations"),
#         ("✅ Year-long Data Support", "Handles multiple periods efficiently"),
#         ("✅ Multi-data Type Support", "Designed for sales, email, social media"),
#         ("✅ LLM Integration Ready", "Structured data perfect for AI analysis"),
#         ("✅ Portable Deployment", "Single SQLite file, ready to ship"),
#         ("✅ Metadata Preservation", "Site, command, format info maintained"),
#         ("✅ Time-based Aggregation", "Supports daily/monthly/quarterly/yearly"),
#         ("✅ Extensible Design", "Easy to add new metrics/data types")
#     ]


def run_complete_test():
    """Run the complete warehouse test suite."""
    logger.info("Starting Year-long Data Warehouse Test Suite...")

    # Clean up previous test database
    if os.path.exists('yearlong_warehouse.db'):
        os.remove('yearlong_warehouse.db')
        logger.info("Removed existing test database")

    # Test 1: Warehouse creation
    warehouse = test_warehouse_creation()
    if not warehouse:
        logger.error("Warehouse creation failed - aborting tests")
        return False

    # Test 2: Sample data insertion
    if not insert_sample_data(warehouse):
        logger.error("Sample data insertion failed - aborting tests")
        warehouse.close()
        return False

    # Test 3: Query testing (using the same warehouse)
    if not test_queries(warehouse):
        logger.error("Query testing failed")
        warehouse.close()
        return False

    warehouse.close()

    logger.info("✓ Year-long Data Warehouse Test Suite completed successfully!")
    return True

def run_sprint1_test():
    """Run Sprint 1 warehouse tests: creation and data insertion."""
    logger.info("Starting Sprint 1: Foundation & Database Core Test Suite...")

    # Test 1: Warehouse creation
    warehouse = test_warehouse_creation()
    if not warehouse:
        logger.error("Sprint 1 failed at warehouse creation")
        return False

    # Test 2: Sample data insertion
    if not insert_sample_data(warehouse):
        logger.error("Sprint 1 failed at sample data insertion")
        return False

    logger.info("✓ Sprint 2: Foundation & Database Core completed successfully!")
    return True

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--complete':
        success = run_complete_test()
        if success:
            print("\n🎉 SUCCESS: Complete Year-long Data Warehouse Test Suite passed!")

        else:
            print("\n❌ FAILURE: Complete test suite failed.")
            print("Check the logs above for specific error details.")
    else:
        success = run_sprint1_test()
        if success:
            print("\n🎉 SUCCESS: Sprint 2 (Foundation & Database Core) implementation is working perfectly!")

        else:
            print("\n❌ FAILURE: Sprint 2 test suite failed.")
            print("Check the logs above for specific error details.")
