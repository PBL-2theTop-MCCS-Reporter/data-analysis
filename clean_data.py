#!/usr/bin/env python3
# clean_data.py
# Requirements: pip install polars pyarrow
# Compatible with a wide range of Polars versions.

import argparse
from datetime import datetime
from typing import List, Optional
import polars as pl

# ---------------- Defaults ----------------

DEFAULT_DT_FORMATS = [
    "%m/%d/%Y %H:%M",        # 11/30/2024 19:50
    "%m/%d/%Y %H:%M:%S",     # 11/30/2024 19:50:30
    "%Y-%m-%d %H:%M",        # 2024-11-30 19:50
    "%Y-%m-%d %H:%M:%S",     # 2024-11-30 19:50:30
    "%Y-%m-%dT%H:%M:%S",     # ISO no fractional seconds
    "%Y-%m-%dT%H:%M:%S%.f",  # ISO with millis
    # Add AM/PM variant if needed:
    # "%m/%d/%Y %I:%M %p",
]

DEFAULT_DATE_FORMATS = [
    "%m/%d/%Y",              # 11/30/2024
    "%Y-%m-%d",              # 2024-11-30
]

# ---------------- Helpers ----------------

def to_snake(s: str) -> str:
    return (
        s.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
        .replace(".", "_")
    )

def standardize_names(lf: pl.LazyFrame) -> pl.LazyFrame:
    mapping = {}
    seen = set()
    for c in lf.columns:
        base = to_snake(c)
        name = base
        i = 1
        while name in seen:
            i += 1
            name = f"{base}_{i}"
        mapping[c] = name
        seen.add(name)
    return lf.rename(mapping)

def blanks_to_null_and_trim(lf: pl.LazyFrame) -> pl.LazyFrame:
    str_cols = [c for c, dt in zip(lf.columns, lf.dtypes) if dt == pl.Utf8]
    if not str_cols:
        return lf
    # Trim
    lf = lf.with_columns([pl.col(c).cast(pl.Utf8, strict=False).str.strip_chars().alias(c) for c in str_cols])
    # Empty -> null
    lf = lf.with_columns([
        pl.when((pl.col(c) == "") | (pl.col(c).str.len_chars() == 0))
        .then(pl.lit(None, dtype=pl.Utf8))
        .otherwise(pl.col(c))
        .alias(c)
        for c in str_cols
    ])
    return lf

def parse_strptime_multi(col: str, fmts: List[str], dtype):
    """
    Try parsing a string column with several formats; take the first that succeeds.
    Unparseable values become null (strict=False), then coalesce.
    """
    exprs = [
        (pl.col(col).cast(pl.Utf8, strict=False)
         .str.strip_chars()
         .str.strptime(dtype, format=f, strict=False, exact=True))
        for f in fmts
    ]
    return pl.coalesce(exprs).alias(col)

def parse_and_normalize(
    lf: pl.LazyFrame,
    dt_formats: List[str],
    date_formats: List[str],
) -> pl.LazyFrame:
    cols = set(lf.columns)

    # --- Date/time ---
    if "sale_date_time" in cols:
        lf = lf.with_columns(parse_strptime_multi("sale_date_time", dt_formats, pl.Datetime))

    if "sale_date" in cols:
        lf = lf.with_columns(parse_strptime_multi("sale_date", date_formats, pl.Date))

    # --- Numeric coercions ---
    for c, dtype in [
        ("site_id", pl.Int32),
        ("slip_no", pl.Int32),
        ("line", pl.Int32),
        ("qty", pl.Int32),
        ("extension_amount", pl.Float64),
    ]:
        if c in cols:
            lf = lf.with_columns(pl.col(c).cast(dtype, strict=False).alias(c))

    if "item_id" in cols:
        lf = lf.with_columns(pl.col("item_id").cast(pl.Int64, strict=False).alias("item_id"))

    # --- Canonicalize text (UPPERCASE for stable categories) ---
    for c in ["store_format", "command_name", "return_ind", "price_status", "site_name", "item_desc"]:
        if c in cols:
            lf = lf.with_columns(
                pl.when(pl.col(c).is_not_null())
                .then(pl.col(c).cast(pl.Utf8, strict=False).str.strip_chars().str.to_uppercase())
                .otherwise(pl.lit(None, dtype=pl.Utf8))
                .alias(c)
            )

    return lf

def impute_numerics(lf: pl.LazyFrame, strategy: Optional[str], candidates: List[str]) -> pl.LazyFrame:
    cols = [c for c in candidates if c in lf.columns]
    if not strategy or not cols:
        return lf

    if strategy == "zero":
        return lf.with_columns([pl.col(c).fill_null(0).alias(c) for c in cols])

    if strategy in {"mean", "median"}:
        aggs = [
            (pl.col(c).mean() if strategy == "mean" else pl.col(c).median()).alias(c)
            for c in cols
        ]
        s = lf.select(aggs).collect()
        fills = {c: s[c][0] for c in cols}
        return lf.with_columns([pl.col(c).fill_null(fills[c]).alias(c) for c in cols])

    return lf

def drop_required_nulls(lf: pl.LazyFrame, required: List[str]) -> pl.LazyFrame:
    for c in required:
        if c in lf.columns:
            lf = lf.filter(pl.col(c).is_not_null())
    return lf

