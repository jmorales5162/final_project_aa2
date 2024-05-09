import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import Config
from pathlib import Path
import joblib
from graficar import graficarResultados
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.ensemble import IsolationForest, RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from cross_validation import cross_validation_regression
from sklearn.cluster import KMeans
from sklearn.metrics import confusion_matrix
from timeit import timeit
from sklearn.decomposition import PCA
from multiprocessing import Process
# AutoEncoder
import tensorflow as tf
from tensorflow.keras import models, layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import datetime

# Ano-malias

def graficarAnomalias(data, outliers):
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.scatter(data['IRRADIATION'], data['DC_POWER'], c=outliers, cmap='viridis')
    plt.scatter(data['IRRADIATION'][outliers == -1], data['DC_POWER'][outliers == -1], 
            edgecolors='r', facecolors='none', s=100, label='Outliers')
    plt.xlabel('IRRADIATION')
    plt.ylabel('DC_POWER')
    plt.title('IRRADIATION vs Watts')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.scatter(data['MODULE_TEMPERATURE'], data['DC_POWER'], c=outliers, cmap='viridis')
    plt.scatter(data['MODULE_TEMPERATURE'][outliers == -1], data['DC_POWER'][outliers == -1], 
            edgecolors='r', facecolors='none', s=100, label='Outliers')
    plt.xlabel('MODULE_TEMPERATURE')
    plt.ylabel('DC_POWER')
    plt.title('MODULE_TEMPERATURE vs DC_POWER')
    plt.legend()

    plt.tight_layout()
    plt.show()

def isolationForest(df):
    X_scaled = StandardScaler().fit_transform(df)
    model = IsolationForest(contamination=0.02)
    model.fit(X_scaled)
    outliers = model.predict(X_scaled)
    graficarAnomalias(df, outliers)    

def kmeans(df, n_clusters):
    X_scaled = StandardScaler().fit_transform(df)
    model = KMeans(n_clusters=n_clusters)
    model.fit(X_scaled)
    cluster_labels = model.predict(X_scaled)
    cluster_centers = model.cluster_centers_
    distances = [np.linalg.norm(x - cluster_centers[cluster]) for x, cluster in zip(X_scaled, cluster_labels)]

    percentile_threshold = 99.5
    threshold_distance = np.percentile(distances, percentile_threshold)

    anomalies = [X_scaled[i] for i, distance in enumerate(distances) if distance > threshold_distance]
    anomalies = np.asarray(anomalies, dtype=np.float32)

    colors = cm.nipy_spectral(cluster_labels.astype(float) / 3)
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.scatter(X_scaled[:, 0], X_scaled[:, 2], marker='.', s=50, lw=0, alpha=0.7,c=colors, edgecolor='k')
    plt.scatter(anomalies[:, 0], anomalies[:, 2], color='red', marker='.', s=50, label='Anomalies')
    plt.xlabel('IRRADIATION'); plt.ylabel('DC_POWER'); plt.title('IRRADIATION vs Watts'); plt.legend()
    plt.subplot(1, 2, 2)
    plt.scatter(X_scaled[:, 1], X_scaled[:, 2], marker='.', s=50, lw=0, alpha=0.7,c=colors, edgecolor='k')
    plt.scatter(anomalies[:, 1], anomalies[:, 2], color='red', marker='.', s=50, label='Anomalies')
    plt.xlabel('MODULE_TEMPERATURE'); plt.ylabel('DC_POWER'); plt.title('MODULE_TEMPERATURE vs DC_POWER'); plt.legend()
    plt.tight_layout()
    plt.show()


