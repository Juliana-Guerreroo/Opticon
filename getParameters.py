import tensorflow as tf

# Cargar el modelo .keras
modelo = tf.keras.models.load_model('./best_models/2024-11-01/15-42-58/2024-11-01_15-42-58--model_9.keras')

# Obtener configuración general del modelo
configuracion = modelo.get_config()
print(configuracion)  # Muestra detalles de cada capa

for capa in modelo.layers:
    print(f"Nombre de la capa: {capa.name}")
    print(f"Tipo de capa: {type(capa)}")
    print("Configuración:", capa.get_config())
    print("----")