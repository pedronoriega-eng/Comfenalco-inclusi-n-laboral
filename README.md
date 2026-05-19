# 🧡 Generador de Informe Técnico de Inclusión Laboral

**Programa Talento Sin Barreras — Comfenalco Santander**

Aplicación web que automatiza la creación de Informes Técnicos de Inclusión Laboral (APT) basados en el marco legal colombiano: Ley 2466/2025, Ley 1618/2013 y Ley 361/1997.

## 🏗️ Arquitectura del Sistema Multiagente

El sistema utiliza tres agentes de IA especializados:

| Agente | Rol | Tecnología |
|--------|-----|------------|
| **A-Vision** | Análisis de accesibilidad y barreras arquitectónicas | Google Gemini (Visión) |
| **A-Legal** | Diagnóstico jurídico y compatibilidad funcional | Google Gemini (NLP) |
| **A-Doc** | Inyección en plantilla Word preservando formato | python-docx |

```
Usuario → Carga Archivos → A-Vision (fotos) → A-Legal (funciones) → A-Doc (Word) → Descarga .docx
```

## 🚀 Ejecución Local

### Requisitos

- Python 3.10+
- pip

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/comfenalco-apt.git
cd comfenalco-apt

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

### Configuración de IA (opcional)

Para habilitar el análisis automático con IA:

1. Obtén una API Key de Google Gemini: https://aistudio.google.com/apikey
2. Ingresa la API Key en la barra lateral de la aplicación.

Sin API Key, la aplicación funciona en **modo manual** con datos pre-cargados.

## 📁 Estructura del Proyecto

```
├── app.py                    # Aplicación web Streamlit (principal)
├── motor_documental.py       # Motor de generación Word (A-Doc)
├── ai_agents.py              # Sistema multiagente IA (A-Vision + A-Legal)
├── generar_informe_APT.py    # Script original (referencia)
├── requirements.txt          # Dependencias Python
├── Procfile                  # Despliegue Streamlit Cloud
├── .streamlit/
│   └── config.toml           # Tema institucional
├── Informe_APT_MasxMenos.docx  # Plantilla APT (ejemplo)
├── Entrada 1.jpg             # Foto ejemplo (acceso)
├── Baños.jpg                 # Foto ejemplo (baños)
└── README.md                 # Este archivo
```

## ☁️ Despliegue en Streamlit Cloud

1. Sube el repositorio a GitHub.
2. Ve a https://share.streamlit.io
3. Conecta tu repositorio.
4. Configura el secreto `GEMINI_API_KEY` en Settings → Secrets:
   ```toml
   GEMINI_API_KEY = "tu-api-key-aqui"
   ```
5. Deploy!

## 📜 Marco Legal

- **Ley 2466 de 2025**: Reforma Laboral — estabilidad laboral reforzada.
- **Ley 1618 de 2013**: Derechos de personas con discapacidad.
- **Ley 361 de 1997**: Protección laboral reforzada.
- **NTC 4143/6047**: Normas técnicas de accesibilidad.

## 🎨 Identidad Visual

| Color | Hex | Uso |
|-------|-----|-----|
| Naranja | `#F39200` | Primario / Acentos |
| Carbón | `#1A1A1B` | Fondo |
| Blanco | `#FFFFFF` | Texto |

---

**Comfenalco Santander** — Inclusión laboral para todos.
