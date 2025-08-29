
import re, ast, unicodedata
import pandas as pd

# ---------- Name & column normalization ----------
def strip_diacritics(s: str) -> str:
    nfkd = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

def canon_name(s: str) -> str:
    s = (str(s) if s is not None else "").strip()
    s = s.strip("[]'\" ")
    s = re.sub(r"\s+", " ", s)
    s = strip_diacritics(s).upper()
    return s

def canon_col(s: str) -> str:
    return "".join((s or "").replace("_"," ").split()).upper()

CANON_TARGETS = {
    "ΟΝΟΜΑ": {"ΟΝΟΜΑ"},
    "ΤΜΗΜΑ": {"ΤΜΗΜΑ"},
    "ΦΙΛΟΙ": {"ΦΙΛΟΙ", "ΦΙΛΙΑ"},
}

def auto_rename_columns(df: pd.DataFrame):
    mapping = {}
    seen = set()
    for col in df.columns:
        c = canon_col(col)
        found_target = None
        for target, keys in CANON_TARGETS.items():
            if c in keys and target not in seen:
                found_target = target
                seen.add(target)
                break
        if found_target:
            mapping[col] = found_target
    return df.rename(columns=mapping), mapping

# ---------- Friends parsing ----------
def parse_friends(cell):
    raw = str(cell) if cell is not None else ""
    raw = raw.strip()
    if not raw:
        return []
    # Try python-like list: ['A','B']
    if raw.startswith("[") and raw.endswith("]"):
        try:
            val = ast.literal_eval(raw)
            if isinstance(val, (list, tuple)):
                return [canon_name(x) for x in val if str(x).strip()]
        except Exception:
            pass
        raw2 = raw.strip("[]")
        parts = re.split(r"[;,]", raw2)
        return [canon_name(p) for p in parts if canon_name(p)]
    # Fallback split
    parts = re.split(r"[;,]", raw)
    return [canon_name(p) for p in parts if canon_name(p)]

# ---------- Core detection ----------
def detect_broken_mutuals(df: pd.DataFrame):
    """
    Return:
      - broken_by_class: pd.Series index=class, value=count_of_broken_pairs_counted_for_this_class
      - broken_pairs_df: DataFrame rows for each broken mutual pair with A/B names & classes
      - mutual_pairs_count: int total mutual pairs (regardless of broken or not)
      - broken_unique_pairs_count: int broken mutual pairs (each pair counted once)
    Notes:
      * Mutual means A lists B and B lists A (after normalization).
      * A broken pair is a mutual pair with different, non-empty classes.
      * broken_by_class counts each broken pair once for each involved class.
    """
    # Ensure required columns exist (after renaming if needed)
    df, _ = auto_rename_columns(df)
    if not {"ΟΝΟΜΑ","ΤΜΗΜΑ","ΦΙΛΟΙ"}.issubset(df.columns):
        empty = pd.Series(dtype=int)
        return empty, pd.DataFrame(), 0, 0

    # Build maps (canonical -> original/class/friends)
    df = df.copy()
    df["__CAN_NAME__"] = df["ΟΝΟΜΑ"].map(canon_name)
    name_to_original = dict(zip(df["__CAN_NAME__"], df["ΟΝΟΜΑ"].astype(str)))
    class_by_name = dict(zip(df["__CAN_NAME__"], df["ΤΜΗΜΑ"].astype(str).str.strip()))
    friends_by_name = dict(zip(df["__CAN_NAME__"], df["ΦΙΛΙΟΙ"].map(parse_friends) if "ΦΙΛΙΟΙ" in df.columns else df["ΦΙΛΟΙ"].map(parse_friends)))

    # Build set of mutual pairs
    mutual_pairs = set()
    for a, flist in friends_by_name.items():
        for b in flist:
            if b in friends_by_name and a in friends_by_name[b]:
                mutual_pairs.add(tuple(sorted([a,b])))

    # Count broken
    broken_rows = []
    broken_by_class = {tmima: 0 for tmima in df["ΤΜΗΜΑ"].dropna().astype(str).str.strip().unique()}
    broken_unique = 0
    for a, b in sorted(mutual_pairs):
        ta = class_by_name.get(a, "")
        tb = class_by_name.get(b, "")
        if ta and tb and ta != tb:
            broken_unique += 1
            broken_by_class[ta] = broken_by_class.get(ta, 0) + 1
            broken_by_class[tb] = broken_by_class.get(tb, 0) + 1
            broken_rows.append({
                "A": name_to_original.get(a, a), "A_ΤΜΗΜΑ": ta,
                "B": name_to_original.get(b, b), "B_ΤΜΗΜΑ": tb,
            })

    broken_by_class = pd.Series(broken_by_class).fillna(0).astype(int)
    broken_pairs_df = pd.DataFrame(broken_rows)

    return broken_by_class, broken_pairs_df, len(mutual_pairs), broken_unique
