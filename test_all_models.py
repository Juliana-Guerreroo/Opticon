import os
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
from datetime import datetime
import glob

# Configuración de rutas y archivo de salida
carpeta_modelos = "./best_models"
ruta_archivo_resultados = f"./results/results_all_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv"
os.makedirs("./results", exist_ok=True)

# Cargar los datos de prueba
df_test = pd.read_csv('./csv/Concretetest.csv', delimiter=';')
df_test = df_test.dropna(axis=0, how='any')

# Características para la predicción
caracteristicas = [
    "loadSize",
    "aggregate1_actual",
    "aggregate2_actual",
    "aggregate3_actual",
    "total_cement_actual",
    "admixture1_actual",
    "admixture2_actual",
    "admixture3_actual",
    "admixture4_actual",
    "total_water_actual",
    "water_to_cement_ratio",
]

# Asegúrate de que todas las características existan en el DataFrame
df_test = df_test[caracteristicas + ['ResistenciaConvertida']].dropna()

# Normalizar las características del conjunto de prueba
X_test = df_test[caracteristicas].values
y_test = df_test['ResistenciaConvertida'].values

# Escalador para las características (X) y la variable de salida (y)
scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_test_scaled = scaler_X.fit_transform(X_test)
y_test_scaled = scaler_y.fit_transform(y_test.reshape(-1, 1))

# Almacenar resultados de cada modelo
resultados = []

# Procesar todos los modelos en la carpeta
for modelo_path in glob.glob(os.path.join(carpeta_modelos, "*.keras")):
    try:
        # Cargar el modelo
        model = tf.keras.models.load_model(modelo_path)

        # Realizar predicciones en los datos de prueba escalados
        predicciones_scaled = model.predict(X_test_scaled)
        predicciones = scaler_y.inverse_transform(predicciones_scaled).flatten()

        # Calcular métricas
        mae = mean_absolute_error(y_test, predicciones)
        mse = mean_squared_error(y_test, predicciones)
        rmse = np.sqrt(mse)

        # Guardar resultados para este modelo
        resultados.append({
            "Prueba": os.path.basename(modelo_path).split("--")[1],  # Extraer identificador del modelo
            "MAE": mae,
            "MSE": mse,
            "RMSE": rmse,
            "Ruta del modelo": modelo_path,
        })

    except Exception as e:
        print(f"Error al procesar el modelo {modelo_path}: {e}")

# Crear un DataFrame con los resultados
df_resultados = pd.DataFrame(resultados)

# Guardar el DataFrame en un archivo CSV
df_resultados.to_csv(ruta_archivo_resultados, index=False)

# Imprimir el DataFrame para revisión
print(df_resultados)
