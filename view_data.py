import polars as pl
import pandas as pd

# Load lazily (does not read full data yet)
file_path = "RetailData(Oct-Nov-24).parquet"

# show all columns and rows
pl.Config.set_tbl_cols(-1)   # -1 means no column truncation
pl.Config.set_tbl_rows(10)   # -1 means no row truncation (be careful on large datasets)
pl.Config.set_tbl_width_chars(0)  # allow full width output (no wrapping)
pl.Config.set_tbl_width_chars(200)   # widen table to 200 characters (adjust as you like)
pl.Config.set_tbl_hide_dataframe_shape(False)  # show shape info cleanly


# Load lazily — does NOT read all data immediately
df = pl.read_parquet(file_path)

# # Collect all data into memory (⚠️ use only if feasible)
# full_df = df.collect()

# # --- View the data ---
# print(full_df)
# print("Shape:", full_df.shape)
# print(full_df.describe())

# View first few rows safely (without collecting everything)
print(df)