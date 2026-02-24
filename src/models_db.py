from sqlalchemy import Column, Integer, String, Float
from src.database import Base
import src.database as db_module
print(">>> MODELS Base ID:", id(db_module.Base))


class RawRecord(Base):
    __tablename__ = "raw_data"

    id = Column(Integer, primary_key=True, index=True)

    Timestamp = Column(String)
    Machine_ID = Column(Float)
    Operation_Mode = Column(String)
    Temperature_C = Column(Float)
    Vibration_Hz = Column(Float)
    Power_Consumption_kW = Column(Float)
    Network_Latency_ms = Column(Float)
    Packet_Loss = Column(Float)
    Quality_Control_Defect_Rate = Column(Float)
    Production_Speed_units_per_hr = Column(Float)
    Predictive_Maintenance_Score = Column(Float)
    Error_Rate = Column(Float)
    Efficiency_Status = Column(String)


class ProcessedRecord(Base):
    __tablename__ = "processed_data"

    id = Column(Integer, primary_key=True, index=True)

    Timestamp = Column(String)
    Machine_ID = Column(Float)
    Operation_Mode = Column(Integer)
    Temperature_C = Column(Float)
    Vibration_Hz = Column(Float)
    Power_Consumption_kW = Column(Float)
    Network_Latency_ms = Column(Float)
    Packet_Loss = Column(Float)
    Quality_Control_Defect_Rate = Column(Float)
    Production_Speed_units_per_hr = Column(Float)
    Predictive_Maintenance_Score = Column(Float)
    Error_Rate = Column(Float)
    Efficiency_Status = Column(String)
