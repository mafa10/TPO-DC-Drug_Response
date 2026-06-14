"""
Análisis de Machine Learning - TPO Orquestación de Datos
Responsable: Tomás Lecuenis

Este script implementa un modelo de aprendizaje SUPERVISADO para predecir
la potencia de un fármaco (ln_ic50) basado en características experimentales.
"""

import duckdb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

def run_ml_pipeline():
    # 1. CONEXIÓN Y CARGA DE DATOS
    print("Cargando datos desde DuckDB...")
    try:
        con = duckdb.connect('TPO_DATA.duckdb')
        df = con.execute("SELECT * FROM mart_ML_drugresponse").df()
        con.close()
    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"Dataset cargado: {df.shape[0]} filas.")

    # 2. SELECCIÓN DE VARIABLES
    y = df['ln_ic50']
    features_cols = [
        'dose_amplitude', 'min_concentration', 'max_concentration', 
        'rmse_score', 'z_score', 'cancer_type', 'biological_pathway'
    ]
    X = df[features_cols]

    # 3. PREPROCESAMIENTO (Encoding)
    print("Realizando One-Hot Encoding...")
    X = pd.get_dummies(X, columns=['cancer_type', 'biological_pathway'], drop_first=True)

    # 4. DIVISIÓN DEL DATASET
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 5. ESCALADO DE DATOS (Scaling)
    print("Escalando datos numéricos...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 6. ENTRENAMIENTO
    print("Entrenando Random Forest... (esto puede demorar)")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)

    # 7. PREDICCIÓN Y MÉTRICAS
    y_pred = model.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # 8. ANÁLISIS DE IMPORTANCIA DE VARIABLES (Texto)
    importances = model.feature_importances_
    feature_names = X.columns
    feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

    print("\n=========================================")
    print("RESULTADOS TÉCNICOS DEL MODELO")
    print("=========================================")
    print(f"R2 Score (Precisión): {r2:.4f}")
    print(f"MSE (Error): {mse:.4f}")
    print("-----------------------------------------")
    print("TOP 10 VARIABLES CON MÁS IMPACTO:")
    # Mostramos las 10 variables que más influyen en el resultado
    print(feature_importance_df.head(10).to_string(index=False))
    print("=========================================\n")

if __name__ == "__main__":
    run_ml_pipeline()
