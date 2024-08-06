from app.models.fair_metrics import FAIRmetrics, FAIRLogs
from app.services.f_indicators import *
from app.services.a_indicators import *
from app.services.i_indicators import *
from app.services.r_indicators import *

class IndicatorComputation:
    def __init__(self, instance):
        self.instance = instance
        self.instance.metrics = FAIRmetrics()  # Initialize metrics in the instance
        self.instance.logs = FAIRLogs()  # Initialize logs in the instance

    def compute_indicators(self):
        self.compute_findability()
        self.compute_accessibility()
        self.compute_interoperability()
        self.compute_reusability()
        return self.instance.metrics, self.instance.logs  # Return the instance metrics and logs

    def compute_findability(self):
        self.instance.metrics.F1_1, self.instance.logs.F1_1 = True, ["The metadata is assigned a name to be identified."]
        self.instance.metrics.F1_2, self.instance.logs.F1_2 = compF1_2(self.instance)
        self.instance.metrics.F2_1, self.instance.logs.F2_1 = compF2_1(self.instance)
        self.instance.metrics.F2_2, self.instance.logs.F2_2 = compF2_2(self.instance)
        self.instance.metrics.F3_1, self.instance.logs.F3_1 = compF3_1(self.instance)
        self.instance.metrics.F3_2, self.instance.logs.F3_2 = compF3_2(self.instance)
        self.instance.metrics.F3_3, self.instance.logs.F3_3 = compF3_3(self.instance)

    def compute_accessibility(self):
        self.instance.metrics.A1_1, self.instance.logs.A1_1 = compA1_1(self.instance)
        self.instance.metrics.A1_2, self.instance.logs.A1_2 = compA1_2(self.instance)
        self.instance.metrics.A1_3, self.instance.logs.A1_3 = compA1_3(self.instance)
        self.instance.metrics.A1_4, self.instance.logs.A1_4 = compA1_4(self.instance)
        self.instance.metrics.A1_5, self.instance.logs.A1_5 = compA1_5(self.instance)
        self.instance.metrics.A2_1, self.instance.logs.A2_1 = False, ["This indicator is currently not measured."]
        self.instance.metrics.A2_2, self.instance.logs.A2_2 = False, ["This indicator is currently not measured."]
        self.instance.metrics.A3_1, self.instance.logs.A3_1 = compA3_1(self.instance)
        self.instance.metrics.A3_2, self.instance.logs.A3_2 = compA3_2(self.instance)
        self.instance.metrics.A3_3, self.instance.logs.A3_3 = compA3_3(self.instance)
        self.instance.metrics.A3_4, self.instance.logs.A3_4 = compA3_4(self.instance)
        self.instance.metrics.A3_5, self.instance.logs.A3_5 = compA3_5(self.instance)

    def compute_interoperability(self):
        self.instance.metrics.I1_1, self.instance.logs.I1_1 = compI1_1(self.instance)
        self.instance.metrics.I1_2, self.instance.logs.I1_2 = compI1_2(self.instance)
        self.instance.metrics.I1_3, self.instance.logs.I1_3 = compI1_3(self.instance)
        self.instance.metrics.I1_4, self.instance.logs.I1_4 = compI1_4(self.instance)
        self.instance.metrics.I1_5, self.instance.logs.I1_5 = False, ["This indicator is currently not measured."]
        self.instance.metrics.I2_1, self.instance.logs.I2_1 = compI2_1(self.instance)
        self.instance.metrics.I2_2, self.instance.logs.I2_2 = compI2_2(self.instance)
        self.instance.metrics.I3_1, self.instance.logs.I3_1 = compI3_1(self.instance)
        self.instance.metrics.I3_2, self.instance.logs.I3_2 = compI3_2(self.instance)
        self.instance.metrics.I3_3, self.instance.logs.I3_3 = compI3_3(self.instance)

    def compute_reusability(self):
        self.instance.metrics.R1_1, self.instance.logs.R1_1 = compR1_1(self.instance)
        self.instance.metrics.R1_2, self.instance.logs.R1_2 = False, ["This indicator is currently not measured."]
        self.instance.metrics.R2_1, self.instance.logs.R2_1 = compR2_1(self.instance)
        self.instance.metrics.R2_2, self.instance.logs.R2_2 = compR2_2(self.instance)
        self.instance.metrics.R3_1, self.instance.logs.R3_1 = compR3_1(self.instance)
        self.instance.metrics.R3_2, self.instance.logs.R3_2 = compR3_2(self.instance)
        self.instance.metrics.R4_1, self.instance.logs.R4_1 = compR4_1(self.instance)
        self.instance.metrics.R4_2, self.instance.logs.R4_2 = compR4_2(self.instance)
        self.instance.metrics.R4_3, self.instance.logs.R4_3 = False, ["This indicator is currently not measured."]
