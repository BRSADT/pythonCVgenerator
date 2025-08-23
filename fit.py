import random
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from catalogs import STACK_ALIASES
import random
import unicodedata
import os
import re
import json
import math
import glob
import argparse
def load_vacantes(jd_paths=None, jd_glob=None):
    """
    Carga múltiples vacantes desde rutas repetidas (--jd) y/o un patrón glob (--jd_glob).
    Devuelve una lista de dicts con un campo '_source' para identificar la vacante.
    """
    files = []
    if jd_paths:
        files.extend(jd_paths)
    if jd_glob:
        files.extend(glob.glob(jd_glob))
    vacantes = []
    for p in files:
        try:
            with open(p, "r", encoding="utf-8") as f:
                jd = json.load(f)
                jd["_source"] = os.path.basename(p)
                vacantes.append(jd)
        except Exception as e:
            print(f"[WARN] No se pudo cargar la vacante {p}: {e}")
    return vacantes

def _norm(s):
    return re.sub(r"\s+", " ", (s or "")).lower().strip()

def cv_plain_text(cv):
    parts = [
        cv["identidad"].get("nombre",""),
        cv["identidad"].get("titulo",""),
        cv.get("resumen","")
    ]
    for e in cv.get("experiencia", []):
        parts += [e.get("puesto",""), e.get("empresa",""), e.get("descripcion","")]
    sk = cv.get("skills", {})
    parts += sk.get("hard_skills", []) + sk.get("soft_skills", [])
    for ed in cv.get("educacion", []):
        parts += [ed.get("grado",""), ed.get("area",""), ed.get("institucion","")]
    return _norm(" ".join(map(str, parts)))

def _contains_phrase(txt, phrase):
    return _norm(phrase) in txt

def _stack_hits(txt, stack_list):
    hits = []
    for s in stack_list:
        pat = r"\b" + re.escape(s.lower()) + r"\b"
        if re.search(pat, txt):
            hits.append(s)
    return hits

def _count_years_experience(cv):
    months = 0
    for e in cv.get("experiencia", []):
        try:
            yi, mi = map(int, e.get("inicio","0000-01").split("-"))
            if e.get("fin","").lower() == "actual":
                yf, mf = datetime.today().year, datetime.today().month
            else:
                yf, mf = map(int, e.get("fin","0000-01").split("-"))
            months += max(0, (yf-yi)*12 + (mf-mi))
        except Exception:
            pass
    return round(months/12.0, 1)

def _has_metrics(cv):
    txt = cv_plain_text(cv)
    # % o puntos porcentuales
    if re.search(r"\b\d{1,3}\s?%\b|\b\d+(\.\d+)?\s?p\.?p\.?\b", txt, flags=re.I):
        return True
    # before-after con unidades válidas (h|ms|min|seg)
    if re.search(r"\bde\s+\d+(\.\d+)?\s?(h|ms|min|m|s)\s+a\s+\d+(\.\d+)?\s?(h|ms|min|m|s)\b", txt, flags=re.I):
        return True
    # magnitudes “M de registros/día”
    if re.search(r"\b\d+\s?M\s+de\s+registros\/d[ií]a\b", txt, flags=re.I):
        return True
    return False


def _soft_evidence(cv, soft_terms):
    exp_txt = _norm("\n".join(e.get("descripcion","") for e in cv.get("experiencia", [])))
    return [s for s in soft_terms if _contains_phrase(exp_txt, s)]

