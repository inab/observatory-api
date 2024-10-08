from pydantic import BaseModel
from typing import List

class FAIRscores(BaseModel):
    F: float = 0.0
    F1: float = 0.0
    F2: float = 0.0
    F3: float = 0.0
    A: float = 0.0
    A1: float = 0.0
    A2: float = 0.0
    A3: float = 0.0
    I: float = 0.0
    I1: float = 0.0
    I2: float = 0.0
    I3: float = 0.0
    R: float = 0.0
    R1: float = 0.0
    R2: float = 0.0
    R3: float = 0.0
    R4: float = 0.0


class FAIRmetrics(BaseModel):
    F1_1: bool = False
    F1_2: bool = False
    F2_1: bool = False
    F2_2: bool = False
    F3_1: bool = False
    F3_2: bool = False
    F3_3: bool = False
    A1_1: bool = False
    A1_2: bool = False
    A1_3: bool = False
    A1_4: bool = False
    A1_5: bool = False
    A2_1: bool = False
    A2_2: bool = False
    A3_1: bool = False
    A3_2: bool = False
    A3_3: bool = False
    A3_4: bool = False
    A3_5: bool = False
    I1_1: bool = False
    I1_2: bool = False
    I1_3: bool = False
    I1_4: bool = False
    I1_5: bool = False
    I2_1: bool = False
    I2_2: bool = False
    I3_1: bool = False
    I3_2: bool = False
    I3_3: bool = False
    R1_1: bool = False
    R1_2: bool = False
    R2_1: bool = False
    R2_2: bool = False
    R3_1: bool = False
    R3_2: bool = False
    R4_1: bool = False
    R4_2: bool = False
    R4_3: bool = False

class FAIRLogs(BaseModel):
    # Each log entry is a list of strings
    F1_1: List[str] = []
    F1_2: List[str] = []
    F2_1: List[str] = []
    F2_2: List[str] = []
    F3_1: List[str] = []
    F3_2: List[str] = []
    F3_3: List[str] = []
    A1_1: List[str] = []
    A1_2: List[str] = []
    A1_3: List[str] = []
    A1_4: List[str] = []
    A1_5: List[str] = []
    A2_1: List[str] = []
    A2_2: List[str] = []
    A3_1: List[str] = []
    A3_2: List[str] = []
    A3_3: List[str] = []
    A3_4: List[str] = []
    A3_5: List[str] = []
    I1_1: List[str] = []
    I1_2: List[str] = []
    I1_3: List[str] = []
    I1_4: List[str] = []
    I1_5: List[str] = []
    I2_1: List[str] = []
    I2_2: List[str] = []
    I3_1: List[str] = []
    I3_2: List[str] = []
    I3_3: List[str] = []
    R1_1: List[str] = []
    R1_2: List[str] = []
    R2_1: List[str] = []
    R2_2: List[str] = []
    R3_1: List[str] = []
    R3_2: List[str] = []
    R4_1: List[str] = []
    R4_2: List[str] = []
    R4_3: List[str] = []
 