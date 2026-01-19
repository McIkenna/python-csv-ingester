set -e
# apt update && apt install -y vim
# pip install pandas numpy argparse pathlib datetime typing
# !/bin/bash

# This script wraps Python CSVIngester methods as bash functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Detect file encoding
detect_encoding() {
  local filepath="$1"

  if [ ! -f "$filepath" ]; then
    echo "Error: File not found - $filepath"
    exit 1
  fi
  detected_encoding=$(python3 -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}')
from CSVIngester import CSVIngester
from pathlib import Path

ingester = CSVIngester()
encoding = ingester.encode_process(Path('${filepath}'))
print(encoding)
")

if [ -z "$detected_encoding" ]; then
    echo "Error: Failed to detect encoding"
    exit 1
fi
  
  echo "$detected_encoding"
}

# Standardize a column name
standardize_column_name() {
   local column_name="$1"
   if [ -z "$column_name" ]; then
    echo "Error: Column name is required"
    exit 1
  fi
     standardized_name=$(python3 -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}')
from CSVIngester import CSVIngester

ingester = CSVIngester()
result = ingester.standardize_column_name('${column_name}')
print(result)
")

if [ -z "$standardized_name" ]; then
    echo "Error: Failed to standardize column name"
    exit 1
  fi
  
  echo "$standardized_name"
}