def score_fit(cv, jd, weights=None, threshold=0.58):
    W = weights or jd.get("weights") or {"keywords":0.30,"stack":0.35,"exp":0.10,"metrics":0.10,"soft":0.07,"nice":0.08}
    threshold = jd.get("threshold", threshold)

    txt = cv_plain_text(cv)
    # 1) Keywords
    must = jd.get("must_keywords", [])
    if must:
        k_hits = sum(_contains_phrase(txt, k) for k in must)
        kw_score = k_hits / max(1, len(must))
    else:
        kw_score = 1.0

    # 2) Stack requerido con alias
    req = _canon_tokens([s for s in jd.get("required_stack", [])])
    s_hits = _stack_hits(txt, req)
    stack_score = len(s_hits) / max(1, len(req)) if req else 1.0

    # 3) Nice-to-have
    nth = _canon_tokens([s for s in jd.get("nice_to_have", [])])
    nice_hits = _stack_hits(txt, nth) if nth else []
    nice_score = len(nice_hits) / max(1, len(nth)) if nth else 0.0

    # 4) Experiencia: curva suave (logística caps a 1.0)
    years = _count_years_experience(cv)
    miny = jd.get("min_years_exp", 0)
    if miny <= 0:
        exp_score = 1.0
    else:
        ratio = years / miny
        exp_score = max(0.0, min(1.0, 0.5 + 0.5 * (ratio - 0.5)))  # suave: 0.5x ~0.25; 1x~0.75; >=1.5x~1.0

    # 5) Métricas
    metrics_score = 1.0 if _has_metrics(cv) else 0.0

    # 6) Soft
    soft_req = jd.get("soft_required", [])
    if soft_req:
        evid = _soft_evidence(cv, soft_req)
        soft_score = min(1.0, len(evid)/len(soft_req))
    else:
        soft_score = 1.0

    final = (W["keywords"]*kw_score + W["stack"]*stack_score + W["exp"]*exp_score +
             W["metrics"]*metrics_score + W["soft"]*soft_score + W["nice"]*nice_score)

    return {
        "score": round(final,3),
        "threshold": threshold,
        "label_fit": final >= threshold,
        "subscores": {
            "keywords": round(kw_score,3),
            "stack": round(stack_score,3),
            "experience": round(exp_score,3),
            "metrics": round(metrics_score,3),
            "soft": round(soft_score,3),
            "nice_to_have": round(nice_score,3)
        },
        "reasons_pos": [
            *([{"keywords_match": must}] if must and kw_score==1.0 else []),
            *([{"stack_match": list(s_hits)}] if req and s_hits else []),
            *([{"nice_to_have_hits": list(nice_hits)}] if nice_hits else []),
            *([{"experience_years": f"{years} >= {miny}"}] if years >= miny else []),
            *([{"metrics_present": True}] if metrics_score==1.0 else []),
        ],
        "reasons_neg": [
            *([{"missing_keywords":[k for k in must if not _contains_phrase(txt,k)]}] if must and kw_score<1.0 else []),
            *([{"missing_stack":[s for s in req if s not in _canon_tokens(s_hits)]}] if req and stack_score<1.0 else []),
            *([{"experience_years": f"{years} < {miny}"}] if miny and years < miny else []),
            *([{"no_metrics": True}] if metrics_score==0.0 else []),
        ]
    }



# --- Normalización y tokens ---
_WORD_RE = re.compile(r"[a-záéíóúüñ0-9+#\.\-]+", re.IGNORECASE)

def _norm(s: str) -> str:
    s = (s or "").lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s).strip()

def _tokens(s: str) -> set:
    return set(_WORD_RE.findall(_norm(s)))

def _canon(term: str) -> str:
    t = _norm(term)
    return STACK_ALIASES.get(t, t)

def _canon_tokens(terms):
    return {_canon(t) for t in terms if t}

# --- Contains con tolerancia (token + n-gramas cortos) ---
def _contains_phrase(txt: str, phrase: str) -> bool:
    T = _tokens(txt)
    ph = _norm(phrase)
    # match exacto por tokens
    if ph in T:
        return True
    # n-grama corto: "power bi", "google cloud", etc.
    if " " in ph and ph in _norm(txt):
        return True
    return False

# --- Stack hits con alias + beginswith tolerante ---
def _stack_hits(txt: str, stack_list):
    T = _tokens(txt)
    hits = []
    for raw in stack_list:
        q = _canon(raw)
        # match exacto token o prefijo común (postgres ~ postgresql, react ~ react.js)
        if q in T or any(t.startswith(q) or q.startswith(t) for t in T):
            hits.append(raw)
    return hits

# --- Métricas: regex más amplia (%, pp, x, k, ms, s, meses) ---
_METRICS_RE = re.compile(
    r"(\b\d{1,3}\s?%|\b\d{1,3}\s?pp\b|\b\d+x\b|\b\d{1,3}k\b|\b\d+\s?(ms|s|seg|m|min)\b|\b\d+\s+(mes|meses|semana|semanas|dia|dias)\b)",
    re.IGNORECASE
)

def _has_metrics(cv):
    txt = cv_plain_text(cv)
    return bool(_METRICS_RE.search(txt))

# --- Evidencia soft: también acepta skills declaradas si no aparecen en experiencia ---
def _soft_evidence(cv, soft_terms):
    exp_txt = _norm("\n".join(e.get("descripcion","") for e in cv.get("experiencia", [])))
    found = [s for s in soft_terms if _contains_phrase(exp_txt, s)]
    if not found:
        declared = [s for s in soft_terms if s in cv.get("skills", {}).get("soft_skills", [])]
        found.extend(declared)
    return list(dict.fromkeys(found))  # únicos y estable
