
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import re, ast, unicodedata

# ---------------------------
# 🔄 Restart helpers
# ---------------------------
def _restart_app():
    """Clear caches & widget states (including file_uploader) and rerun."""
    # rotate uploader key so the file_uploader fully resets
    st.session_state["uploader_key"] = st.session_state.get("uploader_key", 0) + 1
    # clear any previous uploader widget state keys
    for k in list(st.session_state.keys()):
        if str(k).startswith("uploader_"):
            del st.session_state[k]
    # clear caches
    try:
        st.cache_data.clear()
    except Exception:
        pass
    try:
        st.cache_resource.clear()
    except Exception:
        pass
    st.rerun()

st.set_page_config(page_title="📊 Στατιστικά & 🧩 Σπασμένες Φιλίες", page_icon="🧩", layout="wide")
st.title("📊 Στατιστικά")

# Ensure a stable uploader-key in session
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

# ---------------------------
# Sidebar: Legal / Terms + Restart
# ---------------------------
with st.sidebar:
    # 🔄 Restart button (always visible)
    if st.button("🔄 Επανεκκίνηση εφαρμογής", help="Καθαρίζει μνήμη/φορτώσεις και ξεκινά από την αρχή"):
        _restart_app()

    st.markdown("### ⚖️ Όροι χρήσης")
    terms_ok = st.checkbox("Αποδέχομαι τους όρους χρήσης", value=True)
    st.markdown("© 2025 • Πνευματικά δικαιώματα • **Παναγιώτα Γιαννίτσαρου**")

with st.sidebar.expander("Κάτοχος/Δημιουργός & Άδεια", expanded=False):
    st.markdown("""
**Κάτοχος/Δημιουργός:** Παναγιώτα Γιαννίτσαρου  
**Προϊόν:** Στατιστικά/Κατανομή Μαθητών Α΄ Δημοτικού  

- Η εφαρμογή προορίζεται αποκλειστικά για **εκπαιδευτική χρήση** από σχολικές μονάδες/εκπαιδευτικούς.  
- **Πνευματικά δικαιώματα:** © 2025 Παναγιώτα Γιαννίτσαρου. **Απαγορεύεται** αντιγραφή, αναδημοσίευση ή τροποποίηση χωρίς **έγγραφη άδεια**.  
- **Μη εμπορική χρήση** επιτρέπεται σε σχολεία για εσωτερική οργάνωση.  
- Παρέχεται “**ως έχει**” χωρίς εγγυήσεις. Τα αποτελέσματα έχουν **βοηθητικό** χαρακτήρα και **δεν υποκαθιστούν** κανονιστικές αποφάσεις ή παιδαγωγική κρίση.  
- **Επικοινωνία:** panayiotayiannitsarou@gmail.com
""")

with st.sidebar.expander("🔒 Προστασία Δεδομένων (GDPR – Κύπρος)", expanded=False):
    st.markdown("""
- Τα αρχεία Excel ανεβαίνουν από τον χρήστη και χρησιμοποιούνται **μόνο** για άμεσο υπολογισμό. Η εφαρμογή δεν αποθηκεύει μόνιμα δεδομένα.  
- Ο χρήστης/σχολείο ευθύνεται για συμμόρφωση με **GDPR**.  
- **Συστάσεις:** ψευδώνυμα/κωδικοί, ελαχιστοποίηση δεδομένων, περίοδος διατήρησης, ενημέρωση DPO, έλεγχος παρόχου cloud.
""")

if not terms_ok:
    st.warning("⚠️ Για να χρησιμοποιήσεις την εφαρμογή, αποδέξου τους όρους χρήσης (αριστερά).")
    st.stop()

with st.expander("📜 Πλήρεις Όροι Χρήσης & Αποποίηση Ευθύνης", expanded=False):
    st.markdown("""
1) **Σκοπός:** Υποστήριξη εσωτερικού προγραμματισμού/στατιστικών τάξεων Α΄ Δημοτικού.  
2) **Δεδομένα:** Δεν αποθηκεύονται μόνιμα από την εφαρμογή. Ο χρήστης παραμένει υπεύθυνος για **GDPR**.  
3) **Περιορισμοί:** Απαγορεύεται εμπορική εκμετάλλευση/αναδιανομή/τροποποίηση χωρίς άδεια.  
4) **Αποποίηση:** Δεν υπάρχει ευθύνη για αποφάσεις που λαμβάνονται αποκλειστικά με βάση τα αποτελέσματα.  
5) **Τροποποιήσεις:** Η εφαρμογή μπορεί να ενημερώνεται χωρίς προειδοποίηση.
""")

