## Overview

Implement a Python CLI that ingests multiple CSV inputs with inconsistent schemas (varying names, encodings, date formats), standardized column names, ISO-formats dates, imputes missing numericals by median and categoricals as 'Unknown', clips numeric outliers at the 1st/99th percentiles, and outputs a consolidated cleaned dataset and a JSON log of applied cleaning operations.

### Requirements
- Python CLI that ingests multiple CSV inputs
- Inputs must have inconsistent schemas (varying names, encodings, date formats)
- Must have standardized column names, ISO-formats dates
- Change inputs missing numericals to median and categoricals to 'Unknown'
- Clip the numeric outliers at the 1st/99th percentiles
- Should output a consolidated cleaned dataset
- Have a JSON log of applied cleaning operations

## System Requirements

### Required Software
- **Python**: 3.8 or higher
- **Bash**: 4.0 or higher
- **pip**: Python package manager

### Python Dependencies
```bash
pytest==8.4.1 \
argparse==1.4.0 \
datetime==5.5 \
pandas==2.3.3 \
numpy==2.0.2 \
pathlib==1.0.1 \
typing==3.10.0.0 
```

---

## Installation

### 2. Install Python Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install pandas numpy pytest
```

### 3. Make Scripts Executable
```bash
chmod +x solution/CSVIngester.py
chmod +x solution/solve.sh
chmod +x tests/test.sh
```

---

## Project Structure

```
python-csv-ingest/      
├── solution  
|   |__ CSVIngester.py        # Main Python CLI application
|   |__ solve.sh                # Bash shell interface to run the solution
|__ src
|   |__ sample1_data.csv       # Sample data to test the solution
|   |__ sample2_data.csv
├── tests
|    |__ test.sh                # Bash shell to run test interface
|   |__test_outputs.py            # Pytest test suite
|   ├──test_data.csv              # Generated test file
|   ├──test2_data.csv           # Generated test file
|   ├──test3_data.csv          # Generated test file
|   ├──cleaned_data.csv            # Output file (generated and removed after test case completion)
|   └──cleaning_log.json           # Operation log (generated and removed after test case completion)
|   └──final_log.json           # Comprehensive Operation log (generated and removed after test case completion)
├── instruction.md             # This file contains the information about the app
|__ task.toml                 # Contains configurations
```

---

## Core Components

### 1. CSV Ingester `CSVIngester.py`

**Main Class: `CSVIngester`**

**Key Methods:**
- `encode_process()` - Auto-detects file encoding (UTF-8, and Latin-1)
- `standardize_column_name()` - Converts columns to snake_case
- `detect_column_type()` - Identifies numeric/date/categorical columns
- `date_parser()` - Converts various date formats to ISO-8601
- `outlier_truncate()` - Clips values at 1st/99th percentiles
- `logging_process()` - Output a json log of the cleaned process
- `get_operations_log()` - Helper functions to output json logs
- `processed_dataframe()` - Clean and process a single CSV file
- `consolidated_cleaned_dataframes()` - Merge multiple cleaned CSV file 
- `file_processor()` - Full pipeline execution

**Features:**
- ✅ Handles multiple encodings (UTF-8, and Latin-1)
- ✅ Standardizes inconsistent column names
- ✅ Detects and parses 14+ date formats
- ✅ Fills missing numerics with median
- ✅ Fills missing categoricals with "Unknown"
- ✅ Clips outliers at 1st/99th percentiles
- ✅ Generates detailed JSON operation logs

### 2. Shell Interface (`solution/solve.sh`)

**Available Bash Commands:**
- `encoding-detection <filepath>`
- `name-standardization <column_name>`
- `type-detection <csv_file> <column_name>`
- `date-parsing <csv_file> <column_name>`
- `outlier-truncate <csv_file> <column_name>`
- `dataframe-cleaning <csv_file> [output_file]`
- `dataframe-consolidation <output_file> <file1> <file2> ...`
- `file-processing <output_file> <log_file> <file1> <file2> ...`
- `cleaning-log [log_file]`
- `csv-summary <csv_file>`
- `get-operations <output_file>`

### 3. Test Data Generator (`generate_test_csvs.py`)

Three already generated messy CSV files for testing:
- **test_data.csv** (10 rows)
- **test2_data.csv** (10 rows)
- **test3_data.csv** (10 rows)

---

## Usage Guide

### Quick Start

#### 1. Clean Data Using Python CLI
```bash
# Basic usage
python solution/CSVIngester.py tests/test_data.csv tests/test2_data.csv tests/test3_data.csv

# Custom output paths
python solution/CSVIngester.py tests/test_data.csv tests/test2_data.csv -o tests/cleaned.csv -l tests/log.json

# View help
python solution/CSVIngester.py --help
```

#### 3. Clean Data Using Bash Functions
```bash
# Source the shell script
source solution/solve.sh

# Use individual commands
encoding-detection "tests/test_data.csv"
name-standardization "Product Price $"
type-detection "tests/test_data.csv" "Order Date"

