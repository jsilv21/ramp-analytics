from __future__ import annotations

import argparse
from pathlib import Path

import duckdb


def ingest_csvs(raw_dir: Path, db_path: Path, schema: str) -> None:
    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw data directory not found: {raw_dir}")

    csv_paths = sorted(raw_dir.glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found in: {raw_dir}")

    db_path.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(db_path)) as conn:
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

        for csv_path in csv_paths:
            table_name = csv_path.stem
            conn.execute(
                f"""
                CREATE OR REPLACE TABLE {schema}.{table_name} AS
                SELECT * FROM read_csv_auto('{csv_path.as_posix()}', header=true)
                """
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Load raw CSVs into DuckDB.")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--db-path", type=Path, default=Path("warehouse/ramp.duckdb"))
    parser.add_argument("--schema", type=str, default="raw")
    args = parser.parse_args()

    ingest_csvs(raw_dir=args.raw_dir, db_path=args.db_path, schema=args.schema)


if __name__ == "__main__":
    main()
