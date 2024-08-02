import pandas as pd

df = pd.read_csv('/Users/andres/Library/CloudStorage/GoogleDrive-aguilarcarboni@gmail.com/My Drive/Personal/Wallet/Statements/BAC/Cash/Budget.csv')
df1 = pd.read_csv('/Users/andres/Library/CloudStorage/GoogleDrive-aguilarcarboni@gmail.com/My Drive/Personal/Wallet/Statements/BAC/Cash/Processed/072024.csv')

categories = df1['Category'].unique()

for cateogry in categories:
    df2 = df1[df1['Category'] == cateogry]
    print(f'{cateogry}: {df2["Total"].sum()}')