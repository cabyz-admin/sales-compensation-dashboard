"""
Análisis profundo de archivos Excel para identificar métricas adicionales
"""

import pandas as pd
import numpy as np
import json

# Analizar archivo 1: Salesprocess.io Business Unit Case Economics
print("="*80)
print("📊 ANÁLISIS: Salesprocess.io Business Unit Case Economics")
print("="*80)

try:
    # Leer todas las hojas
    excel_file1 = pd.ExcelFile('/Users/castillo/CascadeProjects/comp-structure/Copy of Copy of Salesprocess.io Business Unit Case Economics.xlsx')
    print(f"\n📋 Hojas disponibles: {excel_file1.sheet_names}")
    
    for sheet_name in excel_file1.sheet_names[:5]:  # Primeras 5 hojas
        print(f"\n--- Hoja: {sheet_name} ---")
        df = pd.read_excel(excel_file1, sheet_name=sheet_name, nrows=20)
        print(f"Dimensiones: {df.shape}")
        print(f"Columnas: {list(df.columns)[:10]}")  # Primeras 10 columnas
        
        # Buscar métricas clave
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['ltv', 'cac', 'arpu', 'churn', 'mrr', 'arr', 'payback', 'margin', 'ebitda']):
                print(f"  💰 Métrica encontrada: {col}")
        
        # Buscar valores numéricos interesantes
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print(f"  📈 Columnas numéricas: {list(numeric_cols)[:5]}")

except Exception as e:
    print(f"Error: {e}")

# Analizar archivo 2: Sales Compensation Plan CSV
print("\n" + "="*80)
print("📊 ANÁLISIS: Sales Compensation Plan - AE Model")
print("="*80)

try:
    df2 = pd.read_csv('/Users/castillo/CascadeProjects/comp-structure/Copy of Sales Compensation Plan (MAKE A COPY) - AE Compensation Model.csv')
    print(f"\nDimensiones: {df2.shape}")
    print(f"Columnas: {list(df2.columns)}")
    
    # Mostrar primeras filas para entender estructura
    print("\nPrimeras filas:")
    print(df2.head())
    
    # Buscar patrones de compensación
    for col in df2.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['quota', 'commission', 'bonus', 'tier', 'rate', 'target', 'achievement', 'payout']):
            print(f"  💵 Compensación: {col}")
            if df2[col].dtype in [np.float64, np.int64]:
                print(f"    - Min: {df2[col].min()}, Max: {df2[col].max()}, Mean: {df2[col].mean():.2f}")

except Exception as e:
    print(f"Error: {e}")

# Analizar archivo 3: Sales Compensation Plan XLSX
print("\n" + "="*80)
print("📊 ANÁLISIS: Sales Compensation Plan Excel")
print("="*80)

try:
    excel_file3 = pd.ExcelFile('/Users/castillo/CascadeProjects/comp-structure/Copy of Sales Compensation Plan (MAKE A COPY).xlsx')
    print(f"\n📋 Hojas disponibles: {excel_file3.sheet_names}")
    
    for sheet_name in excel_file3.sheet_names[:5]:  # Primeras 5 hojas
        print(f"\n--- Hoja: {sheet_name} ---")
        try:
            df3 = pd.read_excel(excel_file3, sheet_name=sheet_name, nrows=30)
            print(f"Dimensiones: {df3.shape}")
            
            # Identificar estructuras de compensación
            for col in df3.columns:
                col_str = str(col).lower()
                # Buscar métricas de compensación avanzadas
                if any(keyword in col_str for keyword in [
                    'accelerator', 'decelerator', 'spiff', 'kicker', 'draw', 
                    'clawback', 'tier', 'band', 'threshold', 'excellence',
                    'ote', 'variable', 'base', 'multiplier', 'factor',
                    'ramp', 'guarantee', 'floor', 'cap', 'ceiling'
                ]):
                    print(f"  🎯 Estructura avanzada: {col}")
            
            # Buscar métricas de rendimiento
            for col in df3.columns:
                col_str = str(col).lower()
                if any(keyword in col_str for keyword in [
                    'activity', 'call', 'meeting', 'pipeline', 'forecast',
                    'conversion', 'win rate', 'cycle', 'velocity', 'productivity'
                ]):
                    print(f"  📈 Métrica de rendimiento: {col}")
                    
        except Exception as sheet_error:
            print(f"  Error en hoja {sheet_name}: {sheet_error}")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
print("🔍 INSIGHTS PARA INGENIERÍA INVERSA")
print("="*80)

insights = """
Basado en el análisis, aquí están las opciones de ingeniería inversa que podemos añadir:

1. **REVERSE ENGINEERING DE QUOTA** 🎯
   - Dado: EBITDA objetivo
   - Calcular: Quota individual por rep
   - Variables: # de reps, win rate promedio, deal size

2. **REVERSE ENGINEERING DE ESTRUCTURA DE COMPENSACIÓN** 💰
   - Dado: Costo total de compensación objetivo
   - Calcular: Mix óptimo base/variable
   - Variables: OTE target, # de reps por nivel

3. **REVERSE ENGINEERING DE ACTIVIDAD** 📊
   - Dado: Revenue objetivo
   - Calcular: Actividades diarias requeridas
   - Variables: Conversion rates en cada etapa

4. **REVERSE ENGINEERING DE HEADCOUNT** 👥
   - Dado: Pipeline coverage objetivo (3x-5x)
   - Calcular: # de SDRs/AEs necesarios
   - Variables: Productividad por rep, ramp time

5. **REVERSE ENGINEERING DE TERRITORIOS** 🗺️
   - Dado: TAM y market share objetivo
   - Calcular: # de territorios y tamaño
   - Variables: Penetración esperada, capacity por rep

6. **REVERSE ENGINEERING DE RAMP TIME** 📈
   - Dado: Productividad objetivo en mes X
   - Calcular: Plan de ramp y draw necesario
   - Variables: Learning curve, complejidad producto

7. **REVERSE ENGINEERING DE ACCELERADORES** 🚀
   - Dado: Costo de comp objetivo en overachievement
   - Calcular: Estructura de acceleradores óptima
   - Variables: Distribution de performance histórica

8. **REVERSE ENGINEERING DE SPIFFS/BONUSES** 🎁
   - Dado: Comportamiento deseado (ej: más upsells)
   - Calcular: Estructura de incentivos especiales
   - Variables: Impacto histórico de spiffs

9. **REVERSE ENGINEERING DE CLAWBACK** ⚖️
   - Dado: Riesgo aceptable de churn
   - Calcular: Política de clawback necesaria
   - Variables: Churn rate, deal quality

10. **REVERSE ENGINEERING DE CAPACITY PLANNING** 📅
    - Dado: Pipeline objetivo por quarter
    - Calcular: Hiring plan con lead time
    - Variables: Attrition, ramp time, seasonality
"""

print(insights)
