from data_analysis import calculate_average
import pandas as pd

def test_calculate_average():
    data = {
        "Diet_type": ["Vegan", "Vegan"],
        "Protein(g)": [10, 20],
        "Carbs(g)": [30, 40],
        "Fat(g)": [5, 10]
    }

    df = pd.DataFrame(data)
    result = calculate_average(df)

    assert result["Protein(g)"]["Vegan"] == 15
