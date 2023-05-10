from modules.filters import parsePredictionKeys
from modules.filters import parsePrediction
import pandas as pd
from modules.filters import normGms, normTemp
from modules.GetGm import getGM
from modules.filters import getPossiblePhases
from pycalphad import Database
from tqdm import tqdm
import modules.variables as var
from tensorflow import keras


# Input
amounts = [[0.10640018, 0.07053918, 0.09098721, 0.08310691, 0.1866029,
            0.18583018, 0.17365684, 0.1028766],
           [0.05581862, 0.06488962, 0.21049123, 0.10578128, 0.08068205,
            0.13075854, 0.22992805, 0.12165063],
           [0.0770591, 0.05441745, 0.11515643, 0.17607291, 0.2857176,
            0.12056114, 0.0763749, 0.09464048]]
temp = [1000] * len(amounts)
filter_value = 0.2


print('load TDB file')
# constants:
P = 101325
db_name = 'models/sgsol_2021_pycalphad.tdb'
db = Database(db_name)
all_components = var.all_components
all_phases = var.all_phases
min_temp = 298.15
max_temp = 3000
components = ['CO', 'CR', 'MO', 'NI', 'TA', 'V', 'W', 'ZR']	
possible_phases = getPossiblePhases(db, components)

print('Load model')
model = keras.models.load_model('models/sgsol_2021')

print("Расчет энергий Гиббса")
gms = []
for i in tqdm(range(len(amounts))):
    gms.append(getGM(db, components, all_phases, possible_phases, amounts[i], temp[i]))


print("Обработка энергий Гиббса")
# Нормализаиция энергий Гиббса
X = normGms(gms, all_phases)

# Добавление значение температуры в данные для расчета
if type(temp) == int or type(temp) ==  float:
    X = X.copy()
    X.loc[:, 'Temp'] = temp
else:
    X = pd.concat([X, pd.DataFrame(temp, columns=['Temp'])], axis=1)
    # X = pd.concat([X, pd.DataFrame(temp.to_list(), columns=['Temp'])], axis=1)
# Нормализация значения температуры
X = normTemp(X, min_temp, max_temp)

# Добавление количество компонентов в данные для расчета
X_A = pd.DataFrame(amounts, columns=components)
# X_A = pd.DataFrame(amounts.to_list(), columns=components)
X = pd.concat([X, X_A], axis=1)


print("Предсказание стабильных фаз")
results = model.predict(X)


print("Фильтрация энергий Гиббса")

# for i in range(len(results)):
#     print(parsePrediction(results[i], all_phases, filter_value))


print(f"Значение фильтра = {filter_value}")
for i in range(len(results)):
    print(f"Концентрация = {amounts[i]}\nТемпература = {temp[i]}\n",
          f"Фазы: {parsePredictionKeys(results[i], all_phases, filter_value)}\n")