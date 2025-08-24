# rules.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional
import random
import re
from gen import rnd_typos

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
def ar_personal_data_in_resumen(cv: dict) -> Optional[str]:
    """ Mete datos personales innecesarios directamente en el RESUMEN. """
    genero = cv.get("meta", {}).get("genero", "m")  # default m si no está

    edad = random.randint(21, 45)
    if genero == "f":
        estado = "soltera"
    else:
        estado = "soltero"

    hijos = random.choice(["sin hijos", "1 hijo", "2 hijos"])
    religion = random.choice(["católica", "cristiana", "ninguna"])
    dom = random.choice(["Av. Siempre Viva 742, CDMX", "Calle Falsa 123, GDL"])

    base = (cv.get("resumen") or "").strip()
    inj = f"Tengo {edad} años, {estado}, {hijos}, religión {religion}, domicilio {dom}. "
    cv["resumen"] = (inj + base).strip()
    return "datos_personales_en_resumen"


def ar_personal_data_in_resumen(cv: dict) -> Optional[str]:
    """ Mete datos personales innecesarios directamente en el RESUMEN. """
    edad = random.randint(21, 45)
    estado = random.choice(["soltero/a", "casado/a"])
    hijos = random.choice(["sin hijos", "1 hijo", "2 hijos"])
    religion = random.choice(["católica", "cristiana", "ninguna"])
    dom = random.choice(["Av. Siempre Viva 742, CDMX", "Calle Falsa 123, GDL"])
    base = (cv.get("resumen") or "").strip()
    inj = f"Tengo {edad} años, {estado}, {hijos}, religión {religion}, domicilio {dom}. "
    cv["resumen"] = (inj + base).strip()
    return "datos_personales_en_resumen"

def ar_hobbies_irrelevantes_en_resumen(cv: dict) -> Optional[str]:
    """ Inserta hobbies/pop-culture irrelevantes en el RESUMEN. """
    extras = [
        # Cultura pop y fandoms
        "Me gusta Marvel y el MCU",
        "Fan de Star Wars y colecciono sables láser",
        "Adicto a ver series de anime (Naruto, One Piece, etc.)",
        "Soy gamer de Fortnite y Call of Duty",
        "Me gusta hacer speedruns de Zelda",
        "Fanático de Dragon Ball desde niño",

        # Deportes y equipos (irrelevantes para la vacante)
        "Soy fan del Atlas",
        "Sigo todos los partidos del Real Madrid",
        "Juego FIFA en línea todos los días",
        "Mi pasatiempo es el fantasy football",

        # Redes sociales y lifestyle
        "Sigo realities y hago trends de TikTok",
        "Subo reseñas de comida en mi Instagram",
        "Me encanta grabar vlogs para YouTube",
        "Participo en retos de baile de TikTok",
        "Influencer amateur en Snapchat",

        # Hobbies triviales
        "Colecciono estampas del Mundial",
        "Juego lotería con mi familia cada domingo",
        "Me gusta hacer memes en mis ratos libres",
        "Fanático de los Funko Pop",
        "Paso horas armando rompecabezas",
        "Hago cosplay en mis tiempos libres",
    ]
    cv["resumen"] = (cv.get("resumen") or "") + " " + random.choice(extras)
    return "hobbies_irrelevantes_en_resumen"


def ar_experiencia_solo_tareas_y_motivo_salida(cv: dict) -> Optional[str]:
    """Convierte descripciones en listados de tareas genéricas y añade motivo de salida."""
    exps = cv.get("experiencia", [])
    if not exps: return None
    plantillas = [
        "- Responsable de reportes y apoyo general.\n- Seguimiento de pendientes.\n- Elaboración de minutas.",
        "- Carga de datos y tareas administrativas.\n- Apoyo al área.\n- Revisión de correo.",
        "- Organización de archivos.\n- Actualización de Excel.\n- Llamadas básicas.",
        "- Control de agendas.\n- Apoyo en logística de reuniones.\n- Elaboración de presentaciones sencillas.",
        "- Recepción y canalización de llamadas.\n- Atención a solicitudes internas.\n- Redacción de oficios simples.",
        "- Actualización de bases de datos.\n- Apoyo en inventario.\n- Digitalización de documentos.",
        "- Coordinación de mensajería.\n- Preparación de reportes básicos.\n- Monitoreo de entregas.",
        "- Gestión de citas.\n- Registro de información.\n- Comunicación con proveedores.",
        "- Seguimiento de trámites.\n- Control de asistencia.\n- Apoyo en archivo físico y digital.",
        "- Revisión de documentos.\n- Apoyo en procesos de compras.\n- Recepción de correspondencia.",
        "- Captura de información en sistema.\n- Preparación de listados.\n- Apoyo al área contable.",
        "- Elaboración de reportes sencillos.\n- Control de formatos.\n- Atención de llamadas internas.",

    ]
    for e in exps:
        e["descripcion"] = random.choice(plantillas) + "\n- Motivo de salida: " + random.choice(
            ["me despidieron", "renuncia por motivos personales", "fin de contrato"]
        )
    return "experiencia_tareas_motivo_salida"

