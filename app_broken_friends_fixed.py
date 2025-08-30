
import streamlit as st
import pandas as pd
from datetime import datetime
import re
from io import BytesIO

from friends_utils import detect_broken_mutuals, auto_rename_columns

# ---------------------------
# 🔄 Restart helpers
# ---------------------------
def _restart_app():
    """Clear caches & widget states (including file_uploader) and rerun."""
    st.session_state["uploader_key"] = st.session_state.get("uploader_key", 0) + 1
    for k in list(st.session_state.keys()):
        if str(k).startswith("uploader_"):
            del st.session_state[k]
    try:
        st.cache_data.clear()
    except Exception:
        pass
    try:
        st.cache_resource.clear()
    except Exception:
        pass
    st.rerun()

st.set_page_config(page_title="🔎 Έλεγχος Σπασμένων Αμοιβαίων Δυάδων", page_icon="🧩", layout="wide")
st.title("🔎 Έλεγχος Σπασμένων Αμοιβαίων Δυάδων")

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

st.markdown(
    """
    Ανέβασε ένα **Excel** με **πολλαπλά sheets** (σενάρια).
    Η εφαρμογή εντοπίζει **όλες τις σπασμένες πλήρως αμοιβαίες** φιλίες *ανά σενάριο*
    και σου δίνει **αναφορά Excel** (ένα sheet ανά σενάριο).
    """
)

# Sidebar restart
with st.sidebar:
    if st.button("🔄 Επανεκκίνηση εφαρμογής", help="Καθαρίζει μνήμη/φορτώσεις και ξεκινά από την αρχή"):
        _restart_app()

def sanitize_sheet_name(s: str) -> str:
    s = str(s or "")
    s = re.sub(r'[:\\/?*\\[\\]]', ' ', s)
    return s[:31] if s else "SHEET"

def build_report(xl: pd.ExcelFile) -> BytesIO:
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
        for sheet in xl.sheet_names:
            df_raw = xl.parse(sheet_name=sheet)
            df, mapping = auto_rename_columns(df_raw)

            broken_df = detect_broken_mutuals(df, name_col="name", friends_col="friends", class_col="class")
            out_name = sanitize_sheet_name(f"{sheet}_BROKEN")

            if broken_df.empty:
                pd.DataFrame({"info": ["— καμία σπασμένη —"]}).to_excel(writer, index=False, sheet_name=out_name)
            else:
                broken_df.to_excel(writer, index=False, sheet_name=out_name)
    bio.seek(0)
    return bio

up = st.file_uploader("📤 Μεταφόρτωση Excel", type=["xlsx", "xls"], key=f"uploader_{st.session_state['uploader_key']}")

if up:
    try:
        xl = pd.ExcelFile(up)
        cols1, cols2 = st.columns([1, 2], gap="large")

        with cols1:
            st.subheader("📑 Σενάρια στο αρχείο")
            st.write(xl.sheet_names)

        with cols2:
            st.subheader("🔍 Σύνοψη")
            summary_rows = []
            for sheet in xl.sheet_names:
                df_raw = xl.parse(sheet_name=sheet)
                df, _ = auto_rename_columns(df_raw)
                broken_df = detect_broken_mutuals(df)
                summary_rows.append({"Σενάριο": sheet, "Σπασμένες Δυάδες": int(len(broken_df))})
            summary = pd.DataFrame(summary_rows).sort_values("Σενάριο")
            st.dataframe(summary, use_container_width=True)

        # Download
        st.download_button(
            "⬇️ Κατέβασε αναφορά (Excel)",
            data=build_report(xl),
            file_name=f"broken_friends_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Optional: preview first non-empty
        for sheet in xl.sheet_names:
            df_raw = xl.parse(sheet_name=sheet)
            df, _ = auto_rename_columns(df_raw)
            broken_df = detect_broken_mutuals(df)
            with st.expander(f"Προβολή: {sheet}"):
                if broken_df.empty:
                    st.info("— Καμία σπασμένη πλήρως αμοιβαία δυάδα —")
                else:
                    st.dataframe(broken_df, use_container_width=True)

    except Exception as e:
        st.error(f"Σφάλμα ανάγνωσης: {e}")
else:
    st.info("➕ Επίλεξε ένα Excel για έλεγχο.")
