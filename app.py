
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="📊 Στατιστικά Μαθητών Α' Δημοτικού", page_icon="📊", layout="wide")
st.title("📊 Στατιστικά Μαθητών Α' Δημοτικού")

st.sidebar.markdown("### ⚖️ Όροι χρήσης")
terms_ok = st.sidebar.checkbox("Αποδέχομαι τους όρους χρήσης", value=False)
st.sidebar.markdown("© 2025 • Πνευματικά δικαιώματα • All rights reserved")

if not terms_ok:
    st.warning("⚠️ Για να χρησιμοποιήσεις την εφαρμογή, αποδέξου τους όρους χρήσης (αριστερά).")
    st.stop()

# Session State
for key, default in [("data", None), ("stats_df", None), ("show_upload", False), ("diagnostics", {})]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Column normalization ----------
# Canonical keys: remove spaces/underscores and uppercase
def canon(s: str) -> str:
    return "".join((s or "").replace("_"," ").split()).upper()

CANON_TARGETS = {
    "ΟΝΟΜΑ": {"ΟΝΟΜΑ"},
    "ΦΥΛΟ": {"ΦΥΛΟ"},
    "ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ": {"ΠΑΙΔΙΕΚΠΑΙΔΕΥΤΙΚΟΥ", "ΠΑΙΔΙ-ΕΚΠΑΙΔΕΥΤΙΚΟΥ"},
    "ΖΩΗΡΟΣ": {"ΖΩΗΡΟΣ"},
    "ΙΔΙΑΙΤΕΡΟΤΗΤΑ": {"ΙΔΙΑΙΤΕΡΟΤΗΤΑ"},
    "ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ": {"ΚΑΛΗΓΝΩΣΗΕΛΛΗΝΙΚΩΝ", "ΓΝΩΣΗΕΛΛΗΝΙΚΩΝ"},
    "ΦΙΛΟΙ": {"ΦΙΛΟΙ", "ΦΙΛΙΑ"},
    "ΣΥΓΚΡΟΥΣΗ": {"ΣΥΓΚΡΟΥΣΗ", "ΣΥΓΚΡΟΥΣΕΙΣ"},
    "ΤΜΗΜΑ": {"ΤΜΗΜΑ"},
}

REQUIRED_COLS = ["ΟΝΟΜΑ","ΦΥΛΟ","ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ","ΖΩΗΡΟΣ","ΙΔΙΑΙΤΕΡΟΤΗΤΑ","ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ","ΦΙΛΟΙ","ΣΥΓΚΡΟΥΣΗ","ΤΜΗΜΑ"]

def auto_rename_columns(df: pd.DataFrame):
    mapping = {}
    seen = set()
    for col in df.columns:
        c = canon(col)
        found_target = None
        for target, keys in CANON_TARGETS.items():
            if c in keys and target not in seen:
                found_target = target
                seen.add(target)
                break
        if found_target:
            mapping[col] = found_target
    return df.rename(columns=mapping), mapping

def _normalize_yes_no(series: pd.Series) -> pd.Series:
    if series.dtype == object:
        s = series.fillna("").astype(str).str.strip().str.upper()
        s = s.replace({
            "ΝΑΙ":"Ν","NAI":"Ν","YES":"Ν","Y":"Ν",
            "ΟΧΙ":"Ο","OXI":"Ο","NO":"Ο","N":"Ο","": "Ο"
        })
        return s.where(s.isin(["Ν","Ο"]), other="Ο")
    return series

