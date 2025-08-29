
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="📊 Στατιστικά Μαθητών Α' Δημοτικού", page_icon="📊", layout="wide")
st.title("📊 Στατιστικά Μαθητών Α' Δημοτικού")

# ---------------------------
# Sidebar: Legal / Terms
# ---------------------------
st.sidebar.markdown("### ⚖️ Όροι χρήσης")
terms_ok = st.sidebar.checkbox("Αποδέχομαι τους όρους χρήσης", value=False)
st.sidebar.markdown("© 2025 • Πνευματικά δικαιώματα • **Παναγιώτα Γιαννίτσαρου**")

# Owner / License quick section
with st.sidebar.expander("Κάτοχος/Δημιουργός & Άδεια", expanded=False):
    st.markdown("""
**Κάτοχος/Δημιουργός:** Παναγιώτα Γιαννίτσαρου  
**Προϊόν:** Στατιστικά/Κατανομή Μαθητών Α΄ Δημοτικού  

- Η εφαρμογή προορίζεται αποκλειστικά για **εκπαιδευτική χρήση** από σχολικές μονάδες/εκπαιδευτικούς.  
- **Πνευματικά δικαιώματα:** © 2025 Παναγιώτα Γιαννίτσαρου. **Απαγορεύεται** αντιγραφή, αναδημοσίευση ή τροποποίηση χωρίς **έγγραφη άδεια**.  
- **Μη εμπορική χρήση** επιτρέπεται σε σχολεία για εσωτερική οργάνωση.  
- Παρέχεται “**ως έχει**” χωρίς εγγυήσεις. Τα αποτελέσματα έχουν **βοηθητικό** χαρακτήρα και **δεν υποκαθιστούν** κανονιστικές αποφάσεις ή παιδαγωγική κρίση.  
- **Επικοινωνία:** [panayiotayiannitsarou@gmail.com](mailto:panayiotayiannitsarou@gmail.com)
""")

# Data Protection (GDPR) Guidance
with st.sidebar.expander("🔒 Προστασία Δεδομένων (GDPR – Κύπρος)", expanded=False):
    st.markdown("""
- Τα αρχεία Excel ανεβαίνουν από τον χρήστη και χρησιμοποιούνται **μόνο** για άμεσο υπολογισμό. Η εφαρμογή δεν αποθηκεύει μόνιμα δεδομένα.  
- Ο χρήστης/σχολείο ευθύνεται για συμμόρφωση με **GDPR** (Άρθρο 5: Αρχές, Άρθρο 6: Νομική βάση).  
- **Συστάσεις:**  
  • Χρησιμοποιήστε **ψευδώνυμα/κωδικούς** (π.χ. Α1_001) αντί πλήρων ονομάτων, εφόσον γίνεται.  
  • Εφαρμόστε **ελαχιστοποίηση** (μόνο τα απολύτως αναγκαία πεδία).  
  • Καθορίστε **διάστημα διατήρησης** και διαδικασία **διαγραφής**.  
  • Ενημερώστε τον/την **Υπεύθυνο Προστασίας Δεδομένων (DPO)** του σχολείου.  
  • Αν χρησιμοποιήσετε **cloud** (π.χ. Streamlit Cloud): ελέγξτε πού φιλοξενούνται οι υποδομές, τους όρους επεξεργασίας και αποφύγετε την ανάρτηση **αναγνωρίσιμων** στοιχείων όπου δεν είναι απαραίτητο.
""")

if not terms_ok:
    st.warning("⚠️ Για να χρησιμοποιήσεις την εφαρμογή, αποδέξου τους όρους χρήσης (αριστερά).")
    st.stop()