# ---------------------------
# Canonicalization / Renaming
# ---------------------------
def _canon(s: str) -> str:
    return "".join((s or "").replace("_"," ").split()).upper()

CANON_TARGETS = {
    "ΟΝΟΜΑ": {"ΟΝΟΜΑ"},
    "ΦΥΛΟ": {"ΦΥΛΟ"},
    "ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ": {"ΠΑΙΔΙΕΚΠΑΙΔΕΥΤΙΚΟΥ", "ΠΑΙΔΙ-ΕΚΠΑΙΔΕΥΤΙΚΟΥ"},
    "ΖΩΗΡΟΣ": {"ΖΩΗΡΟΣ"},
    "ΙΔΙΑΙΤΕΡΟΤΗΤΑ": {"ΙΔΙΑΙΤΕΡΟΤΗΤΑ"},
    "ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ": {"ΚΑΛΗΓΝΩΣΗΕΛΛΗΝΙΚΩΝ", "ΓΝΩΣΗΕΛΛΗΝΙΚΩΝ"},
    "ΦΙΛΟΙ": {"ΦΙΛΟΙ", "ΦΙΛΙΑ", "ΦΙΛΟΣ"},
    "ΣΥΓΚΡΟΥΣΗ": {"ΣΥΓΚΡΟΥΣΗ", "ΣΥΓΚΡΟΥΣΕΙΣ"},
    "ΤΜΗΜΑ": {"ΤΜΗΜΑ"},
}
REQUIRED_COLS = ["ΟΝΟΜΑ","ΦΥΛΟ","ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ","ΖΩΗΡΟΣ","ΙΔΙΑΙΤΕΡΟΤΗΤΑ","ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ","ΦΙΛΟΙ","ΣΥΓΚΡΟΥΣΗ","ΤΜΗΜΑ"]

