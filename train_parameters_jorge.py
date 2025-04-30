import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import warnings
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, explained_variance_score
from datetime import datetime
import os
import random
from typing import Dict, Tuple, List

# Configuración de reproducibilidad y advertencias
warnings.filterwarnings('ignore')
tf.keras.utils.set_random_seed(42)
tf.config.experimental.enable_op_determinism()

def load_and_prepare_data(filepath: str) -> Tuple[pd.DataFrame, pd.Series]:
    """Carga y prepara los datos con feature engineering."""
    df = pd.read_csv(filepath, delimiter=";")
    df = df.dropna(axis=0, how="any")
    
    # Columnas originales
    features = [
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
    
    # Feature engineering
    df['total_aggregate'] = df['aggregate1_actual'] + df['aggregate2_actual'] + df['aggregate3_actual']
    df['cement_water_ratio'] = df['total_cement_actual'] / (df['total_water_actual'] + 1e-6)
    df['aggregate_cement_ratio'] = df['total_aggregate'] / (df['total_cement_actual'] + 1e-6)
    
    features.extend(['total_aggregate', 'cement_water_ratio', 'aggregate_cement_ratio'])
    
    # Eliminar filas con valores faltantes
    df = df[features + ["ResistenciaConvertida"]].dropna()
    
    # Manejo conservador de outliers (solo los extremos)
    for col in features:
        q1 = df[col].quantile(0.05)
        q3 = df[col].quantile(0.95)
        iqr = q3 - q1
        df = df[(df[col] >= q1 - 1.5*iqr) & (df[col] <= q3 + 1.5*iqr)]
    
    return df[features], df["ResistenciaConvertida"]

def build_model(input_shape: int, params: Dict) -> tf.keras.Model:
    """Construye el modelo con arquitectura flexible."""
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(input_shape,))
    ])
    
    # Capas ocultas
    for units in params["layers"]:
        model.add(tf.keras.layers.Dense(
            units,
            activation=params["activation"],
            kernel_regularizer=tf.keras.regularizers.l2(params["l2_reg"]),
            kernel_initializer='he_normal'
        ))
        if params["batch_norm"]:
            model.add(tf.keras.layers.BatchNormalization())
        model.add(tf.keras.layers.Dropout(params["dropout"]))
    
    # Capa de salida
    model.add(tf.keras.layers.Dense(1))
    
    # Optimizador con schedule de learning rate
    lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
        initial_learning_rate=params["learning_rate"],
        decay_steps=params["decay_steps"],
        decay_rate=params["decay_rate"])
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)
    
    # Usamos tf.keras.losses.Huber() en lugar del string
    model.compile(
        optimizer=optimizer,
        loss=tf.keras.losses.Huber(),  # Corregido aquí
        metrics=["mae", "mse"]
    )
    
    return model

def train_and_evaluate(
    model: tf.keras.Model,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    params: Dict,
    save_path: str
) -> Tuple[tf.keras.Model, Dict]:
    """Entrena y evalúa el modelo."""
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=params["patience"],
            restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=params["reduce_lr_patience"]),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=save_path,
            save_best_only=True,
            monitor='val_loss')
    ]
    
    # Configuración para evitar advertencias de TensorFlow
    tf.get_logger().setLevel('ERROR')
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=params["epochs"],
        batch_size=params["batch_size"],
        callbacks=callbacks,
        verbose=1
    )
    
    return model, history.history

def evaluate_model(
    model: tf.keras.Model,
    X: np.ndarray,
    y: np.ndarray,
    target_scaler: StandardScaler
) -> Dict:
    """Evalúa el modelo y retorna métricas."""
    y_pred = model.predict(X, verbose=0)
    y_true = target_scaler.inverse_transform(y.reshape(-1, 1))
    y_pred = target_scaler.inverse_transform(y_pred)
    
    return {
        'MAE': mean_absolute_error(y_true, y_pred),
        'MSE': mean_squared_error(y_true, y_pred),
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'R2': r2_score(y_true, y_pred),
        'ExplainedVar': explained_variance_score(y_true, y_pred)
    }

def cross_validate(
    X: pd.DataFrame,
    y: pd.Series,
    params: Dict,
    n_splits: int = 5
) -> Tuple[Dict, str]:
    """Ejecuta validación cruzada."""
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    metrics = []
    best_rmse = float('inf')
    best_model_path = ""
    
    # Convertir a arrays numpy para el entrenamiento
    X_array = X.values
    y_array = y.values
    
    # Directorios para guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(f"models/{timestamp}", exist_ok=True)
    os.makedirs(f"results/{timestamp}", exist_ok=True)
    
    for fold, (train_idx, val_idx) in enumerate(kf.split(X_array)):
        print(f"\nFold {fold + 1}/{n_splits}")
        
        # División y escalado
        X_train, X_val = X_array[train_idx], X_array[val_idx]
        y_train, y_val = y_array[train_idx], y_array[val_idx]
        
        scaler_X = StandardScaler()
        X_train_scaled = scaler_X.fit_transform(X_train)
        X_val_scaled = scaler_X.transform(X_val)
        
        scaler_y = StandardScaler()
        y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1))
        y_val_scaled = scaler_y.transform(y_val.reshape(-1, 1))
        
        # Modelo
        model = build_model(X_train_scaled.shape[1], params)
        
        # Entrenamiento
        model_path = f"models/{timestamp}/fold_{fold}.keras"
        model, history = train_and_evaluate(
            model,
            X_train_scaled,
            y_train_scaled,
            X_val_scaled,
            y_val_scaled,
            params,
            model_path
        )
        
        # Evaluación
        fold_metrics = evaluate_model(model, X_val_scaled, y_val_scaled, scaler_y)
        metrics.append(fold_metrics)
        
        # Actualizar mejor modelo
        if fold_metrics['RMSE'] < best_rmse:
            best_rmse = fold_metrics['RMSE']
            best_model_path = model_path
    
    # Métricas promedio
    avg_metrics = {k: np.mean([m[k] for m in metrics]) for k in metrics[0]}
    return avg_metrics, best_model_path

def main():
    # Cargar datos
    X, y = load_and_prepare_data("./csv/Concretetest.csv")
    
    # Configuración de hiperparámetros
    params = {
        "layers": [256, 128, 64],
        "activation": "swish",
        "dropout": 0.2,
        "batch_norm": True,
        "l2_reg": 0.001,
        "learning_rate": 0.001,
        "decay_steps": 1000,
        "decay_rate": 0.9,
        "epochs": 500,
        "batch_size": 64,
        "patience": 30,
        "reduce_lr_patience": 10
    }
    
    # Validación cruzada
    metrics, best_model_path = cross_validate(X, y, params)
    
    print("\nResultados de Validación Cruzada:")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
    
    # Cargar el mejor modelo
    best_model = tf.keras.models.load_model(best_model_path)
    
    # Evaluación final (opcional)
    scaler_X = StandardScaler().fit(X.values)
    scaler_y = StandardScaler().fit(y.values.reshape(-1, 1))
    X_scaled = scaler_X.transform(X.values)
    y_scaled = scaler_y.transform(y.values.reshape(-1, 1))
    
    final_metrics = evaluate_model(best_model, X_scaled, y_scaled, scaler_y)
    
    print("\nEvaluación Final:")
    for k, v in final_metrics.items():
        print(f"{k}: {v:.4f}")
    
    # Guardar modelo final
    best_model.save("models/best_model_final.keras")
    print("\nModelo final guardado en: models/best_model_final.keras")

if __name__ == "__main__":
    main()