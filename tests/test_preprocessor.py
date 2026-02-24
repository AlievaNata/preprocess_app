import pandas as pd
from src.preprocessing.DataPreprocessor import DataPreprocessor


def test_preprocessor_pipeline():
    df = pd.DataFrame({
        "Temperature_C": [10, 20, 1000],  # выброс
        "Vibration_Hz": [5, 6, 7],
        "Operation_Mode": ["Active", "Idle", "Active"],
        "Efficiency_Status": ["Normal", "Normal", "Low"]
    })

    processor = DataPreprocessor(targetColumn="Efficiency_Status")
    processor.LoadData(df)
    processor.RemoveOutliersAllNumeric()
    processor.FillMissing()
    processor.NormalizeNumeric()
    processor.EncodeCategorical()

    result = processor.GetPreparedDataset()

    assert "Temperature_C" in result.columns
    assert result["Temperature_C"].max() <= 1
    assert result["Temperature_C"].min() >= 0
    assert result["Operation_Mode"].dtype != object
