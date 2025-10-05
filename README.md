# UD3 — El modelo de confianza distribuida

Comparación entre confianza **institucional**, **social** y **algorítmica**; debate guiado y lectura (De Filippi, 2018).

## Requisitos
- Python 3.10+
- `pip install -r requirements.txt`

## Ejecución
```bash
streamlit run app.py
```

## Estructura
- `app.py`: aplicación Streamlit (pestañas, entregables, ZIP y borrado).
- `.streamlit/config.toml`: tema oscuro.
- `data/trust_cases.csv`: casos demo para las actividades.
- `entregas/`, `materiales/`: se llenan en tiempo de ejecución (incluyen `.gitkeep`).

## Notas
- Las entregas y guías se guardan en el **servidor** y puedes descargarlas desde la última pestaña.
- Las tablas usan `width="stretch"` (sin `use_container_width`).
