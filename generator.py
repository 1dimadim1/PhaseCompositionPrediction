import csv
import warnings
from pycalphad import Database, equilibrium, variables as v
import random
import numpy as np
import time
from tqdm import tqdm

# constants:
P = 101325
db_name = 'models/sgsol_2021_pycalphad.tdb'
db = Database(db_name)
# TODO: check 'PM' param
all_components = ['LI', 'BE', 'NA', 'MG', 'AL', 'K', 'CA', 'SC', 'TI', 'V', 'CR', 'MN', 'FE',
                  'CO', 'NI', 'CU', 'ZN', 'GA', 'Y', 'ZR', 'NB', 'MO', 'TC',
                  'RH', 'PD', 'AG', 'CD', 'IN', 'SN', 'BA', 'LA', 'CE', 'PR', 'ND', 'SM', 'EU',
                  'GD', 'TB', 'DY', 'HO', 'ER', 'HF', 'TA', 'W', 'RE', 'OS', 'IR',
                  'PT', 'AU', 'HG', 'TL', 'PB', 'BI', 'C', 'SI']
all_phases = list(db.phases)
all_phases.sort()
all_components.sort()

# phase result parser
def flattenArray(arr):
    result = []
    for item in arr.flat:
        if isinstance(item, np.ndarray):
            result.extend(flattenArray(item))
        else:
            result.append(item)
    return result

# Get all possible phases for that components
def getPossiblePhases(db, components):
    possible_phases = []
    for phase_full in db.phases.items():
        # item[0] - name, item[1] - content
        # item[1]: name, constituents, sublattices, model_hints
        found_sublattices = 0
        phase = phase_full[1]

        for sublattice_c in phase.constituents:
            found = False
            for comp in components:
                if len([species.name for species in sublattice_c if species.name == comp]) > 0:
                    found = True
                    break
            if found:
                found_sublattices += 1
            else:
                break

        if found_sublattices == len(phase.constituents):
            possible_phases.append(phase.name)

    possible_phases.sort()
    return possible_phases

# TODO: fix ordered_phases
def filterOrderedPhases(dbf, candidate_phases=None):
    if candidate_phases == None:
        candidate_phases = dbf.phases.keys()
    else:
        candidate_phases = set(
            candidate_phases).intersection(dbf.phases.keys())
    # all_phases = [{"name": phase, "ordered": dbf.phases[phase].model_hints.get('ordered_phase'),'dis':dbf.phases[phase].model_hints.get('disordered_phase')} for phase in candidate_phases if dbf.phases[phase].model_hints.get('ordered_phase') != None]
    # disordered_phases = [dbf.phases[phase].model_hints.get('disordered_phase') for phase in candidate_phases]
    ordered_phases = [dbf.phases[phase].model_hints.get(
        'ordered_phase') for phase in candidate_phases]

    phases = [phase for phase in candidate_phases if
              (phase not in ordered_phases)]
    #  or (phase in disordered_phases and
    # dbf.phases[phase].model_hints.get('ordered_phase') not in candidate_phases)
    return sorted(phases)


def getPhases(int_mask, all_phases=all_phases):
    return [all_phases[i] for i in range(len(all_phases)) if (int_mask & (1 << i)) > 0]


def phasesToMask(phases, all_phases=all_phases):
    phases.sort()
    mask = [1 if phase in phases else 0 for phase in all_phases][::-1]
    return int(''.join(map(str, mask)), 2)


def phaseToMask(phase, all_phases=all_phases):
    mask = [1 if phase == phase_ else 0 for phase_ in all_phases][::-1]
    return int(''.join(map(str, mask)), 2)

def compToMask(components, all_components=all_components):
    components.sort()
    mask = [1 if comp in components else 0 for comp in all_components][::-1]
    return int(''.join(map(str, mask)), 2)

def getComponents(int_mask, all_components=all_components):
    return [all_components[i] for i in range(len(all_components)) if (int_mask & (1 << i)) > 0]

def equilibriumRow(conditions, components, temp, amounts, iter):
    calc_components = components.copy()
    calc_components.append('VA')
    row_values = {}
    founded_phases = []
    possible_phases = getPossiblePhases(db, components)
    possible_phases = filterOrderedPhases(db, possible_phases)
    # print(set(possible_phases) - set(filtred_phase))

    tic = time.perf_counter()
    try:
        eq = equilibrium(db, calc_components, possible_phases,
                         conditions, verbose=False)
        founded_phases = flattenArray(np.array(eq.Phase))
    except ValueError as error:
        row_values['Error'] = error
    toc = time.perf_counter()

    row_values = {'iter': iter, 'T': temp, 'amounts': amounts, 'Components': compToMask(components), 'phases': phasesToMask(founded_phases),
                  'ellapsed_time': toc - tic, 'possible_phases': phasesToMask(possible_phases), 'P': P, 'Error': ''} | row_values

    return row_values

def parseConditions(temp, amounts, components, P=P):
    conditions = {v.T: temp, v.P: P}

    for i in range(len(components)):
        if i != 0:
            conditions[v.X(components[i])] = amounts[i]

    return conditions

def getAmounts(components):
    amounts = [0.05]*len(components)
    for i in range(len(amounts)):
        amounts[i] += random.uniform(0, min(1 - sum(amounts), 0.3))
    amounts[-1] += 1 - sum(amounts)
    return amounts

# TODO: make random temperature more stable diffuse
def getTemp():
    return random.randint(300, 3000)


warnings.filterwarnings("ignore")

random.seed(42)
line = {}
 
with open('DataSets/main_result.csv', "a") as csv_file:
    header = ['iter', 'T','amounts','Components','phases','ellapsed_time','possible_phases','P', 'Error']
    writer = csv.writer(csv_file, delimiter=';', lineterminator = '\n')
    writer.writerow(header)
    rnd_state = random.getstate()
    for j in range(1):
        # TODO: iterate over components
        components = ['ZR', 'MO', 'W', 'TA', 'V', 'CR', 'CO', 'NI']
        print(f'{j} - {components}')
        for i in tqdm(range(500)):
            temp = getTemp()
            amounts = getAmounts(components)
            if i <= 500:
                continue
            conditions = parseConditions(temp, amounts, components)
            line = equilibriumRow(conditions, components, temp, amounts, i) 
            writer.writerow(list(line.values()))
    # TODO: Save random state in a file and continue from state
    print('Done!')