# ---------------------------
# Full Terms (main page expander)
# ---------------------------
with st.expander("📜 Πλήρεις Όροι Χρήσης & Αποποίηση Ευθύνης", expanded=False):
    st.markdown("""
1) **Σκοπός:** Υποστήριξη εσωτερικού προγραμματισμού/στατιστικών τάξεων Α΄ Δημοτικού.  
2) **Ιδιωτικότητα & Δεδομένα:** Τα δεδομένα παρέχονται αποκλειστικά από τον χρήστη. Δεν αποθηκεύονται μόνιμα από την εφαρμογή, ούτε διαμοιράζονται σε τρίτους. Ο χρήστης παραμένει υπεύθυνος για τη συμμόρφωση με τον **GDPR** και την εθνική νομοθεσία (π.χ. ψευδωνυμοποίηση).  
3) **Περιορισμοί:** Απαγορεύεται η εμπορική εκμετάλλευση, διάθεση σε τρίτους και τροποποίηση χωρίς άδεια.  
4) **Αποποίηση Ευθύνης:** Ο/Η δημιουργός δεν ευθύνεται για αποφάσεις που λαμβάνονται αποκλειστικά με βάση τα αποτελέσματα ή για σφάλματα/ελλείψεις στα εισαγόμενα δεδομένα.  
5) **Τροποποιήσεις:** Η εφαρμογή μπορεί να ενημερώνεται χωρίς προειδοποίηση.  
6) **Αποδοχή:** Η χρήση συνεπάγεται πλήρη αποδοχή των όρων.
""")

# ---------------------------
# Admin Checklist (directors)
# ---------------------------
with st.expander("✅ Checklist για Διευθυντές/ριες Σχολείων", expanded=False):
    st.markdown("""
- [ ] Έχει ενημερωθεί ο/η **DPO**;  
- [ ] Χρησιμοποιούνται **κωδικοί/ψευδώνυμα** αντί για πλήρη ονόματα όπου είναι εφικτό;  
- [ ] Υπάρχει **νομική βάση** επεξεργασίας (Άρθρο 6 GDPR – π.χ. αποστολή δημόσιου καθήκοντος/νόμιμο συμφέρον);  
- [ ] Εφαρμόζεται **ελαχιστοποίηση** και **ανάγκη γνώσης** (μόνο τα απολύτως απαραίτητα δεδομένα/πρόσβαση);  
- [ ] Ορίζεται **περίοδος διατήρησης** και διαδικασία **διαγραφής** αρχείων;  
- [ ] Αν χρησιμοποιείται **cloud**, έχει ελεγχθεί ο πάροχος/τοποθεσία/όροι επεξεργασίας;  
- [ ] Υπάρχει **ενημέρωση** προς γονείς/κηδεμόνες, εφόσον απαιτείται, σχετικά με τον τρόπο χρήσης των δεδομένων;
""")

# ---------------------------
# Session State
# ---------------------------
for key, default in [("data", None), ("stats_df", None), ("show_upload", False), ("diagnostics", {})]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Column normalization ----------
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
    """
    Rename common Greek columns to a canonical set.
    Now more permissive for the 'ΦΙΛΟΙ' column: detects any column whose canonical contains 'ΦΙΛ'.
    Also accepts 'FRIEND'/'FRIENDS'.
    """
    mapping = {}
    seen = set()
    for col in df.columns:
        c = _canon(col)
        found_target = None
        for target, keys in CANON_TARGETS.items():
            if c in keys and target not in seen:
                found_target = target
                seen.add(target)
                break
        if found_target:
            mapping[col] = found_target

    renamed = df.rename(columns=mapping)

    # Fallbacks for friends column if not mapped already
    friends_cols = [c for c in renamed.columns if c in ("ΦΙΛΟΙ","ΦΙΛΙΑ","ΦΙΛΟΣ")]
    if not friends_cols:
        # search candidates by substring
        candidates = []
        for col in df.columns:
            c = _canon(col)
            if "ΦΙΛ" in c or "FRIEND" in c:
                candidates.append(col)
        # If we find multiple friend-like columns, concatenate them into one
        if candidates:
            # Create a combined ΦΙΛΟΙ column by joining non-empty parts with commas
            combined = []
            for _, row in df[candidates].astype(str).iterrows():
                vals = [str(v).strip() for v in row.tolist() if str(v).strip() and str(v).strip().upper() not in ("-", "NA", "NAN")]
                combined.append(", ".join(vals))
            renamed["ΦΙΛΟΙ"] = combined

    # Ensure ΤΜΗΜΑ exists: if not, try to pick the rightmost column that looks like class labels (A1, A2...)
    if "ΤΜΗΜΑ" not in renamed.columns:
        # candidate: column with short string labels and <= 6 unique non-empty values
        best = None
        for col in df.columns[::-1]:
            s = df[col].dropna().astype(str).str.strip()
            if not len(s):
                continue
            if s.str.len().median() <= 4 and s.nunique() <= 10:
                best = col
                break
        if best:
            renamed = renamed.rename(columns={best: "ΤΜΗΜΑ"})

    return renamed, mapping


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
    # Trim only strings, preserve NaN so groupby ignores empty classes
    if "ΤΜΗΜΑ" in df:
        df["ΤΜΗΜΑ"] = df["ΤΜΗΜΑ"].apply(lambda v: v.strip() if isinstance(v, str) else v)
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
        "ΣΥΝΟΛΟ ΜΑΘΗΤΩΝ": total,
    }).fillna(0).astype(int)

    # Safety: if for κάποιο λόγο προέκυψε string 'nan' από παλαιό αρχείο, κρύψ' το
    if hasattr(stats.index, "str"):
        stats = stats.loc[stats.index.str.lower() != "nan"]

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