def ar_shuffle_cronologia_y_gaps(cv: dict) -> Optional[str]:
    """Desordena experiencias y crea gaps largos sin explicación (cleaner no reordena global)."""
    exps = cv.get("experiencia", [])
    if len(exps) < 2: return None
    random.shuffle(exps)  # desorden
    # crea un gap retrocediendo inicio de una experiencia intermedia
    i = random.randrange(len(exps))
    try:
        yi, mi = map(int, (exps[i].get("inicio") or "0000-01").split("-"))
        gap_m = random.choice([12, 18, 24, 36])
        yi = max(2000, yi - gap_m // 12)
        mi = max(1, min(12, mi))
        exps[i]["inicio"] = f"{yi:04d}-{mi:02d}"
    except Exception:
        pass
    cv["experiencia"] = exps
    return "desorden_temporal_y_gaps"

def ar_objetivo_vacio_cliche(cv: dict) -> Optional[str]:
    cv["resumen"] = "Busco crecer en una empresa para dar lo mejor de mí."
    return "objetivo_vacio_cliche"

def ar_redundancias_y_exageraciones(cv: dict) -> Optional[str]:
    """Duplica descripciones entre experiencias y añade claims grandilocuentes sin sustento."""
    exps = cv.get("experiencia", [])
    if len(exps) < 2: return None
    base = exps[0].get("descripcion") or "- Encargado de diversas tareas del área."
    for e in exps[1:]:
        e["descripcion"] = (base + "\n- Líder visionario con pensamiento disruptivo.").strip()
    return "redundancias_y_exageraciones"

def ar_typos_global(cv: dict) -> Optional[str]:
    """Inyecta typos en resumen y experiencias (usa rnd_typos existente)."""
    if cv.get("resumen"):
        cv["resumen"] = rnd_typos(cv["resumen"], prob=0.10, orto_prob=0.08, accent_prob=0.06)
    for e in (cv.get("experiencia") or []):
        if e.get("descripcion"):
            e["descripcion"] = rnd_typos(e["descripcion"], prob=0.10, orto_prob=0.08, accent_prob=0.06)
    return "errores_forma_typos"

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

EXCLUSIVE_GROUPS.setdefault("summary", set()).update({
    ar_degrade_summary,
    ar_personal_data_in_resumen,
    ar_hobbies_irrelevantes_en_resumen,
    ar_emojis_uppercase_summary,
})

EXCLUSIVE_GROUPS.setdefault("experience", set()).update({
    ar_degrade_experience,
    ar_no_metrics,
    ar_remove_descriptions,
})

EXCLUSIVE_GROUPS.setdefault("education", set()).update({
    ar_degrade_education,
})

EXCLUSIVE_GROUPS.setdefault("skills", set()).update({
    ar_degrade_skills,
    ar_missing_hard_skills,
    ar_skills_solo_soft,
    ar_skills_irrelevantes,
    ar_skills_desalineadas,
})

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

    # ===================== NUEVAS ANTI‑REGLAS DE CONTENIDO =====================

    # Resumen mal usado: datos personales/hobbies/objetivo vacío
    Rule("datos_personales_en_resumen", "summary", 0.25, ar_personal_data_in_resumen),
    Rule("hobbies_irrelevantes", "summary", 0.18, ar_hobbies_irrelevantes_en_resumen),


    Rule("datos_personales_en_resumen", "summary", 0.25, ar_personal_data_in_resumen),
    Rule("hobbies_irrelevantes", "summary", 0.18, ar_hobbies_irrelevantes_en_resumen),
    Rule("objetivo_vacio_cliche", "summary", 0.20, ar_objetivo_vacio_cliche),

    Rule("tareas_y_motivo_salida", "experience", 0.25, ar_experiencia_solo_tareas_y_motivo_salida),
    Rule("desorden_y_gaps", "experience", 0.22, ar_shuffle_cronologia_y_gaps),
    Rule("redundancias_exageraciones", "experience", 0.18, ar_redundancias_y_exageraciones),

    Rule("errores_forma_typos", "summary", 0.20, ar_typos_global),

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
