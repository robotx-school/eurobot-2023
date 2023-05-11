# CatBoost; Train code here
import pandas as pd
import catboost
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.inspection import permutation_importance

dataset = pd.read_csv("dataset.csv")

