import pandas as pd

df = pd.read_csv('/Users/andres/Library/CloudStorage/GoogleDrive-aguilarcarboni@gmail.com/My Drive/Personal/Wallet/Budget.csv')
df1 = pd.read_csv('/Users/andres/Library/CloudStorage/GoogleDrive-aguilarcarboni@gmail.com/My Drive/Personal/Wallet/Statements/BAC/Cash/20240716215625.csv')

categories = ['Savings']

for cateogry in categories:
    df2 = df1[df1['Category'] == cateogry]
    print(cateogry, df2['Debit'].sum(), df2['Credit'].sum())