import os
import shutil
from datetime import datetime

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
                # Obtiene la fecha del archivo (suponiendo que la fecha está al inicio del nombre del archivo)
                fecha_str = archivo.split("--")[0]  # Extrae la parte antes de '--'
                try:
                    # Convierte la cadena de fecha a un objeto datetime
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d_%H-%M-%S").date()
                    # Crea el nombre de la subcarpeta con la fecha
                    subcarpeta = os.path.join(carpeta, str(fecha))
                    # Crea la subcarpeta si no existe
                    os.makedirs(subcarpeta, exist_ok=True)
                    # Mueve el archivo a la subcarpeta correspondiente
                    shutil.move(os.path.join(carpeta, archivo), os.path.join(subcarpeta, archivo))
                except ValueError:
                    print(f"El archivo '{archivo}' no tiene un formato de fecha válido.")

print("Organización completada.")