def auto_rename_columns(df: pd.DataFrame):
    """
    Rename common Greek columns to a canonical set.
    More permissive for 'ΦΙΛΟΙ': detects any column whose canonical contains 'ΦΙΛ' or 'FRIEND'.
    If multiple friend-like columns exist, they are concatenated into one.
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
        candidates = []
        for col in df.columns:
            c = _canon(col)
            if "ΦΙΛ" in c or "FRIEND" in c:
                candidates.append(col)
        if candidates:
            combined = []
            for _, row in df[candidates].astype(str).iterrows():
                vals = [str(v).strip() for v in row.tolist() if str(v).strip() and str(v).strip().upper() not in ("-", "NA", "NAN")]
                combined.append(", ".join(vals))
            renamed["ΦΙΛΟΙ"] = combined

    # Ensure ΤΜΗΜΑ exists: if not, try to pick the rightmost column with short labels
    if "ΤΜΗΜΑ" not in renamed.columns:
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


    # ✅ Ensure 'ΣΥΓΚΡΟΥΣΗ' column always exists (normalize plural -> singular or create empty)
    if "ΣΥΓΚΡΟΥΣΗ" not in renamed.columns:
        if "ΣΥΓΚΡΟΥΣΕΙΣ" in renamed.columns:
            renamed = renamed.rename(columns={"ΣΥΓΚΡΟΥΣΕΙΣ": "ΣΥΓΚΡΟΥΣΗ"})
        else:
            renamed["ΣΥΓΚΡΟΥΣΗ"] = ""
    return renamed, mapping

# ✅ Backward-compat alias to avoid NameError if any old code references the typo
def auto_ename_columns(*args, **kwargs):
    return auto_rename_columns(*args, **kwargs)

def _normalize_yes_no(series: pd.Series) -> pd.Series:
    if series.dtype == object:
        s = series.fillna("").astype(str).str.strip().str.upper()
        s = s.replace({
            "ΝΑΙ":"Ν","NAI":"Ν","YES":"Ν","Y":"Ν",
            "ΟΧΙ":"Ο","OXI":"Ο","NO":"Ο","N":"Ο","": "Ο"
        })
        return s.where(s.isin(["Ν","Ο"]), other="Ο")
    return series

# ---------------------------
# Broken friendships helpers
# ---------------------------
def _strip_diacritics(s: str) -> str:
    nfkd = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

def _canon_name(s: str) -> str:
    s = (str(s) if s is not None else "").strip()
    s = s.strip("[]'\" ")
    s = re.sub(r"\s+", " ", s)
    s = _strip_diacritics(s).upper()
    return s

_SPLIT_RE = re.compile(r"\s*(?:,|;|/|\||\band\b|\bκαι\b|\+|\n)\s*", flags=re.IGNORECASE)

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
    parts = [p for p in _SPLIT_RE.split(raw) if p]
    return [_canon_name(p) for p in parts if _canon_name(p)]

def list_broken_mutual_pairs(df: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame with each broken mutual pair (A/B with classes)."""
    fcol = None
    for candidate in ["ΦΙΛΟΙ","ΦΙΛΙΑ","ΦΙΛΟΣ"]:
        if candidate in df.columns:
            fcol = candidate
            break
    if fcol is None or "ΟΝΟΜΑ" not in df.columns or "ΤΜΗΜΑ" not in df.columns:
        return pd.DataFrame(columns=["A","A_ΤΜΗΜΑ","B","B_ΤΜΗΜΑ"])

    df = df.copy()
    df["__CAN_NAME__"] = df["ΟΝΟΜΑ"].map(_canon_name)
    name_to_original = dict(zip(df["__CAN_NAME__"], df["ΟΝΟΜΑ"].astype(str)))
    class_by_name = dict(zip(df["__CAN_NAME__"], df["ΤΜΗΜΑ"].astype(str).str.strip()))

    token_index = {}
    for full in df["__CAN_NAME__"]:
        tokens = [t for t in re.split(r"\s+", full) if t]
        for t in tokens:
            token_index.setdefault(t, set()).add(full)

    def resolve_friend(s: str):
        s = _canon_name(s)
        if not s:
            return None
        if s in name_to_original:
            return s
        toks = [t for t in re.split(r"\s+", s) if t]
        if not toks:
            return None
        if len(toks) >= 2:
            sets = [token_index.get(t, set()) for t in toks]
            inter = set.intersection(*sets) if sets else set()
            if len(inter) == 1:
                return next(iter(inter))
            union = set().union(*sets)
            if len(union) == 1:
                return next(iter(union))
            return None
        else:
            group = token_index.get(toks[0], set())
            return next(iter(group)) if len(group) == 1 else None

    friends_by_name = {}
    for _, row in df.iterrows():
        me = row["__CAN_NAME__"]
        flist_raw = _parse_friends(row[fcol])
        resolved = set()
        for fr in flist_raw:
            r = resolve_friend(fr)
            if r and r != me:
                resolved.add(r)
        friends_by_name[me] = resolved

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

def friend_resolution_diagnostics(df: pd.DataFrame):
    """Return (broken_df, diagnostics) where diagnostics includes unmatched and ambiguous tokens."""
    fcol = None
    for candidate in ["ΦΙΛΟΙ","ΦΙΛΙΑ","ΦΙΛΟΣ"]:
        if candidate in df.columns:
            fcol = candidate
            break
    if fcol is None or "ΟΝΟΜΑ" not in df.columns or "ΤΜΗΜΑ" not in df.columns:
        return pd.DataFrame(columns=["A","A_ΤΜΗΜΑ","B","B_ΤΜΗΜΑ"]), {"unmatched": [], "ambiguous": {}}

    df = df.copy()
    df["__CAN_NAME__"] = df["ΟΝΟΜΑ"].map(_canon_name)
    name_to_original = dict(zip(df["__CAN_NAME__"], df["ΟΝΟΜΑ"].astype(str)))
    class_by_name = dict(zip(df["__CAN_NAME__"], df["ΤΜΗΜΑ"].astype(str).str.strip()))

    token_index = {}
    for full in df["__CAN_NAME__"]:
        tokens = [t for t in re.split(r"\s+", full) if t]
        for t in tokens:
            token_index.setdefault(t, set()).add(full)

    def resolve_friend_diagnose(s: str):
        s = _canon_name(s)
        if not s:
            return None, None
        if s in name_to_original:
            return s, "exact"
        toks = [t for t in re.split(r"\s+", s) if t]
        if not toks:
            return None, None
        if len(toks) >= 2:
            sets = [token_index.get(t, set()) for t in toks]
            inter = set.intersection(*sets) if sets else set()
            if len(inter) == 1:
                return next(iter(inter)), "intersection"
            union = set().union(*sets)
            if len(union) == 1:
                return next(iter(union)), "union-unique"
            return None, ("ambiguous", list(sorted(union)))
        else:
            group = token_index.get(toks[0], set())
            if len(group) == 1:
                return next(iter(group)), "single-unique"
            elif len(group) > 1:
                return None, ("ambiguous", list(sorted(group)))
            else:
                return None, None

    friends_by_name = {}
    unmatched = set()
    ambiguous = {}
    for _, row in df.iterrows():
        me = row["__CAN_NAME__"]
        flist_raw = _parse_friends(row[fcol])
        resolved = set()
        for fr in flist_raw:
            r, how = resolve_friend_diagnose(fr)
            if r is None:
                if isinstance(how, tuple) and how[0] == "ambiguous":
                    ambiguous[_canon_name(fr)] = [name_to_original.get(x, x) for x in how[1]]
                else:
                    unmatched.add(_canon_name(fr))
            elif r != me:
                resolved.add(r)
        friends_by_name[me] = resolved

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
    broken_df = pd.DataFrame(rows)
    return broken_df, {"unmatched": sorted(unmatched), "ambiguous": ambiguous}