def _broken_mutual_friendships_per_class(df: pd.DataFrame) -> pd.Series:
    # Accept ΦΙΛΟΙ (already normalized)
    fcol = "ΦΙΛΟΙ" if "ΦΙΛΟΙ" in df.columns else None
    if fcol is None or "ΟΝΟΜΑ" not in df.columns or "ΤΜΗΜΑ" not in df.columns:
        return df.groupby("ΤΜΗΜΑ").size() * 0

    def norm_name(x: str) -> str:
        return (x or "").strip()

    names = df["ΟΝΟΜΑ"].fillna("").astype(str).apply(norm_name)
    class_by_name = dict(zip(names, df["ΤΜΗΜΑ"]))

    friends_map = {}
    for _, row in df.iterrows():
        me = norm_name(str(row.get("ΟΝΟΜΑ", "")))
        raw = str(row.get(fcol, "") or "")
        flist = [norm_name(p) for p in raw.split(",") if norm_name(p)]
        friends_map[me] = set(flist)

    mutual_pairs = set()
    for a, flist in friends_map.items():
        for b in flist:
            if b in friends_map and a in friends_map[b]:
                mutual_pairs.add(tuple(sorted([a,b])))

    broken_count_by_class = {tmima: 0 for tmima in df["ΤΜΗΜΑ"].dropna().unique()}
    for a, b in mutual_pairs:
        ta = class_by_name.get(a)
        tb = class_by_name.get(b)
        if ta and tb and ta != tb:
            broken_count_by_class[ta] = broken_count_by_class.get(ta, 0) + 1
            broken_count_by_class[tb] = broken_count_by_class.get(tb, 0) + 1

    return pd.Series(broken_count_by_class)

