from modules.Calculate import calculate
import numpy as np


def getGM(db, components, all_phases,possible_phases, amounts, T, P = 101325):
    results = [np.nan] * len(all_phases)
    for i in range(len(all_phases)):
        if all_phases[i] in possible_phases:
            try:
                values = calculate(db, components, all_phases[i] , output = 'GM', P = P, T = T, points = amounts)
                results[i] = values.GM.values.flat[0]
            except Exception as e:
                continue
    return results