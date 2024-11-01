import os
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from datetime import datetime

# Cargar el modelo
model_path = "./best_models/2024-11-01_10-19-53--model_37.keras"  # Reemplaza <timestamp> con la parte correspondiente del nombre del archivo
model = tf.keras.models.load_model(model_path)

# Cargar los datos de entrada para las predicciones
df_test = pd.read_csv('./csv/Concretetest.csv', delimiter=';')
df_test = df_test.dropna(axis=0, how='any')

# Asegúrate de que la columna de ResistenciaConvertida no tenga ceros
df_test = df_test[df_test['ResistenciaConvertida'] != 0]

# Seleccionar las características relevantes para la predicción
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
scaler_X = StandardScaler()  # Debes usar el mismo scaler que utilizaste para entrenar el modelo
scaler_X.fit(X_test)  # Ajusta el scaler (opcional, si no tienes el scaler guardado)
X_test_scaled = scaler_X.transform(X_test)  # Usa el mismo scaler que usaste para X_train

# Realizar las predicciones
predicciones_scaled = model.predict(X_test_scaled)
scaler_y = StandardScaler()  # Nuevamente, asegúrate de usar el mismo scaler que utilizaste para la etiqueta
y_train = df_test['ResistenciaConvertida'].values 
scaler_y.fit(y_train.reshape(-1, 1))  # Ajusta el scaler para y (opcional, si no tienes el scaler guardado)
predicciones = scaler_y.inverse_transform(predicciones_scaled)  # Invertir la normalización de las predicciones

# Crear un DataFrame para los resultados
df_resultados = pd.DataFrame(predicciones, columns=['Predicción de Resistencia'])
df_resultados['Real'] = df_test['ResistenciaConvertida'].values  # Valores reales de la resistencia

# Calcular la diferencia y agregarla como una columna en df_resultados
df_resultados['Diferencia'] = df_resultados['Real'] - df_resultados['Predicción de Resistencia']

# Mostrar el DataFrame con los resultados
print(df_resultados)

# Calcular la suma de los valores absolutos de la diferencia
suma_absoluta = df_resultados['Diferencia'].abs().sum()
print("La suma de los valores absolutos es:", suma_absoluta)

# Crear una carpeta para guardar las predicciones
os.makedirs("./predictions", exist_ok=True)

# Opcional: Guardar en un CSV
df_resultados.to_csv(f'./predictions/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}--predicciones.csv', index=False)
