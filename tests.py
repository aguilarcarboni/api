import pandas as pd

df = pd.read_csv('/Users/andres/Library/CloudStorage/GoogleDrive-aguilarcarboni@gmail.com/My Drive/Personal/Wallet/Statements/BAC/Cash/Budget.csv')
df1 = pd.read_csv('/Users/andres/Library/CloudStorage/GoogleDrive-aguilarcarboni@gmail.com/My Drive/Personal/Wallet/Statements/BAC/Cash/Processed/072024.csv')

categories = df1['Category'].unique()

expensesPerCategory = []
for cateogry in categories:
    expenseDict = {}
    df2 = df1[df1['Category'] == cateogry]
    df2 = df2[df2['Q'] == 'Q2']
    expenseDict = ({'cateogry':cateogry, 'amount':df2["Total"].sum()})
    expensesPerCategory.append(expenseDict)

df3 = pd.DataFrame(expensesPerCategory)
print(df3)
df3.to_csv('test.csv', index=False)