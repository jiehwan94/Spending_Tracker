import pandas as pd

# Read the Excel file
excel_file = 'data/transactions.xlsx'

# Get sheet names
xls = pd.ExcelFile(excel_file)
print("Sheet names:", xls.sheet_names)

# Read the "변동비" sheet
df = pd.read_excel(excel_file, sheet_name="변동비")
print("\nData shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())
print("\nData types:")
print(df.dtypes) 