# Detect column type (numeric, date, or categorical)
detect_column_type() {
  local csv_file="$1"
  local column_name="$2"

  if [ ! -f "$csv_file" ]; then
    echo "Error: File not found - $csv_file"
    exit 1
  fi
  
  if [ -z "$column_name" ]; then
    echo "Error: Column name is required"
    exit 1
  fi
  
  column_type=$(python3 -c "
import sys
import pandas as pd
sys.path.insert(0, '${SCRIPT_DIR}')
from CSVIngester import CSVIngester

ingester = CSVIngester()
df = pd.read_csv('${csv_file}')
if '${column_name}' in df.columns:
    col_type = ingester.detect_column_type(df['${column_name}'])
    print(col_type)
else:
    print('Column not found')
")
  if [ "$column_type" == "Column not found" ]; then
    echo "Error: Column '${column_name}' not found in file"
    exit 1
  fi

  echo "$column_type"
}

# Parse dates in a column to ISO format
parse_dates() {
  local csv_file="$1"
  local column_name="$2"
  
  if [ ! -f "$csv_file" ]; then
    echo "Error: File not found - $csv_file"
    exit 1
  fi
  
  if [ -z "$column_name" ]; then
    echo "Error: Column name is required"
    exit 1
  fi
  parsed_dates=$(python3 -c "
  
import sys
import pandas as pd
import json
sys.path.insert(0, '${SCRIPT_DIR}')
from CSVIngester import CSVIngester

ingester = CSVIngester()
df = pd.read_csv('${csv_file}')
if '${column_name}' in df.columns:
    parsed = ingester.date_parser(df['${column_name}'])
    print(json.dumps(parsed.head(10).tolist()))
else:
    print('Column not found')
")

if [ "$parsed_dates" == "Column not found" ]; then
    echo "Error: Column '${column_name}' not found in file"
    exit 1
  fi
  
  echo "$parsed_dates"
}

# Clip outliers in a numeric column
clip_outliers() {
  local csv_file="$1"
  local column_name="$2"

  if [ ! -f "$csv_file" ]; then
    echo "Error: File not found - $csv_file"
    exit 1
  fi
  
  if [ -z "$column_name" ]; then
    echo "Error: Column name is required"
    exit 1
  fi
  
  clipped_stats=$(python3 -c "
import sys
import pandas as pd
import json
sys.path.insert(0, '${SCRIPT_DIR}')
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

if [ "$clipped_stats" == "Column not found" ]; then
    echo "Error: Column '${column_name}' not found in file"
    exit 1
  fi
  
  echo "$clipped_stats"
}

# Clean a single CSV file
clean_dataframe() {
  local csv_file="$1"
  local output_file="${2:-cleaned_output.csv}"

  if [ ! -f "$csv_file" ]; then
    echo "Error: File not found - $csv_file"
    exit 1
  fi
  
  cleaning_result=$(python3 -c "
import sys
import pandas as pd
import json
sys.path.insert(0, '${SCRIPT_DIR}')
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

if [ ! -f "$output_file" ]; then
    echo "Error: Failed to create output file - $output_file"
    exit 1
  fi
  
  echo "$cleaning_result"
}

# Consolidate multiple CSV files
consolidate_dataframes() {
  local output_file="${1:-consolidated.csv}"
  shift
  local input_files=("$@")

  if [ ${#input_files[@]} -eq 0 ]; then
    echo "Error: No input files provided"
    exit 1
  fi
  
  for file in "${input_files[@]}"; do
    if [ ! -f "$file" ]; then
      echo "Error: File not found - $file"
      exit 1
    fi
  done
  
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
sys.path.insert(0, '${SCRIPT_DIR}')
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

 if [ ! -f "$output_file" ]; then
    echo "Error: Failed to create consolidated file - $output_file"
    exit 1
  fi
  
  echo "$consolidation_result"
}


# Process multiple files (full pipeline)
file_processor() {
  local output_file="${1:-cleaned_data.csv}"
  local log_file="${2:-cleaning_log.json}"
  shift 2
  local input_files=("$@")

  if [ ${#input_files[@]} -eq 0 ]; then
    echo "Error: No input files provided"
    exit 1
  fi
  
  for file in "${input_files[@]}"; do
    if [ ! -f "$file" ]; then
      echo "Error: File not found - $file"
      exit 1
    fi
  done

  local files_str=""
  for file in "${input_files[@]}"; do
    files_str="${files_str}'${file}',"
  done
  files_str="[${files_str%,}]" 
  
  processing_result=$(python3 -c "
import sys
import json
sys.path.insert(0, '${SCRIPT_DIR}')
from CSVIngester import CSVIngester

ingester = CSVIngester()
input_files = ${files_str}
ingester.file_processor(input_files, '${output_file}', '${log_file}')

# Read and return the log
with open('${log_file}', 'r') as f:
    log = json.load(f)
    print(json.dumps(log, indent=2))
")

  if [ ! -f "$output_file" ]; then
    echo "Error: Failed to create output file - $output_file"
    exit 1
  fi
  
  if [ ! -f "$log_file" ]; then
    echo "Error: Failed to create log file - $log_file"
    exit 1
  fi

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

  if [ ! -f "$log_file" ]; then
    echo "Error: Log file not found - $log_file"
    exit 1
  fi

  operations_log=$(python3 -c "
import sys
import json
sys.path.insert(0, '${SCRIPT_DIR}')
from CSVIngester import CSVIngester
from pathlib import Path
ingester = CSVIngester()
operations = ingester.get_operations_log(Path('${log_file}'))
print(json.dumps(operations, indent=2))
")

if [ -z "$operations_log" ]; then
    echo "Error: Failed to retrieve operations log"
    exit 1
  fi

  echo "$operations_log"
}

# Log a custom operation (for testing)
log_operation() {
  local operation="$1"
  local details="$2"

   if [ -z "$operation" ]; then
    echo "Error: Operation name is required"
    exit 1
  fi
  
  if [ -z "$details" ]; then
    echo "Error: Details JSON is required"
    exit 1
  fi
  
  log_result=$(python3 -c "
import sys
import json
sys.path.insert(0, '${SCRIPT_DIR}')
from CSVIngester import CSVIngester

ingester = CSVIngester()
details_dict = json.loads('${details}')
ingester.logging_process('${operation}', details_dict)

print(json.dumps(ingester.data_cleaning_log, indent=2))
")
  if [ -z "$log_result" ]; then
    echo "Error: Failed to log operation"
    exit 1
  fi

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
  echo "$summary" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null || {
    echo "Error: Failed to generate valid summary"
    exit 1
  }
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
        cleaning-log)
            get_cleaning_log "$1" 
            ;;
        get-operations)
            operations_logs "$1"
            ;;
        csv-summary)
            get_csv_summary "$1"
            ;;
        *)
            # echo -e "Running Oracle Solution"
            # detect_encoding "./src/sample1_data.csv"
            # standardize_column_name "Order Date"
            # detect_column_type "./src/sample1_data.csv" "Order Date"
            # parse_dates "./src/sample1_data.csv" "Order Date"
            # clip_outliers "./src/sample1_data.csv" "Total Amount"
            # clean_dataframe "./src/sample1_data.csv" "./src/cleaned_sample1.csv"
            # consolidate_dataframes "./src/consolidated_output.csv" "./src/sample1_data.csv" "./src/sample2_data.csv"
            # file_processor "./src/final_cleaned_data.csv" "./src/final_cleaning_log.json" "./src/sample1_data.csv" "./src/sample2_data.csv"
            # get_cleaning_log "./src/final_cleaning_log.json"
            # operations_logs "./src/final_cleaning_log.json"
            # log_operation "custom_test_operation" '{"test_key": "test_value"}'
            # get_csv_summary "./src/sample1_data.csv"
            # echo ""
            echo "Running Oracle Solution"
            echo "========================"
            
            # Find CSV files in src directory
            SAMPLE1="./src/sample1_data.csv"
            SAMPLE2="./src/sample2_data.csv"
            OUTPUT_DIR="./src"

            # Check if sample files exist
            if [ ! -f "$SAMPLE1" ]; then
                echo "Error: $SAMPLE1 not found"
                exit 1
            fi
            
            echo "1. Detecting encoding..."
            detect_encoding "$SAMPLE1"
            
            echo -e "\n2. Standardizing column name..."
            standardize_column_name "Order Date"
            
            echo -e "\n3. Detecting column type..."
            detect_column_type "$SAMPLE1" "Order Date"
            
            echo -e "\n4. Parsing dates..."
            parse_dates "$SAMPLE1" "Order Date"
            
            echo -e "\n5. Clipping outliers..."
            clip_outliers "$SAMPLE1" "Total Amount"
            
            echo -e "\n6. Cleaning dataframe..."
            clean_dataframe "$SAMPLE1" "${OUTPUT_DIR}/cleaned_sample1.csv"
            
            if [ -f "$SAMPLE2" ]; then
                echo -e "\n7. Consolidating dataframes..."
                consolidate_dataframes "${OUTPUT_DIR}/consolidated_output.csv" "$SAMPLE1" "$SAMPLE2"
                
                echo -e "\n8. Processing files..."
                file_processor "${OUTPUT_DIR}/final_cleaned_data.csv" "${OUTPUT_DIR}/final_cleaning_log.json" "$SAMPLE1" "$SAMPLE2"
                
                echo -e "\n9. Getting cleaning log..."
                get_cleaning_log "${OUTPUT_DIR}/final_cleaning_log.json"
                
                echo -e "\n10. Getting operations log..."
                operations_logs "${OUTPUT_DIR}/final_cleaning_log.json"
            fi
            
            echo -e "\n11. Logging custom operation..."
            log_operation "custom_test_operation" '{"test_key": "test_value"}'
            
            echo -e "\n12. Getting CSV summary..."
            get_csv_summary "$SAMPLE1"
            
            echo -e "\n========================"
            echo "Oracle solution completed successfully!"
            ;;
    esac
}

# If script is run directly, show help
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
  main "$@"
fi