import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error
import optuna
from tqdm import tqdm

# Cargar y preparar los datos
start = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
df = pd.read_csv("./csv/ConcreteNew.csv", delimiter=";")
df = df.dropna(axis=0, how="any")

# Definir las columnas de características
features = [
    "mixCode",
    "curing_time",
    "settlement_value",
    "unit_settlement",
    "fullname",
    "mixercode",
    "Worktoplant",
    "loadSize",
    "aggregate1_name",
    "aggregate1_target",
    "aggregate1_actual",
    "aggregate2_name",
    "aggregate2_target",
    "aggregate2_actual",
    "aggregate3_name",
    "aggregate3_target",
    "aggregate3_actual",
    "cement1_name",
    "cement1_target",
    "cement1_actual",
    "cement2_name",
    "cement2_target",
    "cement2_actual",
    "cement3_name",
    "cement3_target",
    "cement3_actual",
    "admixture1_name",
    "admixture1_target",
    "admixture1_actual",
    "admixture2_name",
    "admixture2_target",
    "admixture2_actual",
    "admixture3_name",
    "admixture3_target",
    "admixture3_actual",
    "admixture4_name",
    "admixture4_target",
    "admixture4_actual",
    "total_water_target",
    "water_to_cement_ratio"
]

# Cargar los datos
df = df[features + ["strength_in_mpa"]].dropna()

# Codificar las columnas categóricas usando One-Hot Encoding
categorical_columns = [
    "mixCode","curing_time","unit_settlement","fullname", "mixercode", "Worktoplant", 
    "aggregate1_name", "aggregate2_name", "aggregate3_name", 
    "cement1_name", "cement2_name", "cement3_name", 
    "admixture1_name", "admixture2_name", "admixture3_name", "admixture4_name"
]

# Aplicar One-Hot Encoding a las columnas categóricas
df = pd.get_dummies(df, columns=categorical_columns)

# Separar características y variable objetivo
X = df.drop(columns=["strength_in_mpa"]).values
y = df["strength_in_mpa"].values

# Normalización de datos
scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

# Dividir en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42)

# Crear carpetas para guardar modelos, gráficas y resultados
os.makedirs("./best_models", exist_ok=True)
os.makedirs("./images", exist_ok=True)
os.makedirs("./results", exist_ok=True)

# Definir la función objetivo para Optuna
def objective(trial):
    # Definir los hiperparámetros a optimizar
    epochs = 300
    learning_rate = trial.suggest_float("learning_rate", 1.3e-4, 2.1e-4, log=True)
    max_num_layers = 4
    num_layers = trial.suggest_int("num_layers", 3, max_num_layers) 
    layers = [trial.suggest_int(f"layer_{i}", 210, 1050, step=70) for i in range(num_layers)]  # Tamaño de cada capa
    dropout = trial.suggest_float("dropout", 0.1, 0.3)
    batch_norm = True
    patience = trial.suggest_int("patience", 29,40)
    lr_reduction_patience = trial.suggest_int("lr_reduction_patience", 5, 28)
    reduce_factor = trial.suggest_float("reduce_factor", 0.1, 0.5)
    batch_size = trial.suggest_int("batch_size", 80,140, step = 10)
    
    # Crear el modelo
    model = tf.keras.Sequential([tf.keras.Input(shape=(X_train.shape[1],))])
    
    for i, layer_size in enumerate(layers):
        model.add(tf.keras.layers.Dense(layer_size, activation="relu", name=f"dense_custom_{i}--{start}"))
        if batch_norm:
            model.add(tf.keras.layers.BatchNormalization(name=f"batch_norm_{i}--{start}"))
        if dropout > 0.0:
            model.add(tf.keras.layers.Dropout(dropout, name=f"dropout_{i}--{start}"))
    
    model.add(tf.keras.layers.Dense(1, name=f"output_layer--{start}"))

    # Compilar el modelo
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(optimizer=optimizer, loss="mean_squared_error")

    # Callbacks
    checkpoint_path = f"./best_models/{start}--optuna_model_{trial.number}.keras"
    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        checkpoint_path, monitor="val_loss", save_best_only=True
    )
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=patience, restore_best_weights=True
    )
    lr_reduction = tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=reduce_factor, patience=lr_reduction_patience
    )

    # Entrenar el modelo
    history = model.fit(
        X_train,
        y_train,
        epochs=epochs,
        validation_split=0.2,
        callbacks=[checkpoint, early_stopping, lr_reduction],
        batch_size=batch_size,
        verbose=1
    )
    
    # Obtener la última época registrada
    last_epoch = len(history.history["loss"])
    
    # Graficar la curva de pérdida
    plt.plot(history.history["loss"], label="Pérdida de entrenamiento")
    plt.plot(history.history["val_loss"], label="Pérdida de validación")
    plt.xlabel("Épocas")
    plt.ylabel("Pérdida")
    plt.legend()
    plt.title(f"Curva de Pérdida del Modelo {trial.number}")
    plt.savefig(f"./images/{start}--optuna_model_{trial.number}_loss_curve.jpg")
    plt.clf()
    
    # Cargar el mejor modelo guardado
    best_model = tf.keras.models.load_model(checkpoint_path)

    # Realizar predicciones y calcular métricas
    predictions_scaled = best_model.predict(X_test)
    predictions = scaler_y.inverse_transform(predictions_scaled)
    y_test_real = scaler_y.inverse_transform(y_test)
    mae = mean_absolute_error(y_test_real, predictions)
    mse = mean_squared_error(y_test_real, predictions)
    rmse = np.sqrt(mse)

    # Guardar los resultados en el archivo CSV
    ruta_archivo = f"./results/{start}--optuna_results.csv"
    with open(ruta_archivo, 'a') as f:
        if trial.number == 0:
            # Escribir encabezados en el archivo CSV
            headers = ["Trial", "MAE", "MSE", "RMSE", "Model_Path", "Last_Epoch"] + \
                    ["layer_" + str(i) for i in range(max_num_layers)] + \
                    [key for key in trial.params.keys() if not key.startswith('layer_')]
            f.write(";".join(headers) + "\n")
        
        layers_values = [str(trial.params.get(f"layer_{i}", "")) for i in range(max_num_layers)]
        
        # Escribir los resultados para el trial
        fila = [str(trial.number), str(mae), str(mse), str(rmse), checkpoint_path, str(last_epoch)] + \
            layers_values + [str(trial.params[k]) for k in trial.params if not k.startswith('layer_')]
        f.write(";".join(fila) + "\n")

    # Devolver el error cuadrático medio (MSE) como métrica objetivo para minimizar
    return mse

# Crear el estudio
study = optuna.create_study(direction="minimize")

# Configuración de tqdm
n_trials = 500
with tqdm(total=n_trials) as pbar:
    for _ in range(n_trials):
        study.optimize(objective, n_trials=1, catch=(Exception,))
        pbar.update(1)

# Mostrar los mejores hiperparámetros y guardar los resultados
print("Mejores hiperparámetros:", study.best_params)
print("Mejor valor de MSE:", study.best_value)

# Visualizar los resultados
optuna.visualization.plot_optimization_history(study).show()
optuna.visualization.plot_param_importances(study).show()