def autoEncoder(data):
    x_train, x_test, y_train, y_test = train_test_split(data[['IRRADIATION', 'MODULE_TEMPERATURE']].to_numpy(), data[['DC_POWER']].to_numpy(), test_size=0.2, random_state=111)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(x_train)
    X_test_scaled = scaler.fit_transform(x_test)
    Y_train_scaled = scaler.fit_transform(x_train)
    Y_test_scaled = scaler.fit_transform(x_test)
    autoencoder = models.Sequential()
    autoencoder.add(layers.Dense(1, input_shape=X_train_scaled.shape[1:], activation='relu'))
    autoencoder.add(layers.Dense(2))
    autoencoder.compile(optimizer='adam', loss='mse')
    autoencoder.summary()
    history = autoencoder.fit(X_train_scaled, Y_train_scaled, 
          epochs=30, 
          batch_size=100,
          validation_data=(X_test_scaled, Y_test_scaled),
          shuffle=True)
    
    mse_train = tf.keras.losses.mse(autoencoder.predict(X_train_scaled), X_train_scaled)
    umbral = np.max(mse_train)

    plt.figure(figsize=(12,4))
    plt.hist(mse_train, bins=50)
    plt.xlabel("Error de reconstrucción (entrenamiento)")
    plt.ylabel("Número de datos")
    plt.axvline(umbral, color='r', linestyle='--')
    plt.legend(["Umbral"], loc="upper center")
    plt.show()
    e_test = autoencoder.predict(X_test_scaled)

    mse_test = np.mean(np.power(X_test_scaled - e_test, 2), axis=1)
    plt.figure(figsize=(12,4))
    plt.plot(range(1,X_train_scaled.shape[0]+1),mse_train,'b.')
    plt.plot(range(X_train_scaled.shape[0]+1,X_train_scaled.shape[0]+X_test_scaled.shape[0]+1),mse_test,'r.')
    plt.axhline(umbral, color='r', linestyle='--')
    plt.xlabel('Índice del dato')
    plt.ylabel('Error de reconstrucción');
    plt.legend(["Entrenamiento", "Test", "Umbral"], loc="upper left")
    plt.show()


def adestrarMetodo(df, model, nome, depVars, indepVars):
    X = df[indepVars]; Y = df[depVars]
    scaler = StandardScaler()
    cross_validation_regression(model, scaler.fit_transform(X), scaler.fit_transform(Y), folds=10, name="Solar production", model_name=nome)
    model.fit(X, Y)
    graficarResultados(model, nome, X, Y)
    output_path = Path(f"models/{nome}/", f"{nome}.pkl")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)


def process_df():
    weather_data = pd.read_csv(Config.weather_path)
    generation_data = pd.read_csv(Config.generation_path)
    generation_data['DATE_TIME'] = pd.to_datetime(generation_data['DATE_TIME'],format = '%d-%m-%Y %H:%M')
    weather_data['DATE_TIME'] = pd.to_datetime(weather_data['DATE_TIME'],format = '%Y-%m-%d %H:%M:%S')
    df_solar = pd.merge(generation_data.drop(columns = ['PLANT_ID']), weather_data.drop(columns = ['PLANT_ID', 'SOURCE_KEY']), on='DATE_TIME')
    return df_solar.drop(columns = ['DATE_TIME', 'SOURCE_KEY', 'DAILY_YIELD', 'TOTAL_YIELD', 'AMBIENT_TEMPERATURE', 'AC_POWER'])

def single_process_regression(df):
    adestrarMetodo(df, Config.mr['lr_pipe'], Config.mr['lr'], Config.depVars, Config.indepVars)
    adestrarMetodo(df, Config.mr['poly_pipe'], Config.mr['poly'], Config.depVars, Config.indepVars)
    adestrarMetodo(df, Config.mr['gBoosting_pipe'], Config.mr['gBoosting'], Config.depVars, Config.indepVars)
    adestrarMetodo(df, Config.mr['rf_pipe'], Config.mr['rf'], Config.depVars, Config.indepVars)

def multi_process_regression_constructor(df):
    p1 = Process(target=adestrarMetodo, args=(df, Config.mr['lr_pipe'], Config.mr['lr'], Config.depVars, Config.indepVars))
    p2 = Process(target=adestrarMetodo, args=(df, Config.mr['poly_pipe'], Config.mr['poly'], Config.depVars, Config.indepVars))
    p3 = Process(target=adestrarMetodo, args=(df, Config.mr['gBoosting_pipe'], Config.mr['gBoosting'], Config.depVars, Config.indepVars))
    p4 = Process(target=adestrarMetodo, args=(df, Config.mr['rf_pipe'], Config.mr['rf'], Config.depVars, Config.indepVars))

    procesos = [p1,p2,p3,p4]

    for proceso in procesos:
        proceso.start()
        
    for proceso in procesos:
        proceso.join()




if __name__ == "__main__":

    # 1: Estudo do conxunto de datos
    tiempos = {}
    df = process_df()
    print(df)
    # 2: Tecnicas de deteccion de anomalias

    #tiempos['single_process'] = timeit("single_process_regression(df)", globals=globals(), number=1)
    tiempos['process_with_constructor'] = timeit("multi_process_regression_constructor(df)", globals=globals(), number=1)

    for metodo,tiempo in tiempos.items():
        print(f"Tiempo de ejecución para {metodo}: {tiempo/60:.2f} min")

    
    #isolationForest(df)
    #kmeans(df, Config.n_clusters)
    #autoEncoder(df)
    


    # 3: Modelos de regresion

