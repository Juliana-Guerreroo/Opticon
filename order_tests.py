import pandas as pd
import os
import shutil
import datetime

file_path_result = 'results'
file_path_models = 'best_models'
file_path_images = 'images'
best_models=[]

# Leer archivos en 'results' y llenar la lista de mejores modelos
if os.path.exists(file_path_result):
    for file in os.listdir(file_path_result):
        if os.path.isfile(os.path.join(file_path_result,file)):
            df = pd.read_csv(os.path.join(file_path_result,file))
            df = df[df["MAE"] <= 55]
            best_models.extend(df['Ruta del modelo'].astype(str).tolist())  # Convertir a lista de strings
            
        
# Convertir las rutas relativas de best_models a rutas absolutas
best_models = {os.path.abspath(model_path) for model_path in best_models}

# Borrar modelos que no están en la lista best_models
if os.path.exists(file_path_models):
    for model_file in os.listdir(file_path_models):
        model_path = os.path.join(file_path_models, model_file)
        if os.path.isfile(model_path) and os.path.abspath(model_path) not in best_models:
            os.remove(model_path)
            print(f"Borrado modelo: {model_path}")
            

# Obtener las rutas de las imágenes correspondientes a los mejores modelos
best_images = set()
for model_path in best_models:
    model_name = os.path.basename(model_path)
    image_name = model_name.replace('.keras', '_loss_curve.jpg')
    image_path = os.path.join(file_path_images, image_name)
    if os.path.exists(image_path):
        best_images.add(os.path.abspath(image_path))

print(best_images)
# Eliminar las imágenes que no correspondan a los mejores modelos
if os.path.exists(file_path_images):
    for image_file in os.listdir(file_path_images):
        image_path = os.path.join(file_path_images, image_file)
        if os.path.isfile(image_path) and os.path.abspath(image_path) not in best_images:
            os.remove(image_path)
            print(f"Imagen eliminada: {image_path}")
            

# Define las carpetas principales
carpetas_principales = ["results", "images", "best_models", "predictions"]

# Itera sobre cada carpeta
for carpeta in carpetas_principales:
    # Verifica si la carpeta existe
    if os.path.exists(carpeta):
        # Itera sobre los archivos en la carpeta
        for archivo in os.listdir(carpeta):
            # Verifica si es un archivo (no una carpeta)
            if os.path.isfile(os.path.join(carpeta, archivo)):
                # Obtiene la fecha y hora del archivo (suponiendo que están al inicio del nombre del archivo)
                fecha_str = archivo.split("--")[0]  # Extrae la parte antes de '--'
                try:
                    # Convierte la cadena de fecha y hora a un objeto datetime
                    fecha_hora = datetime.strptime(fecha_str, "%Y-%m-%d_%H-%M-%S")
                    
                    # Crea el nombre de la subcarpeta con la fecha y la subcarpeta con la hora
                    subcarpeta_fecha = os.path.join(carpeta, fecha_hora.strftime("%Y-%m-%d"))
                    subcarpeta_hora = os.path.join(subcarpeta_fecha, fecha_hora.strftime("%H-%M-%S"))
                    
                    # Crea las subcarpetas si no existen
                    os.makedirs(subcarpeta_hora, exist_ok=True)
                    
                    # Mueve el archivo a la subcarpeta correspondiente
                    shutil.move(os.path.join(carpeta, archivo), os.path.join(subcarpeta_hora, archivo))
                
                except ValueError:
                    print(f"El archivo '{archivo}' no tiene un formato de fecha válido.")

print("Organización completada.")