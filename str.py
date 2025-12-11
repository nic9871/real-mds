import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="S.I.R.A. - Ingeniería",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS idénticos a los tuyos
st.markdown("""
<style>
    .main-header {font-size: 2rem; font-weight: bold; color: #2c3e50; margin-bottom: 20px;}
    .section-header {font-size: 1.5rem; font-weight: bold; color: #34495e; margin-top: 30px; margin-bottom: 10px;}
    .chart-header {font-size: 1.1rem; font-weight: bold; color: #555; text-align: center;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATOS DE ESTUDIANTES (Copiados de tu captura 'Análisis de Estudiantes')
# -----------------------------------------------------------------------------
def generar_base_ejemplo():
    data = {
        "Matriculas": ["2021415201", "2020784512", "2019563289", "2018451278", "2021129834"],
        "Código de carrera": [3309, 3310, 3318, 3311, 3319],
        "Asignaturas reprobadas": [5, 0, 3, 7, 1], 
        "Semestres de atraso": [4, 0, 2, 6, 0],
        "Nivel de motivación": [1.5, 5.0, 3.0, 1.2, 4.2], 
        "Nivel de confianza": [2.0, 5.0, 3.0, 1.5, 4.0],
        "Puntaje PSU": [500, 720, 600, 450, 680]
    }
    return pd.DataFrame(data)

# -----------------------------------------------------------------------------
# 3. DATOS HISTÓRICOS "HARDCODEADOS" (Copiados de tus Tablas y Gráficos)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data_mockup():
    nombres_carreras = {
        3309: "Ing. Civil Industrial", 3310: "Ing. Civil", 
        3311: "Ing. Civil Eléctrica", 3318: "Ing. Civil Electrónica", 
        3319: "Ing. Civil Informática"
    }

    # DATOS EXACTOS DE TUS CAPTURAS (Tablas 1 y 2)
    # Nota: Los Puntajes PSU los estimé basándome en la altura de las barras de tu gráfico
    # ya que en la tabla salían cortados, pero se verán visualmente correctos.
    data_history = {
        "Código de carrera": [3309, 3310, 3311, 3318, 3319],
        "Carrera": ["Ing. Civil Industrial", "Ing. Civil", "Ing. Civil Eléctrica", "Ing. Civil Electrónica", "Ing. Civil Informática"],
        "Media de asignaturas reprobadas": [1.2135, 1.5040, 1.8317, 1.3988, 2.2520],
        "Media de nivel de motivación": [3.9831, 3.4685, 3.7933, 3.3988, 3.5203],
        "Media de nivel de confianza": [3.7093, 3.6022, 3.4309, 3.3396, 3.5711],
        "Estudiantes que planean abandono": [8, 10, 0, 0, 0],
        "Media semestres adicionales": [2.6389, 3.1231, 2.2917, 4.8000, 3.2381],
        "Mediana semestres adicionales": [2, 3, 2, 2, 2],
        "Media puntaje ponderado": [702.5, 709.0, 678.0, 662.0, 658.0], 
        "Mediana puntaje ponderado": [700, 710, 680, 660, 655] 
    }
    df_history = pd.DataFrame(data_history)

    # MATRIZ DE CORRELACIÓN EXACTA (Copiada píxel por píxel de tu mapa de calor)
    cols_corr = [
        "Media de asignaturas reprobadas", "Media de nivel de motivación", "Media de nivel de confianza",
        "Estudiantes que planean abandono", "Media semestres adicionales", "Mediana semestres adicionales",
        "Media puntaje ponderado", "Mediana puntaje ponderado"
    ]
    
    # Valores extraídos de tu imagen
    datos_matriz = [
        [1.00, -0.27, -0.14, -0.59, -0.18, -0.19, -0.62, -0.63],
        [-0.27, 1.00, 0.52, 0.24, -0.75, -0.37, 0.41, 0.42],
        [-0.14, 0.52, 1.00, 0.74, -0.57, 0.27, 0.65, 0.70],
        [-0.59, 0.24, 0.74, 1.00, -0.29, 0.72, 0.95, 0.96],
        [-0.18, -0.75, -0.57, -0.29, 1.00, -0.06, -0.47, -0.45],
        [-0.19, -0.37, 0.27, 0.72, -0.06, 1.00, -0.15, -0.12], # Valores finales estimados por corte de img
        [-0.62, 0.41, 0.65, 0.95, -0.47, -0.15, 1.00, 0.98],
        [-0.63, 0.42, 0.70, 0.96, -0.45, -0.12, 0.98, 1.00]
    ]
    
    matriz_correlacion = pd.DataFrame(datos_matriz, columns=cols_corr, index=cols_corr)

    # Cargar alumnos
    usu = generar_base_ejemplo()

    # CÁLCULO DE RIESGO (Misma lógica original)
    mapa_cols = {
        "Asignaturas reprobadas": "Media de asignaturas reprobadas",
        "Nivel de motivación": "Media de nivel de motivación",
        "Nivel de confianza": "Media de nivel de confianza",
        "Puntaje PSU": "Media puntaje ponderado",
        "Semestres de atraso": "Media semestres adicionales"
    }
    negativos = ["Asignaturas reprobadas", "Semestres de atraso"]
    positivos = ["Nivel de motivación", "Nivel de confianza", "Puntaje PSU"]
    
    indices_riesgo = []
    for idx, row in usu.iterrows():
        cod = row["Código de carrera"]
        ref = df_history[df_history["Código de carrera"] == cod]
        if ref.empty:
            indices_riesgo.append(0)
            continue
        puntos_riesgo = 0
        total = 0
        for col_usu, col_hist in mapa_cols.items():
            if col_usu in usu.columns:
                val_est = row[col_usu]
                val_ref = ref[col_hist].values[0]
                if col_usu in negativos and val_est > val_ref: puntos_riesgo += 1
                elif col_usu in positivos and val_est < val_ref: puntos_riesgo += 1
                total += 1
        indices_riesgo.append(puntos_riesgo / total if total > 0 else 0)

    usu["Índice de Riesgo"] = indices_riesgo
    usu["Carrera"] = usu["Código de carrera"].map(nombres_carreras)

    return df_history, matriz_correlacion, usu, "estudiantes_demo_final.csv", nombres_carreras

# --- Carga ---
df_hist, corr_matrix, df_alumnos, nombre_archivo, nombres_map = load_data_mockup()

# -----------------------------------------------------------------------------
# 4. INTERFAZ GRÁFICA (Visualización)
# -----------------------------------------------------------------------------

st.markdown('<div class="main-header">S.I.R.A.</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Sistema de Identificación de Riesgo Académico</div>', unsafe_allow_html=True)

if df_hist is not None:
    
    # --- SECCIÓN 1: PANORAMA GENERAL ---
    st.markdown('<div class="section-header">1. Panorama Histórico por Carrera</div>', unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("Rendimiento y Motivación")
        cols_acad = ["Carrera", "Media de asignaturas reprobadas", "Media de nivel de motivación", 
                     "Media de nivel de confianza", "Estudiantes que planean abandono"]
        st.dataframe(df_hist[cols_acad], use_container_width=True)
        
    with col_t2:
        st.subheader("Ingreso y Egreso (Detalle)")
        cols_stats = ["Carrera", "Media semestres adicionales", "Mediana semestres adicionales", 
                      "Media puntaje ponderado", "Mediana puntaje ponderado"]
        st.dataframe(df_hist[cols_stats], use_container_width=True)

    # --- SECCIÓN 2: VISUALIZACIONES ---
    st.markdown('<div class="section-header">2. Comparativa Visual de Indicadores</div>', unsafe_allow_html=True)
    carreras_label = df_hist["Carrera"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-header">Media Asignaturas Reprobadas (Riesgo)</div>', unsafe_allow_html=True)
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.bar(carreras_label, df_hist["Media de asignaturas reprobadas"], color="#e74c3c", edgecolor="black")
        plt.xticks(rotation=20, ha='right', fontsize=9)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig1)

    with col2:
        st.markdown('<div class="chart-header">Nivel de Motivación Promedio (Protector)</div>', unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.bar(carreras_label, df_hist["Media de nivel de motivación"], color="#3498db", edgecolor="black")
        plt.xticks(rotation=20, ha='right', fontsize=9)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig2)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="chart-header">Atraso Curricular (Semestres)</div>', unsafe_allow_html=True)
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        ax3.bar(carreras_label, df_hist["Media semestres adicionales"], color="#e67e22", edgecolor="black")
        plt.xticks(rotation=20, ha='right', fontsize=9)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig3)

    with col4:
        st.markdown('<div class="chart-header">Puntaje de Ingreso Promedio (PSU)</div>', unsafe_allow_html=True)
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        ax4.bar(carreras_label, df_hist["Media puntaje ponderado"], color="#2ecc71", edgecolor="black")
        plt.xticks(rotation=20, ha='right', fontsize=9)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig4)

    st.markdown("---")

    # --- SECCIÓN 3: CORRELACIONES ---
    st.markdown('<div class="section-header">3. Matriz de Correlación Estadística</div>', unsafe_allow_html=True)
    
    c_corr1, c_corr2 = st.columns([1, 1.5])
    with c_corr1:
        st.write("Coeficientes de Pearson:")
        st.dataframe(corr_matrix, use_container_width=True, height=400)

    with c_corr2:
        st.write("Mapa de Calor de Relaciones:")
        fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, cbar_kws={'label': 'Correlación'})
        st.pyplot(fig_corr)

    st.markdown("---")

    # --- SECCIÓN 4: DETECTOR DE RIESGO ---
    st.markdown(f'<div class="section-header">4. Análisis de Estudiantes (Archivo: {nombre_archivo})</div>', unsafe_allow_html=True)
    
    umbral = st.slider("Filtrar estudiantes con Índice de Riesgo superior a:", 0.0, 1.0, 0.0, 0.1)
    df_filtrado = df_alumnos[df_alumnos["Índice de Riesgo"] >= umbral]

    def color_risk(val):
        if val >= 0.8: return 'background-color: #ff9999; color: black; font-weight: bold'
        if val >= 0.4: return 'background-color: #ffcccc; color: black'
        if val == 0: return 'background-color: #ccffcc; color: green'
        return ''

    st.dataframe(
        df_filtrado.style.map(color_risk, subset=["Índice de Riesgo"])
                    .format({"Índice de Riesgo": "{:.2%}"}),
        use_container_width=True
    )