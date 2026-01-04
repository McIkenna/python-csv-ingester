set -e
# apt update && apt install -y vim
# pip install pandas numpy argparse pathlib datetime typing
# !/bin/bash

# Solution.sh - Shell interface for CSVIngester functions
# This script wraps Python CSVIngester methods as bash functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/../src/CSVIngester.py"

# Check if CSVIngester.py exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: CSVIngester.py not found in $SCRIPT_DIR"
    exit 1
fi
# Detect file encoding
detect_encoding() {
  local filepath="$1"
  detected_encoding=$(python3 -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}/../src')
from CSVIngester import CSVIngester
from pathlib import Path

ingester = CSVIngester()
encoding = ingester.encode_process(Path('${filepath}'))
print(encoding)
")
  
  echo "$detected_encoding"
}

# Standardize a column name
standardize_column_name() {
   local column_name="$1"
     standardized_name=$(python3 -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}/../src')
from CSVIngester import CSVIngester

ingester = CSVIngester()
result = ingester.standardize_column_name('${column_name}')
print(result)
")
  
  echo "$standardized_name"
}

# Detect column type (numeric, date, or categorical)
detect_column_type() {
  local csv_file="$1"
  local column_name="$2"
  
  column_type=$(python3 -c "
import sys
import pandas as pd
sys.path.insert(0, '${SCRIPT_DIR}/../src')
from CSVIngester import CSVIngester

ingester = CSVIngester()
df = pd.read_csv('${csv_file}')
if '${column_name}' in df.columns:
    col_type = ingester.detect_column_type(df['${column_name}'])
    print(col_type)
else:
    print('Column not found')
")
  
  echo "$column_type"
}

# Parse dates in a column to ISO format
parse_dates() {
  local csv_file="$1"
  local column_name="$2"
  
  parsed_dates=$(python3 -c "
  
import sys
import pandas as pd
import json
sys.path.insert(0, '${SCRIPT_DIR}/../src')
from CSVIngester import CSVIngester

ingester = CSVIngester()
df = pd.read_csv('${csv_file}')
if '${column_name}' in df.columns:
    parsed = ingester.date_parser(df['${column_name}'])
    print(json.dumps(parsed.head(10).tolist()))
else:
    print('Column not found')
")
  
  echo "$parsed_dates"
}

# Clip outliers in a numeric column
clip_outliers() {
  local csv_file="$1"
  local column_name="$2"
  
  clipped_stats=$(python3 -c "
import sys
import pandas as pd
import json
sys.path.insert(0, '${SCRIPT_DIR}/../src')
from CSVIngester import CSVIngester

ingester = CSVIngester()
df = pd.read_csv('${csv_file}')
if '${column_name}' in df.columns:
    series = pd.to_numeric(df['${column_name}'], errors='coerce')
    series.name = '${column_name}'
    lower = series.quantile(0.01)
    upper = series.quantile(0.99)
    clipped = ingester.outlier_truncate(series)
    
    result = {
        'lower_bound': float(lower),
        'upper_bound': float(upper),
        'original_min': float(series.min()),
        'original_max': float(series.max()),
        'clipped_min': float(clipped.min()),
        'clipped_max': float(clipped.max())
    }
    print(json.dumps(result, indent=2))
else:
    print('Column not found')
")
  
  echo "$clipped_stats"
}

# Clean a single CSV file
clean_dataframe() {
  local csv_file="$1"
  local output_file="${2:-cleaned_output.csv}"
  
  cleaning_result=$(python3 -c "
import sys
import pandas as pd
import json
sys.path.insert(0, '${SCRIPT_DIR}/../src')
from CSVIngester import CSVIngester

ingester = CSVIngester()
df = pd.read_csv('${csv_file}')
cleaned_df = ingester.processed_dataframe(df, '${csv_file}')
cleaned_df.to_csv('${output_file}', index=False)

result = {
    'source_file': '${csv_file}',
    'output_file': '${output_file}',
    'rows': len(cleaned_df),
    'columns': len(cleaned_df.columns),
    'column_names': cleaned_df.columns.tolist()
}
print(json.dumps(result, indent=2))
")
  
  echo "$cleaning_result"
}

# Consolidate multiple CSV files
consolidate_dataframes() {
  local output_file="${1:-consolidated.csv}"
  shift
  local input_files=("$@")
  
  # Build Python list of input files
  local files_str=""
  for file in "${input_files[@]}"; do
    files_str="${files_str}'${file}',"
  done
  files_str="[${files_str%,}]"  # Remove trailing comma and wrap in brackets
  
  consolidation_result=$(python3 -c "
import sys
import pandas as pd
import json
sys.path.insert(0, '${SCRIPT_DIR}/../src')
from CSVIngester import CSVIngester

ingester = CSVIngester()
input_files = ${files_str}
dfs = []

for f in input_files:
    try:
        df = pd.read_csv(f)
        dfs.append(df)
    except Exception as e:
        print(f'Error loading {f}: {e}', file=sys.stderr)

if dfs:
    consolidated = ingester.consolidated_cleaned_dataframes(dfs)
    consolidated.to_csv('${output_file}', index=False)
    
    result = {
        'output_file': '${output_file}',
        'input_files_count': len(dfs),
        'total_rows': len(consolidated),
        'total_columns': len(consolidated.columns),
        'columns': consolidated.columns.tolist()
    }
    print(json.dumps(result, indent=2))
else:
    print(json.dumps({'error': 'No valid input files'}))
")
  
  echo "$consolidation_result"
}


# Process multiple files (full pipeline)
file_processor() {
  local output_file="${1:-cleaned_data.csv}"
  local log_file="${2:-cleaning_log.json}"
  shift 2
  local input_files=("$@")

  local files_str=""
  for file in "${input_files[@]}"; do
    files_str="${files_str}'${file}',"
  done
  files_str="[${files_str%,}]" 
  
  processing_result=$(python3 -c "
import sys
import json
sys.path.insert(0, '${SCRIPT_DIR}/../src')
from CSVIngester import CSVIngester

ingester = CSVIngester()
input_files = ${files_str}
ingester.file_processor(input_files, '${output_file}', '${log_file}')

# Read and return the log
with open('${log_file}', 'r') as f:
    log = json.load(f)
    print(json.dumps(log, indent=2))
")
  
  echo "$processing_result"
}

# Get cleaning log operations
get_cleaning_log() {
  local log_file="${1:-cleaning_log.json}"
  
  if [ -f "$log_file" ]; then
    cleaning_log=$(cat "$log_file")
    echo "$cleaning_log"
  else
    echo "{\"error\": \"Log file not found: $log_file\"}"
  fi
}

operations_logs() {
  local log_file="${1:-cleaning_log.json}"

  operations_log=$(python3 -c "
import sys
import json
sys.path.insert(0, '${SCRIPT_DIR}/../src')
from CSVIngester import CSVIngester
from pathlib import Path
ingester = CSVIngester()
operations = ingester.get_operations_log(Path('${log_file}'))
print(json.dumps(operations, indent=2))
")
  echo "$operations_log"
}

# Log a custom operation (for testing)
log_operation() {
  local operation="$1"
  local details="$2"
  
  log_result=$(python3 -c "
import sys
import json
sys.path.insert(0, '${SCRIPT_DIR}/../src')
from CSVIngester import CSVIngester

ingester = CSVIngester()
details_dict = json.loads('${details}')
ingester.logging_process('${operation}', details_dict)

print(json.dumps(ingester.data_cleaning_log, indent=2))
")
  
  echo "$log_result"
}

# Get summary of a CSV file
get_csv_summary() {
  local csv_file="$1"
  if [ ! -f "$csv_file" ]; then
    echo "Error: File not found - $csv_file"
    return 1
  fi
  
  summary=$(python3 -c "
import pandas as pd
import json

df = pd.read_csv('${csv_file}')

summary = {
    'file': '${csv_file}',
    'rows': len(df),
    'columns': len(df.columns),
    'column_names': df.columns.tolist(),
    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
    'missing_values': {col: int(df[col].isna().sum()) for col in df.columns},
    'memory_usage': f\"{df.memory_usage(deep=True).sum() / 1024:.2f} KB\"
}

print(json.dumps(summary, indent=2))
")
  
  echo "$summary"
}

# Main execution example
main() {
  local command="$1"
    shift || true
    
    case "$command" in
    
        encoding-detection)
            detect_encoding "$1"
          ;;
        name-standardization)
            standardize_column_name "$1"
            ;;
        type-detection)
            detect_column_type "$1" "$2"
            ;;
        date-parsing)
            parse_dates "$1" "$2"
            ;;
        outlier-truncate)
            clip_outliers "$1" "$2"
            ;;
        dataframe-cleaning)
            clean_dataframe "$1" "$2"
            ;;
        dataframe-consolidation)
            consolidate_dataframes "$1" "${@:2}"
            ;;
        file-processing)
            file_processor "$1" "$2" "${@:3}"
            ;;
        cleaning_log)
            get_cleaning_log "$1" 
            ;;
        get-operations)
            operations_logs "$1"
            ;;
        csv-summary)
            get_csv_summary "$1"
            ;;
        *)
            echo -e "Error: Unknown command '$command'"
            echo ""
            exit 1
            ;;
    esac
}

# If script is run directly, show help
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
  main "$@"
fi