# Full pipeline
file-processing "output.csv" "log.json" "tests/test_data.csv" "tests/test2_data.csv"
```

### Advanced Usage

#### Inspect CSV Before Cleaning
```bash
source solution/solve.sh
csv-summary "tests/test_data.csv"
```

Output (JSON):
```json
{
  "file": "tests/test_data.csv",
  "rows": 10,
  "columns": 8,
  "column_names": ["Order ID", "Customer Name", "Order Date", ...],
  "missing_values": {"Customer Name": 2, "Quantity!!": 10, ...}
}
```

#### Check Column Type bash
type-detection "tests/test_data.csv" "Order Date"  # Returns: date
type-detection "tests/test_data.csv" "Product Price $"  # Returns: numeric
type-detection "tests/test_data.csv" "Status"  # Returns: categorical
```

#### Analyze Outliers
```bash
outlier-truncate "tests/test_data.csv" "Product Price $"
```

Output (JSON):
```json
{
  "lower_bound": 15.5,
  "upper_bound": 485.2,
  "original_min": 10.0,
  "original_max": 9500.0,
  "clipped_min": 15.5,
  "clipped_max": 485.2
}
```

#### Clean Single File
```bash
dataframe-cleaning "tests/test_data.csv" "tests/cleaned_output.csv"
```

#### Consolidate Multiple Files
```bash
dataframe-consolidation "consolidated_output.csv" "tests/test_data.csv" "tests/test2_data.csv" "tests/test3_data.csv"
```

#### View Cleaning Log
```bash
file-processing "output.csv" "log.json" "tests/test_data.csv"
cleaning-log "log.json"
```

Output (JSON):
```json
{
  "timestamp": "2025-01-03T10:30:45.123456",
  "operations": [
   {
      "operation": "load_file",
      "details": {
        "source": "tests/test_data.csv",
        "rows": 10,
        "columns": 8
      },
      "timestamp": "2026-01-03T11:15:21.457038"
    },
    {
      "operation": "standardize_columns",
      "details": {
        "source": "tests/test_data.csv",
        "mappings": {
          "Order ID": "order_id",
          "Customer Name": "customer_name",
          "Order Date": "order_date",
          "Product Price $": "product_price",
          "Quantity!!": "quantity",
          "Total Amount": "total_amount",
          "Ship Date": "ship_date",
          "Status": "status"
        }
      },
      "timestamp": "2026-01-03T11:15:21.457205"
    }
    ...
  ]
}
```

---

## Testing

### Running Tests

#### Run All Tests
```bash
pytest tests/test_outputs.py -v
```

#### Run Specific Test
```bash
pytest tests/test_outputs.py::test_should_detect_encoding -v
pytest tests/test_outputs.py::test_get_cleaning_log -v
```

#### Run with Detailed Output
```bash
pytest tests/test_outputs.py -vv --tb=short
```

#### Run with Coverage (Optional)
```bash
pip install pytest-cov
pytest tests/test_outputs.py --cov=csv_cleaner --cov-report=html
```

### Test Suite Overview

**Total Tests:** 26
## Test Cases

### Test Case 1: Column Name Standardization

**Input:**
```python
"Product Price $"
"Order ID"
"Quantity!!"
"Customer Name"
```

**Expected Output:**
```python
"product_price"
"order_id"
"quantity"
"customer_name"
```

**Test:**
```bash
pytest tests/test_outputs.py::test_standardize_spaces_col_name -v  
pytest tests/test_outputs.py::test_standardize_any_special_chars -v
pytest tests/test_outputs.py::test_standardize_any_casing -v
```

---

### Test Case 2: Date Format Detection

**Input CSV:**
```csv
Order Date
2025-01-01
01/05/2025
Jan 10, 2025
15-01-2025
2025/01/20
```

**Expected:**
- Column type detected as: `date`
- All dates converted to: `YYYY-MM-DD` format

**Test:**
```bash
pytest tests/test_outputs.py::test_detect_date_column -v
pytest tests/test_outputs.py::test_parse_iso_dates -v
pytest tests/test_outputs.py::test_parse_mixed_date_formats -v
```

### Test Case 3: Missing Value Imputation

**Input CSV:**
```csv
ID,Price,Quantity,Category
1,100,5,Electronics
2,150,,Furniture
3,,10,Electronics
4,120,8,
```

**Expected Output:**
- Price (numeric): Missing filled with median (120)
- Quantity (numeric): Missing filled with median (7.5)
- Category (categorical): Missing filled with "Unknown"

**Test:**
```bash
pytest tests/test_outputs.py::test_clean_single_dataframe -v
pytest tests/test_outputs.py::test_cleaned_columns_standardized -v
```
---

### Test Case 4: Outlier Clipping

**Input CSV:**
```csv
Product,Price
Widget,100
Gadget,150
Outlier,9999
Normal,120
```

**Expected:**
- Outliers (9999) clipped to 99th percentile
- 1% lowest values clipped to 1st percentile
- Log shows clipping operation