# ---------------------------
# UI Buttons
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
        st.session_state.diagnostics = {}
        st.rerun()

# ---------------------------
# Upload + Diagnostics + Preview
# ---------------------------
if st.session_state.show_upload:
    st.markdown("### 📥 Εισαγωγή Αρχείου Excel")
    up = st.file_uploader("Επίλεξε αρχείο Excel με δεδομένα μαθητών", type=["xlsx","xls"])
    if up:
        try:
            df_raw = pd.read_excel(up)
            df_norm, ren_map = auto_rename_columns(df_raw)
            # Trim 'ΤΜΗΜΑ' only if it's string; keep NaN
            if "ΤΜΗΜΑ" in df_norm.columns:
                df_norm["ΤΜΗΜΑ"] = df_norm["ΤΜΗΜΑ"].apply(lambda v: v.strip() if isinstance(v, str) else v)

            st.session_state.data = df_norm.copy()

            present = list(df_norm.columns)
            missing = [c for c in REQUIRED_COLS if c not in present]
            classes = sorted([str(x) for x in df_norm["ΤΜΗΜΑ"].dropna().unique()]) if "ΤΜΗΜΑ" in df_norm else []
            missing_classes = int(df_norm["ΤΜΗΜΑ"].isna().sum()) if "ΤΜΗΜΑ" in df_norm else 0

            st.session_state.diagnostics = {
                "recognized_columns": present,
                "renamed": ren_map,
                "missing_required": missing,
                "classes_found": classes,
                "missing_class_rows": missing_classes,
            }

            st.success(f"✅ Επιτυχής φόρτωση! Βρέθηκαν {len(df_norm)} μαθητές.")
            with st.expander("🔎 Διάγνωση αρχείου (στήλες που αναγνωρίστηκαν)", expanded=False):
                st.write("Αναγνωρισμένες στήλες:", present)
                if ren_map:
                    st.write("Αυτόματες μετονομασίες:", ren_map)
                if missing:
                    st.error("❌ Λείπουν υποχρεωτικές στήλες: " + ", ".join(missing))
                if "ΤΜΗΜΑ" in df_norm:
                    st.write("Τμήματα που βρέθηκαν:", classes)
                    if missing_classes:
                        st.warning(f"Υπάρχουν {missing_classes} εγγραφές χωρίς τιμή στο πεδίο ΤΜΗΜΑ — δεν θα συμπεριληφθούν στα στατιστικά.")

            if not missing:
                st.markdown("### 👀 Προεπισκόπηση Πίνακα Στατιστικών")
                preview = _generate_stats(df_norm)
                st.session_state.stats_df = preview
                st.dataframe(preview, use_container_width=True)
            else:
                st.info("Συμπλήρωσε/διόρθωσε τις στήλες που λείπουν και ξαναφόρτωσε το αρχείο.")

        except Exception as e:
            st.error(f"❌ Σφάλμα κατά τη φόρτωση: {e}")

# ---------------------------
# Export
# ---------------------------
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

# ---------------------------
# Footer
# ---------------------------
st.markdown("""
—  © 2025 **Παναγιώτα Γιαννίτσαρου** — *Στατιστικά/Κατανομή Μαθητών Α΄ Δημοτικού*. 
Μόνο για εκπαιδευτική χρήση. Όλα τα δικαιώματα διατηρούνται.
""")




# ===== Appended robust mutual-broken detection (patch FIXED, clean) =====

# === PATCH: Robust mutual-broken detection (CLOUD-SAFE) ===
import re, ast, unicodedata
import pandas as pd

def _strip_diacritics(s: str) -> str:
    nfkd = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

