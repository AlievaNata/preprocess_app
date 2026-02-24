import numpy as np
import pandas as pd
from typing import Optional, Dict


class DataPreprocessor:

    def __init__(self, targetColumn: str = "Efficiency_Status"):
        self.rawData: Optional[pd.DataFrame] = None
        self.cleanedData: Optional[pd.DataFrame] = None
        self.targetColumn = targetColumn
        self.operationModeMap: Dict[str, int] = {}

    # -----------------------------
    # Загрузка данных
    # -----------------------------
    def LoadData(self, data: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Ожидался pandas.DataFrame")
        self.rawData = data.copy()
        self.cleanedData = data.copy()
        return self.rawData

    # -----------------------------
    # Удаление выбросов по числовым колонкам
    # (вторая версия + защита из первой)
    # -----------------------------
    def RemoveOutliersAllNumeric(self, threshold: float = 1.5) -> pd.DataFrame:
        if self.cleanedData is None:
            raise RuntimeError("Данные не загружены")

        df = self.cleanedData.copy()
        numericCols = df.select_dtypes(include=[np.number]).columns

        if len(numericCols) == 0:
            self.cleanedData = df
            return df

        # Вычисляем IQR для каждого числового столбца
        Q1 = df[numericCols].quantile(0.25)
        Q3 = df[numericCols].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR

        # Маска: строка остаётся, если ВСЕ числовые значения в пределах IQR
        mask = ~((df[numericCols] < lower_bound) | (df[numericCols] > upper_bound)).any(axis=1)

        # Если ВСЕ строки выбросы — НЕ удаляем ничего
        if mask.sum() == 0:
            self.cleanedData = df
            return df

        self.cleanedData = df[mask].copy()
        return self.cleanedData


    # -----------------------------
    # Заполнение пропусков
    # (вторая версия)
    # -----------------------------
    def FillMissing(self, method: str = "mean") -> pd.DataFrame:
        if self.cleanedData is None:
            raise RuntimeError("Нет данных для заполнения пропусков")

        df = self.cleanedData.copy()

        numericCols = df.select_dtypes(include=[np.number]).columns
        categoricalCols = df.select_dtypes(exclude=[np.number]).columns

        # Числовые признаки
        df[numericCols] = df[numericCols].fillna(df[numericCols].mean())

        # Категориальные признаки — ВСЕ
        for col in categoricalCols:
            modeValue = df[col].mode(dropna=True)
            if not modeValue.empty:
                df[col] = df[col].fillna(modeValue.iloc[0])

        self.cleanedData = df
        return df

    # -----------------------------
    # Нормализация числовых признаков
    # (вторая версия)
    # -----------------------------
    def NormalizeNumeric(self) -> pd.DataFrame:
        if self.cleanedData is None:
            raise RuntimeError("Нет данных для нормализации")

        df = self.cleanedData.copy()
        numericCols = df.select_dtypes(include=[np.number]).columns

        # НЕ нормализуем Operation_Mode и Efficiency_Status
        numericCols = [
            c for c in numericCols
            if c not in ["Operation_Mode", self.targetColumn]
        ]

        for col in numericCols:
            colMin = df[col].min()
            colMax = df[col].max()
            if colMax == colMin:
                df[col] = 0.0
            else:
                df[col] = (df[col] - colMin) / (colMax - colMin)

        self.cleanedData = df
        return df

    # -----------------------------
    # Кодирование категориальных признаков
    # (вторая версия + sorted)
    # -----------------------------
    def EncodeCategorical(self) -> pd.DataFrame:
        if self.cleanedData is None:
            raise RuntimeError("Нет данных для кодирования")

        df = self.cleanedData.copy()

        if "Operation_Mode" in df.columns:
            if not self.operationModeMap:
                uniqueModes = sorted(df["Operation_Mode"].unique())
                self.operationModeMap = {mode: idx for idx, mode in enumerate(uniqueModes)}

            df["Operation_Mode"] = df["Operation_Mode"].map(self.operationModeMap)

        self.cleanedData = df
        return df

    # -----------------------------
    # Итоговый датасет
    # -----------------------------
    def GetPreparedDataset(self) -> pd.DataFrame:
        if self.cleanedData is None:
            raise RuntimeError("Данные ещё не были обработаны")
        return self.cleanedData.copy()
