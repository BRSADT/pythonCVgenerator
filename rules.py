# rules.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional
import random
import re

# Generadores usados por los degraders y utilidades
from gen import (
    make_summary_bad,
    make_education_bad,
    make_experience_bad,
    make_skills_bad,
    make_contact_bad,
    make_bullet_coherent,
    make_cute_email,
)

# Catálogos/pools
from catalogs import (
    EMOJIS,
    SOFT_SKILLS_POOL,
    BASIC_OFFICE_SKILLS,
    OUT_OF_FOCUS_HARD,
    JOB_TITLES,
)

# =============== helpers internos ===============

def _ensure_extras(cv: dict) -> None:
    if "extras" not in cv:
        cv["extras"] = {}

def _strip_metrics(text: str) -> str:
    """
    Elimina o neutraliza porcentajes y números para quitar impacto medido.
    """
    text = re.sub(r"\b\d{1,3}\s?%\b", "X%", text)
    text = re.sub(r"\b\d+\b", "N", text)
    return text

# =============== anti‑reglas “seguras” ===============

def ar_emojis_uppercase_summary(cv: dict) -> Optional[str]:
    cv["resumen"] = cv.get("resumen", "").upper() + " " + " ".join(
        random.sample(EMOJIS, k=random.randint(1, 3))
    )
    return "emojis_y_mayus_en_resumen"

def ar_instagram_contact(cv: dict) -> Optional[str]:
    nombre = cv.get("identidad", {}).get("nombre", "user")
    handle = "@" + re.sub(r"\s+", "", nombre.lower())
    cv.setdefault("contacto", {})["instagram"] = handle
    return "incluye_instagram_personal"

def ar_links_broken(cv: dict) -> Optional[str]:
    c = cv.setdefault("contacto", {})
    if c.get("linkedin"):
        c["linkedin"] = "http://link-broken.example"
    if "web" in c:
        c["web"] = "http://404.example"
    return "links_rotos"

def ar_remove_descriptions(cv: dict) -> Optional[str]:
    """
    Vacía descripciones de varias experiencias (señal negativa),
    pero garantiza que al menos UNA conserve texto para evitar patrones triviales.
    """
    exps = cv.get("experiencia", [])
    if not exps:
        return None

    had_any = any(e.get("descripcion") for e in exps)
    touched = False

    for e in exps:
        if e.get("descripcion") and random.random() < 0.6:
            e["descripcion"] = ""
            touched = True

    # Asegura que queda al menos una con algo de texto
    if touched and not any(e.get("descripcion") for e in exps):
        idx = random.randrange(len(exps))
        titulo = cv.get("identidad", {}).get("titulo") or random.choice(JOB_TITLES)
        exps[idx]["descripcion"] = "- " + make_bullet_coherent(titulo, positive=True)

    return "experiencia_sin_descripcion" if (touched or had_any) else None

def ar_no_metrics(cv: dict) -> Optional[str]:
    """
    Neutraliza métricas en bullets para quitar impacto cuantitativo.
    """
    for e in cv.get("experiencia", []):
        if e.get("descripcion"):
            e["descripcion"] = _strip_metrics(e["descripcion"])
    return "sin_metricas"

def ar_cute_email(cv: dict) -> Optional[str]:
    """
    Sustituye el email por un patrón poco profesional.
    """
    ident = cv.get("identidad", {}).get("nombre", "Nombre Apellido").split(" ", 1)
    first = ident[0]
    last = ident[1] if len(ident) > 1 else ""
    cv.setdefault("contacto", {})["email"] = make_cute_email(first, last)
    return "email_poco_profesional"

def ar_missing_hard_skills(cv: dict) -> Optional[str]:
    """
    Vacía hard skills (mantiene soft si existen) para que haya variedad.
    """
    sk = cv.setdefault("skills", {})
    sk["hard_skills"] = []
    sk.setdefault("soft_skills", [])
    return "faltan_hard_skills"

def ar_contact_block_huge(cv: dict) -> Optional[str]:
    """
    Infla el bloque de contacto con canales irrelevantes.
    """
    c = cv.setdefault("contacto", {})
    nombre = cv.get("identidad", {}).get("nombre", "user")
    base_handle = nombre.split()[0].lower()
    c.setdefault("telefono", "+52 55 0000 0000")
    c["telefono_alterno"] = c["telefono"]
    c["tiktok"] = f"@{base_handle}"
    c["facebook"] = f"fb.com/{nombre.replace(' ', '.').lower()}"
    return "contacto_demasiado_grande"

# --- variantes en skills “malos” (sin sesgo) ---

def ar_skills_solo_soft(cv: dict) -> Optional[str]:
    """
    Deja solo 1–4 soft skills al azar.
    """
    n = random.randint(1, 4)
    soft = random.sample(SOFT_SKILLS_POOL, k=min(n, len(SOFT_SKILLS_POOL)))
    random.shuffle(soft)
    cv["skills"] = {"hard_skills": [], "soft_skills": soft}
    return "skills_solo_soft"

def ar_skills_irrelevantes(cv: dict) -> Optional[str]:
    """
    Marca skills duras básicas (ofimática) como principales.
    """
    n = random.randint(1, min(3, len(BASIC_OFFICE_SKILLS)))
    hard = random.sample(BASIC_OFFICE_SKILLS, k=n)
    soft = random.sample(SOFT_SKILLS_POOL, k=random.randint(0, 2))
    cv["skills"] = {"hard_skills": hard, "soft_skills": soft}
    return "skills_irrelevantes"