def broken_count_by_class(df: pd.DataFrame) -> pd.Series:
    pairs = list_broken_mutual_pairs(df)
    if pairs.empty:
        return pd.Series({tmima: 0 for tmima in df["ΤΜΗΜΑ"].dropna().astype(str).str.strip().unique()})
    counts = {}
    for _, row in pairs.iterrows():
        a_c = str(row["A_ΤΜΗΜΑ"]).strip()
        b_c = str(row["B_ΤΜΗΜΑ"]).strip()
        counts[a_c] = counts.get(a_c, 0) + 1
        counts[b_c] = counts.get(b_c, 0) + 1
    return pd.Series(counts).astype(int)


# ---------------------------
# Conflicts helpers (ΣΥΓΚΡΟΥΣΗ)
# ---------------------------
def _parse_conflict_targets(cell):
    """Parse ΣΥΓΚΡΟΥΣΗ cell to list of canonical names (supports comma/semicolon/slash/pipe/newline)."""
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
    parts = [p for p in _SPLIT_RE.split(raw) if p]
    return [_canon_name(p) for p in parts if _canon_name(p)]

def _build_name_resolution(df: pd.DataFrame):
    df = df.copy()
    df["__CAN_NAME__"] = df["ΟΝΟΜΑ"].map(_canon_name)
    name_to_original = dict(zip(df["__CAN_NAME__"], df["ΟΝΟΜΑ"].astype(str)))
    class_by_name = dict(zip(df["__CAN_NAME__"], df["ΤΜΗΜΑ"].astype(str).str.strip()))
    token_index = {}
    for full in df["__CAN_NAME__"]:
        tokens = [t for t in re.split(r"\s+", full) if t]
        for t in tokens:
            token_index.setdefault(t, set()).add(full)
    def resolve_name(s: str):
        s = _canon_name(s)
        if not s:
            return None
        if s in name_to_original:
            return s
        toks = [t for t in re.split(r"\s+", s) if t]
        if not toks:
            return None
        if len(toks) >= 2:
            sets = [token_index.get(t, set()) for t in toks]
            inter = set.intersection(*sets) if sets else set()
            if len(inter) == 1:
                return next(iter(inter))
            union = set().union(*sets)
            if len(union) == 1:
                return next(iter(union))
            return None
        else:
            group = token_index.get(toks[0], set())
            return next(iter(group)) if len(group) == 1 else None
    return name_to_original, class_by_name, resolve_name


