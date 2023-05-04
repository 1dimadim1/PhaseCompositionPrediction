from pycalphad import Database
import numpy as np
import time
from tqdm import tqdm
import modules.variables as var
import os
from modules.GetGm import getGM
from modules.mask import getComponents, getPhases
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

def parseArray(amounts_str):
    amounts = amounts_str.replace('[', '').replace(']', '')
    return np.array(amounts.split(','), dtype=np.float32)


def getTimeGM(db, Components, all_phases, possible_phases, amounts, T):
    tic = time.perf_counter()
    gm = getGM(db, Components, all_phases, possible_phases, amounts, T)
    toc = time.perf_counter()
    return (toc-tic, gm)


def addDFLineToCSV(df, path='./DataSets/parsedDataset.csv'):
    df.to_csv(path, mode='a', sep=";", header=not os.path.exists(path))


# constants:
P = 101325
db_name = 'models/sgsol_2021_pycalphad.tdb'
db = Database(db_name)
all_components = var.all_components
all_phases = var.all_phases
# Parsing
df_origin = pd.read_csv('DataSets/main_test.csv', delimiter=';')
df_origin = df_origin[df_origin['Error'].isna()].reset_index(drop=True)
df = df_origin.reset_index(drop=True)
df_origin['gm_time'] = np.nan
df_origin['GM'] = np.nan
df_origin['GM'] = df_origin['GM'].astype(object)

df = df.drop(['Error'], axis=1)
df = df.rename(columns={"T": "Temp"})
df['Components'] = df['Components'].apply(getComponents)
df['possible_phases'] = df['possible_phases'].apply(getPhases)
df['phases'] = df['phases'].apply(getPhases)
df['amounts'] = df['amounts'].apply(parseArray)

i = df_origin.index[0]
df_line = []
for i in tqdm(df_origin.index):
    if i < 1425:
        continue
    df_line = df_origin.loc[i:i].copy()
    df_line.loc[:, 'gm_temp'] = df.loc[i:i].apply(lambda x: getTimeGM(
        db, x.Components, all_phases, x.possible_phases, x.amounts, x.Temp), axis=1)
    df_line.loc[:, 'gm_time'] = df_line.apply(lambda x: x.gm_temp[0], axis=1)
    df_line.loc[:, 'GM'] = df_line.apply(lambda x: x.gm_temp[1], axis=1)
    df_line = df_line.drop(['gm_temp'], axis=1)
    addDFLineToCSV(df_line)

print('Done!')
