import streamlit as st
import ssl
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import altair as alt
import io
import time

# --- 1. CONFIGURACIÓN Y SEGURIDAD ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

st.set_page_config(
    page_title="Monitoreo de Spots",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GESTIÓN DE USUARIOS (LOGIN) ---
USUARIOS = {
    "admin": "Master",
    "BodegA": "Prueba",
    "Prueba": "Prueba"
}

PERMISOS = {
    "admin": "TODOS",
    "BodegA": ["BodegaAurrera", "Walmart"],
    "Prueba": ["BUZO CON EL DRENAJE", "CocaCola"]
}

if 'logueado' not in st.session_state:
    st.session_state['logueado'] = False
if 'usuario_actual' not in st.session_state:
    st.session_state['usuario_actual'] = None

# --- 3. ESTILOS CSS ---
st.markdown("""
    <style>
    /* Estilos Generales Dashboard */
    .badge-freq {
        background-color: #e6f3ff;
        color: #0068c9;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8em;
        font-weight: 700;
        border: 1px solid #cce5ff;
    }
    .spot-highlight {
        color: #d93025;
        font-weight: 600;
    }
    div[data-testid="stSidebar"] button {
        width: 100%;
    }
    .streamlit-expanderHeader {
        font-size: 0.9em;
        padding: 0px !important;
    }
    
    /* --- CSS LOGIN CORREGIDO --- */
    
    /* 1. Títulos FUERA de la tarjeta */
    .login-header {
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff; 
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .login-sub {
        font-size: 1.2rem;
        color: #e5e7eb;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 400;
        letter-spacing: 1px;
    }

    /* 2. LA TARJETA BLANCA */
    div[data-testid="stForm"] {
        background-color: #ffffff !important;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border: 1px solid #e5e7eb;
    }

    /* 3. TEXTOS NEGROS (CORREGIDO) */
    /* Solo aplicamos negro a etiquetas y títulos, NO a los botones para evitar que se pongan negros */
    div[data-testid="stForm"] h3,
    div[data-testid="stForm"] label,
    div[data-testid="stForm"] span,
    div[data-testid="stForm"] div.stMarkdown p {
        color: #111827 !important;
    }

    /* 4. ARREGLO DEL INPUT PASSWORD (Ocultar "Press Enter") */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }
    
    /* 5. Inputs */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="input"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    input[type="text"], input[type="password"] {
        color: #000000 !important;
        caret-color: #000000 !important;
    }

    /* 6. BOTÓN PRINCIPAL (INGRESAR) - CORREGIDO */
    div[data-testid="stForm"] > button {
        background-color: #2563eb !important; /* Azul */
        border: none !important;
        padding: 12px !important;
        border-radius: 6px !important;
        margin-top: 15px;
        width: 100%;
    }
    /* Forzamos el texto del botón a BLANCO explícitamente */
    div[data-testid="stForm"] > button p {
        color: #ffffff !important; 
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    div[data-testid="stForm"] > button:hover {
        background-color: #1d4ed8 !important;
    }

    /* 7. BOTÓN "VER CONTRASEÑA" (OJO) */
    div[data-baseweb="input"] button {
        background-color: transparent !important;
        border: none !important;
        color: #6b7280 !important;
        margin-top: 0 !important;
        padding: 0 10px !important;
        width: auto !important;
        box-shadow: none !important;
    }
    div[data-baseweb="input"] button:hover {
        background-color: transparent !important;
        color: #111827 !important;
    }
    div[data-baseweb="input"] svg {
        fill: #6b7280 !important;
    }

    .login-footer {
        text-align: center;
        color: #9ca3af;
        font-size: 0.8em;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIN ---
def mostrar_login():
    c1, c2, c3 = st.columns([1, 0.8, 1])
    
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div class='login-header'>Monitor Radio</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-sub'>Intelligence Dashboard</div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### Acceso a Cliente")
            st.caption("Ingresa tus credenciales para continuar")
            st.markdown("<br>", unsafe_allow_html=True)
            
            usuario = st.text_input("Usuario", placeholder="Usuario asignado")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
            
            if submitted:
                if usuario in USUARIOS and USUARIOS[usuario] == password:
                    st.session_state['logueado'] = True
                    st.session_state['usuario_actual'] = usuario
                    st.success("✅ Acceso concedido")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")

        st.markdown("<div class='login-footer'>&copy; 2025 Media Intelligence System</div>", unsafe_allow_html=True)

if not st.session_state['logueado']:
    mostrar_login()
    st.stop()

# ==============================================================================
# DATOS Y DASHBOARD
# ==============================================================================

# --- 5. LÓGICA DE DATOS ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=10)
def cargar_datos():
    # ⚠️ TU ENLACE REAL
    url_hoja = "https://docs.google.com/spreadsheets/d/1ZCwGhzMl8TLQlDzg4AFMfni50rShkfhALqQkLWzK454/edit?gid=0#gid=0"
    try:
        data = conn.read(spreadsheet=url_hoja, worksheet=0)
        data.columns = data.columns.str.strip()
        mapa = {
            'HORA EXACTA': 'HORA',
            'HORA BLOQUE': 'HORA_B',
            'KEYWORD/SPOT': 'SPOT',
            'ESTACIÓN': 'ESTACION',
            'ESTENOGRÁFICA': 'TEXTO_FULL',
            'CONTEXTO': 'CONTEXTO_RAW',
            'FRECUENCIA': 'FRECUENCIA',
            'PROGRAMA': 'PROGRAMA',
            'LINK': 'LINK',
            'CIUDAD': 'CIUDAD'
        }
        data = data.rename(columns=mapa)
        if 'HORA' not in data.columns and 'HORA_B' in data.columns:
            data['HORA'] = data['HORA_B']
        data['FECHA'] = pd.to_datetime(data['FECHA'], dayfirst=True, errors='coerce')
        data['HORA_NUM'] = pd.to_numeric(data['HORA'].astype(str).str.split(':').str[0], errors='coerce').fillna(0).astype(int)
        data['KEYWORDS'] = data['CONTEXTO_RAW'].astype(str).str.replace(r'MATCH.*', '', regex=True).str.strip()
        return data
    except Exception as e:
        return None

# --- 6. SIDEBAR ---
with st.sidebar:
    usuario = st.session_state['usuario_actual']
    st.write(f"Hola, **{usuario}** 👋")
    if st.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state['logueado'] = False
        st.session_state['usuario_actual'] = None
        st.rerun()

# --- 7. CARGA ---
df_raw = cargar_datos()
if df_raw is None:
    st.error("⚠️ Error conectando a Google Sheets.")
    st.stop()

permisos = PERMISOS.get(usuario, [])
if permisos != "TODOS":
    df_raw = df_raw[df_raw['SPOT'].isin(permisos)]

st.title("Monitoreo de Spots")
if permisos != "TODOS":
    st.caption(f"Visualizando datos para: {', '.join(permisos)}")
st.markdown("---")

# --- 8. FILTROS ---
c_filtros_1 = st.columns(4)
min_date_avail = df_raw['FECHA'].min().date() if not df_raw.empty else datetime.date.today()
max_date_avail = df_raw['FECHA'].max().date() if not df_raw.empty else datetime.date.today()

with c_filtros_1[0]:
    f_inicio = st.date_input("📅 Desde", min_date_avail, format="DD/MM/YYYY")
with c_filtros_1[1]:
    f_fin = st.date_input("📅 Hasta", max_date_avail, format="DD/MM/YYYY")
with c_filtros_1[2]:
    criterio = st.selectbox("Ordenar por", ["Fecha/Hora", "Estación", "Spot"])
with c_filtros_1[3]:
    direccion = st.selectbox("Orden", ["Descendente", "Ascendente"])

c_filtros_2 = st.columns(2)
lista_estaciones = sorted(df_raw['ESTACION'].dropna().unique().tolist()) if not df_raw.empty else []
lista_ciudades = sorted(df_raw['CIUDAD'].dropna().unique().tolist()) if not df_raw.empty else []

with c_filtros_2[0]:
    filtro_estaciones = st.multiselect("📡 Filtrar por Estación", lista_estaciones)
with c_filtros_2[1]:
    filtro_ciudades = st.multiselect("🏙️ Filtrar por Ciudad", lista_ciudades)

# --- 9. APLICACIÓN DE FILTROS ---
df = df_raw.copy()
if f_inicio and f_fin:
    df = df[(df['FECHA'].dt.date >= f_inicio) & (df['FECHA'].dt.date <= f_fin)]
if filtro_estaciones:
    df = df[df['ESTACION'].isin(filtro_estaciones)]
if filtro_ciudades:
    df = df[df['CIUDAD'].isin(filtro_ciudades)]

# --- 10. KPIs ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3 = st.columns(3)
k1.metric("Spots Totales", len(df))
est_lider = df['ESTACION'].mode()[0] if not df.empty else "-"
k2.metric("Top Estación", est_lider)
prog_lider = df['PROGRAMA'].mode()[0] if not df.empty else "-"
k3.metric("Top Programa", prog_lider)
st.markdown("---")

# --- 11. GRÁFICAS ---
if not df.empty:
    st.subheader("📊 Análisis Visual")
    g1, g2 = st.columns([1, 1.5])
    
    with g1:
        st.caption("Share de Estaciones")
        df_pie = df['ESTACION'].value_counts().reset_index()
        df_pie.columns = ['Estación', 'Spots']
        pie = alt.Chart(df_pie).mark_arc(innerRadius=60).encode(
            theta='Spots', color='Estación', tooltip=['Estación', 'Spots']
        ).properties(height=250)
        st.altair_chart(pie, use_container_width=True)
    
    with g2:
        st.caption("🏆 Top 10 Programas")
        df_prog = df['PROGRAMA'].value_counts().head(10).reset_index()
        df_prog.columns = ['Programa', 'Spots']
        df_prog['Etiqueta'] = df_prog['Programa'].str.slice(0, 25) + " (" + df_prog['Spots'].astype(str) + ")"
        
        bar = alt.Chart(df_prog).mark_bar().encode(
            x='Spots', 
            y=alt.Y('Etiqueta', sort='-x', title=None),
            color=alt.Color('Programa', legend=None), 
            tooltip=['Programa', 'Spots']
        )
        text = bar.mark_text(align='left', dx=2).encode(text='Spots')
        st.altair_chart(bar + text, use_container_width=True)

    t1, t2 = st.columns(2)
    with t1:
        st.caption("Tendencia Diaria")
        df_line = df.groupby(df['FECHA'].dt.date).size().reset_index(name='Spots')
        df_line['Fecha'] = df_line['FECHA'].astype(str)
        line = alt.Chart(df_line).mark_line(point=True).encode(
            x='Fecha', y='Spots', tooltip=['Fecha', 'Spots']
        ).properties(height=250)
        st.altair_chart(line, use_container_width=True)
    with t2:
        st.caption("Mapa Horario")
        df_hour = df.groupby('HORA_NUM').size().reset_index(name='Spots')
        area = alt.Chart(df_hour).mark_area(opacity=0.3, color='red').encode(
            x='HORA_NUM', y='Spots'
        )
        st.altair_chart(area, use_container_width=True)

# --- 12. BUSCADOR Y TABLA ---
st.markdown("---")
busqueda_texto = st.text_input("🔍 Buscador Profundo: Filtra por contenido...", placeholder="Escribe aquí para buscar dentro de las transcripciones...")

if busqueda_texto:
    df_tabla = df[df['TEXTO_FULL'].astype(str).str.contains(busqueda_texto, case=False, na=False)]
else:
    df_tabla = df

# --- AJUSTE DE COLUMNAS SOLICITADO ---
# Texto (Index 6) reducido de 2.7 -> 1.5
# Audio (Index 7) aumentado de 1.2 -> 2.5
cols_width = [0.7, 0.5, 0.7, 1.0, 1.0, 1.2, 1.5, 2.5, 0.4]

ancho_titulo = sum(cols_width[:8])
ancho_boton = cols_width[8] + 0.5 

c_feed_h, c_feed_b = st.columns([4, 1])

with c_feed_h:
    st.subheader(f"📋 Feed de Resultados ({len(df_tabla)})")

with c_feed_b:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_export = df_tabla.copy()
        df_export['FECHA'] = df_export['FECHA'].dt.strftime('%d/%m/%Y')
        df_export.to_excel(writer, sheet_name='Reporte', index=False)
    
    st.download_button(
        "📥 Descargar Excel", 
        buffer.getvalue(), 
        f"Reporte_{datetime.date.today().strftime('%d-%m-%Y')}.xlsx", 
        use_container_width=True
    )

headers = ["📅 Fecha", "⏰ Hora", "🏙️ Ciudad", "📡 Estación", "🎙️ Programa", "🏷️ Spot", "📝 Texto", "▶️ Audio", "🔗"]
h_cols = st.columns(cols_width)
for i, h in enumerate(headers):
    h_cols[i].markdown(f"**{h}**")
st.markdown("<hr style='margin: 5px 0; border-top: 2px solid #ddd;'>", unsafe_allow_html=True)

asc = True if direccion == "Ascendente" else False
if criterio == "Fecha/Hora": df_tabla = df_tabla.sort_values(by=['FECHA', 'HORA'], ascending=asc)
elif criterio == "Estación": df_tabla = df_tabla.sort_values(by=['ESTACION', 'FECHA'], ascending=asc)
elif criterio == "Spot": df_tabla = df_tabla.sort_values(by=['SPOT', 'FECHA'], ascending=asc)

if not df_tabla.empty:
    for _, row in df_tabla.iterrows():
        fecha = row['FECHA'].strftime("%d/%m/%Y") if pd.notnull(row['FECHA']) else "-"
        hora = str(row.get('HORA', '-'))[:5]
        ciudad = str(row.get('CIUDAD', ''))
        est = str(row.get('ESTACION', ''))
        freq = str(row.get('FRECUENCIA', ''))
        prog = str(row.get('PROGRAMA', ''))
        spot = str(row.get('SPOT', ''))
        txt_full = str(row.get('TEXTO_FULL', ''))
        keywords = str(row.get('KEYWORDS', ''))
        link = str(row.get('LINK', ''))
        txt_short = (txt_full[:60] + '...') if len(txt_full) > 60 else txt_full

        c = st.columns(cols_width)
        c[0].write(fecha)
        c[1].write(hora)
        c[2].write(ciudad)
        c[3].markdown(f"**{est}**<br><span class='badge-freq'>{freq}</span>", unsafe_allow_html=True)
        c[4].caption(prog)
        c[5].markdown(f"<span class='spot-highlight'>{spot}</span>", unsafe_allow_html=True)
        
        with c[6]:
            with st.expander(txt_short):
                st.markdown(f"**Transcripción Completa:**")
                st.write(txt_full)
                if keywords:
                    st.divider()
                    st.info(f"🔑 **Keywords:** {keywords}")
        
        with c[7]:
            if link.startswith("http"): st.audio(link)
        
        with c[8]:
            if link.startswith("http"): st.link_button("🔗", link)
            
        st.markdown("<hr style='margin: 0; opacity: 0.2;'>", unsafe_allow_html=True)
else:
    st.info("No se encontraron resultados con los filtros actuales.")