def compute_conflict_counts_and_pairs(df: pd.DataFrame):
    """
    Return (counts_series, pairs_df, names_series).
    - counts_series: per-student integer count of conflicts seated in the SAME class.
    - pairs_df: deduplicated pairs (A,B) where either A listed B (or B listed A) and both are in the same class.
    - names_series: per-student comma-separated string of conflict names that are in the same class.
    """
    required = {"ΟΝΟΜΑ", "ΤΜΗΜΑ", "ΣΥΓΚΡΟΥΣΗ"}
    if not required.issubset(set(df.columns)):
        return (
            pd.Series([0]*len(df), index=df.index),
            pd.DataFrame(columns=["A","A_ΤΜΗΜΑ","B","B_ΤΜΗΜΑ"]),
            pd.Series([""]*len(df), index=df.index),
        )

    name_to_original, class_by_name, resolve_name = _build_name_resolution(df)

    # Build canonical name per row for alignment
    canon_names = df["ΟΝΟΜΑ"].map(_canon_name)
    counts = [0]*len(df)
    names = [""]*len(df)
    pairs = set()

    # map index by canonical name for alignment
    index_by_canon = {cn: i for i, cn in enumerate(canon_names)}

    for i, row in df.iterrows():
        me = _canon_name(row["ΟΝΟΜΑ"])
        my_class = class_by_name.get(me, "")
        targets = _parse_conflict_targets(row["ΣΥΓΚΡΟΥΣΗ"])
        same_class_names = []
        for t in targets:
            r = resolve_name(t)
            if r and r != me:
                if class_by_name.get(r, None) == my_class and my_class:
                    same_class_names.append(name_to_original.get(r, r))
                    pair = tuple(sorted([me, r]))
                    pairs.add(pair)
        counts[index_by_canon.get(me, i)] = len(same_class_names)
        names[index_by_canon.get(me, i)] = ", ".join(same_class_names)

    rows = []
    for a, b in sorted(pairs):
        ta = class_by_name.get(a, "")
        tb = class_by_name.get(b, "")
        if ta == tb and ta:
            rows.append({
                "A": name_to_original.get(a, a), "A_ΤΜΗΜΑ": ta,
                "B": name_to_original.get(b, b), "B_ΤΜΗΜΑ": tb,
            })
    pairs_df = pd.DataFrame(rows)
    return pd.Series(counts, index=df.index), pairs_df, pd.Series(names, index=df.index)


