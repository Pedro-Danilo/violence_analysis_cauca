import psycopg2
import pandas as pd
import os
from consultas_sql import consultas  # Importa el diccionario de consultas

# Configuración de la conexión
conn_params = {
    "host": "localhost",
    "port": "5432",
    "database": "db_proyecto",
    "user": "postgres",
    "password": "cauca"
}
# Directorio de salida
output_dir = 'D:/CUN/Analitica_de_datos_especializacion/proyecto_grado/ejecucion_proyecto/CSV_finales'

# Asegurar que el directorio de salida exista
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Manejo de la conexión
try:
    with psycopg2.connect(**conn_params) as conn:
        for consulta_nombre, query in consultas.items():
            try:
                # Ejecutar la consulta
                df = pd.read_sql_query(query, conn)
                print(f"Consulta '{consulta_nombre}' ejecutada exitosamente.")
                
                # Definir el nombre del archivo de salida
                output_file = os.path.join(output_dir, f'{consulta_nombre}.csv')

                # Guardar resultado de la consulta en archivo CSV
                df.to_csv(output_file, index=False)
                print(f"Archivo guardado en: {output_file}")

            except Exception as e:
                print(f"Error al ejecutar la consulta '{consulta_nombre}': {e}")
                continue  # Continuar con la siguiente consulta si ocurre un error
except Exception as e:
    print(f"Error al conectar con la base de datos: {e}")
    raise