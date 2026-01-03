import os
from sys import stdout
import pytest
import json
import subprocess
import shlex
from unittest.mock import patch
import csv
from pathlib import Path


def extract_json_from_output(output):
    """Extract JSON from output that may contain other text"""
    # Try to find JSON object or array
    # Look for balanced braces or brackets
    try:
        # First, try parsing the whole thing
        return json.loads(output)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON starting with { or [
    for start_char in ['{', '[']:
        start_idx = output.find(start_char)
        if start_idx != -1:
            # Find the matching closing brace/bracket
            depth = 0
            end_char = '}' if start_char == '{' else ']'
            
            for i in range(start_idx, len(output)):
                if output[i] == start_char:
                    depth += 1
                elif output[i] == end_char:
                    depth -= 1
                    if depth == 0:
                        # Found complete JSON
                        json_str = output[start_idx:i+1]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            continue
    
    # If all else fails, raise error
    raise json.JSONDecodeError(f"No valid JSON found in output", output, 0)

@pytest.fixture
def mock_test_data():
    filepath = os.path.join('tests', 'test_data.csv')
    return filepath

@pytest.fixture
def mock_test_data_two():
    filepath = os.path.join('tests', 'test2_data.csv')
    return filepath

@pytest.fixture
def mock_test_data_three():
    filepath = os.path.join('tests', 'test3_data.csv')
    return filepath

@pytest.fixture
def solve_sh_path():
    """Get path to solve.sh"""
    return os.path.join('solution', "solve.sh")

def run_bash_command(command_name, args, file_path):
    cmd = f"{file_path} {command_name} {args}"
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        executable='/bin/bash'
    )
    stdout = result.stdout.strip()
    
    # If output contains JSON, extract only the JSON part
    # Look for the first occurrence of '[' or '{' to find where JSON starts
    json_start = -1
    for char in ['[', '{']:
        pos = stdout.find(char)
        if pos != -1:
            if json_start == -1 or pos < json_start:
                json_start = pos
    
    if json_start > 0:
        # Check if there's content before JSON (like pip messages)
        pre_json = stdout[:json_start].strip()
        if pre_json:
            # Extract only the JSON part
            stdout = stdout[json_start:]
    
    return stdout, result.stderr.strip(), result.returncode

def test_should_detect_encoding(mock_test_data, solve_sh_path):
    """Test for encoding detection"""
    stdout, stderr, returncode = run_bash_command(
            "encoding-detection",
            f'"{mock_test_data}"',
            solve_sh_path
        )
    assert returncode == 0
    assert "utf" in stdout.lower() or "utf-8" in stdout.lower()

def test_should_detect_encoding_nonexistent_file(solve_sh_path):
    """Test with non-existent file"""
    fake_file = os.path.join('tests', "nonexistent.csv")
    stdout, stderr, returncode = run_bash_command(
        "encoding-detection",
        f'"{fake_file}"',
        solve_sh_path
    )
    assert returncode != 0

def test_standardize_spaces_col_name(solve_sh_path):
        """Test standardizing column with spaces"""
        stdout, stderr, returncode = run_bash_command(
            "name-standardization",
            '"Order Date"',
            solve_sh_path
        )
        assert returncode == 0
        assert stdout.strip() == "order_date"

def test_standardize_any_special_chars(solve_sh_path):
        """Test standardizing column with special characters"""
        stdout, stderr, returncode = run_bash_command(
            "name-standardization",
            '"Price $!!"',
            solve_sh_path
        )
        assert returncode == 0
        assert stdout.strip() == "price"

def test_standardize_any_casing(solve_sh_path):
        """Test standardizing column with special characters"""
        stdout, stderr, returncode = run_bash_command(
            "name-standardization",
            '"ProductPrice"',
            solve_sh_path
        )
        assert returncode == 0
        assert stdout.strip() == "product_price"

# =============================================================================
# Detect Column Type Tests
# =============================================================================

def test_detect_numeric_column(mock_test_data, solve_sh_path):
        """Test detection of numeric column"""
        stdout, stderr, returncode = run_bash_command(
            "type-detection",
            f'"{mock_test_data}" "Product Price $"',
            solve_sh_path
        )
        assert returncode == 0
        assert stdout.strip() == "numeric"

def test_detect_date_column(mock_test_data_two, solve_sh_path):
    """Test detection of date column"""
    stdout, stderr, returncode = run_bash_command(
        "type-detection",
        f'"{mock_test_data_two}" "Last Restock"',
        solve_sh_path
    )
    assert returncode == 0
    assert stdout.strip() == "date"

def test_detect_categorical_column(mock_test_data_two, solve_sh_path):
    """Test detection of categorical column"""
    stdout, stderr, returncode = run_bash_command(
        "type-detection",
        f'"{mock_test_data_two}" "Supplier"',
        solve_sh_path
    )
    assert returncode == 0
    assert stdout.strip() == "categorical"

def test_detect_nonexistent_column(mock_test_data_three, solve_sh_path):
    """Test with non-existent column"""
    stdout, stderr, returncode = run_bash_command(
        "type-detection",
        f'"{mock_test_data_three}" "NonExistent"',
        solve_sh_path
    )
    assert returncode == 0
    assert "not found" in stdout.lower()


# =============================================================================
# Date Parsing Tests
# =============================================================================

def test_parse_iso_dates(mock_test_data, solve_sh_path):
        """Test parsing of ISO format dates"""
        stdout, stderr, returncode = run_bash_command(
            "date-parsing",
            f'"{mock_test_data}" "Order Date"',
            solve_sh_path
        )
        assert returncode == 0
        # Should return JSON array
        dates = extract_json_from_output(stdout)
        assert isinstance(dates, list)
        assert dates[0] == "2023-10-01" or "2023" in dates[0]

def test_parse_mixed_date_formats( mock_test_data_two, solve_sh_path):
    """Test parsing of mixed date formats"""
    stdout, stderr, returncode = run_bash_command(
        "date-parsing",
        f'"{mock_test_data_two}" "Last Restock"',
        solve_sh_path
    )
    assert returncode == 0
    dates = extract_json_from_output(stdout)
    assert isinstance(dates, list)
    # At least one should be parsed
    assert dates[1] == "2023-09-23" or "2023" in dates[1]


#=============================================================================
# Outlier Truncation Tests
#=============================================================================
def test_clip_numeric_outliers(mock_test_data, solve_sh_path):
    """Test clipping of numeric outliers"""
    stdout, stderr, returncode = run_bash_command(
        "outlier-truncate",
        f'"{mock_test_data}" "Total Amount"',
        solve_sh_path
    )
    assert returncode == 0
    result = extract_json_from_output(stdout)
    
    # Validate structure
    assert "lower_bound" in result
    assert "upper_bound" in result
    assert "original_max" in result
    assert "clipped_max" in result
    
    # Clipped max should be <= original max
    assert result["clipped_max"] <= result["original_max"]


#=============================================================================
# DataFrame Cleaning Tests
#=============================================================================
def test_clean_single_dataframe(mock_test_data, solve_sh_path):
    """Test cleaning of entire dataframe"""
    output_file = os.path.join('tests', 'cleaned_output.csv')
    if os.path.exists(output_file):
        os.remove(output_file)
    
    stdout, stderr, returncode = run_bash_command(
        "dataframe-cleaning",
        f'"{mock_test_data}" "{output_file}"',
        solve_sh_path
    )
    assert returncode == 0
    assert os.path.exists(output_file)
    
    # Basic check on cleaned file
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert "order_date" in headers
        assert "product_price" in headers
    
    # Clean up
    os.remove(output_file)

def test_cleaned_columns_standardized(mock_test_data, solve_sh_path):
        """Test that cleaned CSV has standardized column names"""
        output_file = os.path.join('tests', 'cleaned_output.csv')
        stdout, stderr, returncode = run_bash_command(
            "dataframe-cleaning",
            f'"{mock_test_data}" "{output_file}"',
            solve_sh_path
        )
        assert returncode == 0
        result = extract_json_from_output(stdout)
        
        # Check column names are standardized (snake_case, no special chars)
        for col in result["column_names"]:
            assert " " not in col  # No spaces
            assert col.islower() or "_" in col 
        
        # Clean up
        os.remove(output_file)


#=============================================================================
# Test For Consolidation of DataFrames
#=============================================================================
def test_consolidate_dataframes(mock_test_data, mock_test_data_two, mock_test_data_three, solve_sh_path):
    """Test consolidation of multiple dataframes"""
    output_file = os.path.join('tests', 'consolidated_output.csv')
    
    stdout, stderr, returncode = run_bash_command(
        "dataframe-consolidation",
        f'"{output_file}" "{mock_test_data}" "{mock_test_data_two}" "{mock_test_data_three}"',
        solve_sh_path
    )
    assert returncode == 0
    result = extract_json_from_output(stdout)
        # Validate structure
    assert "output_file" in result
    assert "input_files_count" in result
    assert "total_rows" in result
    
    # Should have combined rows from both files each having at least 10 rows
    assert result["total_rows"] >= 30 
    
   
    # Clean up
    os.remove(output_file)


def test_process_full_pipeline(mock_test_data, mock_test_data_two, mock_test_data_three, solve_sh_path):
        """Test the complete processing pipeline"""
        output_file = os.path.join('tests', "final_output.csv")
        log_file = os.path.join('tests', "process_log.json")
        
        stdout, stderr, returncode = run_bash_command(
            "file-processing",
            f'"{output_file}" "{log_file}" "{mock_test_data}" "{mock_test_data_two}" "{mock_test_data_three}"',
            solve_sh_path
        )
        assert returncode == 0
        
        # Parse the log output
        log = extract_json_from_output(stdout)
        
        # Validate log structure
        assert "timestamp" in log
        assert "operations" in log
        assert isinstance(log["operations"], list)
        assert len(log["operations"]) > 0
        
        # Output files should exist
        assert os.path.exists(output_file)
        assert os.path.exists(log_file)

        os.remove(output_file)
        os.remove(log_file)

def test_process_log_contains_operations(mock_test_data_two,solve_sh_path):
        """Test that processing log contains expected operations"""
        output_file = os.path.join('tests', "output.csv")
        log_file = os.path.join('tests', "log.json")
        
        stdout, stderr, returncode = run_bash_command(
            "file-processing",
            f'"{output_file}" "{log_file}" "{mock_test_data_two}"',
            solve_sh_path
        )
        assert returncode == 0
        
        log = extract_json_from_output(stdout)
        operations = [op["operation"] for op in log["operations"]]
        
        # Should contain key operations
        assert "load_file" in operations
        assert "standardize_columns" in operations
        os.remove(output_file)
        os.remove(log_file)

def test_get_existing_operations(mock_test_data, solve_sh_path):
  
        output_file = os.path.join('tests', "output.csv")
        log_file = os.path.join('tests', "log.json")
        
        # First, run processing to generate log
        stdout, stderr, returncode = run_bash_command(
            "file-processing",
            f'"{output_file}" "{log_file}" "{mock_test_data}"',
            solve_sh_path
        )
        assert returncode == 0
        
        # Now, get existing operations
        stdout, stderr, returncode = run_bash_command(
            "get-operations",
            f'"{log_file}"',
            solve_sh_path
        )
        assert returncode == 0
        
        operations = extract_json_from_output(stdout)
        assert isinstance(operations, list)
        assert len(operations) > 0
        
        # Clean up
        os.remove(output_file)
        os.remove(log_file)


#=============================================================================
# Test Get Cleaning Log
#=============================================================================
def test_get_cleaning_log(mock_test_data, solve_sh_path):
        """Test retrieval of cleaning log"""
        output_file = os.path.join('tests', "output.csv")
        log_file = os.path.join('tests', "log.json")
        
        # First, run processing to generate log
        stdout, stderr, returncode = run_bash_command(
            "file-processing",
            f'"{output_file}" "{log_file}" "{mock_test_data}"',
            solve_sh_path
        )
        assert returncode == 0
        
        # Now, get cleaning log
        stdout, stderr, returncode = run_bash_command(
            "cleaning_log",
            f'"{log_file}"',
            solve_sh_path
        )
        assert returncode == 0
        
        cleaning_log = extract_json_from_output(stdout)
        assert isinstance(cleaning_log, dict)
        assert "operations" in cleaning_log
        assert isinstance(cleaning_log["operations"], list)
        
        # Clean up
        os.remove(output_file)
        os.remove(log_file)

def test_get_cleaning_log_nonexistent_file(solve_sh_path):
        """Test retrieval of cleaning log from non-existent file"""
        fake_log_file = os.path.join('tests', "nonexistent_log.json")
        
        stdout, stderr, returncode = run_bash_command(
            "cleaning_log",
            f'"{fake_log_file}"',
            solve_sh_path
        )
        assert returncode == 0
        
        error_response = extract_json_from_output(stdout)
        assert "error" in error_response
        assert "not found" in error_response["error"].lower()

#=============================================================================
# Test Get CSV Summary
#=============================================================================
def test_get_csv_summary(mock_test_data, solve_sh_path):
        
        # First, run processing to generate log
        stdout, stderr, returncode = run_bash_command(
            "csv-summary",
            f'"{mock_test_data}"',
            solve_sh_path
        )
        assert returncode == 0
        
        summary = extract_json_from_output(stdout)
        
        # Validate structure
        assert "file" in summary
        assert "rows" in summary
        assert "columns" in summary
        assert "column_names" in summary
        assert "missing_values" in summary
        
        # Validate data
        assert summary["rows"] > 0
        assert summary["columns"] > 0
        assert isinstance(summary["column_names"], list)

def test_summary_shows_missing_values( mock_test_data_two, solve_sh_path):
        """Test that summary correctly identifies missing values"""
        stdout, stderr, returncode = run_bash_command(
            "csv-summary",
            f'"{mock_test_data_two}"',
            solve_sh_path
        )
        assert returncode == 0
        
        summary = extract_json_from_output(stdout)
        
        # Should have missing values dict
        assert "missing_values" in summary
        assert isinstance(summary["missing_values"], dict)

#=============================================================================
# Full Integration of muiltiple components
#=============================================================================

"""Integration tests combining multiple functions"""
    
def test_full_workflow(mock_test_data, mock_test_data_two,  mock_test_data_three,
                        solve_sh_path):
    """Test a complete workflow using multiple functions"""
    
    # 1. Get summary of input files
    stdout1, _, _ = run_bash_command(
        "csv-summary",
        f'"{mock_test_data}"',
        solve_sh_path
    )
    summary1 = extract_json_from_output(stdout1)
    assert summary1["rows"] > 0
    
    # 2. Detect column types
    stdout2, _, _ = run_bash_command(
        "type-detection",
        f'"{mock_test_data}" "Product Price $"',
        solve_sh_path
    )
    assert "numeric" in stdout2.strip()
    
    # 3. Process files
    output_file = os.path.join('tests', "final.csv")
    log_file = os.path.join('tests', "final_log.json")
    stdout3, _, _ = run_bash_command(
        "file-processing",
        f'"{output_file}" "{log_file}" "{mock_test_data}" "{mock_test_data_two}" "{mock_test_data_three}"',
        solve_sh_path
    )
    log = extract_json_from_output(stdout3)
    assert len(log["operations"]) > 0
    
    # 4. Get summary of output file
    stdout4, _, _ = run_bash_command(
        "csv-summary",
        f'"{output_file}"',
        solve_sh_path
    )
    summary2 = extract_json_from_output(stdout4)

    # Output should have combined rows
    assert summary2["rows"] >= summary1["rows"]

    # Clean up
    os.remove(output_file)
    os.remove(log_file)