#!/usr/bin/env python3
"""
Generate three dummy CSV files with messy data for testing the CSV cleaner
"""

import csv
import random
from datetime import datetime, timedelta

def generate_sales_data():
    """Generate messy sales data with inconsistent naming and formats"""
    
    # Inconsistent column names with spaces, special characters, capitals
    headers = ['Order ID', 'Customer Name', 'Order Date', 'Product Price $', 
               'Quantity!!', 'Total Amount', 'Ship Date', 'Status']
    
    statuses = ['Shipped', 'Pending', 'Delivered', None, 'Cancelled', '']
    products = ['Widget', 'Gadget', 'Doohickey', 'Thingamajig']
    names = ['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Williams', None, '']
    
    rows = []
    base_date = datetime(2023, 1, 1)
    
    for i in range(150):
        order_id = f'ORD{1000 + i}'
        customer = random.choice(names)
        
        # Various date formats
        order_date_obj = base_date + timedelta(days=random.randint(0, 365))
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d', '%d.%m.%Y']
        order_date = order_date_obj.strftime(random.choice(formats)) if random.random() > 0.05 else ''
        
        # Prices with outliers
        if random.random() < 0.02:  # 2% extreme outliers
            price = random.uniform(5000, 10000)
        else:
            price = random.uniform(10, 500)
        
        quantity = random.randint(1, 20) if random.random() > 0.05 else None
        total = price * (quantity if quantity else 0)
        
        ship_date_obj = order_date_obj + timedelta(days=random.randint(1, 10))
        ship_date = ship_date_obj.strftime(random.choice(formats)) if random.random() > 0.1 else None
        
        status = random.choice(statuses)
        
        rows.append([order_id, customer, order_date, price, quantity, total, ship_date, status])
    
    # Write CSV
    with open('sales_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print("✓ Generated sales_data.csv (150 rows)")


def generate_employee_data():
    """Generate messy employee data with different encoding and schema"""
    
    # Different column naming convention
    headers = ['EMP_ID', 'Full Name', 'hire-date', 'Department Name', 
               'Annual_Salary', 'Performance Score', 'Email Address']
    
    departments = ['Sales', 'Engineering', 'Marketing', None, 'HR', 'Finance', '']
    first_names = ['Michael', 'Sarah', 'David', 'Emma', 'James', 'Olivia']
    last_names = ['Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor']
    
    rows = []
    base_date = datetime(2015, 1, 1)
    
    for i in range(100):
        emp_id = f'E{2000 + i}'
        
        # Some missing names
        if random.random() > 0.05:
            full_name = f'{random.choice(first_names)} {random.choice(last_names)}'
        else:
            full_name = None
        
        # Different date formats
        hire_date_obj = base_date + timedelta(days=random.randint(0, 3000))
        formats = ['%Y-%m-%d', '%m/%d/%y', '%d/%m/%Y', '%Y.%m.%d']
        hire_date = hire_date_obj.strftime(random.choice(formats)) if random.random() > 0.03 else ''
        
        department = random.choice(departments)
        
        # Salaries with outliers
        if random.random() < 0.03:  # 3% extreme outliers
            salary = random.uniform(500000, 1000000)
        else:
            salary = random.uniform(40000, 150000)
        
        # Performance scores 1-10 with some missing
        perf_score = random.randint(1, 10) if random.random() > 0.08 else None
        
        email = f'{full_name.lower().replace(" ", ".")}@company.com' if full_name else ''
        
        rows.append([emp_id, full_name, hire_date, department, salary, perf_score, email])
    
    # Write CSV with latin-1 encoding to test encoding detection
    with open('employee_data.csv', 'w', newline='', encoding='latin-1') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print("✓ Generated employee_data.csv (100 rows, latin-1 encoding)")


def generate_inventory_data():
    """Generate messy inventory data with yet another schema"""
    
    # More inconsistent naming
    headers = ['SKU#', 'Product  Name', 'stock_qty', 'Unit Cost ($)', 
               'Last Restock', 'Supplier', 'Category Type']
    
    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Desk', 'Chair', 'Headphones']
    suppliers = ['TechCorp', 'OfficeSupply Inc', 'GlobalTech', None, 'MegaStore', '']
    categories = ['Electronics', 'Furniture', 'Accessories', None, '']
    
    rows = []
    base_date = datetime(2024, 1, 1)
    
    for i in range(80):
        sku = f'SKU-{3000 + i}'
        product = random.choice(products) if random.random() > 0.02 else None
        
        # Stock quantities with outliers
        if random.random() < 0.02:
            stock = random.randint(5000, 20000)  # Outlier
        else:
            stock = random.randint(0, 500)
        
        # Unit costs with outliers
        if random.random() < 0.02:
            cost = random.uniform(5000, 15000)  # Outlier
        else:
            cost = random.uniform(5, 2000)
        
        # Various date formats
        restock_date_obj = base_date + timedelta(days=random.randint(-180, 0))
        formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%Y/%m/%d']
        restock_date = restock_date_obj.strftime(random.choice(formats)) if random.random() > 0.1 else ''
        
        supplier = random.choice(suppliers)
        category = random.choice(categories)
        
        rows.append([sku, product, stock, cost, restock_date, supplier, category])
    
    # Write CSV
    with open('inventory_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print("✓ Generated inventory_data.csv (80 rows)")


def main():
    print("Generating test CSV files with messy data...")
    print()
    
    generate_sales_data()
    generate_employee_data()
    generate_inventory_data()
    
    print()
    print("All files generated successfully!")
    print()
    print("Test these files with:")
    print("  python csv_cleaner.py sales_data.csv employee_data.csv inventory_data.csv")
    print()
    print("Issues in the files:")
    print("  • Inconsistent column naming (spaces, special chars, mixed case)")
    print("  • Multiple date formats (YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY, etc.)")
    print("  • Missing values in multiple columns")
    print("  • Numeric outliers (extreme high values)")
    print("  • Different file encodings (UTF-8 and Latin-1)")
    print("  • Empty strings vs NULL values")


if __name__ == '__main__':
    main()