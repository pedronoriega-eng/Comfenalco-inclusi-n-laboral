# -*- coding: utf-8 -*-
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  APLICACIÓN WEB — Generador de Informe Técnico de Inclusión Laboral        ║
# ║  Programa Talento Sin Barreras — Comfenalco Santander                     ║
# ║                                                                            ║
# ║  Ejecutar: streamlit run app.py                                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import tempfile
import os
import time
import io
from pathlib import Path
from datetime import datetime

# ── Módulos del proyecto con recarga forzada para Streamlit Cloud ────
import importlib
import motor_documental
import ai_agents

importlib.reload(motor_documental)
importlib.reload(ai_agents)

from motor_documental import DatosProyecto, MotorDocumental, generar_informe
from ai_agents import (
    SistemaMultiagente,
    extraer_texto_docx,
    extraer_datos_manual,
    verificar_api_key,
    GEMINI_DISPONIBLE,
)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CONFIGURACIÓN DE PÁGINA                                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

st.set_page_config(
    page_title="Informe APT — Talento Sin Barreras",
    page_icon="🧡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  ESTILOS CSS PERSONALIZADOS                                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

st.markdown("""
<style>
    /* ─── Fuente global ─── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ─── Variables de color ─── */
    :root {
        --naranja: #F39200;
        --naranja-hover: #E08500;
        --naranja-glow: rgba(243, 146, 0, 0.3);
        --carbon: #1A1A1B;
        --carbon-light: #2D2D2E;
        --carbon-lighter: #3A3A3B;
        --blanco: #FFFFFF;
        --gris-texto: #B0B0B0;
        --verde-ok: #00C853;
        --rojo-error: #FF5252;
    }

    /* ─── Header principal ─── */
    .main-header {
        background: linear-gradient(135deg, #1A1A1B 0%, #2D2D2E 50%, #1A1A1B 100%);
        border: 1px solid rgba(243, 146, 0, 0.2);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #F39200, #FFB74D, #F39200);
    }
    .main-header h1 {
        color: #FFFFFF;
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .main-header .subtitle {
        color: #F39200;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 0.25rem;
    }
    .main-header .legal {
        color: #B0B0B0;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }

    /* ─── Cards de sección ─── */
    .section-card {
        background: linear-gradient(180deg, #2D2D2E 0%, #252526 100%);
        border: 1px solid #3A3A3B;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.3s ease;
    }
    .section-card:hover {
        border-color: rgba(243, 146, 0, 0.4);
    }
    .section-title {
        color: #F39200;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ─── Status badges ─── */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-success {
        background: rgba(0, 200, 83, 0.15);
        color: #00C853;
        border: 1px solid rgba(0, 200, 83, 0.3);
    }
    .badge-warning {
        background: rgba(243, 146, 0, 0.15);
        color: #F39200;
        border: 1px solid rgba(243, 146, 0, 0.3);
    }
    .badge-error {
        background: rgba(255, 82, 82, 0.15);
        color: #FF5252;
        border: 1px solid rgba(255, 82, 82, 0.3);
    }
    .badge-info {
        background: rgba(100, 181, 246, 0.15);
        color: #64B5F6;
        border: 1px solid rgba(100, 181, 246, 0.3);
    }

    /* ─── Botón principal ─── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #F39200 0%, #E08500 100%);
        color: white;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(243, 146, 0, 0.3);
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(243, 146, 0, 0.5);
    }

    /* ─── Upload area ─── */
    .upload-zone {
        border: 2px dashed rgba(243, 146, 0, 0.4);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        background: rgba(243, 146, 0, 0.05);
        transition: all 0.3s ease;
    }
    .upload-zone:hover {
        border-color: #F39200;
        background: rgba(243, 146, 0, 0.1);
    }

    /* ─── Pipeline visual ─── */
    .pipeline {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 1.5rem 0;
        padding: 1rem;
        background: rgba(45, 45, 46, 0.8);
        border-radius: 12px;
        border: 1px solid #3A3A3B;
    }
    .pipeline-step {
        text-align: center;
        flex: 1;
        padding: 0.5rem;
    }
    .pipeline-step .icon {
        font-size: 2rem;
        margin-bottom: 0.25rem;
    }
    .pipeline-step .label {
        font-size: 0.75rem;
        color: #B0B0B0;
        font-weight: 500;
    }
    .pipeline-step.active .label {
        color: #F39200;
        font-weight: 700;
    }
    .pipeline-step.done .label {
        color: #00C853;
    }
    .pipeline-arrow {
        color: #3A3A3B;
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    .pipeline-arrow.active {
        color: #F39200;
    }

    /* ─── Stats cards ─── */
    .stat-card {
        background: linear-gradient(135deg, #2D2D2E, #353536);
        border: 1px solid #3A3A3B;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .stat-card .number {
        font-size: 2rem;
        font-weight: 800;
        color: #F39200;
    }
    .stat-card .label {
        font-size: 0.75rem;
        color: #B0B0B0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ─── Sidebar enhancements ─── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1A1B 0%, #151516 100%);
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #F39200;
    }

    /* ─── Animación de carga ─── */
    @keyframes pulse-orange {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .loading-pulse {
        animation: pulse-orange 1.5s ease-in-out infinite;
    }

    /* ─── Footer ─── */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #666;
        font-size: 0.75rem;
        border-top: 1px solid #3A3A3B;
        margin-top: 3rem;
    }
    .footer a {
        color: #F39200;
        text-decoration: none;
    }

    /* ─── Expander styling ─── */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* ─── Hide Streamlit branding ─── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ─── Log viewer ─── */
    .log-viewer {
        background: #0D0D0E;
        border: 1px solid #3A3A3B;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.8rem;
        color: #00C853;
        max-height: 300px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  ESTADO DE SESIÓN                                                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def init_session_state():
    """Inicializa variables de sesión."""
    # Detectar API key de secrets o env
    api_key_default = ""
    api_verificada_default = False
    
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key_default = st.secrets["GEMINI_API_KEY"]
            api_verificada_default = True
    except Exception:
        pass
        
    if not api_key_default:
        env_key = os.environ.get("GEMINI_API_KEY", "")
        if env_key:
            api_key_default = env_key
            api_verificada_default = True

    defaults = {
        "autenticado": False,
        "api_key": api_key_default,
        "api_verificada": api_verificada_default,
        "plantilla_cargada": False,
        "plantilla_bytes": None,
        "manual_cargado": False,
        "manual_bytes": None,
        "manual_datos": None,
        "fotos_cargadas": [],
        "fotos_bytes": {},
        "analisis_ejecutado": False,
        "analisis_resultado": None,
        "informe_generado": False,
        "informe_bytes": None,
        "informe_stats": None,
        "informe_logs": "",
        "fase_actual": "inicio",
        # Datos editables del informe
        "datos_empresa": None,
        "datos_cargo": None,
        "datos_accesibilidad": None,
        "datos_competencias": None,
        "datos_ajustes": None,
        "datos_conclusiones": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


# ── Verificación de Contraseña de Acceso ──
if not st.session_state.get("autenticado", False):
    # Ocultar sidebar en el login
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1A1A1B 0%, #2D2D2E 100%); border: 1px solid rgba(243, 146, 0, 0.2); border-radius: 16px; padding: 2.5rem; text-align: center; box-shadow: 0 8px 32px rgba(243, 146, 0, 0.15);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🔒</div>
            <h2 style="color: #FFFFFF; font-weight: 800; margin: 0; font-size: 1.6rem; letter-spacing: -0.02em;">Acceso Restringido</h2>
            <div style="color: #F39200; font-size: 0.95rem; font-weight: 600; margin-top: 0.25rem;">Talento Sin Barreras · Comfenalco</div>
            <p style="color: #B0B0B0; font-size: 0.8rem; margin-top: 0.5rem; margin-bottom: 2rem;">Ingrese la contraseña de seguridad para acceder al generador de informes APT.</p>
        </div>
        """, unsafe_allow_html=True)
        
        pass_input = st.text_input("Contraseña de Acceso", type="password", key="password_gate", placeholder="Escribe la contraseña aquí...")
        
        if st.button("🔓 Ingresar al Sistema", type="primary", use_container_width=True):
            if pass_input == "Comfenalco_2026":
                st.session_state.autenticado = True
                st.success("✓ Acceso concedido")
                time.sleep(0.5)
                st.rerun()
            elif pass_input != "":
                st.error("✗ Contraseña incorrecta. Por favor intente nuevamente.")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
    st.stop()


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  UTILIDADES                                                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

BASE_DIR = Path(__file__).parent


def guardar_archivo_temporal(uploaded_file, extension=None):
    """Guarda un archivo subido en un directorio temporal y retorna la ruta."""
    if extension is None:
        extension = Path(uploaded_file.name).suffix

    tmp_dir = BASE_DIR / "temp_uploads"
    tmp_dir.mkdir(exist_ok=True)

    ruta = tmp_dir / uploaded_file.name
    with open(ruta, "wb") as f:
        f.write(uploaded_file.getvalue())
    return str(ruta)


def limpiar_temporales():
    """Limpia archivos temporales."""
    tmp_dir = BASE_DIR / "temp_uploads"
    if tmp_dir.exists():
        for f in tmp_dir.iterdir():
            try:
                f.unlink()
            except Exception:
                pass


def obtener_api_key():
    """Obtiene la API key de Gemini desde secrets o session_state."""
    # Primero intentar desde Streamlit secrets (para deploy)
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    # Luego desde variable de entorno
    env_key = os.environ.get("GEMINI_API_KEY", "")
    if env_key:
        return env_key
    # Finalmente desde session_state (input del usuario)
    return st.session_state.get("api_key", "")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  HEADER PRINCIPAL                                                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

st.markdown("""
<div class="main-header">
    <h1>🧡 Informe Técnico de Inclusión Laboral</h1>
    <div class="subtitle">Programa Talento Sin Barreras — Comfenalco Santander</div>
    <div class="legal">Marco Legal: Ley 2466/2025 · Ley 1618/2013 · Ley 361/1997</div>
</div>
""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PIPELINE VISUAL                                                           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def mostrar_pipeline():
    """Muestra el pipeline visual de procesamiento."""
    fase = st.session_state.fase_actual

    fases = {
        "inicio": 0,
        "archivos": 1,
        "analisis": 2,
        "revision": 3,
        "generacion": 4,
        "descarga": 5,
    }
    paso_actual = fases.get(fase, 0)

    steps = [
        ("📁", "Cargar\nArchivos"),
        ("🤖", "Análisis\nIA"),
        ("✏️", "Revisión\nDatos"),
        ("⚙️", "Generar\nInforme"),
        ("📥", "Descargar\n.docx"),
    ]

    html = '<div class="pipeline">'
    for i, (icon, label) in enumerate(steps):
        cls = ""
        if i < paso_actual:
            cls = "done"
        elif i == paso_actual:
            cls = "active"

        html += f'<div class="pipeline-step {cls}">'
        html += f'<div class="icon">{icon}</div>'
        html += f'<div class="label">{label}</div>'
        html += '</div>'

        if i < len(steps) - 1:
            arrow_cls = "active" if i < paso_actual else ""
            html += f'<div class="pipeline-arrow {arrow_cls}">→</div>'

    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


mostrar_pipeline()


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  SIDEBAR — Carga de Archivos                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

with st.sidebar:
    st.markdown("### 🔑 Configuración de IA")

    # API Key
    api_key_input = st.text_input(
        "API Key de Google Gemini",
        type="password",
        value=st.session_state.api_key,
        help="Necesaria para el análisis automático con IA. "
             "Obténla en: https://aistudio.google.com/apikey",
        placeholder="AIza...",
    )
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
        st.session_state.api_verificada = False

    # Verificar API Key
    if api_key_input and not st.session_state.api_verificada:
        if st.button("✓ Verificar API Key", use_container_width=True):
            with st.spinner("Verificando..."):
                valida, mensaje = verificar_api_key(api_key_input)
                if valida:
                    st.session_state.api_verificada = True
                    st.success("✓ API Key válida")
                    st.rerun()
                else:
                    st.error(f"✗ {mensaje}")

    if st.session_state.api_verificada:
        st.markdown('<span class="badge badge-success">● IA Conectada</span>',
                    unsafe_allow_html=True)
    elif api_key_input:
        st.markdown('<span class="badge badge-warning">● Sin verificar</span>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-info">● Modo manual</span>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📁 Carga de Archivos")

    # ── Plantilla APT ──
    st.markdown("**📋 Plantilla APT (.docx)**")

    plantilla_file = st.file_uploader(
        "Subir nueva plantilla (.docx)",
        type=["docx"],
        key="upload_plantilla",
        help="Sube una nueva plantilla de informe Word con placeholders [[REF_IA_X]]",
    )
    if plantilla_file:
        ruta = guardar_archivo_temporal(plantilla_file)
        st.session_state.plantilla_cargada = True
        st.session_state.plantilla_path = ruta
        st.markdown('<span class="badge badge-success">● Nueva plantilla cargada</span>',
                    unsafe_allow_html=True)
    else:
        # Fallback a la de ejemplo si no hay cargada una por el usuario
        plantilla_default = BASE_DIR / "Informe_APT_MasxMenos.docx"
        if plantilla_default.exists():
            st.session_state.plantilla_cargada = True
            st.session_state.plantilla_path = str(plantilla_default)
            st.markdown('<span class="badge badge-info">● Usando plantilla de ejemplo</span>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-error">● Sin plantilla disponible</span>',
                        unsafe_allow_html=True)

    st.markdown("")

    # ── Manual de Funciones ──
    st.markdown("**📖 Manual de Funciones**")
    manual_file = st.file_uploader(
        "Subir Manual de Funciones",
        type=["docx", "doc", "pdf", "xls", "xlsx", "txt"],
        key="upload_manual",
        help="Sube el archivo del manual de funciones o descripción de cargo (Word, PDF, Excel, TXT).",
    )
    if manual_file:
        ruta = guardar_archivo_temporal(manual_file)
        st.session_state.manual_cargado = True
        st.session_state.manual_path = ruta
        st.markdown('<span class="badge badge-success">● Manual de funciones cargado</span>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-info">● Opcional (Modo manual activo)</span>',
                    unsafe_allow_html=True)

    st.markdown("")

    # ── Evidencias Fotográficas ──
    st.markdown("**📷 Evidencias Fotográficas**")

    fotos_files = st.file_uploader(
        "Subir nuevas fotos",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="upload_fotos",
        help="Sube las fotos de las instalaciones del nuevo puesto de trabajo",
    )
    if fotos_files:
        rutas = []
        for foto in fotos_files:
            ruta = guardar_archivo_temporal(foto)
            rutas.append(ruta)
        st.session_state.fotos_cargadas = rutas
        st.markdown(f'<span class="badge badge-success">● {len(rutas)} nuevas fotos cargadas</span>',
                    unsafe_allow_html=True)
    else:
        # Fallback a las fotos de ejemplo
        fotos_default = []
        for nombre in ["Entrada 1.jpg", "Baños.jpg"]:
            ruta = BASE_DIR / nombre
            if ruta.exists():
                fotos_default.append(str(ruta))
        
        if fotos_default:
            st.session_state.fotos_cargadas = fotos_default
            st.markdown(f'<span class="badge badge-info">● Usando {len(fotos_default)} fotos de ejemplo</span>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-warning">● Sin fotos cargadas</span>',
                        unsafe_allow_html=True)

    st.markdown("---")

    # ── Info del sistema ──
    st.markdown("### ℹ️ Sistema")
    st.markdown(f"""
    <div style="font-size: 0.75rem; color: #888;">
    <strong>Versión:</strong> 2.0<br>
    <strong>Motor:</strong> python-docx<br>
    <strong>IA:</strong> {'Gemini ✓' if st.session_state.api_verificada else 'No configurada'}<br>
    <strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y')}
    </div>
    """, unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CONTENIDO PRINCIPAL                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ── Verificar archivos cargados ──
if not st.session_state.plantilla_cargada:
    st.session_state.fase_actual = "inicio"
    st.markdown("""
    <div class="section-card" style="text-align: center; padding: 3rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📋</div>
        <div class="section-title" style="justify-content: center;">
            Bienvenido al Generador de Informes APT
        </div>
        <p style="color: #B0B0B0; max-width: 600px; margin: 0 auto;">
            Este sistema multiagente de IA analiza evidencias fotográficas y
            documentación organizacional para generar automáticamente el
            Informe Técnico de Inclusión Laboral bajo la Ley 2466 de 2025.
        </p>
        <br>
        <p style="color: #F39200; font-weight: 600;">
            ← Configure los archivos en la barra lateral para comenzar
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Mostrar arquitectura del sistema
    st.markdown("""
    <div class="section-card">
        <div class="section-title">🏗️ Arquitectura del Sistema Multiagente</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="number">👁️</div>
            <div class="label" style="color: #F39200; font-weight: 700; margin: 0.5rem 0;">
                A-Vision
            </div>
            <div style="font-size: 0.8rem; color: #B0B0B0;">
                Analiza fotos con visión artificial.<br>
                Identifica barreras arquitectónicas<br>
                y riesgos de accesibilidad.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="number">⚖️</div>
            <div class="label" style="color: #F39200; font-weight: 700; margin: 0.5rem 0;">
                A-Legal
            </div>
            <div style="font-size: 0.8rem; color: #B0B0B0;">
                Cruza funciones del cargo<br>
                con perfiles de discapacidad.<br>
                Define ajustes razonables.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="number">📄</div>
            <div class="label" style="color: #F39200; font-weight: 700; margin: 0.5rem 0;">
                A-Doc
            </div>
            <div style="font-size: 0.8rem; color: #B0B0B0;">
                Inyecta los análisis en la<br>
                plantilla Word preservando<br>
                formato original.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# ══════════════════════════════════════════════════════════════════════
# Si llegamos aquí, la plantilla está cargada. Mostrar interfaz principal.
# ══════════════════════════════════════════════════════════════════════

st.session_state.fase_actual = "archivos"

# ── Tabs principales ──
tab_analisis, tab_datos, tab_generar = st.tabs([
    "🤖 Análisis con IA",
    "✏️ Datos del Informe",
    "⚙️ Generar y Descargar"
])


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  TAB 1: ANÁLISIS CON IA                                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

with tab_analisis:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">🤖 Sistema Multiagente de Análisis</div>
        <p style="color: #B0B0B0; font-size: 0.9rem;">
            El sistema ejecuta tres agentes de IA en secuencia:
            <strong style="color: #F39200;">A-Vision</strong> (análisis visual) →
            <strong style="color: #F39200;">A-Legal</strong> (diagnóstico jurídico) →
            <strong style="color: #F39200;">A-Doc</strong> (construcción documental).
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Verificar prerequisites
    api_key = obtener_api_key()
    tiene_ia = bool(api_key) and st.session_state.api_verificada
    tiene_fotos = bool(st.session_state.fotos_cargadas)

    col_check1, col_check2, col_check3 = st.columns(3)
    with col_check1:
        if tiene_ia:
            st.success("✓ IA conectada (Gemini)")
        else:
            st.warning("⚠ Sin API Key — Modo manual")
    with col_check2:
        if st.session_state.plantilla_cargada:
            st.success("✓ Plantilla APT cargada")
        else:
            st.error("✗ Plantilla requerida")
    with col_check3:
        if tiene_fotos:
            st.success(f"✓ {len(st.session_state.fotos_cargadas)} foto(s) cargada(s)")
        else:
            st.info("ℹ Sin fotos — Se omitirá análisis visual")

    st.markdown("")

    # ── Mostrar fotos cargadas ──
    if tiene_fotos:
        st.markdown("**📷 Evidencias fotográficas cargadas:**")
        cols_fotos = st.columns(min(len(st.session_state.fotos_cargadas), 4))
        for i, ruta in enumerate(st.session_state.fotos_cargadas):
            with cols_fotos[i % len(cols_fotos)]:
                try:
                    st.image(ruta, caption=os.path.basename(ruta), use_container_width=True)
                except Exception:
                    st.warning(f"No se pudo cargar: {os.path.basename(ruta)}")

    st.markdown("---")

    # ── Botón de análisis ──
    if tiene_ia and tiene_fotos:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <p style="color: #B0B0B0;">
                Al hacer clic, el sistema enviará las fotos a Google Gemini para análisis.
                El proceso puede tomar entre 30 segundos y 2 minutos.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button(
                "🚀 Ejecutar Análisis Multiagente",
                type="primary",
                use_container_width=True,
                key="btn_analisis",
            ):
                st.session_state.fase_actual = "analisis"

                # Datos del cargo (de DatosProyecto por defecto)
                datos_cargo = {
                    "nombre": DatosProyecto.DEFAULTS["cargo_encabezado"][0],
                    "tipo": DatosProyecto.DEFAULTS["cargo_encabezado"][1],
                    "objetivo": DatosProyecto.DEFAULTS["cargo_objetivo"],
                    "tareas": DatosProyecto.DEFAULTS["cargo_tareas"],
                }

                # Si hay manual cargado y datos extraídos, usarlos
                if st.session_state.manual_cargado:
                    try:
                        manual_data = extraer_datos_manual(
                            st.session_state.manual_path,
                            api_key,
                        )
                        if "cargo_nombre" in manual_data:
                            datos_cargo["nombre"] = manual_data["cargo_nombre"]
                        if "cargo_tipo" in manual_data:
                            datos_cargo["tipo"] = manual_data["cargo_tipo"]
                        if "cargo_objetivo" in manual_data:
                            datos_cargo["objetivo"] = manual_data["cargo_objetivo"]
                        if "cargo_tareas" in manual_data:
                            datos_cargo["tareas"] = manual_data["cargo_tareas"]
                        st.session_state.manual_datos = manual_data
                    except Exception as e:
                        st.warning(f"No se pudo extraer datos del manual: {e}")

                # Ejecutar sistema multiagente
                progress_bar = st.progress(0, text="Iniciando sistema multiagente...")
                status_text = st.empty()
                log_container = st.empty()

                def progress_cb(fase, progreso):
                    progress_bar.progress(progreso, text=fase)
                    status_text.markdown(
                        f'<span class="badge badge-warning loading-pulse">● {fase}</span>',
                        unsafe_allow_html=True,
                    )

                try:
                    sistema = SistemaMultiagente(api_key)
                    resultado = sistema.ejecutar_analisis_completo(
                        rutas_fotos=st.session_state.fotos_cargadas,
                        datos_cargo=datos_cargo,
                        progress_callback=progress_cb,
                    )

                    st.session_state.analisis_resultado = resultado
                    st.session_state.analisis_ejecutado = True

                    # Aplicar resultados a datos editables
                    st.session_state.datos_accesibilidad = resultado.get("accesibilidad")
                    st.session_state.datos_competencias = resultado.get("competencias")
                    st.session_state.datos_ajustes = resultado.get("ajustes_razonables")
                    st.session_state.datos_conclusiones = resultado.get("conclusiones")

                    progress_bar.progress(1.0, text="¡Análisis completado!")
                    status_text.markdown(
                        '<span class="badge badge-success">✓ Análisis completado exitosamente</span>',
                        unsafe_allow_html=True,
                    )

                    # Mostrar logs
                    with st.expander("📋 Logs del sistema multiagente", expanded=False):
                        st.code(sistema.get_logs(), language="text")

                    st.rerun()

                except Exception as e:
                    progress_bar.empty()
                    st.error(f"Error en el análisis: {e}")
                    st.info("Puede continuar en modo manual editando los datos en la pestaña 'Datos del Informe'.")

    elif not tiene_ia:
        st.markdown("""
        <div class="section-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔑</div>
            <p style="color: #F39200; font-weight: 600;">Modo Manual Activo</p>
            <p style="color: #B0B0B0; font-size: 0.85rem;">
                Sin API Key de Gemini, el sistema funciona en modo manual.<br>
                Puede editar todos los datos directamente en la pestaña
                <strong>"Datos del Informe"</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Mostrar resultado del análisis si ya se ejecutó
    if st.session_state.analisis_ejecutado and st.session_state.analisis_resultado:
        st.markdown("---")
        st.markdown("""
        <div class="section-card">
            <div class="section-title">✅ Resultado del Análisis</div>
        </div>
        """, unsafe_allow_html=True)

        resultado = st.session_state.analisis_resultado

        with st.expander("👁️ A-Vision: Análisis de Accesibilidad", expanded=True):
            for i, texto in enumerate(resultado.get("accesibilidad", [])):
                if texto:
                    etiquetas = [
                        "Acceso Principal", "Foto Entrada", "Baños",
                        "Foto Baños", "Cafetería", "Foto Cafetería",
                        "Rampas", "Información y Comunicación",
                        "Actitudinales y Sociales"
                    ]
                    etiqueta = etiquetas[i] if i < len(etiquetas) else f"Fila {i}"
                    st.markdown(f"**{etiqueta}:** {texto[:200]}...")

        with st.expander("⚖️ A-Legal: Diagnóstico Jurídico", expanded=True):
            disc = resultado.get("discapacidades_sugeridas", [])
            st.markdown(f"**Discapacidades compatibles:** {', '.join(disc)}")
            for ajuste in resultado.get("ajustes_razonables", []):
                st.markdown(f"- **{ajuste.get('tipo', '')}**: {ajuste.get('fisicas', '')[:150]}...")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  TAB 2: DATOS DEL INFORME (Editable)                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

with tab_datos:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">✏️ Datos del Informe — Edición y Revisión</div>
        <p style="color: #B0B0B0; font-size: 0.85rem;">
            Estos datos se inyectarán en la plantilla Word.
            Puede editarlos manualmente o extraerlos del Manual con IA usando el botón de abajo.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.manual_cargado and st.session_state.api_verificada:
        if st.button("🪄 Extraer Datos del Manual con IA", type="primary", use_container_width=True):
            with st.spinner("Leyendo documento y extrayendo información..."):
                try:
                    manual_data = extraer_datos_manual(
                        st.session_state.manual_path,
                        obtener_api_key(),
                    )
                    st.session_state.manual_datos = manual_data
                    
                    st.session_state["emp_0"] = manual_data.get("empresa_nombre", "")
                    st.session_state["emp_1"] = manual_data.get("empresa_actividad", "")
                    st.session_state["emp_2"] = manual_data.get("empresa_nit", "")
                    st.session_state["emp_3"] = manual_data.get("empresa_sede", "")
                    st.session_state["emp_4"] = manual_data.get("empresa_direccion", "")
                    st.session_state["emp_5"] = manual_data.get("empresa_telefono", "")
                    st.session_state["emp_6"] = manual_data.get("empresa_fecha", "")
                    
                    st.session_state["cargo_0"] = manual_data.get("cargo_nombre", "")
                    st.session_state["cargo_1"] = manual_data.get("cargo_tipo", "")
                    st.session_state["cargo_2"] = manual_data.get("cargo_dependencia", "")
                    st.session_state["cargo_3"] = manual_data.get("cargo_reporta", "")
                    st.session_state["cargo_obj"] = manual_data.get("cargo_objetivo", "")
                    
                    st.session_state["req_0"] = manual_data.get("cargo_requisito_educativo", "")
                    st.session_state["req_1"] = manual_data.get("cargo_requisito_certificaciones", "")
                    st.session_state["req_2"] = manual_data.get("cargo_requisito_conocimientos", "")
                    st.session_state["req_3"] = manual_data.get("cargo_requisito_experiencia", "")
                    st.session_state["req_4"] = manual_data.get("cargo_requisito_entrenamiento", "")
                    st.session_state["req_5"] = manual_data.get("cargo_requisito_disponibilidad", "")
                    st.session_state["req_6"] = manual_data.get("cargo_requisito_examenes", "")
                    
                    tareas_extraidas = manual_data.get("cargo_tareas", [])
                    if isinstance(tareas_extraidas, list):
                        for i in range(13):
                            if i < len(tareas_extraidas):
                                st.session_state[f"tarea_{i}"] = str(tareas_extraidas[i])
                            else:
                                st.session_state[f"tarea_{i}"] = ""

                    st.session_state["cond_0"] = manual_data.get("condiciones_jornada", "")
                    st.session_state["cond_1"] = manual_data.get("condiciones_turnos", "")
                    st.session_state["cond_2"] = manual_data.get("condiciones_rotativos", "")
                    st.session_state["cond_3"] = manual_data.get("condiciones_rotacion", "")
                    st.session_state["cond_4"] = manual_data.get("condiciones_horas_extras", "")

                    st.session_state["rec_0"] = manual_data.get("recursos_equipos", "")
                    st.session_state["rec_1"] = manual_data.get("recursos_mobiliario", "")
                    st.session_state["rec_2"] = manual_data.get("recursos_maquinas", "")
                    st.session_state["rec_3"] = manual_data.get("recursos_herramientas", "")
                    st.session_state["rec_4"] = manual_data.get("recursos_materiales", "")
                    st.session_state["rec_5"] = manual_data.get("recursos_accesorios", "")
                    st.session_state["rec_6"] = manual_data.get("recursos_epp", "")

                    st.success("✓ Datos extraídos y campos actualizados.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error en la extracción: {e}")

    # Obtener defaults
    defaults = DatosProyecto.DEFAULTS

    # ── SECCIÓN 1: Datos de la Empresa ──
    with st.expander("🏢 Datos Generales de la Empresa", expanded=False):
        emp = defaults["empresa"]
        empresa_nombre = st.text_input("Nombre de la empresa", value=emp[0], key="emp_0")
        empresa_actividad = st.text_area("Actividad económica", value=emp[1], key="emp_1", height=80)
        c1, c2 = st.columns(2)
        with c1:
            empresa_nit = st.text_input("NIT", value=emp[2], key="emp_2")
            empresa_sede = st.text_input("Sede", value=emp[3], key="emp_3")
        with c2:
            empresa_direccion = st.text_input("Dirección", value=emp[4], key="emp_4")
            empresa_telefono = st.text_input("Teléfono", value=emp[5], key="emp_5")
        empresa_fecha = st.text_input("Fecha del estudio", value=emp[6], key="emp_6")

    # ── SECCIÓN 2: Perfil de Cargo ──
    with st.expander("👤 Perfil de Cargo", expanded=False):
        enc = defaults["cargo_encabezado"]
        c1, c2 = st.columns(2)
        with c1:
            cargo_nombre = st.text_input("Nombre del cargo", value=enc[0], key="cargo_0")
            cargo_tipo = st.text_input("Tipo de cargo", value=enc[1], key="cargo_1")
        with c2:
            cargo_dep = st.text_input("Dependencia / Sede", value=enc[2], key="cargo_2")
            cargo_reporta = st.text_input("Reporta a", value=enc[3], key="cargo_3")

        cargo_objetivo = st.text_area(
            "Objetivo del cargo",
            value=defaults["cargo_objetivo"],
            key="cargo_obj",
            height=100,
        )

    # ── SECCIÓN 3: Requisitos ──
    with st.expander("📋 Requisitos del Cargo", expanded=False):
        reqs = defaults["cargo_requisitos"]
        req_educ = st.text_input("Nivel educativo", value=reqs[0], key="req_0")
        req_cert = st.text_input("Actualizaciones/Certificaciones", value=reqs[1], key="req_1")
        req_conoc = st.text_input("Conocimientos específicos", value=reqs[2], key="req_2")
        req_exp = st.text_input("Experiencia previa", value=reqs[3], key="req_3")
        req_entr = st.text_input("Entrenamiento", value=reqs[4], key="req_4")
        req_disp = st.text_input("Disponibilidad", value=reqs[5], key="req_5")
        req_exam = st.text_input("Exámenes", value=reqs[6], key="req_6")

    # ── SECCIÓN 4: Tareas ──
    with st.expander("📝 Descripción de Tareas (13 tareas)", expanded=False):
        tareas_editadas = []
        for i, tarea in enumerate(defaults["cargo_tareas"]):
            t = st.text_area(f"Tarea {i+1}", value=tarea, key=f"tarea_{i}", height=70)
            tareas_editadas.append(t)

    # ── SECCIÓN 5: Condiciones Organizacionales ──
    with st.expander("🏗️ Condiciones Organizacionales", expanded=False):
        cond = defaults["condiciones_org"]
        conds_editadas = []
        etiquetas_cond = ["Jornada laboral", "Turnos", "Turnos rotativos", "Rotación", "Horas extras"]
        for i, (etiq, val) in enumerate(zip(etiquetas_cond, cond)):
            c = st.text_area(etiq, value=val, key=f"cond_{i}", height=60)
            conds_editadas.append(c)

    # ── SECCIÓN 6: Recursos Materiales ──
    with st.expander("🔧 Recursos Materiales", expanded=False):
        rec = defaults["recursos"]
        recs_editados = []
        etiquetas_rec = ["Equipos", "Mobiliario", "Máquinas", "Herramientas",
                         "Materiales consumo", "Accesorios", "EPP"]
        for i, (etiq, val) in enumerate(zip(etiquetas_rec, rec)):
            r = st.text_area(etiq, value=val, key=f"rec_{i}", height=60)
            recs_editados.append(r)

    # ── SECCIÓN 7: Accesibilidad ──
    with st.expander("♿ Accesibilidad y Barreras (A-Vision)", expanded=False):
        acc = st.session_state.datos_accesibilidad or defaults["accesibilidad"]
        acc_editada = []
        etiquetas_acc = [
            "Acceso principal", "Registro foto entrada",
            "Batería de Baños", "Registro foto baños",
            "Cafetería", "Registro foto cafetería",
            "Rampas", "Información y comunicación",
            "Actitudinales y sociales",
        ]
        for i, (etiq, val) in enumerate(zip(etiquetas_acc, acc)):
            if "foto" in etiq.lower():
                acc_editada.append(val)
            else:
                a = st.text_area(etiq, value=val, key=f"acc_{i}", height=120)
                acc_editada.append(a)

        if st.session_state.analisis_ejecutado:
            st.info("✓ Estos datos fueron generados por el Agente A-Vision.")

    # ── SECCIÓN 8: Discapacidades y Ajustes ──
    with st.expander("⚖️ Discapacidades y Ajustes Razonables (A-Legal)", expanded=False):
        disc_defaults = st.session_state.analisis_resultado.get(
            "discapacidades_sugeridas",
            defaults["discapacidades_sugeridas"]
        ) if st.session_state.analisis_resultado else defaults["discapacidades_sugeridas"]

        st.markdown("**Discapacidades compatibles con el cargo:**")
        disc_editadas = []
        for i, d in enumerate(disc_defaults):
            disc = st.text_input(f"Discapacidad {i+1}", value=d, key=f"disc_{i}")
            disc_editadas.append(disc)

        st.markdown("---")
        st.markdown("**Plan de Ajustes Razonables:**")

        ajustes_defaults = st.session_state.datos_ajustes or defaults["ajustes_razonables"]
        ajustes_editados = []
        for j, ajuste in enumerate(ajustes_defaults):
            st.markdown(f"##### Discapacidad: {ajuste.get('tipo', f'Tipo {j+1}')}")
            tipo = st.text_input("Tipo", value=ajuste.get("tipo", ""), key=f"aj_tipo_{j}")
            fisicas = st.text_area(
                "Barreras Físicas", value=ajuste.get("fisicas", ""),
                key=f"aj_fis_{j}", height=120
            )
            comunicacion = st.text_area(
                "Barreras de Comunicación", value=ajuste.get("comunicacion", ""),
                key=f"aj_com_{j}", height=120
            )
            actitudinales = st.text_area(
                "Barreras Actitudinales", value=ajuste.get("actitudinales", ""),
                key=f"aj_act_{j}", height=120
            )
            ajustes_editados.append({
                "tipo": tipo,
                "fisicas": fisicas,
                "comunicacion": comunicacion,
                "actitudinales": actitudinales,
            })

    # ── SECCIÓN 9: Conclusiones ──
    with st.expander("📊 Conclusiones", expanded=False):
        conc_default = st.session_state.datos_conclusiones or defaults["conclusiones"]
        conclusiones_editadas = st.text_area(
            "Conclusiones del informe",
            value=conc_default,
            key="conclusiones",
            height=300,
        )

        if st.session_state.analisis_ejecutado:
            st.info("✓ Conclusiones generadas por el Agente A-Legal.")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  TAB 3: GENERAR Y DESCARGAR                                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

with tab_generar:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">⚙️ Generar Informe Técnico</div>
        <p style="color: #B0B0B0; font-size: 0.85rem;">
            El Agente A-Doc inyectará todos los datos en la plantilla Word,
            preservando el formato original (fuentes, bordes, alineaciones)
            e insertará las fotografías en las celdas correspondientes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Resumen de datos
    st.markdown("### 📋 Resumen de Datos")

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="number">📋</div>
            <div class="label">Plantilla</div>
            <div style="font-size: 0.75rem; color: {'#00C853' if st.session_state.plantilla_cargada else '#FF5252'};">
                {'✓ Cargada' if st.session_state.plantilla_cargada else '✗ Pendiente'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        n_fotos = len(st.session_state.fotos_cargadas)
        st.markdown(f"""
        <div class="stat-card">
            <div class="number">{n_fotos}</div>
            <div class="label">Fotos</div>
            <div style="font-size: 0.75rem; color: #B0B0B0;">Evidencias</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="number">{'✓' if st.session_state.analisis_ejecutado else '—'}</div>
            <div class="label">IA</div>
            <div style="font-size: 0.75rem; color: {'#00C853' if st.session_state.analisis_ejecutado else '#B0B0B0'};">
                {'Analizado' if st.session_state.analisis_ejecutado else 'Manual'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_s4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="number">10</div>
            <div class="label">Tablas</div>
            <div style="font-size: 0.75rem; color: #B0B0B0;">En plantilla</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Botón de generación ──
    col_g1, col_g2, col_g3 = st.columns([1, 2, 1])
    with col_g2:
        if st.button(
            "🔨 Generar Informe Word (.docx)",
            type="primary",
            use_container_width=True,
            key="btn_generar",
        ):
            st.session_state.fase_actual = "generacion"

            # Construir configuración desde los widgets
            config = {
                "plantilla_path": st.session_state.plantilla_path,
                "salida_path": "",  # No se usa en modo memoria
                "empresa": [
                    st.session_state.get("emp_0", defaults["empresa"][0]),
                    st.session_state.get("emp_1", defaults["empresa"][1]),
                    st.session_state.get("emp_2", defaults["empresa"][2]),
                    st.session_state.get("emp_3", defaults["empresa"][3]),
                    st.session_state.get("emp_4", defaults["empresa"][4]),
                    st.session_state.get("emp_5", defaults["empresa"][5]),
                    st.session_state.get("emp_6", defaults["empresa"][6]),
                ],
                "cargo_encabezado": [
                    st.session_state.get("cargo_0", defaults["cargo_encabezado"][0]),
                    st.session_state.get("cargo_1", defaults["cargo_encabezado"][1]),
                    st.session_state.get("cargo_2", defaults["cargo_encabezado"][2]),
                    st.session_state.get("cargo_3", defaults["cargo_encabezado"][3]),
                ],
                "cargo_objetivo": st.session_state.get("cargo_obj", defaults["cargo_objetivo"]),
                "cargo_requisitos": [
                    st.session_state.get(f"req_{i}", defaults["cargo_requisitos"][i])
                    for i in range(7)
                ],
                "cargo_tareas": [
                    st.session_state.get(f"tarea_{i}", defaults["cargo_tareas"][i])
                    for i in range(13)
                ],
                "condiciones_org": [
                    st.session_state.get(f"cond_{i}", defaults["condiciones_org"][i])
                    for i in range(5)
                ],
                "recursos": [
                    st.session_state.get(f"rec_{i}", defaults["recursos"][i])
                    for i in range(7)
                ],
                "accesibilidad": [
                    st.session_state.get(f"acc_{i}", (
                        st.session_state.datos_accesibilidad or defaults["accesibilidad"]
                    )[i])
                    for i in range(9)
                ],
                "condiciones_amb": st.session_state.datos_accesibilidad and [
                    st.session_state.analisis_resultado.get("condiciones_amb", defaults["condiciones_amb"])[i]
                    for i in range(5)
                ] if st.session_state.analisis_resultado else defaults["condiciones_amb"],
                "condiciones_seguridad": (
                    st.session_state.analisis_resultado.get(
                        "condiciones_seguridad", defaults["condiciones_seguridad"]
                    ) if st.session_state.analisis_resultado
                    else defaults["condiciones_seguridad"]
                ),
                "competencias": (
                    st.session_state.datos_competencias or defaults["competencias"]
                ),
                "discapacidades_sugeridas": [
                    st.session_state.get(f"disc_{i}", defaults["discapacidades_sugeridas"][i])
                    for i in range(len(defaults["discapacidades_sugeridas"]))
                ],
                "ajustes_razonables": [
                    {
                        "tipo": st.session_state.get(f"aj_tipo_{j}", defaults["ajustes_razonables"][j]["tipo"]),
                        "fisicas": st.session_state.get(f"aj_fis_{j}", defaults["ajustes_razonables"][j]["fisicas"]),
                        "comunicacion": st.session_state.get(f"aj_com_{j}", defaults["ajustes_razonables"][j]["comunicacion"]),
                        "actitudinales": st.session_state.get(f"aj_act_{j}", defaults["ajustes_razonables"][j]["actitudinales"]),
                    }
                    for j in range(len(defaults["ajustes_razonables"]))
                ],
                "conclusiones": st.session_state.get("conclusiones", defaults["conclusiones"]),
            }

            # Mapear fotos a las filas de la tabla de accesibilidad
            fotos_dict = {}
            for i, ruta in enumerate(st.session_state.fotos_cargadas):
                if i == 0:
                    fotos_dict[2] = ruta  # Fila 2 = Entrada
                elif i == 1:
                    fotos_dict[4] = ruta  # Fila 4 = Baños
                elif i == 2:
                    fotos_dict[6] = ruta  # Fila 6 = Cafetería
            config["fotos"] = fotos_dict

            # Generar informe con barra de progreso
            progress = st.progress(0, text="Iniciando generación del informe...")

            def prog_cb(fase, valor):
                progress.progress(valor, text=f"A-Doc: {fase}")

            try:
                docx_bytes, stats, logs = generar_informe(config, prog_cb)

                st.session_state.informe_generado = True
                st.session_state.informe_bytes = docx_bytes
                st.session_state.informe_stats = stats
                st.session_state.informe_logs = logs
                st.session_state.fase_actual = "descarga"

                progress.progress(1.0, text="¡Informe generado exitosamente!")
                time.sleep(1)
                st.rerun()

            except Exception as e:
                progress.empty()
                st.error(f"Error al generar el informe: {e}")
                st.code(str(e))

    # ── Resultados de generación ──
    if st.session_state.informe_generado:
        st.markdown("---")

        st.markdown("""
        <div class="section-card" style="text-align: center; border-color: #00C853;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">✅</div>
            <div class="section-title" style="justify-content: center; color: #00C853;">
                Informe Generado Exitosamente
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Estadísticas
        stats = st.session_state.informe_stats
        col_st1, col_st2, col_st3, col_st4 = st.columns(4)
        with col_st1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="number" style="color: #00C853;">{stats.get('reemplazos', 0)}</div>
                <div class="label">Reemplazos</div>
            </div>
            """, unsafe_allow_html=True)
        with col_st2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="number" style="color: #00C853;">{stats.get('fotos', 0)}</div>
                <div class="label">Fotos insertadas</div>
            </div>
            """, unsafe_allow_html=True)
        with col_st3:
            restantes = stats.get('placeholders_restantes', 0)
            color = '#00C853' if restantes == 0 else '#FF5252'
            st.markdown(f"""
            <div class="stat-card">
                <div class="number" style="color: {color};">{restantes}</div>
                <div class="label">Pendientes</div>
            </div>
            """, unsafe_allow_html=True)
        with col_st4:
            errores = len(stats.get('errores', []))
            color = '#00C853' if errores == 0 else '#F39200'
            st.markdown(f"""
            <div class="stat-card">
                <div class="number" style="color: {color};">{errores}</div>
                <div class="label">Errores</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        # Botón de descarga
        col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
        with col_d2:
            empresa_name = st.session_state.get("emp_0", "Informe")
            nombre_archivo = f"Informe_APT_{empresa_name.replace(' ', '_')}_FINAL.docx"

            st.download_button(
                label="📥 Descargar Informe Final (.docx)",
                data=st.session_state.informe_bytes,
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
                key="btn_download",
            )

        # Logs
        with st.expander("📋 Logs de generación (A-Doc)", expanded=False):
            st.code(st.session_state.informe_logs, language="text")

        if stats.get("errores"):
            with st.expander("⚠️ Errores detectados", expanded=True):
                for err in stats["errores"]:
                    st.warning(err)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  FOOTER                                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

st.markdown("""
<div class="footer">
    <strong>Programa Talento Sin Barreras</strong> — Comfenalco Santander<br>
    Ley 2466/2025 · Ley 1618/2013 · Ley 361/1997<br>
    Desarrollado con ❤️ para la inclusión laboral en Colombia
</div>
""", unsafe_allow_html=True)
