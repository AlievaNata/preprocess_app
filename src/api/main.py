from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
import pandas as pd

from src.preprocessing.DataPreprocessor import DataPreprocessor
from src.database import get_db
from src.models_db import RawRecord, ProcessedRecord
import src.database as db_module
from src.database import engine, Base
print(">>> MAIN Base ID:", id(db_module.Base))

app = FastAPI(
    title="Data Preprocessing Subsystem",
    description="Сервис предобработки данных для интеллектуального производства",
    version="1.0"
)

@app.on_event("startup") 
def on_startup(): 
    Base.metadata.create_all(bind=engine)

processor = DataPreprocessor(targetColumn="Efficiency_Status")


@app.post("/load_csv")
async def load_csv(file: UploadFile = File(...), db=Depends(get_db)):

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Файл должен быть CSV")

    contents = await file.read()

    try:
        df = pd.read_csv(pd.io.common.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Ошибка чтения CSV")

    db.query(RawRecord).delete()
    db.commit()

    for _, row in df.iterrows():
        db.add(RawRecord(
            Timestamp=row["Timestamp"],
            Machine_ID=row["Machine_ID"],
            Operation_Mode=row["Operation_Mode"],
            Temperature_C=row["Temperature_C"],
            Vibration_Hz=row["Vibration_Hz"],
            Power_Consumption_kW=row["Power_Consumption_kW"],
            Network_Latency_ms=row["Network_Latency_ms"],
            Packet_Loss=row["Packet_Loss_%"],
            Quality_Control_Defect_Rate=row["Quality_Control_Defect_Rate_%"],
            Production_Speed_units_per_hr=row["Production_Speed_units_per_hr"],
            Predictive_Maintenance_Score=row["Predictive_Maintenance_Score"],
            Error_Rate=row["Error_Rate_%"],
            Efficiency_Status=row["Efficiency_Status"]
        ))

    db.commit()
    return {"status": "ok", "rows_loaded": len(df)}


@app.post("/preprocess")
def preprocess(db=Depends(get_db)):

    raw_rows = db.query(RawRecord).all()

    if not raw_rows:
        raise HTTPException(status_code=400, detail="В таблице raw_data нет данных")

    df = pd.DataFrame([{
        "Timestamp": r.Timestamp,
        "Machine_ID": r.Machine_ID,
        "Operation_Mode": r.Operation_Mode,
        "Temperature_C": r.Temperature_C,
        "Vibration_Hz": r.Vibration_Hz,
        "Power_Consumption_kW": r.Power_Consumption_kW,
        "Network_Latency_ms": r.Network_Latency_ms,
        "Packet_Loss_%": r.Packet_Loss,
        "Quality_Control_Defect_Rate_%": r.Quality_Control_Defect_Rate,
        "Production_Speed_units_per_hr": r.Production_Speed_units_per_hr,
        "Predictive_Maintenance_Score": r.Predictive_Maintenance_Score,
        "Error_Rate_%": r.Error_Rate,
        "Efficiency_Status": r.Efficiency_Status
    } for r in raw_rows])

    processor.LoadData(df)
    processor.RemoveOutliersAllNumeric()
    processor.FillMissing()
    processor.NormalizeNumeric()
    processor.EncodeCategorical()

    processed = processor.GetPreparedDataset()

    # Переименовываем колонки под модель ProcessedRecord
    processed = processed.rename(columns={
        "Packet_Loss_%": "Packet_Loss",
        "Quality_Control_Defect_Rate_%": "Quality_Control_Defect_Rate",
        "Error_Rate_%": "Error_Rate"
    })

    if processed.empty:
        raise HTTPException(status_code=500, detail="Предобработка вернула пустой набор данных")

    db.query(ProcessedRecord).delete()
    db.commit()

    for _, row in processed.iterrows():
        db.add(ProcessedRecord(**row.to_dict()))

    db.commit()


    return {
        "rows": len(processed),
        "columns": list(processed.columns),
        "preview": processed.head(20).to_dict(orient="records")
    }


@app.get("/processed")
def get_processed(db=Depends(get_db)):

    rows = db.query(ProcessedRecord).all()

    data = [{
        "Timestamp": r.Timestamp,
        "Machine_ID": r.Machine_ID,
        "Operation_Mode": r.Operation_Mode,
        "Temperature_C": r.Temperature_C,
        "Vibration_Hz": r.Vibration_Hz,
        "Power_Consumption_kW": r.Power_Consumption_kW,
        "Network_Latency_ms": r.Network_Latency_ms,
        "Packet_Loss": r.Packet_Loss,
        "Quality_Control_Defect_Rate": r.Quality_Control_Defect_Rate,
        "Production_Speed_units_per_hr": r.Production_Speed_units_per_hr,
        "Predictive_Maintenance_Score": r.Predictive_Maintenance_Score,
        "Error_Rate": r.Error_Rate,
        "Efficiency_Status": r.Efficiency_Status
    } for r in rows]

    return {
        "rows": len(data),
        "preview": data[:20]
    }
