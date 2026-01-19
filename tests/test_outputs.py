import os
import pytest
import json
import subprocess
import csv


def get_test_directory():
    """Get test directory with Oracle/local fallback"""
    if os.path.exists('/tests') and os.path.isdir('/tests'):
        return '/tests'
    return os.path.dirname(os.path.abspath(__file__))

def get_solve_sh_path():
    """Find solve.sh with multiple fallback locations"""
    possible_paths = [
        '/solution/solve.sh',  # Oracle absolute path
        'solution/solve.sh',   # Relative from project root
        os.path.join(os.path.dirname(get_test_directory()), 'solution', 'solve.sh'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError(f"solve.sh not found. Tried: {possible_paths}")

TEST_DIR = get_test_directory()
# os.path.dirname(os.path.abspath(__file__)) 
# PROJECT_ROOT = os.path.dirname(TEST_DIR)
# PROJECT_ROOT= "app/solution"
def extract_json_from_output(output):
    """Extract JSON from output that may contain other text"""
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON starting with { or [
    for start_char in ['{', '[']:
        start_idx = output.find(start_char)
        if start_idx != -1:
            depth = 0
            end_char = '}' if start_char == '{' else ']'
            
            for i in range(start_idx, len(output)):
                if output[i] == start_char:
                    depth += 1
                elif output[i] == end_char:
                    depth -= 1
                    if depth == 0:
                        json_str = output[start_idx:i+1]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            continue

    raise json.JSONDecodeError("No valid JSON found in output", output, 0)

@pytest.fixture
def mock_latin1_data():
    filepath = os.path.join(TEST_DIR, 'latin1_data.csv')
    latin1_bytes = (
    b"Order Date,Product Price \xa3,Quantity!!,Total Amount,Ship Date\n"
    b"01-10-2023,264.31,7,1850.19,09-10-2023\n"
    b"2023-04-02,171.54,17,2916.21,\n"
    b"05.12.2023,195.14,17,3317.41,2023-12-11\n"
    b"29.08.2023,70.21,10,702.15,09/07/2023\n"
    b"2023/01/09,318.75,8,2550.02,\n"
    b"14-02-2023,90.52,14,1267.33,\n"
    b"20.04.2023,432.02,2,864.05,21.04.2023\n"
    b"11/24/2023,68.48,7,479.39,2023/11/29\n"
    b"03/22/2023,481.85,15,7227.81,\n"
    b"25.07.2023,111.05,11,1221.60,03-08-2023\n"
)
    csv_text = [line.decode('latin-1').split(',') for line in latin1_bytes.split(b'\n') if line]
    with open(filepath, 'w', newline='', encoding='latin-1') as f:
        writer = csv.writer(f)
        writer.writerows(csv_text)

    print(f"Created mock Latin-1 data file at: {filepath}")
    yield filepath

    if os.path.exists(filepath):
        os.remove(filepath)

@pytest.fixture
def mock_test_data():
    filepath = os.path.join(TEST_DIR, 'test_data.csv')
    data = [
    ["Order ID", "Customer Name", "Order Date", "Product Price $", "Quantity!!", "Total Amount", "Ship Date", "Status"],
    ["ORD1000", "", "01-10-2023", "264.3134984759545", "7", "1850.1944893316813", "09-10-2023", ""],
    ["ORD1001", "", "2023-04-02", "171.54224088174146", "17", "2916.2180949896047", "", "Shipped"],
    ["ORD1002", "Bob Johnson", "05.12.2023","" , "17", "3317.4124189023737", "2023-12-11", ""],
    ["ORD1003", "Alice Williams", "29.08.2023", "70.21586678937072", "10", "702.1586678937072", "09/07/2023", ""],
    ["ORD1004", "John Smith", "2023/01/09", "318.7528395915485", "8", "2550.022716732388", "", ""],
    ["ORD1005", "Alice Williams", "14-02-2023", "90.523993705531", "14", "1267.335911877434", "", "Cancelled"],
    ["ORD1006", "Alice Williams", "20.04.2023", "432.0255346209029", "2", "864.0510692418057", "21.04.2023", "Cancelled"],
    ["ORD1007", "", "11/24/2023", "68.48485841399017", "7", "479.39400889793114", "2023/11/29", ""],
    ["ORD1008", "Jane Doe", "03/22/2023", "481.85449697522034", "15", "7227.817454628305", "", ""],
    ["ORD1009", "Alice Williams", "25.07.2023", "111.05535490816476", "11", "1221.6089039898125", "03-08-2023", "Shipped"],
]

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    yield filepath

    if os.path.exists(filepath):
        os.remove(filepath)

@pytest.fixture
def mock_test_data_two():
    filepath = os.path.join(TEST_DIR, 'test2_data.csv')
    data = [
    ["SKU#", "Product  Name", "stock_qty", "Unit Cost ($)", "Last Restock", "Supplier", "Category Type"],
    ["SKU-3000", "Monitor", "261", "32.30900302329", "2023-11-11", "", "Accessories"],
    ["SKU-3001", "Mouse", "431", "194.71833117751393", "23-09-2023", "MegaStore", "Accessories"],
    ["SKU-3002", "Chair", "406", "1994.9345575090506", "2023/10/15", "", "Electronics"],
    ["SKU-3003", "Monitor", "411", "1763.1557275063572", "2023/11/08", "GlobalTech", "Accessories"],
    ["SKU-3004", "Mouse", "124", "1402.7151131444941", "2023-10-28", "GlobalTech", "Accessories"],
    ["SKU-3005", "Keyboard", "375", "1195.107567789151", "04-08-2023", "OfficeSupply Inc", ""],
    ["SKU-3006", "Monitor", "43", "1893.1068424782395", "05-12-2023", "GlobalTech", "Electronics"],
    ["SKU-3007", "Mouse", "13930", "399.4540451996029", "08/04/2023", "TechCorp", "Accessories"],
    ["SKU-3008", "Laptop", "266", "1170.1888689891994", "2023/11/24", "", ""],
    ["SKU-3009", "Desk", "6", "32.92113306832887", "08/22/2023", "OfficeSupply Inc", "Accessories"],
]
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    yield filepath

    if os.path.exists(filepath):
        os.remove(filepath)

@pytest.fixture
def mock_test_data_three():
    filepath = os.path.join(TEST_DIR, 'test3_data.csv')
    data = [
    ["EMP_ID", "Full Name", "hire-date", "Department Name", "Annual_Salary", "Performance Score", "Email Address"],
    ["E2000", "David Wilson", "12/11/21", "Finance", "114970.72704852688", "2", "david.wilson@company.com"],
    ["E2001", "Olivia Davis", "2022.09.21", "", "100384.15881094255", "6", "olivia.davis@company.com"],
    ["E2002", "Sarah Wilson", "24/07/2017", "HR", "93612.46734951547", "1", "sarah.wilson@company.com"],
    ["E2003", "David Moore", "", "Finance", "44620.187981135394", "6", "david.moore@company.com"],
    ["E2004", "Michael Wilson", "11/07/2022", "", "139059.60025167133", "10", "michael.wilson@company.com"],
    ["E2005", "Michael Miller", "2019.11.14", "Sales", "60261.168774296195", "3", "michael.miller@company.com"],
    ["E2006", "", "2022.06.14", "HR", "89472.57725628052", "10", ""],
    ["E2007", "Michael Taylor", "08/21/17", "HR", "131550.1613921459", "5", "michael.taylor@company.com"],
    ["E2008", "Emma Davis", "2020.11.24", "HR", "149362.38813439483", "7", "emma.davis@company.com"],
    ["E2009", "David Moore", "2022-04-03", "", "81289.58900750658", "10", "david.moore@company.com"],
]
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    yield filepath

    if os.path.exists(filepath):
        os.remove(filepath)

@pytest.fixture
def solve_sh_path():
    """Return the absolute path to solve.sh"""
    path = get_solve_sh_path()
    return path

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

def test_should_detect_utf8_encoding(mock_test_data_two, solve_sh_path):
    """Test for encoding detection"""
    stdout, stderr, returncode = run_bash_command(
            "encoding-detection",
            f'"{mock_test_data_two}"',
            solve_sh_path
        )
    assert returncode == 0
    assert "utf" in stdout.lower() or "utf-8" in stdout.lower()

def test_should_detect_latin_encoding(mock_latin1_data, solve_sh_path):
    """Test for encoding detection"""
    stdout, stderr, returncode = run_bash_command(
            "encoding-detection",
            f'"{mock_latin1_data}"',
            solve_sh_path
        )
    assert returncode == 0
    assert "latin" in stdout.lower() or "latin-1" in stdout.lower()
    cleanup_file = mock_latin1_data
    if os.path.exists(cleanup_file):
        os.remove(cleanup_file)

def test_should_detect_encoding_nonexistent_file(solve_sh_path):
    """Test with non-existent file"""
    fake_file = os.path.join(TEST_DIR, "nonexistent.csv")
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
    assert returncode == 1
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
    print('solve_sh_path:', solve_sh_path)
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
    output_file = os.path.join(TEST_DIR, 'cleaned_output.csv')
    if os.path.exists(output_file):
        os.remove(output_file)
    
    stdout, stderr, returncode = run_bash_command(
        "dataframe-cleaning",
        f'"{mock_test_data}" "{output_file}"',
        solve_sh_path
    )
    assert returncode == 0
    assert os.path.exists(output_file)
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert "order_date" in headers
        assert "product_price" in headers
    
    # Clean up
    os.remove(output_file)

def test_cleaned_columns_standardized(mock_test_data, solve_sh_path):
        """Test that cleaned CSV has standardized column names"""
        output_file = os.path.join(TEST_DIR, 'cleaned_output.csv')
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
    output_file = os.path.join(TEST_DIR, 'consolidated_output.csv')
    
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
    
    assert result["total_rows"] >= 30 
    
   
    # Clean up
    os.remove(output_file)


def test_process_full_pipeline(mock_test_data, mock_test_data_two, mock_test_data_three, solve_sh_path):
        """Test the complete processing pipeline"""
        output_file = os.path.join(TEST_DIR, "final_output.csv")
        log_file = os.path.join(TEST_DIR, "process_log.json")
        
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
        output_file = os.path.join(TEST_DIR, "output.csv")
        log_file = os.path.join(TEST_DIR, "log.json")
        
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
  
        output_file = os.path.join(TEST_DIR, "output.csv")
        log_file = os.path.join(TEST_DIR, "log.json")
        
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
# Test Replace Missing Datasets
#=============================================================================
def test_get_median_for_missing(mock_test_data, solve_sh_path):
    """Test to replace missing categorical values with 'Unknown'"""
    output_file = os.path.join(TEST_DIR, 'output.csv')
    log_file = os.path.join(TEST_DIR, "log.json")
    if os.path.exists(output_file):
        os.remove(output_file)
    with open(mock_test_data, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert "Product Price $" in headers
        empty_data_idx = headers.index("Product Price $")
        next(reader)
        next(reader)
        third_row = next(reader)
        # test the value in the first data row
        assert third_row[empty_data_idx] is None or third_row[empty_data_idx] == ""
    
    stdout, stderr, returncode = run_bash_command(
        "file-processing",
       f'"{output_file}" "{log_file}" "{mock_test_data}"',
        solve_sh_path
    )
    assert returncode == 0
    log = extract_json_from_output(stdout)
    assert os.path.exists(output_file)

    operations = [op["operation"] for op in log["operations"]]
        
        # Should contain key operations
    assert "fill_missing_numeric" in operations

    details = [op for op in log["operations"] if op["operation"] == "fill_missing_numeric"][0]["details"]
    assert details["column"] == "product_price"
    assert details["fill_value"] is not None or details["fill_value"] != ""
    # # Basic check on cleaned file
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert "product_price" in headers
        empty_data_idx = headers.index("product_price")
        next(reader)
        next(reader)
        third_row = next(reader)
        # test the value in the first data row
        assert third_row[empty_data_idx] is not None or details["fill_value"] != ""

    # os.remove(output_file)
    # os.remove(log_file)


def test_get_unknown_for_missing(mock_test_data_two, solve_sh_path):
    """Test to replace missing categorical values with 'Unknown'"""
    output_file = os.path.join(TEST_DIR, 'output.csv')
    log_file = os.path.join(TEST_DIR, "log.json")
    if os.path.exists(output_file):
        os.remove(output_file)
    with open(mock_test_data_two, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert "Supplier" in headers
        empty_data_idx = headers.index("Supplier")
        # test the value in the first data row
        first_row = next(reader)
        assert first_row[empty_data_idx] == ""
    
    stdout, stderr, returncode = run_bash_command(
        "file-processing",
       f'"{output_file}" "{log_file}" "{mock_test_data_two}"',
        solve_sh_path
    )
    assert returncode == 0
    log = extract_json_from_output(stdout)
    assert os.path.exists(output_file)

    operations = [op["operation"] for op in log["operations"]]
        
        # Should contain key operations
    assert "fill_missing_categorical" in operations

    details = [op for op in log["operations"] if op["operation"] == "fill_missing_categorical"][0]["details"]
    assert details["column"] == "supplier"
    assert details["fill_value"] == "Unknown"
    # # Basic check on cleaned file
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        headers = [h.strip().lower().replace(" ", "_") for h in headers]
        assert "supplier" in headers
        empty_data_idx = headers.index("supplier")
        first_row = next(reader)
        assert first_row[empty_data_idx] == "Unknown"

    os.remove(output_file)
    os.remove(log_file)


#=============================================================================
# Test Get Cleaning Log
#=============================================================================
def test_get_cleaning_log(mock_test_data, solve_sh_path):
        """Test retrieval of cleaning log"""
        output_file = os.path.join(TEST_DIR, "output.csv")
        log_file = os.path.join(TEST_DIR, "log.json")
        
        # First, run processing to generate log
        stdout, stderr, returncode = run_bash_command(
            "file-processing",
            f'"{output_file}" "{log_file}" "{mock_test_data}"',
            solve_sh_path
        )
        assert returncode == 0
        
        # Now, get cleaning log
        stdout, stderr, returncode = run_bash_command(
            "cleaning-log",
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
        fake_log_file = os.path.join(TEST_DIR, "nonexistent_log.json")
        
        stdout, stderr, returncode = run_bash_command(
            "cleaning-log",
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
# Full Integration of multiple components
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
    output_file = os.path.join(TEST_DIR, "final.csv")
    log_file = os.path.join(TEST_DIR, "final_log.json")
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