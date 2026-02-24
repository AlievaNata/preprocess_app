import io
import pandas as pd


def test_load_csv_success(client):
    df = pd.DataFrame({
        "Timestamp": ["2024-01-01 00:00:00"],
        "Machine_ID": [1],
        "Operation_Mode": ["Active"],
        "Temperature_C": [50],
        "Vibration_Hz": [10],
        "Power_Consumption_kW": [5],
        "Network_Latency_ms": [2],
        "Packet_Loss_%": [0.1],
        "Quality_Control_Defect_Rate_%": [0.2],
        "Production_Speed_units_per_hr": [100],
        "Predictive_Maintenance_Score": [0.8],
        "Error_Rate_%": [0.05],
        "Efficiency_Status": ["Normal"]
    })

    file_bytes = io.BytesIO()
    df.to_csv(file_bytes, index=False)
    file_bytes.seek(0)

    response = client.post(
        "/load_csv",
        files={"file": ("test.csv", file_bytes, "text/csv")}
    )

    assert response.status_code == 200
    assert response.json()["rows_loaded"] == 1
