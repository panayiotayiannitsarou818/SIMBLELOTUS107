
import streamlit as st
import pandas as pd
from datetime import datetime
import re, os, zipfile, sys
from io import BytesIO

# Load helper
sys.path.append("/mnt/data")
from friends_utils import detect_broken_mutuals, auto_rename_columns

st.set_page_config(page_title="🔎 Έλεγχος Σπασμένων Αμοιβαίων Δυάδων", page_icon="🧩", layout="wide")
st.title("🔎 Έλεγχος Σπασμένων Αμοιβαίων Δυάδων")

st.markdown("Ανέβασε ένα **Excel** με **πολλαπλά sheets** (σενάρια). Η εφαρμογή εντοπίζει **όλες τις σπασμένες πλήρως αμοιβαίες** φιλίες ανά σενάριο.")

up = st.file_uploader("Επίλεξε Excel (.xlsx)", type=["xlsx"])
if not up:
    st.stop()

# Read workbook
xl = pd.ExcelFile(up)
sheet_names = xl.sheet_names

summary_rows = []
per_sheet_stats = {}
per_sheet_broken = {}

for sheet in sheet_names:
    df_raw = pd.read_excel(up, sheet_name=sheet)
    df, _ = auto_rename_columns(df_raw)
    # Basic stats
    total = df.groupby("ΤΜΗΜΑ").size() if "ΤΜΗΜΑ" in df else pd.Series(dtype=int)
    # Broken detector
    broken_by_class, broken_list_df, mutual_total, broken_total = detect_broken_mutuals(df)
    st.subheader(f"Σενάριο: {sheet}")
    cols = st.columns([2,3])
    with cols[0]:
        if not total.empty:
            st.write("**Πληθυσμός ανά τμήμα**")
            st.dataframe(total.rename("ΣΥΝΟΛΟ ΜΑΘΗΤΩΝ").to_frame())
        st.write("**Σπασμένες αμοιβαίες δυάδες ανά τμήμα**")
        st.dataframe(broken_by_class.rename("ΣΠΑΣΜΕΝΗ ΦΙΛΙΑ").to_frame())
    with cols[1]:
        st.write(f"**Broken pairs (σύνολο: {broken_total} / mutual: {mutual_total})**")
        st.dataframe(broken_list_df if not broken_list_df.empty else pd.DataFrame({"info": ["— καμία —"]}))

    per_sheet_stats[sheet] = total.rename("ΣΥΝΟΛΟ ΜΑΘΗΤΩΝ").to_frame()
    per_sheet_broken[sheet] = broken_list_df.copy()

    summary_rows.append({
        "ΣΕΝΑΡΙΟ": sheet,
        "ΣΥΝΟΛΟ ΜΑΘΗΤΩΝ": int(total.sum()) if not total.empty else 0,
        "ΤΜΗΜΑΤΑ": len(total.index),
        "MUTUAL_ΠΑΙΡΝΩ": mutual_total,
        "BROKEN_MUTUAL_ΠΑΙΡΝΩ": broken_total,
        "OK (καμία σπασμένη)": "ΝΑΙ" if broken_total == 0 else "ΟΧΙ"
    })

summary_df = pd.DataFrame(summary_rows).sort_values("ΣΕΝΑΡΙΟ")
st.markdown("### SUMMARY")
st.dataframe(summary_df)

# Export button: build a single Excel with SUMMARY + per-scenario sheets + per-scenario BROKEN sheets
def build_output():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as w:
        summary_df.to_excel(w, index=False, sheet_name="SUMMARY")
        for scen, stats_df in per_sheet_stats.items():
            stats_df.to_excel(w, sheet_name=re.sub(r'[:\\/?*\\[\\]]',' ',str(scen))[:31])
        for scen, broken_df in per_sheet_broken.items():
            name = re.sub(r'[:\\/?*\\[\\]]',' ',str(scen))[:25] + "_BROKEN"
            if broken_df.empty:
                pd.DataFrame({"info": ["— καμία σπασμένη —"]}).to_excel(w, index=False, sheet_name=name[:31])
            else:
                broken_df.to_excel(w, index=False, sheet_name=name[:31])
    bio.seek(0)
    return bio

st.download_button(
    "⬇️ Λήψη αναφοράς (Excel)",
    data=build_output(),
    file_name=f"broken_friends_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
