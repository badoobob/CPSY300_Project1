import pandas as pd

def calculate_average(df):
    """
    Calculate average macronutrients per diet type.
    """
    return df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean()

if __name__ == "__main__":
    print("Data analysis container executed successfully.") 