**Test:**
```bash
pytest tests/test_outputs.py::test_clip_numeric_outliers -v
```

Expected JSON:
```json
{
  "lower_bound": 15.5,
  "upper_bound": 485.2,
  "original_min": 10.0,
  "original_max": 9500.0,
  "clipped_min": 15.5,
  "clipped_max": 485.2
}
```

---

### Test Case 5: Multi-File Consolidation

**Input:**
- `tests/test_data.csv` (150 rows, 8 columns)
- `employee_data.csv` (100 rows, 7 columns)
- `inventory_data.csv` (80 rows, 7 columns)

**Expected:**
- All files merged into single CSV
- Total rows: 330
- Columns: Union of all unique columns
- Missing columns filled with NaN

**Test:**
```bash
pytest tests/test_outputs.py::test_consolidate_dataframes -v
```

---

### Test Case 6: Encoding Detection

**Input:**
- `tests/test_data.csv` (UTF-8 encoding)
- `tests/latin1_data.csv` (Latin-1 encoding)

**Expected:**
- UTF-8 detected for tests/test_data.csv
- Latin-1 detected for employee_data.csv
- Both files read correctly

**Test:**
```bash
pytest tests/test_outputs.py::test_should_detect_utf8_encoding -v
pytest tests/test_outputs.py::test_should_detect_latin_encoding -v
pytest tests/test_outputs.py::test_should_detect_encoding_nonexistent_file -v
```

---

### Test Case 7: Full Pipeline Execution

**Input:**
- Multiple CSV files with various issues
- Inconsistent schemas
- Missing values
- Outliers
- Multiple date formats

**Expected Output:**
1. Cleaned and consolidated CSV
2. Detailed JSON log with all operations
3. Standardized column names
4. All dates in ISO format
5. Missing values filled
6. Outliers clipped

**Test:**
```bash
pytest tests/test_outputs.py::test_process_full_pipeline -v
pytest tests/test_outputs.py::test_full_workflow -v
```
---

### Test Case 8: Column Type Detection Accuracy

**Input CSV:**
```csv
ID,Date,Amount,Status
1,2025-01-01,100.50,Active
2,01/05/2025,200.75,Pending
3,Jan 10 2025,150.25,Active
```

**Expected:**
- ID: `numeric`
- Date: `date`
- Amount: `numeric`
- Status: `categorical`

**Test:**
```bash
pytest tests/test_outputs.py::test_detect_numeric_column -v
pytest tests/test_outputs.py::test_detect_categorical_column -v

```

---

### Test Case 9: Error Handling

**Scenarios:**
1. Non-existent file
2. Non-existent column
3. Invalid CSV format
4. Empty CSV

**Expected:**
- Graceful error messages
- No crashes
- Appropriate return codes

**Test:**
```bash
pytest tests/test_outputs.py::test_detect_nonexistent_column -v
pytest tests/test_outputs.py::test_get_cleaning_log_nonexistent_file -v
pytest tests/test_outputs.py::test_should_detect_encoding_nonexistent_file -v
pytest tests/test_outputs.py::test_summary_shows_missing_values -v
```

---

### Test Case 10: CSV Summary

**Input:**
- CSV files

**Expected Output:**
1.A summary of the csv file


**Test:**
```bash
pytest tests/test_outputs.py::test_get_csv_summary -v
pytest tests/test_outputs.py::test_summary_shows_missing_values -v
```
--

### Test Case 11: Log Operations Data

**Input:**
- CSV files

**Expected Output:**
1.Test retrieval of existing operations from log
2.Check logs contains an operation


**Test:**
```bash
pytest tests/test_outputs.py::test_get_existing_operations -v
pytest tests/test_outputs.py::test_process_log_contains_operations -v
```

### Test Case 12: Replacing Empty Values
**Input:**
- CSV files

**Expected Output:**
1.Process data to replace empty categoricals with Unknown
2.Process data to replace empty numerical with median


**Test:**
```bash
pytest tests/test_outputs.py::test_get_unknown_for_missing -v
pytest tests/test_outputs.py::test_get_median_for_missing -v
```
## Additional Resources

### Supported Date Formats

The system automatically detects and parses these formats:
- ISO: `2025-01-01`, `2025/01/01`, `2025.01.01`
- US: `01/15/2025`, `01/15/25`, `1-15-2025`
- European: `15/01/2025`, `15.01.2025`, `15-01-2025`
- Text: `Jan 15, 2025`, `15 Jan 2025`, `January 15, 2025`

### Column Name Transformations

| Original | Standardized |
|----------|-------------|
| `Product Name` | `product_name` |
| `Price $` | `price` |
| `Quantity!!` | `quantity` |
| `Order-ID` | `order_id` |
| `Customer_Email` | `customer_email` |

### Performance Tips

1. **Large Files:** Process in batches
2. **Many Columns:** Consider selective cleaning
3. **Memory Issues:** Increase system swap space
4. **Speed:** Use SSD for temporary files