def _canon_name(s: str) -> str:
    s = (str(s) if s is not None else "").strip()
    s = s.strip("[]'\" ")
    s = re.sub(r"\s+", " ", s)
    s = _strip_diacritics(s).upper()
    return s

def _parse_friends(cell):
    raw = str(cell) if cell is not None else ""
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith("[") and raw.endswith("]"):
        try:
            val = ast.literal_eval(raw)
            if isinstance(val, (list, tuple)):
                return [_canon_name(x) for x in val if str(x).strip()]
        except Exception:
            pass
        raw2 = raw.strip("[]")
        parts = re.split(r"[;,]", raw2)
        return [_canon_name(p) for p in parts if _canon_name(p)]
    parts = re.split(r"[;,]", raw)
    return [_canon_name(p) for p in parts if _canon_name(p)]

def _broken_mutual_friendships_per_class(df: pd.DataFrame) -> pd.Series:
    """Return Series with count of broken mutual pairs per class.
    Mutual: A lists B AND B lists A (after normalization).
    Broken = mutual pair placed in different non-empty classes.
    Each broken pair is counted once for each involved class.
    """
    alt_fcol = "ΦΙΛΟΙ" if "ΦΙΛΟΙ" in df.columns else ("ΦΙΛΙΟΙ" if "ΦΙΛΙΟΙ" in df.columns else None)
    if alt_fcol is None or "ΟΝΟΜΑ" not in df.columns or "ΤΜΗΜΑ" not in df.columns:
        return df.groupby("ΤΜΗΜΑ").size() * 0

    df = df.copy()
    df["__CAN_NAME__"] = df["ΟΝΟΜΑ"].map(_canon_name)
    class_by_name = dict(zip(df["__CAN_NAME__"], df["ΤΜΗΜΑ"].astype(str).str.strip()))
    friends_by_name = dict(zip(df["__CAN_NAME__"], df[alt_fcol].map(_parse_friends)))

    mutual_pairs = set()
    for a, flist in friends_by_name.items():
        for b in flist:
            if b in friends_by_name and a in friends_by_name[b]:
                mutual_pairs.add(tuple(sorted([a,b])))

    broken_by_class = {tmima: 0 for tmima in df["ΤΜΗΜΑ"].dropna().astype(str).str.strip().unique()}
    for a, b in sorted(mutual_pairs):
        ta = class_by_name.get(a, "")
        tb = class_by_name.get(b, "")
        if ta and tb and ta != tb:
            broken_by_class[ta] = broken_by_class.get(ta, 0) + 1
            broken_by_class[tb] = broken_by_class.get(tb, 0) + 1
    return pd.Series(broken_by_class).fillna(0).astype(int)

def _list_broken_mutual_friendships(df: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame with each broken mutual pair (A/B with classes)."""
    alt_fcol = "ΦΙΛΟΙ" if "ΦΙΛΟΙ" in df.columns else ("ΦΙΛΙΟΙ" if "ΦΙΛΙΟΙ" in df.columns else None)
    if alt_fcol is None or "ΟΝΟΜΑ" not in df.columns or "ΤΜΗΜΑ" not in df.columns:
        return pd.DataFrame(columns=["A","A_ΤΜΗΜΑ","B","B_ΤΜΗΜΑ"])

    df = df.copy()
    df["__CAN_NAME__"] = df["ΟΝΟΜΑ"].map(_canon_name)
    name_to_original = dict(zip(df["__CAN_NAME__"], df["ΟΝΟΜΑ"].astype(str)))
    class_by_name = dict(zip(df["__CAN_NAME__"], df["ΤΜΗΜΑ"].astype(str).str.strip()))
    friends_by_name = dict(zip(df["__CAN_NAME__"], df[alt_fcol].map(_parse_friends)))

    mutual_pairs = set()
    for a, flist in friends_by_name.items():
        for b in flist:
            if b in friends_by_name and a in friends_by_name[b]:
                mutual_pairs.add(tuple(sorted([a,b])))

    rows = []
    for a, b in sorted(mutual_pairs):
        ta = class_by_name.get(a, "")
        tb = class_by_name.get(b, "")
        if ta and tb and ta != tb:
            rows.append({
                "A": name_to_original.get(a, a), "A_ΤΜΗΜΑ": ta,
                "B": name_to_original.get(b, b), "B_ΤΜΗΜΑ": tb,
            })
    return pd.DataFrame(rows)

