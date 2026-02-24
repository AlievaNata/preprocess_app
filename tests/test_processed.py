def test_processed_endpoint(client):
    csv = (
        "Timestamp,Machine_ID,Operation_Mode,Temperature_C,Vibration_Hz,"
        "Power_Consumption_kW,Network_Latency_ms,Packet_Loss_%,"
        "Quality_Control_Defect_Rate_%,Production_Speed_units_per_hr,"
        "Predictive_Maintenance_Score,Error_Rate_%,Efficiency_Status\n"
        "2024-01-01 00:00:00,1,Active,50,10,5,2,0.1,0.2,100,0.8,0.05,Normal"
    )

    client.post("/load_csv", files={"file": ("test.csv", csv, "text/csv")})
    client.post("/preprocess")

    response = client.get("/processed")

    assert response.status_code == 200
    data = response.json()
    assert "rows" in data
    assert data["rows"] >= 1