def _generate_stats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalize core fields
    if "ΦΥΛΟ" in df:
        df["ΦΥΛΟ"] = df["ΦΥΛΟ"].fillna("").astype(str).str.strip().str.upper()
    for col in ["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ","ΖΩΗΡΟΣ","ΙΔΙΑΙΤΕΡΟΤΗΤΑ","ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ"]:
        if col in df:
            df[col] = _normalize_yes_no(df[col])

    boys = df[df["ΦΥΛΟ"] == "Α"].groupby("ΤΜΗΜΑ").size()
    girls = df[df["ΦΥΛΟ"] == "Κ"].groupby("ΤΜΗΜΑ").size()
    educators = df[df["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν"].groupby("ΤΜΗΜΑ").size()
    energetic = df[df["ΖΩΗΡΟΣ"] == "Ν"].groupby("ΤΜΗΜΑ").size()
    special = df[df["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν"].groupby("ΤΜΗΜΑ").size()
    greek = df[df["ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ"] == "Ν"].groupby("ΤΜΗΜΑ").size()
    total = df.groupby("ΤΜΗΜΑ").size()

    broken_by_class = _broken_mutual_friendships_per_class(df)

    stats = pd.DataFrame({
        "ΑΓΟΡΙΑ": boys,
        "ΚΟΡΙΤΣΙΑ": girls,
        "ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ": educators,
        "ΖΩΗΡΟΙ": energetic,
        "ΙΔΙΑΙΤΕΡΟΤΗΤΑ": special,
        "ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ": greek,
        "ΣΠΑΣΜΕΝΗ ΦΙΛΙΑ": broken_by_class,
        "ΣΥΝΟΛΟ": total,
    }).fillna(0).astype(int)

    try:
        stats = stats.sort_index(key=lambda x: x.str.extract(r"(\d+)")[0].astype(float))
    except Exception:
        stats = stats.sort_index()

    return stats

def _export_to_excel(stats_df: pd.DataFrame) -> BytesIO:
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            stats_df.to_excel(writer, index=True, sheet_name="Στατιστικά", index_label="ΤΜΗΜΑ")
            wb = writer.book
            ws = writer.sheets["Στατιστικά"]
            header_fmt = wb.add_format({"bold": True, "valign":"vcenter", "text_wrap": True, "border":1})
            for col_idx, value in enumerate(["ΤΜΗΜΑ"] + list(stats_df.columns)):
                ws.write(0, col_idx, value, header_fmt)
            for i in range(0, len(stats_df.columns)+1):
                ws.set_column(i, i, 18)
    except Exception:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            stats_df.to_excel(writer, index=True, sheet_name="Στατιστικά", index_label="ΤΜΗΜΑ")
    output.seek(0)
    return output

# ---------- UI ----------
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("📥 Εισαγωγή Excel", type="primary"):
        st.session_state.show_upload = True
with c2:
    export_clicked = st.button("📊 Εξαγωγή ΠΙΝΑΚΑ ΣΤΑΤΙΣΤΙΚΩΝ", disabled=st.session_state.data is None)
with c3:
    if st.button("🔄 Επανεκκίνηση"):
        st.session_state.data = None
        st.session_state.stats_df = None
        st.session_state.show_upload = False
        st.session_state.diagnostics = {}
        st.rerun()

if st.session_state.show_upload:
    st.markdown("### 📥 Εισαγωγή Αρχείου Excel")
    up = st.file_uploader("Επίλεξε αρχείο Excel με δεδομένα μαθητών", type=["xlsx","xls"])
    if up:
        try:
            df_raw = pd.read_excel(up)
            df_norm, ren_map = auto_rename_columns(df_raw)
            st.session_state.data = df_norm.copy()

            # Diagnostics
            present = list(df_norm.columns)
            missing = [c for c in REQUIRED_COLS if c not in present]
            st.session_state.diagnostics = {
                "recognized_columns": present,
                "renamed": ren_map,
                "missing_required": missing,
                "classes_found": sorted([str(x) for x in df_norm["ΤΜΗΜΑ"].dropna().unique()]) if "ΤΜΗΜΑ" in df_norm else []
            }

            st.success(f"✅ Επιτυχής φόρτωση! Βρέθηκαν {len(df_norm)} μαθητές.")
            with st.expander("🔎 Διάγνωση αρχείου (στήλες που αναγνωρίστηκαν)", expanded=False):
                st.write("Αναγνωρισμένες στήλες:", present)
                if ren_map:
                    st.write("Αυτόματες μετονομασίες:", ren_map)
                if missing:
                    st.error("❌ Λείπουν υποχρεωτικές στήλες: " + ", ".join(missing))
                if "ΤΜΗΜΑ" in df_norm:
                    st.write("Τμήματα που βρέθηκαν:", st.session_state.diagnostics["classes_found"])

            # Live preview stats (αν δεν λείπουν υποχρεωτικές)
            if not st.session_state.diagnostics["missing_required"]:
                st.markdown("### 👀 Προεπισκόπηση Πίνακα Στατιστικών")
                preview = _generate_stats(df_norm)
                st.session_state.stats_df = preview
                st.dataframe(preview, use_container_width=True)
            else:
                st.info("Συμπλήρωσε/διόρθωσε τις στήλες που λείπουν και ξαναφόρτωσε το αρχείο.")

        except Exception as e:
            st.error(f"❌ Σφάλμα κατά τη φόρτωση: {e}")

# Export
if export_clicked and st.session_state.data is not None:
    if st.session_state.diagnostics and st.session_state.diagnostics.get("missing_required"):
        st.error("Δεν γίνεται εξαγωγή: λείπουν υποχρεωτικές στήλες: " + ", ".join(st.session_state.diagnostics["missing_required"]))
    else:
        st.markdown("### 📊 Πίνακας Στατιστικών")
        stats_df = _generate_stats(st.session_state.data)
        st.session_state.stats_df = stats_df
        st.dataframe(stats_df, use_container_width=True)
        output = _export_to_excel(stats_df)
        st.download_button(
            label="💾 Λήψη Πίνακα Στατιστικών (Excel)",
            data=output.getvalue(),
            file_name=f"statistika_mathiton_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

# Sidebar tips
st.sidebar.markdown("### 🧭 Οδηγίες")
st.sidebar.markdown(
    "- Πατήστε **Εισαγωγή Excel** και φορτώστε το αρχείο δεδομένων.\n"
    "- Αν αναγνωριστούν όλες οι στήλες, θα δείτε **προεπισκόπηση** του πίνακα.\n"
    "- Πατήστε **Εξαγωγή ΠΙΝΑΚΑ ΣΤΑΤΙΣΤΙΚΩΝ** για λήψη του Excel.\n"
    "- Αποδεκτές στήλες (ευέλικτη γραφή): ΟΝΟΜΑ, ΦΥΛΟ (Α/Κ), ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ, ΖΩΗΡΟΣ, ΙΔΙΑΙΤΕΡΟΤΗΤΑ, "
    "ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ (ή ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ), ΦΙΛΟΙ/ΦΙΛΙΑ, ΣΥΓΚΡΟΥΣΗ, ΤΜΗΜΑ."
)