def generate_stats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "ΤΜΗΜΑ" in df:
        df["ΤΜΗΜΑ"] = df["ΤΜΗΜΑ"].apply(lambda v: v.strip() if isinstance(v, str) else v)
    if "ΦΥΛΟ" in df:
        df["ΦΥΛΟ"] = df["ΦΥΛΟ"].fillna("").astype(str).str.strip().str.upper()
    for col in ["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ","ΖΩΗΡΟΣ","ΙΔΙΑΙΤΕΡΟΤΗΤΑ","ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ"]:
        if col in df:
            df[col] = _normalize_yes_no(df[col])

    boys = df[df["ΦΥΛΟ"] == "Α"].groupby("ΤΜΗΜΑ").size() if "ΦΥΛΟ" in df else pd.Series(dtype=int)
    girls = df[df["ΦΥΛΟ"] == "Κ"].groupby("ΤΜΗΜΑ").size() if "ΦΥΛΟ" in df else pd.Series(dtype=int)
    educators = df[df["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν"].groupby("ΤΜΗΜΑ").size() if "ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ" in df else pd.Series(dtype=int)
    energetic = df[df["ΖΩΗΡΟΣ"] == "Ν"].groupby("ΤΜΗΜΑ").size() if "ΖΩΗΡΟΣ" in df else pd.Series(dtype=int)
    special = df[df["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν"].groupby("ΤΜΗΜΑ").size() if "ΙΔΙΑΙΤΕΡΟΤΗΤΑ" in df else pd.Series(dtype=int)
    greek = df[df["ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ"] == "Ν"].groupby("ΤΜΗΜΑ").size() if "ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ" in df else pd.Series(dtype=int)
    total = df.groupby("ΤΜΗΜΑ").size() if "ΤΜΗΜΑ" in df else pd.Series(dtype=int)
    broken = broken_count_by_class(df) if "ΤΜΗΜΑ" in df else pd.Series(dtype=int)

    # ✅ Conflicts per class (count of conflict pairs seated in the same class)
    try:
        counts_series, pairs_df, _names_series = compute_conflict_counts_and_pairs(df)
        if pairs_df.empty:
            conflict_by_class = pd.Series({tmima: 0 for tmima in df["ΤΜΗΜΑ"].dropna().astype(str).str.strip().unique()})
        else:
            conflict_counts = {}
            for _, row in pairs_df.iterrows():
                c = str(row["A_ΤΜΗΜΑ"]).strip()
                conflict_counts[c] = conflict_counts.setdefault(c, 0) + 1
            conflict_by_class = pd.Series(conflict_counts).astype(int)
    except Exception:
        # Fallback safe default
        conflict_by_class = pd.Series({tmima: 0 for tmima in df.get("ΤΜΗΜΑ", pd.Series(dtype=str)).dropna().astype(str).str.strip().unique()})

    stats = pd.DataFrame({
        "ΑΓΟΡΙΑ": boys,
        "ΚΟΡΙΤΣΙΑ": girls,
        "ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ": educators,
        "ΖΩΗΡΟΙ": energetic,
        "ΙΔΙΑΙΤΕΡΟΤΗΤΑ": special,
        "ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ": greek,
        "ΣΥΓΚΡΟΥΣΗ": conflict_by_class,
        "ΣΠΑΣΜΕΝΗ ΦΙΛΙΑ": broken,
        "ΣΥΝΟΛΟ ΜΑΘΗΤΩΝ": total,
    }).fillna(0).astype(int)

    if hasattr(stats.index, "str"):
        stats = stats.loc[stats.index.str.lower() != "nan"]
    try:
        stats = stats.sort_index(key=lambda x: x.str.extract(r"(\d+)")[0].astype(float))
    except Exception:
        stats = stats.sort_index()
    return stats

def export_stats_to_excel(stats_df: pd.DataFrame) -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        stats_df.to_excel(writer, index=True, sheet_name="Στατιστικά", index_label="ΤΜΗΜΑ")
        wb = writer.book
        ws = writer.sheets["Στατιστικά"]
        header_fmt = wb.add_format({"bold": True, "valign":"vcenter", "text_wrap": True, "border":1})
        for col_idx, value in enumerate(["ΤΜΗΜΑ"] + list(stats_df.columns)):
            ws.write(0, col_idx, value, header_fmt)
        for i in range(0, len(stats_df.columns)+1):
            ws.set_column(i, i, 18)
    output.seek(0)
    return output

def sanitize_sheet_name(s: str) -> str:
    s = str(s or "")
    s = re.sub(r'[:\\/?*\\[\\]]', ' ', s)
    return s[:31] if s else "SHEET"

def build_broken_report(xl: pd.ExcelFile, mode: str = "full") -> BytesIO:
    bio = BytesIO()
    summary_rows = []
    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
        # copy originals
        for sheet in xl.sheet_names:
            df_raw = xl.parse(sheet_name=sheet)
            df_raw.to_excel(writer, index=False, sheet_name=sanitize_sheet_name(sheet))
        # broken per sheet
        for sheet in xl.sheet_names:
            df_raw = xl.parse(sheet_name=sheet)
            df_norm, _ = auto_rename_columns(df_raw)
            broken_df = list_broken_mutual_pairs(df_norm)
            summary_rows.append({"Σενάριο (sheet)": sheet, "Σπασμένες Δυάδες": int(len(broken_df))})
            out_name = sanitize_sheet_name(f"{sheet}_BROKEN")
            if broken_df.empty:
                pd.DataFrame({"info": ["— καμία σπασμένη —"]}).to_excel(writer, index=False, sheet_name=out_name)
            else:
                broken_df.to_excel(writer, index=False, sheet_name=out_name)
        # summary
        summary_df = pd.DataFrame(summary_rows).sort_values("Σενάριο (sheet)")
        summary_df.to_excel(writer, index=False, sheet_name="Σύνοψη")
    bio.seek(0)
    return bio

# ---------------------------
# Upload (with resettable key)
# ---------------------------
st.markdown("### 📥 Εισαγωγή Αρχείου Excel")
uploaded = st.file_uploader(
    "Επίλεξε **Excel** με ένα ή περισσότερα sheets (σενάρια)",
    type=["xlsx","xls"],
    key=f"uploader_{st.session_state['uploader_key']}"
)

if not uploaded:
    st.info("➕ Ανέβασε ένα Excel για να συνεχίσεις.")
    st.stop()

try:
    xl = pd.ExcelFile(uploaded)
    st.success(f"✅ Επεξεργασία αρχείου: **{uploaded.name}** — Βρέθηκαν {len(xl.sheet_names)} sheet(s).")
except Exception as e:
    st.error(f"❌ Σφάλμα ανάγνωσης: {e}")
    st.stop()

# ---------------------------
# Tabs
# ---------------------------
tab_stats, tab_broken = st.tabs(["📊 Στατιστικά (1 sheet)", "🧩 Σπασμένες αμοιβαίες (όλα τα sheets) — Έξοδος: Πλήρες αντίγραφο + *_BROKEN + Σύνοψη"])

with tab_stats:
    st.subheader("📊 Υπολογισμός Στατιστικών για Επιλεγμένο Sheet")
    sheet = st.selectbox("Διάλεξε sheet", options=xl.sheet_names, index=0)
    df_raw = xl.parse(sheet_name=sheet)
    df_norm, ren_map = auto_rename_columns(df_raw)

    # ✅ Υπολογισμός μετρητή ΣΥΓΚΡΟΥΣΗΣ και ζευγών στην ίδια τάξη
    conflict_counts, conflict_pairs, conflict_names = compute_conflict_counts_and_pairs(df_norm)
    try:
        df_with_conflicts = df_norm.copy()
        df_with_conflicts["ΣΥΓΚΡΟΥΣΗ"] = conflict_counts.astype(int)
        df_with_conflicts["ΣΥΓΚΡΟΥΣΗ_ΟΝΟΜΑ"] = conflict_names
    except Exception:
        df_with_conflicts = df_norm

    missing = [c for c in REQUIRED_COLS if c not in df_norm.columns]
    with st.expander("🔎 Διάγνωση/Μετονομασίες", expanded=False):
        st.write("Αναγνωρισμένες στήλες:", list(df_norm.columns))
        if ren_map:
            st.write("Αυτόματες μετονομασίες:", ren_map)
        if missing:
            st.error("❌ Λείπουν υποχρεωτικές στήλες: " + ", ".join(missing))

    if not missing:
        with st.expander("👁️ Προβολή πίνακα μαθητών με μετρητή ΣΥΓΚΡΟΥΣΗΣ και τμήμα", expanded=False):
            st.dataframe(df_with_conflicts, use_container_width=True)
        with st.expander("🚫 Ζεύγη σύγκρουσης που βρέθηκαν στην ίδια τάξη (για το επιλεγμένο sheet)", expanded=False):
            if conflict_pairs.empty:
                st.info("— Δεν βρέθηκαν ζεύγη σύγκρουσης στην ίδια τάξη —")
            else:
                st.dataframe(conflict_pairs, use_container_width=True)


        # 🧩 Σπασμένες αμοιβαίες για το επιλεγμένο sheet — εμφάνιση ονομάτων (+ φίλτρο ανά τμήμα)
        with st.expander("🧩 Σπασμένες αμοιβαίες (ονόματα) για το επιλεγμένο sheet", expanded=False):
            try:
                broken_df_for_sheet = list_broken_mutual_pairs(df_norm)
                if broken_df_for_sheet.empty:
                    st.info("— Δεν βρέθηκαν σπασμένες πλήρως αμοιβαίες δυάδες στο επιλεγμένο sheet —")
                else:
                    classes = sorted(set(broken_df_for_sheet["A_ΤΜΗΜΑ"].astype(str)) | set(broken_df_for_sheet["B_ΤΜΗΜΑ"].astype(str)))
                    sel = st.selectbox("Φίλτρο ανά τμήμα", options=["Όλα"] + classes, index=0)
                    if sel != "Όλα":
                        mask = (broken_df_for_sheet["A_ΤΜΗΜΑ"].astype(str) == sel) | (broken_df_for_sheet["B_ΤΜΗΜΑ"].astype(str) == sel)
                        view_df = broken_df_for_sheet[mask].reset_index(drop=True)
                    else:
                        view_df = broken_df_for_sheet.reset_index(drop=True)
                    st.dataframe(view_df, use_container_width=True)
                    # Download as Excel
                    from io import BytesIO
                    bio = BytesIO()
                    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
                        view_df.to_excel(writer, index=False, sheet_name="Σπασμένες_Δυάδες")
                    bio.seek(0)
                    st.download_button(
                        "⬇️ Κατέβασε ονόματα σπασμένων δυάδων (Excel)",
                        data=bio.getvalue(),
                        file_name=f"broken_pairs_{sanitize_sheet_name(sheet)}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.warning(f"Δεν ήταν δυνατή η εμφάνιση ονομάτων σπασμένων δυάδων: {e}")


    if not missing:
        stats_df = generate_stats(df_norm)
        st.dataframe(stats_df, use_container_width=True)
        st.download_button(
            "💾 Λήψη Πίνακα Στατιστικών (Excel)",
            data=export_stats_to_excel(stats_df).getvalue(),
            file_name=f"statistika_{sanitize_sheet_name(sheet)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    else:
        st.info("Συμπλήρωσε/διόρθωσε τις στήλες που λείπουν στο Excel και ξαναφόρτωσέ το.")

with tab_broken:
    st.subheader("🧩 Αναφορά Σπασμένων Πλήρως Αμοιβαίων Δυάδων (όλα τα sheets)")
    # Summary table
    summary_rows = []
    for sheet in xl.sheet_names:
        df_raw = xl.parse(sheet_name=sheet)
        df_norm, _ = auto_rename_columns(df_raw)
        broken_df = list_broken_mutual_pairs(df_norm)
        summary_rows.append({"Σενάριο (sheet)": sheet, "Σπασμένες Δυάδες": int(len(broken_df))})
    summary = pd.DataFrame(summary_rows).sort_values("Σενάριο (sheet)")
    st.dataframe(summary, use_container_width=True)

    st.download_button(
        "⬇️ Κατέβασε αναφορά (Πλήρες αντίγραφο + σπασμένες + σύνοψη)",
        data=build_broken_report(xl, mode="full").getvalue(),
        file_name=f"broken_friends_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Detailed preview + diagnostics
    with st.expander("🔍 Προβολή αναλυτικών ζευγών & διάγνωση ανά sheet"):
        for sheet in xl.sheet_names:
            df_raw = xl.parse(sheet_name=sheet)
            df_norm, _ = auto_rename_columns(df_raw)  # ✅ fixed: correct function name only
            broken_df, diag = friend_resolution_diagnostics(df_norm)
            st.markdown(f"**{sheet}**")
            if broken_df.empty:
                st.info("— Καμία σπασμένη πλήρως αμοιβαία δυάδα —")
            else:
                st.dataframe(broken_df, use_container_width=True)
            if diag["unmatched"] or diag["ambiguous"]:
                with st.expander("🛠️ Διάγνωση αντιστοίχισης ονομάτων"):
                    if diag["unmatched"]:
                        st.warning("Μη αντιστοιχισμένα ονόματα φίλων: " + ", ".join(diag["unmatched"]))
                    if diag["ambiguous"]:
                        st.error("Αμφίβολα ονόματα (ίδιο μικρό/επώνυμο σε πολλούς):")
                        for tok, cand in diag["ambiguous"].items():
                            st.write(f"- **{tok}** → πιθανοί: {', '.join(cand)}")


with st.tabs(["📊 Στατιστικά (1 sheet)", "🧩 Σπασμένες αμοιβαίες (όλα τα sheets) — Έξοδος: Πλήρες αντίγραφο + Σύνοψη", "🚫 Συγκρούσεις (όλα τα sheets)"])[2]:
    st.subheader("🚫 Αναφορά Συγκρούσεων στην ίδια τάξη (όλα τα sheets)")
    # Summary per sheet
    sum_rows = []
    pairs_by_sheet = {}
    for sheet in xl.sheet_names:
        df_raw = xl.parse(sheet_name=sheet)
        df_norm, _ = auto_rename_columns(df_raw)
        counts, pairs, _ = compute_conflict_counts_and_pairs(df_norm)
        sum_rows.append({"Σενάριο (sheet)": sheet, "Ζεύγη σύγκρουσης στην ίδια τάξη": int(len(pairs))})
        pairs_by_sheet[sheet] = pairs
    summ_conf = pd.DataFrame(sum_rows).sort_values("Σενάριο (sheet)")
    st.dataframe(summ_conf, use_container_width=True)
    # Detailed per sheet
    with st.expander("🔍 Αναλυτικά ζεύγη ανά sheet"):
        for sheet in xl.sheet_names:
            st.markdown(f"**{sheet}**")
            pairs = pairs_by_sheet[sheet]
            if pairs.empty:
                st.info("— Δεν βρέθηκαν ζεύγη σύγκρουσης στην ίδια τάξη —")
            else:
                st.dataframe(pairs, use_container_width=True)

