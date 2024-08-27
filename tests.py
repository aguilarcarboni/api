import pandas as pd

def categorize_transactions(df):
    # Define categories
    expense_categories = ['Food', 'Misc', 'Subscriptions', 'Transportation', 'Savings']
    income_categories = ['Misc', 'Income', 'Savings']
    
    # Initialize dictionaries to store categorized transactions
    categorized_expenses = {cat: [] for cat in expense_categories}
    categorized_income = {cat: [] for cat in income_categories}
    
    # Categorize transactions
    for _, row in df.iterrows():
        amount = row['Total']
        category = row['Category']
        
        if amount < 0:  # Expense
            if category in expense_categories:
                categorized_expenses[category].append(row)
            else:
                categorized_expenses['Misc'].append(row)
        else:  # Income
            if category in income_categories:
                categorized_income[category].append(row)
            else:
                categorized_income['Misc'].append(row)
    
    # Convert lists to DataFrames
    for cat in expense_categories:
        categorized_expenses[cat] = pd.DataFrame(categorized_expenses[cat])
    for cat in income_categories:
        categorized_income[cat] = pd.DataFrame(categorized_income[cat])
    
    return categorized_expenses, categorized_income

# Read CSV files
df_budget = pd.read_csv('/Users/andres/Library/CloudStorage/GoogleDrive-aguilarcarboni@gmail.com/My Drive/Personal/Wallet/Statements/BAC/Cash/Budget.csv')
df_processed = pd.read_csv('/Users/andres/Library/CloudStorage/GoogleDrive-aguilarcarboni@gmail.com/My Drive/Personal/Wallet/Statements/BAC/Cash/Processed/072024.csv')

# Categorize transactions
categorized_expenses, categorized_income = categorize_transactions(df_processed)


"""
# Print results
print("Expenses:")
for category, df in categorized_expenses.items():
    print(f"\n{category}:")
    print(df)

print("\nIncome:")
for category, df in categorized_income.items():
    print(f"\n{category}:")
    print(df)
"""

print('Total income:', categorized_income['Income']['Total'].sum())
print('\n')
print('Savings: ', categorized_income['Savings']['Total'].sum() + categorized_expenses['Savings']['Total'].sum())
print('\n')
print('Miscellaneous Expenses: ', categorized_income['Misc']['Total'].sum() + categorized_expenses['Misc']['Total'].sum())
print('Transportation Expenses: ', categorized_expenses['Transportation']['Total'].sum())
print('Food Expenses: ', categorized_expenses['Food']['Total'].sum())
print('Subscriptions Expenses: ', categorized_expenses['Subscriptions']['Total'].sum())