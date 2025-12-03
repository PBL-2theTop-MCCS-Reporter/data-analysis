import pandas as pd

# Read CSV file
df = pd.read_csv('output.csv')

# Display first few rows to verify
print(df.head(20))

# Display basic information about the dataset
print("\nDataset Info:")
print(df.info())