from app.models.instance import Instance
from app.models.fair_metrics import FAIRmetrics, FAIRscores

def compute_fair_scores(instance: Instance) -> dict:
    instance.scores = FAIRscores()
    
    # Compute Findability Scores
    instance.scores.F1 = (0.8 * instance.metrics.F1_1 + 0.2 * instance.metrics.F1_2)
    instance.scores.F2 = 0.6 * instance.metrics.F2_1 + 0.4 * instance.metrics.F2_2
    
    acc = [instance.metrics.F3_1, instance.metrics.F3_2, instance.metrics.F3_3].count(True)
    if acc == 1:
        instance.scores.F3 = 0.7
    elif acc == 2:
        instance.scores.F3 = 0.85
    elif acc == 3:
        instance.scores.F3 = 1
    
    instance.scores.F = (0.4 * instance.scores.F1 + 0.2 * instance.scores.F2 + 0.4 * instance.scores.F3)
    
    # Compute Accessibility Scores
    if instance.super_type == 'web':
        instance.scores.A1 = (0.6 * instance.metrics.A1_1 + 0.4 * instance.metrics.A1_4)
        instance.scores.A3 = 1.0 * instance.metrics.A3_1
    else:
        # print the instance.metrics.A1_2, instance.metrics.A1_3, instance.metrics.A1_4, instance.metrics.A1_5
        print('Accessiblity 1:')
        print(instance.metrics.A1_2, instance.metrics.A1_3, instance.metrics.A1_4, instance.metrics.A1_5)
        instance.scores.A1 = (0.5 * instance.metrics.A1_2 + 0.2 * instance.metrics.A1_3 + 0.1 * instance.metrics.A1_4 + 0.2 * instance.metrics.A1_5)
        instance.scores.A3 = (1 / 4) * (instance.metrics.A3_2 + instance.metrics.A3_3 + instance.metrics.A3_4 + instance.metrics.A3_5)
    
    instance.scores.A = (0.7 * instance.scores.A1 + 0.3 * instance.scores.A3)
    
    # Compute Interoperability Scores
    instance.scores.I1 = (0.5 * instance.metrics.I1_1 + 0.3 * instance.metrics.I1_2 + 0.3 * instance.metrics.I1_3 + 0.2 * instance.metrics.I1_4)
    instance.scores.I2 = (0.5 * instance.metrics.I2_1 + 0.5 * instance.metrics.I2_2)
    instance.scores.I3 = (1 / 3) * (instance.metrics.I3_1 + instance.metrics.I3_2 + instance.metrics.I3_3)
    instance.scores.I = (0.6 * instance.scores.I1 + 0.1 * instance.scores.I2 + 0.3 * instance.scores.I3)
    
    # Compute Reusability Scores
    instance.scores.R1 = 1.0 * instance.metrics.R1_1
    if instance.metrics.R2_1:
        instance.scores.R2 = 1.0
    elif instance.metrics.R2_2:
        instance.scores.R2 = 1.0
    else:
        instance.scores.R2 = 0.0
    
    instance.scores.R3 = 1.0 * instance.metrics.R3_2
    instance.scores.R4 = 1.0 * instance.metrics.R4_1
    instance.scores.R = (0.3 * instance.scores.R1 + 0.3 * instance.scores.R2 + 0.2 * instance.scores.R3 + 0.2 * instance.scores.R4)
    
    # Prepare the result dictionary
    result = {
        "name": instance.name,
        "type": instance.type,
        "version": instance.version,
        "F": instance.scores.F,
        "F1": instance.scores.F1,
        "F1_1": instance.metrics.F1_1,
        "F1_2": instance.metrics.F1_2,
        "F2": instance.scores.F2,
        "F2_1": instance.metrics.F2_1,
        "F2_2": instance.metrics.F2_2,
        "F3": instance.scores.F3,
        "F3_1": instance.metrics.F3_1,
        "F3_2": instance.metrics.F3_2,
        "F3_3": instance.metrics.F3_3,
        "A": instance.scores.A,
        "A1": instance.scores.A1,
        "A1_1": instance.metrics.A1_1,
        "A1_2": instance.metrics.A1_2,
        "A1_3": instance.metrics.A1_3,
        "A1_4": instance.metrics.A1_4,
        "A1_5": instance.metrics.A1_5,
        "A2": 0.0,  # Placeholder
        "A2_1": False,  # Placeholder
        "A2_2": False,  # Placeholder
        "A3": instance.scores.A3,
        "A3_1": instance.metrics.A3_1,
        "A3_2": instance.metrics.A3_2,
        "A3_3": instance.metrics.A3_3,
        "A3_4": instance.metrics.A3_4,
        "A3_5": instance.metrics.A3_5,
        "I": instance.scores.I,
        "I1": instance.scores.I1,
        "I1_1": instance.metrics.I1_1,
        "I1_2": instance.metrics.I1_2,
        "I1_3": instance.metrics.I1_3,
        "I1_4": instance.metrics.I1_4,
        "I1_5": False,  # Placeholder
        "I2": instance.scores.I2,
        "I2_1": instance.metrics.I2_1,
        "I2_2": instance.metrics.I2_2,
        "I3": instance.scores.I3,
        "I3_1": instance.metrics.I3_1,
        "I3_2": instance.metrics.I3_2,
        "I3_3": instance.metrics.I3_3,
        "R": instance.scores.R,
        "R1": instance.scores.R1,
        "R1_1": instance.metrics.R1_1,
        "R1_2": False,  # Placeholder
        "R2": instance.scores.R2,
        "R2_1": instance.metrics.R2_1,
        "R2_2": instance.metrics.R2_2,
        "R3": instance.scores.R3,
        "R3_1": False,  # Placeholder
        "R3_2": instance.metrics.R3_2,
        "R4": instance.scores.R4,
        "R4_1": instance.metrics.R4_1,
        "R4_2": False,  # Placeholder
        "R4_3": False  # Placeholder
    }

    return result
