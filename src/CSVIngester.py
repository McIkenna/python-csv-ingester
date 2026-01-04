
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from dateutil import parser
import re
import pandas as pd
import numpy as np



class CSVIngester:
    def __init__(self):
        self.data_cleaning_log = {
            "timestamp": datetime.now().isoformat(),
            "operations": []
        }
        self.column_mappings = {}


    def get_operations_log(self, filepath: Path,) -> List[Dict[str, Any]]:
        """Return operations from the cleaning log. If no operation_type provided, return all operations."""
        with open(filepath, 'r') as f:
            log = json.load(f)  
        return log.get("operations", [])
        
    def logging_process(self, operation: str, details: Dict[str, Any]):
        """Log a cleaning operation"""
        self.data_cleaning_log["operations"].append({
            "operation": operation,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def encode_process(self, filepath: Path) -> str:
        """Detect file encoding"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    f.read()
                return enc
            except UnicodeDecodeError:
                continue
        return 'utf-8'
    
    def standardize_column_name(self, col: str) -> str:
        """Standardize column names to snake_case"""

        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', col)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        clean = ''.join(c if c.isalnum() or c == '_' else '_' for c in s2.lower()) 
        clean = '_'.join(filter(None, clean.split('_'))) 
        return clean
        # Convert CamelCase / PascalCase to snake_case
        
    
    def detect_column_type(self, series: pd.Series) -> str:
        try:
            pd.to_numeric(series.dropna(), errors='raise')
            return 'numeric'
        except (ValueError, TypeError):
            pass
        
        # Try date detection using pandas' flexible parser
        non_null = series.dropna()
        if len(non_null) > 0:
            date_count = 0
            date_samples = min(len(non_null), 100)
            
            for val in non_null.head(date_samples):
                val_str = str(val).strip()
                if not val_str:
                    continue
                
                try:
                    parser.parse(str(val), dayfirst=True)
                    date_count += 1
                except:
                    pass
            
            # If more than 50% of values parse as dates, classify as date
            if date_count / date_samples > 0.5:
                return 'date'
        
        return 'categorical'
    
    def date_parser(self, series: pd.Series) -> pd.Series:
        def parse_single(val):
            try:
                # Parse each value individually
                dt = parser.parse(str(val), dayfirst=True)
                return dt.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                # Return None if parsing fails
                return None

        # Apply to the entire Series
        iso_series = series.apply(parse_single)
        
        return iso_series
    
    def outlier_truncate(self, series: pd.Series) -> pd.Series:
        """Clip numeric outliers at 1st and 99th percentiles"""
        lower = series.quantile(0.01)
        upper = series.quantile(0.99)
        clipped = series.clip(lower=lower, upper=upper)
        
        n_clipped = ((series < lower) | (series > upper)).sum()
        if n_clipped > 0:
            self.logging_process("outlier_truncate", {
                "column": series.name,
                "lower_bound": float(lower),
                "upper_bound": float(upper),
                "values_clipped": int(n_clipped)
            })
        
        return clipped
    
    def processed_dataframe(self, df: pd.DataFrame, source_file: str) -> pd.DataFrame:
        """Clean a single dataframe"""
        self.logging_process("load_file", {
            "source": source_file,
            "rows": len(df),
            "columns": len(df.columns)
        })
        
        # Standardize column names
        original_cols = df.columns.tolist()
        df.columns = [self.standardize_column_name(col) for col in df.columns]
        
        col_mapping = dict(zip(original_cols, df.columns))
        self.logging_process("standardize_columns", {
            "source": source_file,
            "mappings": col_mapping
        })
        
        # Detect and clean each column type
        for col in df.columns:
            col_type = self.detect_column_type(df[col])
            
            if col_type == 'numeric':
                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Fill missing with median
                if df[col].isna().any():
                    median_val = df[col].median()
                    missing_count = df[col].isna().sum()
                    # df[col].fillna({col: median_val}, inplace=True)
                    df[col] = df[col].fillna(median_val)
                    
                    self.logging_process("fill_missing_numeric", {
                        "column": col,
                        "fill_value": float(median_val),
                        "missing_count": int(missing_count)
                    })
                
                # Clip outliers
                df[col] = self.outlier_truncate(df[col])
                
            elif col_type == 'date':
            
                # Parse and format dates
                df[col] = self.date_parser(df[col])
                
                self.logging_process("format_dates", {
                    "column": col,
                    "format": "ISO-8601 (YYYY-MM-DD)"
                })
                
            else:  # categorical
                # Fill missing with 'Unknown'
                if df[col].isna().any():
                    missing_count = df[col].isna().sum()
                    # df[col].fillna({col: 'Unknown'}, inplace=True)
                    df[col] = df[col].fillna('Unknown')
                    
                    self.logging_process("fill_missing_categorical", {
                        "column": col,
                        "fill_value": "Unknown",
                        "missing_count": int(missing_count)
                    })
        
        return df
    
    def consolidated_cleaned_dataframes(self, dfs: List[pd.DataFrame]) -> pd.DataFrame:
        """Consolidate multiple dataframes into one"""
        if not dfs:
            return pd.DataFrame()
        
        # Get all unique columns
        all_columns = set()
        for df in dfs:
            all_columns.update(df.columns)
        
        # Reindex all dataframes to have same columns
        normalized_dfs = []
        for df in dfs:
            missing_cols = all_columns - set(df.columns)
            for col in missing_cols:
                df[col] = np.nan
            normalized_dfs.append(df[sorted(all_columns)])
        
        # Concatenate
        consolidated = pd.concat(normalized_dfs, ignore_index=True)
        
        self.logging_process("consolidate", {
            "total_dataframes": len(dfs),
            "total_rows": len(consolidated),
            "total_columns": len(consolidated.columns)
        })
        
        return consolidated
    
    def file_processor(self, input_files: List[str], output_file: str, log_file: str):
        """Main processing pipeline"""
        print(f"Processing {len(input_files)} CSV file(s)...")
        
        cleaned_dfs = []
        
        for filepath in input_files:
            path = Path(filepath)
            if not path.exists():
                print(f"Warning: {filepath} does not exist, skipping...")
                continue
            
            print(f"  Loading {path.name}...")
            
            # this detect encoding
            encoding = self.encode_process(path)
            
            # Load CSV
            try:
                df = pd.read_csv(path, encoding=encoding)
            except Exception as e:
                print(f"  Error loading {path.name}: {e}")
                continue
            
            # Clean dataframe
            cleaned_df = self.processed_dataframe(df, str(path))
            cleaned_dfs.append(cleaned_df)
        
        if not cleaned_dfs:
            print("Error: No data to process")
            return
        
        # Consolidate all dataframes
        print("Consolidating datasets...")
        final_df = self.consolidated_cleaned_dataframes(cleaned_dfs)
        
        # Save output
        print(f"Writing cleaned data to {output_file}...")
        final_df.to_csv(output_file, index=False)
        
        # Save log
        print(f"Writing cleaning log to {log_file}...")
        with open(log_file, 'w') as f:
            json.dump(self.data_cleaning_log, f, indent=2)
        
        print(f"\nComplete!")
        print(f"  Processed: {len(cleaned_dfs)} file(s)")
        print(f"  Output rows: {len(final_df)}")
        print(f"  Output columns: {len(final_df.columns)}")


def main():
    parser = argparse.ArgumentParser(
        description='Clean and consolidate multiple CSV files with inconsistent schemas'
    )
    parser.add_argument(
        'input_files',
        nargs='+',
        help='Input CSV file paths'
    )
    parser.add_argument(
        '-o', '--output',
        default='cleaned_data.csv',
        help='Output CSV file path (default: cleaned_data.csv)'
    )
    parser.add_argument(
        '-l', '--log',
        default='data_cleaning_log.json',
        help='Output log file path (default: data_cleaning_log.json)'
    )
    
    args = parser.parse_args()
    
    processor = CSVIngester()
    processor.file_processor(args.input_files, args.output, args.log)


if __name__ == '__main__':
    main()