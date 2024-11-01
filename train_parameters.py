import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error
import random
import itertools

# Cargar y preparar los datos
start = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
df = pd.read_csv("./csv/Concretetest.csv", delimiter=";")
df = df.dropna(axis=0, how="any")
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
df = df[caracteristicas + ["ResistenciaConvertida"]].dropna()
X = df[caracteristicas].values
y = df["ResistenciaConvertida"].values

# Normalización de datos
scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_scaled, test_size=0.2, random_state=42
)

# Crear carpetas para guardar modelos, gráficas y resultados
os.makedirs("./best_models", exist_ok=True)
os.makedirs("./images", exist_ok=True)
os.makedirs("./results", exist_ok=True)

# Cargar el modelo base (modelo_527)
modelo_base = tf.keras.models.load_model('./best_models/2024-11-01_10-19-53--model_37.keras')

# Hiperparámetros para la prueba
# Valores de cada parámetro
epochs_values = [300,350,400]
learning_rate_values = [0.0005, 0.001, 0.002]
layers_values = [
    [512, 256, 128, 64],
    [2048, 1024, 512, 256],
    [1024, 512, 256, 128],
]
dropout_values = [None,0.1, 0.2, 0.3]
batch_norm_values = [True, False]
patience_values = range(20, 31)
lr_reduction_patience_values = range(10, 16)
reduce_factor_values = [0.1, 0.2, 0.3]
batch_size_values = [40, 50,60]

# Generar todas las combinaciones de parámetros
parametros = [
    {
        "epochs": e,
        "learning_rate": lr,
        "layers": l,
        "dropout": d,
        "batch_norm": bn,
        "patience": p,
        "lr_reduction_patience": lrp,
        "reduce_factor": rf,
        "batch_size": bs,
    }
    for e, lr, l, d, bn, p, lrp, rf, bs in itertools.product(
        epochs_values,
        learning_rate_values,
        layers_values,
        dropout_values,
        batch_norm_values,
        patience_values,
        lr_reduction_patience_values,
        reduce_factor_values,
        batch_size_values,
    )
]

# Configuración para almacenar métricas de rendimiento
resultados = []
mejor_val_loss = np.inf
mejor_modelo_path = None

for idx, params in enumerate(parametros):
    print(f"\nPrueba {idx + 1} con parámetros: {params}")

    # Clonar el modelo base
    model = tf.keras.models.clone_model(modelo_base)
    model.set_weights(modelo_base.get_weights())

    # Ajustar hiperparámetros en capas adicionales
    for layer_size in params["layers"]:
        model.add(tf.keras.layers.Dense(layer_size, activation="relu"))
        if params["batch_norm"]:
            model.add(tf.keras.layers.BatchNormalization())
        if params["dropout"]:
            model.add(tf.keras.layers.Dropout(params["dropout"]))
    model.add(tf.keras.layers.Dense(1))

    optimizer = tf.keras.optimizers.Adam(learning_rate=params["learning_rate"])
    model.compile(optimizer=optimizer, loss="mean_squared_error")

    # Callbacks
    model_path = f"./best_models/{start}--model_{idx + 1}.keras"
    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        model_path, monitor="val_loss", save_best_only=True
    )
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=params["patience"], restore_best_weights=True
    )
    lr_reduction = tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=params["reduce_factor"],
        patience=params["lr_reduction_patience"],
    )

    # Entrenar el modelo
    history = model.fit(
        X_train,
        y_train,
        epochs=params["epochs"],
        validation_split=0.2,
        callbacks=[checkpoint, early_stopping, lr_reduction],
        batch_size=params["batch_size"]
    )

    # Cargar el mejor modelo guardado
    best_model = tf.keras.models.load_model(model_path)

    # Realizar predicciones con el conjunto de prueba
    predicciones_scaled = best_model.predict(X_test)
    predicciones = scaler_y.inverse_transform(predicciones_scaled)

    # Calcular métricas
    y_test_real = scaler_y.inverse_transform(y_test)
    mae = mean_absolute_error(y_test_real, predicciones)
    mse = mean_squared_error(y_test_real, predicciones)
    rmse = np.sqrt(mse)

    # Guardar resultados en la lista
    resultados.append(
        {"Prueba": idx + 1, "Parametros": params, "MAE": mae, "MSE": mse, "RMSE": rmse}
    )

    # Guardar el modelo si es el mejor hasta ahora
    val_loss_min = min(history.history["val_loss"])
    if val_loss_min < mejor_val_loss:
        mejor_val_loss = val_loss_min
        mejor_modelo_path = model_path

    # Graficar la curva de pérdida
    plt.plot(history.history["loss"], label="Pérdida de entrenamiento")
    plt.plot(history.history["val_loss"], label="Pérdida de validación")
    plt.xlabel("Épocas")
    plt.ylabel("Pérdida")
    plt.legend()
    plt.title(f"Curva de Pérdida del Modelo {idx + 1}")
    plt.savefig(f"./images/{start}--model_{idx + 1}_loss_curve.jpg")
    plt.clf()

# Mostrar resultados
print(f"\nEl mejor modelo se guardó en: {mejor_modelo_path} con una pérdida de validación mínima de: {mejor_val_loss}")
for resultado in resultados:
    print(f"\nPrueba {resultado['Prueba']} - {resultado['Parametros']}")
    print(f"MAE: {resultado['MAE']}, MSE: {resultado['MSE']}, RMSE: {resultado['RMSE']}")

# Guardar resultados en archivo CSV
ruta_archivo = f"./results/{start}--results.csv"

# Crear un DataFrame con los resultados
df_resultados = pd.DataFrame([
    {
        "Prueba": resultado['Prueba'],
        "MAE": resultado['MAE'],
        "MSE": resultado['MSE'],
        "RMSE": resultado['RMSE'],
        "Ruta del modelo": f"./best_models/{start}--model_{resultado['Prueba']}.keras",
        **resultado['Parametros']  # Descomponer los parámetros en columnas
    }
    for resultado in resultados
])

# Guardar el DataFrame en un archivo CSV
df_resultados.to_csv(ruta_archivo, index=False)
print(f"Los resultados se han guardado en: {ruta_archivo}")
