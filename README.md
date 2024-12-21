# Análisis de Machine Learning sobre Violencia en el Cauca

## Descripción del Proyecto
Este repositorio contiene la segunda parte del proyecto de investigación titulado *"Violencia en el Cauca (2019-2023): Análisis mediante Técnicas de Machine Learning"*. La primera etapa consistió en la creación de una mega-base de datos relacional, accesible en el repositorio [violence_mega_database](https://github.com/Pedro-Danilo/violence_mega_database), que centraliza información socioeconómica y de violencia en Colombia.

La segunda etapa, documentada aquí, se enfoca en el análisis de los datos específicos del Departamento del Cauca utilizando técnicas de machine learning. Este análisis incluye la extracción, transformación e integración de datos, así como la aplicación de modelos no supervisados y supervisados para descubrir patrones y relaciones entre variables de violencia y socioeconómicas.

---

## Contenido del Repositorio

### Estructura del Proyecto
```plaintext
violence_analysis_cauca/
├── data/                  # Archivos CSV generados por consultas SQL
├── models/                # Notebooks y datasets para modelado
├── results/               # Informe final del proyecto
├── scripts/               # Scripts para consultas SQL y generación de datasets
├── README.md              # Documentación principal
├── LICENSE                # Licencia del repositorio
└── requirements.txt       # Dependencias de Python
```

### Descripción de Carpetas y Archivos

#### **1. data/**
Contiene 52 archivos CSV resultantes de consultas SQL ejecutadas contra la mega-base de datos. Estos archivos incluyen datos sobre violencia y variables socioeconómicas del Departamento del Cauca. Ejemplo de archivos:
- `armas_confiscadas_polinal.csv`
- `cultivos_coca.csv`
- `tasas_alfabetas_censo_2018.csv`

Estos archivos se incluyen para facilitar la reproducción del análisis o su adaptación a otros contextos.

#### **2. models/**
- **`construccion_dataset_final.ipynb`**: Notebook en Google Colab para integrar los 52 datasets en un único dataset final (`df_final.csv`).
- **`transformaciones_para_ML.ipynb`**: Contiene las transformaciones aplicadas a `df_final.csv`, generando dos vistas minables:
  - `df_violencia_final.csv`
  - `df_socieconomico_final.csv`
- **`modelado.ipynb`**: Implementa PCA, k-means y detección de anomalías sobre `df_violencia_final.csv`.
- **`modelado_parte_2.ipynb`**: Modelado de `df_socieconomico_final.csv` mediante regresión logística usando los clústeres generados por k-means.

#### **3. results/**
- **`Documento_final.pdf`**: Informe final del proyecto que detalla la creación de la mega-base de datos y los análisis de machine learning.

#### **4. scripts/**
- **`consultas_sql.py`**: Diccionario con las 52 consultas SQL.
- **`procesamiento_consultas_sql.py`**: Script que ejecuta automáticamente las consultas SQL y genera los archivos CSV en `data/`.

Estos scripts se incluyen para facilitar la reproducción del análisis o su adaptación a otros contextos.
---

## Requisitos Previos

1. **Software necesario**:
   - Python 3.8 o superior.
   - PostgreSQL (si deseas reproducir las consultas SQL).
2. **Librerías Python**: Ver archivo `requirements.txt`.
3. **Espacio en disco**: Aproximadamente 500 MB para datos y resultados.

---

## Pasos para Reproducir el Análisis

### 1. Clonar el Repositorio
```bash
git clone https://github.com/Pedro-Danilo/violence_analysis_cauca.git
cd violence_analysis_cauca
```

### 2. Instalar Dependencias
Recomendamos crear un entorno virtual:
```bash
python -m venv env
source env/bin/activate # Para Linux/Mac
env\Scripts\activate   # Para Windows
pip install -r requirements.txt
```

### 3. Generar Archivos CSV (Opcional)
Si deseas regenerar los 52 archivos CSV:
1. Configura las credenciales de tu base de datos PostgreSQL en `procesamiento_consultas_sql.py`.
2. Ejecuta el script:
   ```bash
   python scripts/procesamiento_consultas_sql.py
   ```

### 4. Ejecutar los Notebooks
Sigue este orden:
1. **`construccion_dataset_final.ipynb`**: Integra los datasets en `df_final.csv`.
2. **`transformaciones_para_ML.ipynb`**: Genera las vistas minables.
3. **`modelado.ipynb`**: Realiza el análisis de violencia.
4. **`modelado_parte_2.ipynb`**: Modela las variables socioeconómicas.

---

## Resultados y Conexión con la Mega-Base de Datos

El análisis aquí presentado complementa la mega-base de datos accesible en [violence_mega_database](https://github.com/Pedro-Danilo/violence_mega_database). Ambos repositorios están interconectados para ofrecer un marco integral de análisis de la violencia en el Cauca.

### Productos Generados:
- Perfiles de violencia en municipios del Cauca basados en clústeres de k-means.
- Relaciones entre variables socioeconómicas y niveles de violencia mediante regresión logística.

---

## Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.