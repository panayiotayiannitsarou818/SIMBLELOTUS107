
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# ---------------------------
# Page / App Setup
# ---------------------------
st.set_page_config(page_title="📊 Στατιστικά Μαθητών Α' Δημοτικού", page_icon="📊", layout="wide")
st.title("📊 Στατιστικά Μαθητών Α' Δημοτικού")

# Sidebar: Legal / Terms
st.sidebar.markdown("### ⚖️ Όροι χρήσης")
terms_ok = st.sidebar.checkbox("Αποδέχομαι τους όρους χρήσης", value=False)
st.sidebar.markdown("© 2025 • Πνευματικά δικαιώματα • All rights reserved")

if not terms_ok:
    st.warning("⚠️ Για να χρησιμοποιήσεις την εφαρμογή, αποδέξου τους όρους χρήσης (αριστερά).")
    st.stop()

# ---------------------------
# Session State
# ---------------------------
for key, default in [
    ("data", None),
    ("stats_df", None),
    ("show_upload", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------
# Helper functions
# ---------------------------
REQUIRED_COLS = [
    "ΟΝΟΜΑ",
    "ΦΥΛΟ",
    "ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ",
    "ΖΩΗΡΟΣ",
    "ΙΔΙΑΙΤΕΡΟΤΗΤΑ",
    "ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ",
    # Θα δεχτούμε ΦΙΛΟΙ ή ΦΙΛΙΑ και θα το ομογενοποιήσουμε σε ΦΙΛΟΙ
    "ΦΙΛΟΙ/ΦΙΛΙΑ",
    "ΣΥΓΚΡΟΥΣΗ",
    "ΤΜΗΜΑ",
]

def _normalize_yes_no(series: pd.Series) -> pd.Series:
    if series.dtype == object:
        s = series.fillna("").astype(str).str.strip().str.upper()
        # Επιτρέπουμε μερικές παραλλαγές
        s = (s.replace({
            "ΝΑΙ":"Ν","NAI":"Ν","YES":"Ν","Y":"Ν",
            "ΟΧΙ":"Ο","OXI":"Ο","NO":"Ο","N":"Ο","": "Ο"
        }))
        # Τελική ασφάλεια: κρατάμε μόνο Ν/Ο
        return s.where(s.isin(["Ν","Ο"]), other="Ο")
    return series

def _generate_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Ενιαίος πίνακας στατιστικών ανά τμήμα, σύμφωνα με τις οδηγίες."""
    df = df.copy()

    # Ομογενοποίηση ονομάτων στηλών ΦΙΛΟΙ/ΦΙΛΙΑ -> ΦΙΛΟΙ
    if "ΦΙΛΟΙ" not in df.columns and "ΦΙΛΙΑ" in df.columns:
        df = df.rename(columns={"ΦΙΛΙΑ":"ΦΙΛΟΙ"})

    # Καθαρισμός πεδίων
    if "ΦΥΛΟ" in df:
        df["ΦΥΛΟ"] = df["ΦΥΛΟ"].fillna("").astype(str).str.strip().str.upper()
    for col in ["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ","ΖΩΗΡΟΣ","ΙΔΙΑΙΤΕΡΟΤΗΤΑ","ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ"]:
        if col in df:
            df[col] = _normalize_yes_no(df[col])

    # Υπολογισμοί ανά τμήμα
    boys = df[df["ΦΥΛΟ"] == "Α"].groupby("ΤΜΗΜΑ").size()
    girls = df[df["ΦΥΛΟ"] == "Κ"].groupby("ΤΜΗΜΑ").size()
    educators = df[df["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν"].groupby("ΤΜΗΜΑ").size()
    energetic = df[df["ΖΩΗΡΟΣ"] == "Ν"].groupby("ΤΜΗΜΑ").size()
    special = df[df["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν"].groupby("ΤΜΗΜΑ").size()
    greek = df[df["ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ"] == "Ν"].groupby("ΤΜΗΜΑ").size()
    total = df.groupby("ΤΜΗΜΑ").size()

    # Σπασμένες πλήρως αμοιβαίες φιλίες (μετράμε τους μαθητές του τμήματος που η αμοιβαία τους δυάδα είναι σε άλλο τμήμα)
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

    # Ταξινόμηση Α1, Α2, ... με βάση το νούμερο αν υπάρχει
    try:
        stats = stats.sort_index(key=lambda x: x.str.extract(r"(\d+)")[0].astype(float))
    except Exception:
        stats = stats.sort_index()

    return stats

def _broken_mutual_friendships_per_class(df: pd.DataFrame) -> pd.Series:
    """Επιστρέφει series με index=ΤΜΗΜΑ, value=αριθμός μαθητών του τμήματος
    που έχουν ΠΛΗΡΩΣ αμοιβαία δυάδα σε άλλο τμήμα.
    - Υποστηρίζονται μόνο ΔΥΑΔΕΣ (σύμφωνα με οδηγία 22/8/2025).
    - Το πεδίο χρησιμοποιείται από τη στήλη 'ΦΙΛΟΙ' ή 'ΦΙΛΙΑ' (ονόματα χωρισμένα με κόμμα).
    """
    if "ΦΙΛΟΙ" not in df.columns and "ΦΙΛΙΑ" in df.columns:
        fcol = "ΦΙΛΙΑ"
    else:
        fcol = "ΦΙΛΟΙ" if "ΦΙΛΟΙ" in df.columns else None

    if not fcol or "ΟΝΟΜΑ" not in df.columns or "ΤΜΗΜΑ" not in df.columns:
        # Δεν μπορούμε να υπολογίσουμε
        return df.groupby("ΤΜΗΜΑ").size() * 0

    # Χάρτες ονομάτων (κανονικοποιημένα) -> τάξη/πραγματικό όνομα
    def norm_name(x: str) -> str:
        return (x or "").strip()

    names = df["ΟΝΟΜΑ"].fillna("").astype(str).apply(norm_name)
    class_by_name = dict(zip(names, df["ΤΜΗΜΑ"]))

    # Λίστες φίλων (ομαλοποιημένες)
    friends_map = {}
    for _, row in df.iterrows():
        me = norm_name(str(row.get("ΟΝΟΜΑ", "")))
        raw = str(row.get(fcol, "") or "")
        flist = [norm_name(p) for p in raw.split(",") if norm_name(p)]
        friends_map[me] = set(flist)

    # Εύρεση πλήρως αμοιβαίων ΔΥΑΔΩΝ
    mutual_pairs = set()
    for a, flist in friends_map.items():
        for b in flist:
            if b in friends_map and a in friends_map[b]:
                pair = tuple(sorted([a, b]))
                # Επιτρέπουμε μόνο δυάδες. Αν κάποιος έχει παραπάνω από 1 αμοιβαίο φίλο,
                # εδώ μετράμε κάθε αμοιβαία σχέση ξεχωριστά.
                mutual_pairs.add(pair)

    # Για κάθε δυάδα, αν είναι σε διαφορετικά τμήματα -> "σπασμένη"
    broken_count_by_class = {tmima: 0 for tmima in df["ΤΜΗΜΑ"].unique()}
    for a, b in mutual_pairs:
        ta = class_by_name.get(a)
        tb = class_by_name.get(b)
        if ta and tb and ta != tb:
            # Μετράμε έναν "σπασμένο" για τον κάθε μαθητή στο δικό του τμήμα
            broken_count_by_class[ta] = broken_count_by_class.get(ta, 0) + 1
            broken_count_by_class[tb] = broken_count_by_class.get(tb, 0) + 1

    return pd.Series(broken_count_by_class)

def _export_to_excel(stats_df: pd.DataFrame) -> BytesIO:
    """Μορφοποιημένη εξαγωγή του πίνακα στατιστικών σε Excel."""
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            stats_df.to_excel(writer, index=True, sheet_name="Στατιστικά", index_label="ΤΜΗΜΑ")
            wb = writer.book
            ws = writer.sheets["Στατιστικά"]

            header_fmt = wb.add_format({"bold": True, "valign":"vcenter", "text_wrap": True, "border":1})
            for col_idx, value in enumerate(["ΤΜΗΜΑ"] + list(stats_df.columns)):
                ws.write(0, col_idx, value, header_fmt)

            # Auto-fit-ish
            for i in range(0, len(stats_df.columns)+1):
                ws.set_column(i, i, 18)
    except Exception:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            stats_df.to_excel(writer, index=True, sheet_name="Στατιστικά", index_label="ΤΜΗΜΑ")

    output.seek(0)
    return output

# ---------------------------
# Top Buttons
# ---------------------------
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
        st.rerun()

# ---------------------------
# Upload area
# ---------------------------
if st.session_state.show_upload:
    st.markdown("### 📥 Εισαγωγή Αρχείου Excel")
    up = st.file_uploader(
        "Επίλεξε αρχείο Excel με δεδομένα μαθητών",
        type=["xlsx","xls"],
        help="Το αρχείο πρέπει να περιέχει τις στήλες: " + ", ".join(REQUIRED_COLS).replace("ΦΙΛΟΙ/ΦΙΛΙΑ","ΦΙΛΟΙ ή ΦΙΛΙΑ")
    )
    if up:
        try:
            df = pd.read_excel(up)

            # Έλεγχος στηλών — δεχόμαστε ΦΙΛΟΙ ή ΦΙΛΙΑ
            cols = set(df.columns)
            missing = []
            for c in REQUIRED_COLS:
                if c == "ΦΙΛΟΙ/ΦΙΛΙΑ":
                    if "ΦΙΛΟΙ" not in cols and "ΦΙΛΙΑ" not in cols:
                        missing.append("ΦΙΛΟΙ (ή ΦΙΛΙΑ)")
                else:
                    if c not in cols:
                        missing.append(c)
            if missing:
                st.error("❌ Λείπουν οι στήλες: " + ", ".join(missing))
            else:
                # Ομογενοποίηση ΦΙΛΙΑ -> ΦΙΛΟΙ
                if "ΦΙΛΟΙ" not in df.columns and "ΦΙΛΙΑ" in df.columns:
                    df = df.rename(columns={"ΦΙΛΙΑ":"ΦΙΛΟΙ"})

                st.session_state.data = df.copy()
                st.success(f"✅ Επιτυχής φόρτωση! Βρέθηκαν {len(df)} μαθητές.")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Σφάλμα κατά τη φόρτωση: {e}")

# ---------------------------
# Generate + Export
# ---------------------------
if export_clicked and st.session_state.data is not None:
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

# ---------------------------
# Sidebar Help
# ---------------------------
st.sidebar.markdown("### 🧭 Οδηγίες")
st.sidebar.markdown(
    "- Πατήστε **Εισαγωγή Excel** και φορτώστε το αρχείο δεδομένων.\n"
    "- Πατήστε **Εξαγωγή ΠΙΝΑΚΑ ΣΤΑΤΙΣΤΙΚΩΝ** για προβολή/λήψη του πίνακα.\n"
    "- Υποστηρίζονται στήλες: ΟΝΟΜΑ, ΦΥΛΟ (Α/Κ), ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ (Ν/Ο), ΖΩΗΡΟΣ (Ν/Ο), "
    "ΙΔΙΑΙΤΕΡΟΤΗΤΑ (Ν/Ο), ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ (Ν/Ο), ΦΙΛΟΙ/ΦΙΛΙΑ, ΣΥΓΚΡΟΥΣΗ, ΤΜΗΜΑ.\n"
    "- Η **ΣΠΑΣΜΕΝΗ ΦΙΛΙΑ** μετρά τους μαθητές κάθε τμήματος των οποίων η **πλήρως αμοιβαία** δυάδα "
    "βρίσκεται σε άλλο τμήμα."
)