def dedupe(lf: pl.LazyFrame, keys: List[str]) -> pl.LazyFrame:
    keys = [k for k in keys if k in lf.columns]
    return lf.unique(subset=keys, keep="first", maintain_order=True) if keys else lf.unique(keep="first", maintain_order=True)

# ---------------- Main ----------------

def main():
    ap = argparse.ArgumentParser(description="Clean a large Parquet dataset (missing values, duplicates, formats).")
    ap.add_argument("--input", required=True, help="Parquet file or glob (local path or cloud URI).")
    ap.add_argument("--output", required=True, help="Output Parquet file or directory.")
    ap.add_argument("--compression", default="zstd",
                    choices=["zstd", "snappy", "gzip", "lz4", "uncompressed"])
    ap.add_argument("--rechunk", action="store_true", help="Collect and rechunk before writing (uses more RAM).")

    # Handling knobs
    ap.add_argument("--impute-numerics", choices=["zero", "mean", "median"], default="median",
                    help="Impute numeric nulls after type casting.")
    ap.add_argument("--required",
        nargs="*", default=["sale_date_time","site_id","slip_no","line","extension_amount","qty"],
        help="Rows missing any of these are dropped (after imputation).")
    ap.add_argument("--dedupe-by",
        nargs="*", default=["sale_date_time","site_id","slip_no","line","item_id","qty","extension_amount"],
        help="Columns that define duplicate rows.")

    # Date window
    ap.add_argument("--min-date", default=None, help="Drop rows with sale_date_time before this (YYYY-MM-DD).")
    ap.add_argument("--max-date", default=None, help="Drop rows with sale_date_time after this (YYYY-MM-DD).")

    # Soft sanity constraints
    ap.add_argument("--nonnegative-qty", action="store_true", help="Make QTY nonnegative (abs).")
    ap.add_argument("--nonnegative-amount", action="store_true", help="Make EXTENSION_AMOUNT nonnegative (abs).")

    # Format overrides
    ap.add_argument("--dt-format", action="append", default=[],
                    help="Extra datetime format(s) to try (can repeat).")
    ap.add_argument("--date-format", action="append", default=[],
                    help="Extra date format(s) to try (can repeat).")

    args = ap.parse_args()

    # Build final format lists (user-provided take precedence)
    dt_formats = list(dict.fromkeys(args.dt_format + DEFAULT_DT_FORMATS))
    date_formats = list(dict.fromkeys(args.date_format + DEFAULT_DATE_FORMATS))

    # 1) Lazy scan (version-safe args)
    lf = pl.scan_parquet(
        args.input,
        low_memory=True,
        use_statistics=True,
        hive_partitioning=True,
    )

    # 2) Column names → snake_case
    lf = standardize_names(lf)

    # 3) Clean strings and blank→null
    lf = blanks_to_null_and_trim(lf)

    # 4) Parse & normalize columns
    lf = parse_and_normalize(lf, dt_formats=dt_formats, date_formats=date_formats)

    # 5) Date window filters (use Python datetime for compatibility)
    if args.min_date and "sale_date_time" in lf.columns:
        dt_min = datetime.fromisoformat(args.min_date)
        lf = lf.filter(pl.col("sale_date_time").is_null() | (pl.col("sale_date_time") >= pl.lit(dt_min)))

    if args.max_date and "sale_date_time" in lf.columns:
        dt_max = datetime.fromisoformat(args.max_date)
        lf = lf.filter(pl.col("sale_date_time").is_null() | (pl.col("sale_date_time") <= pl.lit(dt_max)))

    # 6) Impute numeric nulls
    numeric_candidates = [
        c for c, dt in zip(lf.columns, lf.dtypes)
        if dt in (pl.Int8, pl.Int16, pl.Int32, pl.Int64,
                  pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                  pl.Float32, pl.Float64)
    ]
    lf = impute_numerics(lf, args.impute_numerics, numeric_candidates)

    # 7) Drop rows missing required fields
    lf = drop_required_nulls(lf, args.required)

    # 8) Soft sanity constraints
    if args.nonnegative_qty and "qty" in lf.columns:
        lf = lf.with_columns(
            pl.when(pl.col("qty") < 0).then(-pl.col("qty")).otherwise(pl.col("qty")).alias("qty")
        )
    if args.nonnegative_amount and "extension_amount" in lf.columns:
        lf = lf.with_columns(
            pl.when(pl.col("extension_amount") < 0)
            .then(-pl.col("extension_amount"))
            .otherwise(pl.col("extension_amount"))
            .alias("extension_amount")
        )

    # 9) Dedupe
    lf = dedupe(lf, args.dedupe_by)

    # 10) Execute & write
    if args.rechunk:
        print("⚙️  Rechunking: collecting to DataFrame (uses RAM) ...")
        df = lf.collect().rechunk()
        # Polars versions differ on write_parquet kwargs; try with statistics then fallback
        try:
            df.write_parquet(args.output, compression=args.compression, statistics=True)
        except TypeError:
            df.write_parquet(args.output, compression=args.compression)
    else:
        # Keep it lazy; write directly if available, else collect->write
        try:
            lf.sink_parquet(args.output, compression=args.compression, maintain_order=True, statistics=True)
        except AttributeError:
            # Older Polars may not have sink_parquet; fallback
            df = lf.collect()
            try:
                df.write_parquet(args.output, compression=args.compression, statistics=True)
            except TypeError:
                df.write_parquet(args.output, compression=args.compression)

    print("✅ Cleaning complete:", args.output)


if __name__ == "__main__":
    main()
