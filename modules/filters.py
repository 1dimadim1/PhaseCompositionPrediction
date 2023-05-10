from pycalphad.core.utils import filter_phases, unpack_components
import pandas as pd 
from sklearn import preprocessing
import numpy as np

# Get all possible phases for that components
def getPossiblePhases(db, components):
    comps = list(components)
    comps = unpack_components(db, comps)
    return filter_phases(db, comps)

# Neural network input parsing
def normTemp(df, min_t, max_t, column_name = 'Temp'):
    df[column_name] = (df[column_name] - min_t) / max_t
    return df
def normDFColumn(df):
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled=pd.DataFrame(min_max_scaler.fit_transform(df.T).T,columns=df.columns)
    # x_scaled = min_max_scaler.fit_transform(x)
    return pd.DataFrame(x_scaled)
def normGms(gms, all_phases):
    X = pd.DataFrame(gms, columns=all_phases)
    X_max = X.replace([np.inf, -np.inf], np.nan).max().max()
    X_min = X.replace([np.inf, -np.inf], np.nan).min().min()
    X[np.isneginf(X)] = X_min
    X[np.isinf(X)] = X_max
    X = X.apply(lambda row: row.replace(np.inf, max(row)), axis=1)
    X = X.apply(lambda row: row.replace(-np.inf, min(row)), axis=1)
    X = X.apply(lambda row: row.fillna(row.max()), axis=1)
    X = X.multiply(-1)
    X[all_phases] = normDFColumn(X[all_phases])
    return X

def parsePrediction(predictions, all_phases, tres = 0, top = 8):
    if len(predictions) != len(all_phases):
        raise Exception('Wrong prediction dimensions!')
    top_ind = sorted(range(len(predictions)), key=lambda i: predictions[i])[-top:]
    predictions_ind = [(ind,predictions[ind]) for ind in top_ind if predictions[ind] > tres]
    predictions_out = {}
    for ind_prediction in predictions_ind:
        predictions_out[all_phases[ind_prediction[0]]] = ind_prediction[1]
    return predictions_out


def parsePredictionKeys(predictions, all_phases, tres = 0, top = 8):
    if len(predictions) != len(all_phases):
        raise Exception('Wrong prediction dimensions!')
    top_ind = sorted(range(len(predictions)), key=lambda i: predictions[i])[-top:]
    predictions_ind = [ind for ind in top_ind if predictions[ind] > tres]
    return [all_phases[ind] for ind in predictions_ind ]