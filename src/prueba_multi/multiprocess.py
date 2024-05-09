from pathos.multiprocessing import ProcessingPool
from timeit import timeit
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import Config
from pathlib import Path
import joblib
from graficar import graficarResultados
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import make_pipeline
from multiprocessing import Process
from cross_validation import cross_validation_regression
from sklearn.cluster import KMeans

from concurrent.futures import ThreadPoolExecutor
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf

def adestrarMetodo(datafile, metodo, nome, depVars, indepVars):
    df = pd.read_csv(datafile); X = df[indepVars]; Y = df[depVars]
    model = make_pipeline(StandardScaler(), metodo)
    cross_validation_regression(model, X, Y, folds=10, name="Solar production", model_name=nome)
    model.fit(X, Y)
    graficarResultados(model, nome, X, Y)
    output_path = Path(f"models/{nome}/", f"{nome}.pkl")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)

def multi_process_regression_pathos():
    with ProcessingPool() as pool:
        # Añadir las funciones al pool para su ejecución asíncrona
        #resultado1 = pool.apipe(adestrarMetodo, Config.path, Config.mr['lr_pipe'], Config.mr['lr'], Config.depVars, Config.indepVars)
        #resultado2 = pool.apipe(adestrarMetodo, Config.path, Config.mr['poly_pipe'], Config.mr['poly'], Config.depVars, Config.indepVars)
        resultado3 = pool.apipe(adestrarMetodo, Config.path, Config.mr['gBoosting_pipe'], Config.mr['gBoosting'], Config.depVars, Config.indepVars)
        #resultado4 = pool.apipe(adestrarMetodo, Config.path, Config.mr['rf_pipe'], Config.mr['rf'], Config.depVars, Config.indepVars)
        
        # Esperar a que finalicen las funciones y obtener los resultados
        #resultado1.get()
        #resultado2.get()
        resultado3.get()
        #resultado4.get()

def multi_process_regression_constructor():
    procesos = []
    proceso1 = Process(target=adestrarMetodo, args=(Config.path, Config.mr['gBoosting_pipe'], Config.mr['gBoosting'], Config.depVars, Config.indepVars))
    proceso1.start()
    procesos.append(proceso1)
    for proceso in procesos:
        proceso.join()

def single_process_regression():
    #adestrarMetodo(Config.path, Config.mr['lr_pipe'], Config.mr['lr'], Config.depVars, Config.indepVars)
    #adestrarMetodo(Config.path, Config.mr['poly_pipe'], Config.mr['poly'], Config.depVars, Config.indepVars)
    adestrarMetodo(Config.path, Config.mr['gBoosting_pipe'], Config.mr['gBoosting'], Config.depVars, Config.indepVars)
    #adestrarMetodo(Config.path, Config.mr['rf_pipe'], Config.mr['rf'], Config.depVars, Config.indepVars)

if __name__ == "__main__":
    
    tiempos = {}

    tiempos['single_process'] = timeit("single_process_regression()", globals=globals(), number=1)
    tiempos['process_with_pathos'] = timeit("multi_process_regression_pathos()", globals=globals(), number=1)
    tiempos['process_with_constructor'] = timeit("multi_process_regression_constructor()", globals=globals(), number=1)

    for metodo,tiempo in tiempos.items():
        print(f"Tiempo de ejecución para {metodo}: {tiempo/60:.2f} min")