import os
from sklearn.preprocessing import StandardScaler, PolynomialFeatures 
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

path = os.path.join(os.path.dirname(__file__), "datasetProba", "todo.csv")
depVars = "W"
indepVars = ["radiation", "temperature"]
n_clusters = 3

mr = {  #models regression
'lr'            : "linealRegression",
'lr_pipe'       :  make_pipeline(StandardScaler(), LinearRegression()),
'poly'          : "polynomialMethod",
'poly_pipe'     :  make_pipeline(PolynomialFeatures(2, include_bias=False),StandardScaler(),LinearRegression()),
'gBoosting'     : "gradientBoostingMethod",
'gBoosting_pipe': make_pipeline(StandardScaler(),GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)),
'rf'            : "rdmForestMethod",
'rf_pipe'       : make_pipeline(StandardScaler(), RandomForestRegressor(n_estimators=100))
}