def ar_skills_desalineadas(cv: dict) -> Optional[str]:
    """
    Coloca 1–2 hard skills fuera de foco + algunas soft.
    """
    n = random.randint(1, min(2, len(OUT_OF_FOCUS_HARD)))
    hard = random.sample(OUT_OF_FOCUS_HARD, k=n)
    soft = random.sample(SOFT_SKILLS_POOL, k=random.randint(0, 2))
    cv["skills"] = {"hard_skills": hard, "soft_skills": soft}
    return "skills_desalineadas"

# =============== degraders por sección ===============

def ar_degrade_summary(cv: dict) -> Optional[str]:
    """
    Sustituye el resumen “bueno” por uno débil/ambiguo.
    Requiere que el generador haya colocado meta.ctx['fake'] y meta.ctx['titulo'].
    """
    ctx = cv.get("meta", {}).get("ctx", {})
    fake = ctx.get("fake")
    if fake:
        cv["resumen"] = make_summary_bad(fake)
        return "resumen_debil"
    return None

def ar_degrade_education(cv: dict) -> Optional[str]:
    ctx = cv.get("meta", {}).get("ctx", {})
    fake = ctx.get("fake")
    if fake:
        cv["educacion"] = make_education_bad(fake)
        return "educacion_pobre"
    return None

def ar_degrade_skills(cv: dict) -> Optional[str]:
    cv["skills"] = make_skills_bad()
    return "skills_debil"

def ar_degrade_experience(cv: dict) -> Optional[str]:
    ctx = cv.get("meta", {}).get("ctx", {})
    fake = ctx.get("fake")
    if fake:
        cv["experiencia"] = make_experience_bad(fake)
        return "experiencia_vaga"
    return None

def ar_degrade_contact(cv: dict) -> Optional[str]:
    ctx = cv.get("meta", {}).get("ctx", {})
    fake = ctx.get("fake")
    first = ctx.get("first")
    last = ctx.get("last") or ""
    if fake and first:
        cv["contacto"] = make_contact_bad(fake, first, last)
        return "contacto_poco_prof"
    return None

# =============== mapeo de grupos exclusivos ===============

EXCLUSIVE_GROUPS = {
    "summary": {ar_degrade_summary, ar_emojis_uppercase_summary},
    "skills": {
        ar_degrade_skills,
        ar_missing_hard_skills,
        ar_skills_solo_soft,
        ar_skills_irrelevantes,
        ar_skills_desalineadas,
    },
    "experience": {ar_degrade_experience, ar_remove_descriptions, ar_no_metrics},
    "contact": {ar_degrade_contact, ar_contact_block_huge, ar_links_broken, ar_cute_email},
    "education": {ar_degrade_education},
}
FUNC2GROUP = {f: g for g, fs in EXCLUSIVE_GROUPS.items() for f in fs}

def apply_rules_with_exclusivity(cv_tmp: dict, funcs: List[Callable[[dict], Optional[str]]]) -> List[str]:
    """
    Aplica reglas garantizando exclusividad por sección (un máximo por grupo).
    Devuelve la lista de tags aplicados.
    """
    used_groups = set()
    applied: List[str] = []
    for func in funcs:
        group = FUNC2GROUP.get(func)
        if group and group in used_groups:
            continue
        tag = func(cv_tmp)
        if tag:
            applied.append(tag)
            if group:
                used_groups.add(group)
    return applied

# =============== registro de reglas con pesos ===============

@dataclass(frozen=True)
class Rule:
    name: str
    group: str            # 'summary' | 'skills' | 'experience' | 'contact' | 'education'
    weight: float         # prioridad relativa para muestreo
    func: Callable[[dict], Optional[str]]

RULES: List[Rule] = [
    # Degraders por sección (una por grupo si hay exclusividad)
    Rule("resumen_debil", "summary",   0.22, ar_degrade_summary),
    Rule("educacion_pobre", "education",0.25, ar_degrade_education),
    Rule("skills_debil",   "skills",    0.18, ar_degrade_skills),
    Rule("experiencia_vaga","experience",0.22, ar_degrade_experience),
    Rule("contacto_poco_prof","contact",0.20, ar_degrade_contact),

    # Anti‑reglas complementarias, mismas firmas
    Rule("faltan_hard_skills", "skills",     0.15, ar_missing_hard_skills),
    Rule("sin_metricas",       "experience", 0.25, ar_no_metrics),
    Rule("experiencia_sin_desc","experience",0.25, ar_remove_descriptions),
    Rule("instagram_personal", "contact",    0.25, ar_instagram_contact),
    Rule("email_poco_prof",    "contact",    0.25, ar_cute_email),
    Rule("contacto_grande",    "contact",    0.20, ar_contact_block_huge),
    Rule("links_rotos",        "contact",    0.15, ar_links_broken),
    Rule("emojis_mayus",       "summary",    0.15, ar_emojis_uppercase_summary),

    # Variantes de skills “malos”
    Rule("skills_solo_soft",   "skills",     0.25, ar_skills_solo_soft),
    Rule("skills_irrelevantes","skills",     0.20, ar_skills_irrelevantes),
    Rule("skills_desalineadas","skills",     0.20, ar_skills_desalineadas),
]

def weighted_sample_rules(k: int, allow_multi_per_group: bool = False) -> List[Rule]:
    """
    Selecciona k reglas sin reemplazo, ponderadas por 'weight'.
    Por defecto aplica exclusividad de grupo (una por sección).
    """
    pool = RULES[:]
    picked: List[Rule] = []
    used_groups = set()

    for _ in range(min(k, len(pool))):
        candidates = [r for r in pool if (allow_multi_per_group or r.group not in used_groups)]
        if not candidates:
            break
        weights = [r.weight for r in candidates]
        idx = random.choices(range(len(candidates)), weights=weights, k=1)[0]
        choice = candidates[idx]
        picked.append(choice)
        used_groups.add(choice.group)
        pool.remove(choice)

    return picked
