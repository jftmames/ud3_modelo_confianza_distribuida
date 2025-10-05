import os
import io
import zipfile
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

# ---------------------------
# Configuración general
# ---------------------------
st.set_page_config(
    page_title="UD3 — El modelo de confianza distribuida",
    page_icon="🤝",
    layout="wide",
)

# Tema oscuro: pequeños ajustes de contraste
st.markdown("""
<style>
pre, code, .stCode, .stMarkdown code { background:#0f1b2d !important; color:#e5e7eb !important; }
[data-testid="stTable"] th, [data-testid="stDataFrame"] thead th { background:#0f172a !important; color:#e5e7eb !important; }
</style>
""", unsafe_allow_html=True)

os.makedirs("entregas", exist_ok=True)
os.makedirs("materiales", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ---------------------------
# Utilidades
# ---------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def download_csv_button(df: pd.DataFrame, label: str, filename: str):
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    st.download_button(label, buf.getvalue(), file_name=filename, mime="text/csv")

def _zip_folder_md(folder_path: str) -> io.BytesIO:
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, folder_path)
                    zf.write(full_path, arcname=arcname)
    mem.seek(0)
    return mem

def _list_md_files(folder: str):
    if not os.path.isdir(folder):
        return []
    return sorted([f for f in os.listdir(folder) if f.endswith(".md")])

def _delete_md_in_folder(folder: str) -> int:
    if not os.path.isdir(folder):
        return 0
    count = 0
    for f in os.listdir(folder):
        if f.endswith(".md"):
            try:
                os.remove(os.path.join(folder, f))
                count += 1
            except Exception:
                pass
    return count

# ---------------------------
# Datos demo
# ---------------------------
@st.cache_data
def load_trust_cases():
    # Opcional: si creas data/trust_cases.csv con columnas: caso, descripcion
    try:
        return pd.read_csv("data/trust_cases.csv")
    except Exception:
        return pd.DataFrame({
            "caso": [
                "Registro Civil",
                "Marketplace entre particulares",
                "Cadena de suministros (food trust)",
                "DAO de inversión"
            ],
            "descripcion": [
                "Actos de estado civil bajo fe pública y procedimiento legal.",
                "Transacciones P2P basadas en reputación y reseñas.",
                "Trazabilidad de origen y transformación con registros compartidos.",
                "Decisiones por voto on-chain y tesorería multifirma."
            ]
        })

trust_cases = load_trust_cases()

# ---------------------------
# Estado inicial seguro
# ---------------------------
if "debate_posicion" not in st.session_state:
    st.session_state["debate_posicion"] = "Depende"

# ---------------------------
# Encabezado
# ---------------------------
st.title("UD3 — El modelo de confianza distribuida")
st.caption("Comparación entre confianza **institucional**, **social** y **algorítmica**; debate y lectura guiada (De Filippi, 2018).")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Modelos", "3 enfoques", delta="Institucional/Social/Algorítmica")
c2.metric("Debate", "¿Code is Law?", delta="Marco jurídico vs código")
c3.metric("Lectura", "De Filippi (2018)", delta="Guía y preguntas")
c4.metric("Entrega", "S1 + S2 + Debate", delta="Descarga/ZIP/Borrado")
st.divider()

tabs = st.tabs([
    "1) Teoría",
    "2) S1 — Comparativa de confianza",
    "3) S2 — Protocolo de validación",
    "4) Debate orientador",
    "5) Lecturas guiadas",
    "6) Entregables y rúbrica"
])

# ---------------------------
# 1) Teoría
# ---------------------------
with tabs[0]:
    st.subheader("Tres modelos de confianza y su lógica")
    st.markdown(
        """
**Institucional (TTP):** autoridad, procedimiento, responsabilidad pública.  
**Social (reputación):** normas, comunidad, redes de confianza, sanción social.  
**Algorítmica (blockchain):** reglas de consenso, criptografía, réplica, automatización (smart contracts).

**Claves comparadas**
- **Garantía principal:** fe pública | reputación | inmutabilidad probabilística.
- **Mecanismo:** validación formal | evaluación social | verificación criptográfica y consenso.
- **Riesgos típicos:** error humano/corrupción | colusión/manipulación | bugs/gobernanza de protocolo.
- **Efectos frente a terceros:** reconocimiento jurídico | legitimidad comunitaria | depende del marco normativo.
"""
    )
    st.info("Idea-faro: la blockchain no elimina el Derecho; **mueve** parte de la validación al **código + red**. El encaje jurídico sigue importando.")

    st.markdown("### Casos de uso para enmarcar")
    case = st.selectbox(
        "Selecciona un caso (puedes usarlo en S1 y S2):",
        options=trust_cases["caso"].tolist(),
        index=0
    )
    st.write(trust_cases.loc[trust_cases["caso"] == case, "descripcion"].values[0])

# ---------------------------
# 2) S1 — Comparativa de confianza
# ---------------------------
with tabs[1]:
    st.header("S1 — Matriz comparativa: institucional vs social vs algorítmica")

    st.markdown("#### 2.1 Valora qué modelo cubre mejor cada **función jurídica** (1–5)")
    base = pd.DataFrame([
        ["Identidad/Autenticidad", 5, 3, 3],
        ["Integridad del registro", 4, 2, 5],
        ["Trazabilidad/Historial", 3, 2, 5],
        ["Publicidad/Oponibilidad", 5, 3, 3],
        ["Gobernanza/Actualización", 4, 3, 4],
    ], columns=["Función", "Institucional", "Social", "Algorítmica"])
    s1_table = st.data_editor(base, width="stretch", num_rows="dynamic")

    st.markdown("#### 2.2 Observa el perfil agregado")
    try:
        sums = s1_table[["Institucional", "Social", "Algorítmica"]].sum()
        chart_df = pd.DataFrame({"Modelo": sums.index, "Puntuación": sums.values})
        st.bar_chart(chart_df.set_index("Modelo"))
    except Exception:
        st.caption("Completa valores numéricos para ver el gráfico.")

    st.markdown("#### 2.3 Comentario breve (5–7 líneas)")
    # Botón/Callback antes del text_area para no mutar key tras instanciación
    st.text_area(
        "¿Qué patrón ves entre los tres modelos? ¿Dónde falta soporte jurídico?",
        height=140, key="s1_comentario"
    )

    colL, colR = st.columns([1, 1])
    with colL:
        if st.button("💾 Guardar entrega S1 (MD)"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"entregas/UD3_S1_{ts}.md"
            with open(fname, "w", encoding="utf-8") as f:
                f.write("# UD3 — Entrega S1 (Comparativa de confianza)\n\n")
                f.write(f"**Fecha:** {ts}\n\n")
                f.write("## Matriz (suma de puntuaciones)\n\n")
                try:
                    f.write(s1_table.to_csv(index=False))
                except Exception:
                    f.write("Tabla no disponible.\n")
                f.write("\n## Comentario\n\n")
                f.write((st.session_state.get("s1_comentario") or "").strip() + "\n")
            st.success(f"Entrega guardada en {fname}")
            with open(fname, "r", encoding="utf-8") as fh:
                st.download_button("⬇️ Descargar ahora (UD3 S1)", fh.read(),
                                   file_name=os.path.basename(fname), mime="text/markdown", key=f"dl_ud3s1_{ts}")
    with colR:
        download_csv_button(s1_table, "⬇️ Descargar matriz CSV", "UD3_S1_matriz.csv")

# ---------------------------
# 3) S2 — Protocolo de validación
# ---------------------------
with tabs[2]:
    st.header("S2 — Diseña un **protocolo de validación** para el caso seleccionado")

    st.markdown("#### 3.1 Pasos típicos por modelo (elige y ordena mentalmente)")
    colA, colB, colC = st.columns(3)

    pasos_inst = [
        "Identificación presencial/administrativa",
        "Revisión formal (legal/registral)",
        "Firma/fe pública",
        "Asiento y publicidad formal",
        "Recurso/impugnación"
    ]
    pasos_soc = [
        "Verificación por pares/comunidad",
        "Historial/reputación del actor",
        "Garantías/escrow comunitario",
        "Moderación/mediación",
        "Sanción social/listas negras"
    ]
    pasos_algo = [
        "Preparar transacción y firmar",
        "Propagar a la red",
        "Incluir en bloque (consenso)",
        "Confirmaciones/finalidad",
        "Ejecución automática (smart contract)"
    ]

    with colA:
        sel_inst = st.multiselect("Institucional", options=pasos_inst, default=pasos_inst[:3], key="s2_inst")
    with colB:
        sel_soc = st.multiselect("Social", options=pasos_soc, default=pasos_soc[:3], key="s2_soc")
    with colC:
        sel_algo = st.multiselect("Algorítmica", options=pasos_algo, default=pasos_algo[:3], key="s2_algo")

    st.markdown("#### 3.2 Riesgos y mitigaciones (marca los que apliquen)")
    colR1, colR2, colR3 = st.columns(3)
    with colR1:
        r_inst = st.multiselect("Riesgos institucionales", ["error humano", "corrupción", "retrasos/procedimiento"], key="r_inst")
    with colR2:
        r_soc = st.multiselect("Riesgos sociales", ["colusión", "astroturfing", "sesgos/comunidades cerradas"], key="r_soc")
    with colR3:
        r_algo = st.multiselect("Riesgos algorítmicos", ["bug/contrato", "clave comprometida", "captura de gobernanza"], key="r_algo")

    st.markdown("#### 3.3 Síntesis en 6–8 líneas")
    s2_sintesis = st.text_area(
        "Describe tu protocolo híbrido: qué valida cada capa, dónde se ancla la oponibilidad y cómo gestionas los riesgos.",
        height=160, key="s2_sintesis"
    )

    if st.button("💾 Guardar entrega S2 (MD)"):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"entregas/UD3_S2_{ts}.md"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("# UD3 — Entrega S2 (Protocolo de validación)\n\n")
            f.write(f"**Fecha:** {ts}\n\n")
            f.write(f"**Caso:** {case}\n\n")
            f.write("## Pasos seleccionados\n\n")
            f.write(f"- Institucional: {', '.join(sel_inst) or '—'}\n")
            f.write(f"- Social: {', '.join(sel_soc) or '—'}\n")
            f.write(f"- Algorítmica: {', '.join(sel_algo) or '—'}\n\n")
            f.write("## Riesgos señalados\n\n")
            f.write(f"- Institucional: {', '.join(r_inst) or '—'}\n")
            f.write(f"- Social: {', '.join(r_soc) or '—'}\n")
            f.write(f"- Algorítmica: {', '.join(r_algo) or '—'}\n\n")
            f.write("## Síntesis\n\n")
            f.write((s2_sintesis or "").strip() + "\n")
        st.success(f"Entrega guardada en {fname}")
        with open(fname, "r", encoding="utf-8") as fh:
            st.download_button("⬇️ Descargar ahora (UD3 S2)", fh.read(),
                               file_name=os.path.basename(fname), mime="text/markdown", key=f"dl_ud3s2_{ts}")

# ---------------------------
# 4) Debate orientador
# ---------------------------
with tabs[3]:
    st.header("Debate: “¿Es la blockchain una nueva forma de Derecho?”")

    st.markdown(
        """
**Instrucción:** elige postura inicial y redacta **tesis (1)**, **tres argumentos (3)**, **contraargumento (1)** y **matiz final (1)**.  
Apóyate en los modelos de confianza y en el encaje normativo.
"""
    )

    st.radio(
        "Postura inicial",
        options=["Sí", "No", "Depende"],
        key="debate_posicion",
        horizontal=True
    )

    with st.expander("Sugerencias de línea argumental (orientativas)"):
        st.markdown(
            """
- **Sí:** el código regula conductas y genera efectos predecibles; smart contracts como “normas ejecutables”.  
- **No:** el Derecho implica legitimidad democrática, interpretación y garantías; el código carece de jurisdicción y debido proceso.  
- **Depende:** código + normas + gobernanza; la blockchain **complementa** funciones (integridad/trazabilidad) pero no reemplaza oponibilidad ni garantías sin reconocimiento legal.
"""
        )

    colA, colB = st.columns(2)
    with colA:
        t_tesis = st.text_area("Tesis (1–2 frases)", height=80, key="deb_tesis")
        a1 = st.text_area("Argumento 1", height=80, key="deb_a1")
        a2 = st.text_area("Argumento 2", height=80, key="deb_a2")
        a3 = st.text_area("Argumento 3", height=80, key="deb_a3")
    with colB:
        c1 = st.text_area("Contraargumento a tu postura", height=120, key="deb_contra")
        m1 = st.text_area("Matiz final / condiciones", height=120, key="deb_matiz")

    if st.button("💾 Guardar entrega Debate (MD)"):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"entregas/UD3_Debate_{ts}.md"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("# UD3 — Debate: ¿Blockchain = nueva forma de Derecho?\n\n")
            f.write(f"**Fecha:** {ts}\n\n")
            f.write(f"**Postura inicial:** {st.session_state.get('debate_posicion')}\n\n")
            f.write("## Tesis\n\n" + (t_tesis or "").strip() + "\n\n")
            f.write("## Argumentos\n\n")
            f.write("- " + (a1 or "").strip() + "\n")
            f.write("- " + (a2 or "").strip() + "\n")
            f.write("- " + (a3 or "").strip() + "\n\n")
            f.write("## Contraargumento\n\n" + (c1 or "").strip() + "\n\n")
            f.write("## Matiz final\n\n" + (m1 or "").strip() + "\n")
        st.success(f"Entrega guardada en {fname}")
        with open(fname, "r", encoding="utf-8") as fh:
            st.download_button("⬇️ Descargar ahora (UD3 Debate)", fh.read(),
                               file_name=os.path.basename(fname), mime="text/markdown", key=f"dl_ud3deb_{ts}")

# ---------------------------
# 5) Lecturas guiadas
# ---------------------------
with tabs[4]:
    st.header("Lectura complementaria — Primavera De Filippi (2018): *Blockchain and the Law*")
    st.markdown(
        """
**Ejes para UD3**
- Arquitectura descentralizada y **gobernanza** del protocolo.
- **Lex cryptographica**: qué puede y qué no puede “regular” el código.
- Interoperabilidad con el **ordenamiento** (identidad, jurisdicción, responsabilidad).

**Preguntas guía**
1) ¿Qué funciones jurídicas se desplazan al código y cuáles permanecen en la norma?  
2) ¿Cómo se articula la **responsabilidad** cuando la validación es distribuida?  
3) ¿Qué dependencias jurídicas persisten para lograr **oponibilidad**?
"""
    )

    if st.button("📄 Generar y guardar guía (MD)"):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"materiales/UD3_lecturas_{ts}.md"
        content = """# Guía de lectura — UD3

## De Filippi (2018): Blockchain and the Law
- Ejes: gobernanza del protocolo, lex cryptographica, encaje con ordenamiento.
- Foco UD3: cambio de paradigma en validación (institucional/social → algorítmica) y límites.

## Preguntas guía
1) ¿Qué funciones jurídicas pasa a ejecutar el código?
2) ¿Cómo se distribuye la responsabilidad en redes sin TTP?
3) ¿Qué requiere la oponibilidad/efectos frente a terceros?
"""
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
        st.success(f"Guía guardada en {fname}")
        with open(fname, "r", encoding="utf-8") as fh:
            st.download_button(
                "⬇️ Descargar ahora (Guía UD3)",
                fh.read(),
                file_name=os.path.basename(fname),
                mime="text/markdown",
                key=f"dl_ud3_{ts}"
            )

    st.markdown("---")
    st.info("ℹ️ Las guías se guardan en `./materiales`. Abajo puedes descargar cualquiera o todas en ZIP.")

    mats = _list_md_files("materiales")
    if mats:
        for idx, f in enumerate(mats):
            path = os.path.join("materiales", f)
            with open(path, "r", encoding="utf-8") as fh:
                st.download_button(
                    f"⬇️ Descargar {f}",
                    fh.read(),
                    file_name=f,
                    mime="text/markdown",
                    key=f"dl_mat_{idx}_{f}"
                )
        memzip_mat = _zip_folder_md("materiales")
        st.download_button(
            "⬇️ Descargar TODO (ZIP)",
            memzip_mat,
            file_name="materiales_ud3.zip",
            mime="application/zip",
            key="zip_mat_ud3"
        )
    else:
        st.caption("No hay materiales .md para comprimir aún.")

# ---------------------------
# 6) Entregables y rúbrica
# ---------------------------
with tabs[5]:
    st.header("Entregables (UD3) y rúbrica")
    st.info(
        "ℹ️ Al guardar, los archivos se crean en el **servidor** dentro de `./entregas`. "
        "Desde aquí puedes **descargar** cada entrega o **todas en ZIP** y, si quieres, **borrarlas**."
    )

    st.markdown("#### Entregas guardadas")
    files = _list_md_files("entregas")
    if files:
        for idx, f in enumerate(files):
            p = os.path.join("entregas", f)
            with open(p, "r", encoding="utf-8") as fh:
                st.download_button(
                    f"⬇️ Descargar {f}",
                    fh.read(),
                    file_name=f,
                    mime="text/markdown",
                    key=f"dl_ent_{idx}_{f}"
                )
        memzip = _zip_folder_md("entregas")
        st.download_button(
            "⬇️ Descargar TODO (ZIP)",
            memzip,
            file_name="entregas_ud3.zip",
            mime="application/zip",
            key="zip_ent_ud3"
        )
    else:
        st.caption("Aún no hay entregas guardadas.")

    st.markdown("#### Borrado tras descarga")
    confirm = st.checkbox("He descargado mis entregas y quiero borrarlas del servidor")
    if st.button("🧹 Borrar todas las entregas (.md)", disabled=not confirm):
        removed = _delete_md_in_folder("entregas")
        if removed > 0:
            st.success(f"Se borraron {removed} archivo(s) .md de 'entregas'.")
        else:
            st.warning("No había archivos .md que borrar.")

    st.markdown("---")
    st.caption(
        "Rúbrica general: precisión conceptual (40%), claridad y argumentación (30%), "
        "aplicación a casos/encaje jurídico (30%).\n\n"
        "Conclusión UD3: describe el **cambio de paradigma** en la validación jurídica: "
        "de la **autoridad** y la **reputación** hacia una **validación algorítmica** replicada, "
        "sin perder de vista la oponibilidad y la responsabilidad en el ordenamiento."
    )
