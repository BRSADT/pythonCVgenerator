import random
import unicodedata
import os
import re
import json
import math
import glob
import argparse
import random
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from summaries import SummaryGenerator
from typing import Optional
from catalogs import ROLE_KEYWORDS, ROLE_STACKS



from catalogs import (
    ACCION_VERBS_ES, GOOD_VERBS, HARD_SKILLS_POOL, SOFT_SKILLS_POOL,
    JOB_TITLES, INDUSTRIAS, EMAIL_CUTE_PATTERNS, DOMINIOS_PRO, EMOJIS,ROLE_METRICS,
    DEFAULT_METRICS,LOWER_IS_BETTER,HIGHER_IS_BETTER,EDU_FIELDS_TECH,EDU_INSTITUTIONS_GENERIC,
    CERT_CATALOG,PROF_LEVELS,HARD_CATEGORIES,ROLE_SYNONYMS, ROLE_STACKS, ROLE_KEYWORDS, ROLE_BULLETS,ROLE_SKILLS_PRESETS,_canon_role,
    ROLE_SYNONYMS, ROLE_SKILLS_PRESETS, ROLE_SUMMARY_KEYWORDS,    BULLET_TEMPLATES_WITH_METRIC,
    BULLET_TEMPLATES_NO_METRIC,
    BULLET_ACTIONS,
    BULLET_OBJ_QUALIFIERS,
    BULLET_CONNECTORS,
    BULLET_QUAL_IMPACTS
    # ... + catálogos de educación/certs si los usas
)
_ART_GENDER = {
    "API": "la", "estrategia": "la", "herramienta": "la",
    "plataforma": "la", "documentación": "la",
    "pipeline": "el", "servicio": "el", "módulo": "el", "dashboard": "el", "ETL": "el", "proceso": "el", "flujo": "el"
}
_ART_POOL = list(_ART_GENDER.keys())
import re, unicodedata

def _slug_ascii(s: str) -> str:
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r'[^a-z0-9-]', '-', s.lower())
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s

def _ascii_local(s: str) -> str:
    # para email local-part (más permisivo que slug)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r'[^a-z0-9._+-]', '', s.lower())
    return s
def _rng_artifact():
    return random.choice(_ART_POOL)

def _with_article(noun):
    art = _ART_GENDER.get(noun, "")
    return f"{_art_noun(art)}  {noun}" if art else noun

def _neutral(noun):
    # evita artículo cuando no estés seguro
    return noun

# --- Config de estilo de resumen ---
SUMMARY_STYLE_WEIGHTS = {
    "role_impact": 0.35,     # menos “impacto/negocio”
    "profile_first": 0.45,   # más “sobre mí”
    "story_brief": 0.20,     # micro‑historia sin métricas
}
SUMMARY_METRICS_PROB = 0.25  # << antes 0.55
STYLE_METRICS_PROB = {
    "role_impact": 0.45,     # a veces sí
    "profile_first": 0.10,    # casi nunca
    "story_brief": 0.00,      # nunca
}

QUAL_IMPACTS = [
    "mejorando la estabilidad del servicio",
    "reduciendo incidentes críticos en producción",
    "mejorando la mantenibilidad y la legibilidad del código",
    "acortando el time‑to‑review y el time‑to‑merge",
    "aumentando la claridad de los contratos y la trazabilidad"
]
BULLET_METRICS_PROB = 0.7  # 70% con métricas; 30% cualitativo
SUMMARY_LENGTH_WEIGHTS = {"short": 0.45, "medium": 0.40, "long": 0.15}

def _pick_len():
    r = random.random()
    acc = 0
    for k, w in SUMMARY_LENGTH_WEIGHTS.items():
        acc += w
        if r <= acc: return k
    return "medium"


# --- NUEVO: helpers de variedad de bullets (pegar en gen.py, junto a make_bullet_coherent) ---
def _rng_timeframe():
    return random.choice(["en 3 meses", "en 6 meses", "en 1 trimestre", ""])



def _rng_scope():
    return random.choice([
        "para +1M de usuarios",
        "en 5 países",
        "cubriendo 12 microservicios",
        "para 3 unidades de negocio",
        "en 2 regiones cloud"
    ])

def _rng_artifact():
    return random.choice(["pipeline", "servicio", "módulo", "estrategia", "dashboard", "API", "ETL"])

def _rng_action():
    return random.choice(GOOD_VERBS[:-4])  # evita Aumenté/Reduje al inicio

def _rng_stack(stack=None):
    # si ya traes stack del rol, úsalo; si no, inventa 1–2 tecnologias del pool
    from catalogs import HARD_SKILLS_POOL
    if stack:
        return ", ".join(stack[:2])
    return ", ".join(random.sample(HARD_SKILLS_POOL, k=2))

# --- artículos por sustantivo (evita "el/la") ---
_ART_GENDER = {"API":"la","pipeline":"el","servicio":"el","estrategia":"la","ETL":"el","módulo":"el","dashboard":"el"}
def _art_noun(n):
    art = _ART_GENDER.get(n, "")
    return f"{_art_noun(art)}  {n}" if art else n


def make_bullet_varied(titulo, positive=True, stack=None):
    """Genera un bullet con alta variedad léxica y estructural."""
    metric = _pick_metric_for_role(titulo)
    eff = _effect_verb(metric, positive=positive)
    delta = random.randint(8, 45)
    timeframe = _rng_timeframe()  # "en 3 meses" / "" etc.
    horizon = f" {timeframe}" if timeframe else ""
    art = _rng_artifact()
    act = random.choice(BULLET_ACTIONS)  # más variedad que GOOD_VERBS fijo

    # objeto con artículo correcto + posible calificador
    obj = _art_noun(art)
    obj_q = obj + " " + random.choice(BULLET_OBJ_QUALIFIERS)

    # variaciones numéricas y de contexto
    before_after = _format_before_after(metric)  # usa ms/h/pp según métrica
    volume = random.randint(5, 50)
    deploys = random.randint(3, 12)
    nine = random.randint(5, 9)
    scope = _rng_scope()
    maybe_connector = random.choice(BULLET_CONNECTORS) if random.random() < 0.35 else ""
    maybe_stack = (f" Usando {_rng_stack(stack)}." if random.random() < 0.5 else "")

    # Decide si va con métrica o cualitativo (50/50 aprox.)
    with_metric = (random.random() < 0.5)

    tmpl_pool = BULLET_TEMPLATES_WITH_METRIC if with_metric else BULLET_TEMPLATES_NO_METRIC
    tmpl = random.choice(tmpl_pool)

    # Rellena placeholders
    bullet_txt = tmpl.format(
        act=act,
        obj=obj,
        obj_q=obj_q,
        eff=eff,
        metric=metric,
        delta=delta,
        horizon=horizon,
        before_after=before_after,
        volume=volume,
        deploys=deploys,
        nine=nine,
        scope=scope,
        maybe_connector=maybe_connector
    )

    # Añade stack ocasional
    bullet_txt = bullet_txt.strip()
    if maybe_stack and not bullet_txt.endswith("."):
        bullet_txt += "."
    bullet_txt += maybe_stack

    # Limpia espacios dobles y “el el / la la” si llegaran a darse por errores previos
    bullet_txt = re.sub(r"\s{2,}", " ", bullet_txt)
    bullet_txt = re.sub(r"\b(el|la)\s+(el|la)\b", r"\1", bullet_txt, flags=re.I)
    bullet_txt = re.sub(r"\s+([;,:.])", r"\1", bullet_txt)  # sin espacio antes de ; , .
    bullet_txt = bullet_txt.strip()
    if not bullet_txt.startswith("- "):
        bullet_txt = "- " + bullet_txt

    return bullet_txt




def _canon_role_from_title(titulo: str) -> str:
    t = (titulo or "").lower()
    import unicodedata, re
    t = unicodedata.normalize("NFKD", t).encode("ascii","ignore").decode("ascii")
    t = re.sub(r"\s+", " ", t)
    for canon, syns in ROLE_SYNONYMS.items():
        if any(s in t for s in syns):
            return canon
    return ""

def infer_base_role(titulo: str) -> Optional[str]:
    t = (titulo or "").lower().strip()
    for base, syns in ROLE_SYNONYMS.items():
        if any(s in t for s in syns):
            return base
    return None
def _choose_k_bad(args):
    if args.bad_min is not None and args.bad_max is not None:
        return random.randint(args.bad_min, args.bad_max)
    if args.bad_severity == "soft":
        return random.randint(1, 2)
    if args.bad_severity == "hard":
        return random.randint(4, 7)
    # default med
    return random.randint(2, 4)



def rnd_typos(text, prob=0.08, orto_prob=0.06, accent_prob=0.04):
    """
    Inserta ruido en el texto:
    - typos: swaps y letras extra/omitidas (prob)
    - faltas ortográficas comunes en ES (orto_prob)
    - pérdida de tildes/acentos (accent_prob)
    """
    def strip_accents(s):
        return ''.join(ch for ch in unicodedata.normalize('NFD', s)
                       if unicodedata.category(ch) != 'Mn')

    def swap_chars(w):
        if len(w) > 4:
            i = random.randint(1, len(w)-2)
            return w[:i] + w[i+1] + w[i] + w[i+2:]
        return w

    def add_or_drop_letter(w):
        if len(w) < 3:
            return w
        if random.random() < 0.5:  # duplicar una letra interna
            i = random.randint(1, len(w)-2)
            return w[:i] + w[i] + w[i:]  # dup
        else:  # eliminar una letra interna
            i = random.randint(1, len(w)-2)
            return w[:i] + w[i+1:]

    # reglas de "faltas" ortográficas frecuentes (se aplica UNA al azar)
    def misspell_word(w):
        lw = w.lower()

        # 1) b/v (ej: "objetivo"->"ovjetivo" o "clave"->"clabe")
        if any(ch in lw for ch in "bv") and random.random() < 0.25:
            w = re.sub(r'B', 'V', w)
            w = re.sub(r'b', 'v', w)
        elif any(ch in lw for ch in "bv") and random.random() < 0.50:
            w = re.sub(r'V', 'B', w)
            w = re.sub(r'v', 'b', w)

        # 2) c/s/z antes de e/i (ej: "ciencia"->"siencia", "certero"->"sertero")
        if re.search(r'(?i)c[ei]', w) and random.random() < 0.25:
            w = re.sub(r'(?i)c([ei])', r's\1', w)

        # 3) g/j ante e/i (ej: "gestión"->"jestion", "gimnasio"->"jimnasio")
        if re.search(r'(?i)g[ei]', w) and random.random() < 0.25:
            w = re.sub(r'(?i)g([ei])', r'j\1', w)

        # 4) qu/k (ej: "que"->"ke", "quitar"->"kitar")
        if re.search(r'(?i)qu', w) and random.random() < 0.20:
            w = re.sub(r'(?i)qu', 'k', w)

        # 5) h muda (quitar/agregar) (ej: "hacer"->"acer", "abía"->"había")
        if 'h' in lw and random.random() < 0.20:
            w = re.sub(r'(?i)h', '', w)  # quitar h en cualquier posición
        elif random.random() < 0.10 and len(w) > 3:
            w = 'h' + w  # agregar 'h' al inicio

        # 6) -ción -> -sion (ej: "información"->"informasion")
        if re.search(r'(?i)ción\b', w) and random.random() < 0.35:
            w = re.sub(r'(?i)ción\b', 'sion', w)

        # 7) y/ll (ej: "llave"->"yave")
        if re.search(r'(?i)ll', w) and random.random() < 0.20:
            w = re.sub(r'(?i)ll', 'y', w)

        return w

    tokens = re.findall(r"\w+|\W+", text, flags=re.UNICODE)
    out = []
    for t in tokens:
        if not re.match(r"\w+", t):
            out.append(t)
            continue

        w = t
        r = random.random()

        # acentos primero (afecta a toda la palabra)
        if r < accent_prob:
            w = strip_accents(w)
            r = random.random()  # nuevo tiro para otras transformaciones

        # faltas ortográficas
        if r < orto_prob:
            w = misspell_word(w)
            r = random.random()

        # typos mecánicos
        if r < prob:
            if random.random() < 0.5:
                w = swap_chars(w)
            else:
                w = add_or_drop_letter(w)

        out.append(w)

    return "".join(out)


def month_delta(start, months):
    return start + relativedelta(months=+months)

def random_date_between(start_year=2012, end_year=date.today().year):
    y = random.randint(start_year, end_year)
    m = random.randint(1, 12)
    d = random.randint(1, min(28, (date(y, m, 1) + relativedelta(months=1) - timedelta(days=1)).day))
    return date(y, m, d)




def _unique(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            out.append(x); seen.add(x)
    return out


def _sample_with_category_balance(pool, k):
    """
    Toma hasta k skills del pool asegurando diversidad (lenguajes/cloud/datos/etc).
    No introduce sesgo demográfico; solo garantiza variedad técnica.
    """
    from itertools import cycle
    # orden cíclico por categorías
    cat_order = ["lenguajes","cloud_devops","datos_ml","backend_front","bi_analytics","bigdata_stream"]
    picks = []
    cat_iter = cycle(cat_order)
    attempt = 0
    while len(picks) < k and attempt < 200:
        attempt += 1
        cat = next(cat_iter)
        cat_pool = list(HARD_CATEGORIES.get(cat, set()) & set(pool))
        if not cat_pool:
            continue
        picks.append(random.choice(cat_pool))
        picks = _unique(picks)
    # si faltan, rellena del pool general
    if len(picks) < k:
        extra = [s for s in pool if s not in picks]
        random.shuffle(extra)
        picks += extra[:max(0, k - len(picks))]
    return picks[:k]

def _build_hard_detailed(skills):
    """
    Enriquecido opcional para features: nivel y años (0–6).
    No afecta tu formato actual (sigue existiendo 'hard_skills' como lista).
    """
    detailed = []
    for s in skills:
        nivel = random.choices(PROF_LEVELS, weights=[2, 4, 3], k=1)[0]  # más prob. Intermedio
        anios = random.randint(0, 6)
        detailed.append({"skill": s, "nivel": nivel, "años": anios})
    return detailed


def _is_lower_better(metric):
    m = metric.lower()
    return any(m.startswith(x.split()[0]) for x in LOWER_IS_BETTER)

def _is_higher_better(metric):
    m = metric.lower()
    return any(m.startswith(x.split()[0]) for x in HIGHER_IS_BETTER)

def _effect_verb(metric, positive=True):
    # elige verbo de efecto acorde a la dirección
    if _is_lower_better(metric):
        return "reduje" if positive else "aumenté"
    if _is_higher_better(metric):
        return "aumenté" if positive else "reduje"
    return "mejoré" if positive else "empeoré"

def _pick_metric_for_role(titulo):
    pool = ROLE_METRICS.get(titulo, (DEFAULT_METRICS, []))[0]
    return random.choice(pool)


def make_professional_email(first, last):
    dom = random.choice(DOMINIOS_PRO)
    base = f"{_ascii_local(first)}.{_ascii_local(last)}"
    base = re.sub(r'\.+', '.', base).strip('.')
    return f"{base}@{dom}"

def make_cute_email(first, last):
    pattern = random.choice(EMAIL_CUTE_PATTERNS)
    return pattern.format(nombre=first.lower(), apellido=last.lower(), num=random.randint(7, 999))

def make_linkedin(first, last):
    handle = _slug_ascii(f"{first}-{last}") + str(random.randint(10, 99))
    return f"https://www.linkedin.com/in/{handle}"

def make_web(first, last):
    return f"https://{_slug_ascii(first+last)}.dev"

SUMMARY_GEN = SummaryGenerator(
    role_keywords=ROLE_KEYWORDS,
    role_stacks=ROLE_STACKS,
    infer_base_role_fn=infer_base_role,
    pick_metric_fn=_pick_metric_for_role,
    effect_verb_fn=_effect_verb,
    # Sube longitud mínima a 2 frases y métricas globales ~30%
    min_sentences=3,
    global_metrics_prob=0.30,
    metrics_ratio_by_family={
        "data_driven": 0.60,          # muchos con métrica
        "operacion_procesos": 0.45,
        "liderazgo_entrega": 0.35,
        "producto_valor": 0.30
    },
    # Si quisieras aún menos “short”, puedes forzar:
    length_weights={"short": 0.10, "medium": 0.10, "long": 0.80},
)

def make_summary_good(fake, titulo, resumen_existente="", style_weights=None, metrics_prob=None):
    return SUMMARY_GEN.generate(titulo)



def make_summary_bad(fake):
    """
    Genera resúmenes 'malos' variados SIN el string fijo.
    Evita métricas/impacto, abusa de clichés/buzzwords o agrega info irrelevante.
    No añade emojis ni MAYÚSCULAS por defecto (eso queda para anti-reglas).
    """
    titulo = random.choice(JOB_TITLES)
    templates = [
        "Objetivo: Obtener un puesto donde pueda aplicar mis habilidades y crecer profesionalmente en un ambiente dinámico.",
        "Profesional proactivo, responsable y orientado a resultados, con gran capacidad de trabajo bajo presión y excelentes habilidades de comunicación.",
        "Palabras clave: liderazgo, comunicación, trabajo en equipo, Office, Excel, PowerPoint, responsabilidad, puntualidad.",
        "Tengo {edad} años, {estado_civil}, vivo con mi familia. Busco estabilidad y buen ambiente laboral.",
        "Encargado de diversas tareas relacionadas con {titulo}; apoyo general al equipo y cumplimiento de actividades asignadas.",
        "Apasionado por la excelencia y el pensamiento disruptivo, con fuerte enfoque holístico y mentalidad de crecimiento.",
        "Soy el candidato ideal para cualquier posición, me adapto a todo y aprendo muy rápido en cualquier área.",
        "Busco un rol que me permita viajar con frecuencia y tener horarios flexibles para mis proyectos personales.",
        "Desarrollador con experiencia en herramientas modernas; me gusta React pero puedo ver otras cosas si es necesario.",
        "Realización de actividades varias en el área, apoyo en proyectos, seguimiento de pendientes y coordinación básica."
    ]
    edad = random.randint(21, 42)
    estado_civil = random.choice(["soltero/a", "casado/a"])
    base = random.choice(templates).format(edad=edad, estado_civil=estado_civil, titulo=titulo.lower())
    if random.random() < 0.35:
        base = rnd_typos(base, prob=0.06)
    if random.random() < 0.25:
        base += " También cuento con gran disposición para aprender."
    return base


def make_bullet_coherent(titulo, positive=True, include_version=False, stack=None):
    verb = random.choice(GOOD_VERBS[:-4])
    metric = _pick_metric_for_role(titulo)
    eff = _effect_verb(metric, positive=positive)

    use_metric = (random.random() < BULLET_METRICS_PROB)
    if use_metric:
        delta = random.randint(8, 45)
        timeframe = random.choice(["en 3 meses","en 6 meses","en 1 trimestre",""])
        core = f"{verb} el {random.choice(['pipeline','proceso','servicio','módulo','flujo'])} clave, {eff} {metric} en {delta}%"
        if timeframe: core += f" {timeframe}"
    else:
        qual = random.choice(QUAL_IMPACTS)
        core = f"{verb} el {random.choice(['pipeline','proceso','servicio','módulo','flujo'])} clave, {qual}"

    if include_version and stack:
        core += f". Usando {', '.join(stack)}"
    return core + "."



def make_experience_good(fake, titulo):
    n = random.randint(2, 4)
    items = []
    start = random_date_between(2015, max(2019, date.today().year-3))
    for i in range(n):
        end = month_delta(start, random.randint(10, 30))
        if end > date.today():
            end = date.today()
        bullets = []
        for _ in range(random.randint(3, 5)):
            bullets.append(make_bullet_varied(titulo, positive=True))
        items.append({
            "puesto": titulo if i == 0 else random.choice(JOB_TITLES),
            "empresa": fake.company(),
            "inicio": start.strftime("%Y-%m"),
            "fin": end.strftime("%Y-%m") if end != date.today() else "Actual",
            "descripcion": "\n".join(bullets)
        })
        start = end - relativedelta(months=random.randint(0, 4))
    items.sort(key=lambda x: x["inicio"], reverse=True)
    return items

def make_experience_bad(fake):
    n = random.randint(1, 3)
    items = []
    for _ in range(n):
        inicio = random_date_between(2016, 2024)
        fin = month_delta(inicio, random.randint(1, 8))
        bullets = []
        # 0–2 bullets genéricos, y opcional 1 negativo plausible
        for _ in range(random.randint(0, 2)):
            bullets.append(random.choice([
                "- Encargado de varias tareas del área.",
                "- Apoyo general en actividades asignadas.",
                "- Responsable de reportes y seguimiento."
            ]))
        if random.random() < 0.5:  # 50% genera un bullet con impacto negativo verosímil
            titulo = random.choice(JOB_TITLES)
            bullets.append("- " + make_bullet_coherent(titulo, positive=False))
        items.append({
            "puesto": random.choice(JOB_TITLES),
            "empresa": fake.company(),
            "inicio": inicio.strftime("%Y-%m"),
            "fin": fin.strftime("%Y-%m"),
            "descripcion": "\n".join(bullets)
        })
    random.shuffle(items)
    return items


def make_education_good(fake):
    grad_year = random.randint(2015, 2023)
    entries = [{
        "grado": "Licenciatura",
        "area": random.choice(["Ingeniería en Computación", "Matemáticas", "Informática", "Sistemas"]),
        "institucion": fake.company() + " University",
        "fin": str(grad_year),
        "logros": "Graduación con promedio destacado. Participación en proyectos aplicados."
    }]
    seen = {}
    clean = []
    for e in entries:
        k = (e.get("grado",""), e.get("area",""), e.get("institucion",""))
        if k in seen:
            # Si es la misma cert/estudio y solo cambia el año, márcalo como recertificación
            prev = seen[k]
            if e["grado"] == "Certificación" and e["area"] == prev["area"]:
                if e["fin"] != prev["fin"]:
                    e["area"] = e["area"] + " (Recertificación)"
                    clean.append(e)
            # Si es exactamente igual, se descarta
            continue
        seen[k] = e
        clean.append(e)
    return clean

def make_education_bad(fake):
    # Campos faltantes / vagos
    return [{
        "grado": random.choice(["Curso", "Diploma", "Licenciatura"]),
        "area": "",
        "institucion": "Escuela X",
        "fin": "",
        "logros": "" if random.random() < 0.6 else "varias cosas"
    }]

def make_education_good(fake):
    """
    Educación 'buena' sin sesgos:
    - Instituciones genéricas (no ligadas a país/ciudad).
    - Campos técnicos variados.
    - Fechas consistentes y posibilidad de estudios en curso.
    - Opcional: posgrado/diplomado y 1–3 certificaciones relevantes.
    - Logros neutrales (proyecto, tesis, beca, participación).
    """
    current_year = date.today().year
    start_year_min = 2012
    grad_year = random.randint(2015, min(current_year, 2024))
    in_progress = (random.random() < 0.1 and grad_year == current_year)

    primary = {
        "grado": random.choice(["Licenciatura", "Ingeniería"]),
        "area": random.choice(EDU_FIELDS_TECH),
        "institucion": random.choice(EDU_INSTITUTIONS_GENERIC),
        "fin": "Actual" if in_progress else str(grad_year),
        "logros": random.choice([
            "Proyecto de titulación aplicado en entorno real.",
            "Participación en laboratorio de investigación y proyectos aplicados.",
            "Beca por desempeño académico y colaboración en proyectos.",
            "Tesis enfocada en solución de problema con datos y software."
        ])
    }

    entries = [primary]

    # Posibilidad de posgrado/diplomado posterior (20–35%)
    if random.random() < 0.3:
        post_year = min(current_year, grad_year + random.randint(1, 4))
        entries.append({
            "grado": random.choice(["Maestría", "Especialización", "Diplomado"]),
            "area": random.choice([
                "Arquitectura de Software", "Gestión de Proyectos Ágiles",
                "Ciencia de Datos Avanzada", "Seguridad en la Nube",
                "Machine Learning aplicado"
            ]),
            "institucion": random.choice(EDU_INSTITUTIONS_GENERIC),
            "fin": str(post_year) if post_year <= current_year else "Actual",
            "logros": random.choice([
                "Trabajo final con despliegue en nube y documentación completa.",
                "Proyecto integrador con métricas de calidad y pruebas automatizadas.",
                "Publicación/ponencia interna sobre resultados del proyecto."
            ])
        })

    # 1–3 certificaciones con año consistente
    n_certs = random.randint(1, 3)
    cert_start = min(current_year, grad_year + random.randint(0, 2))
    for _ in range(n_certs):
        cert_year = random.randint(min(cert_start, current_year), current_year)
        entries.append({
            "grado": "Certificación",
            "area": random.choice(CERT_CATALOG),
            "institucion": "Proveedor oficial",
            "fin": str(cert_year),
            "logros": ""
        })

    return entries


def make_education_bad(fake):
    """
    Genera entradas de educación 'malas':
    - Datos vagos, inconsistentes o poco relevantes.
    - Fechas faltantes o incoherentes.
    - Logros triviales o vacíos.
    """
    grados = ["Curso", "Diploma", "Licenciatura", "Certificado", "Taller"]
    instituciones = [
        "Escuela X",
        "Centro de Estudios",
        "Instituto",
        "Academia sin nombre",
        "Colegio"
    ]
    logros_malos = [
        "",
        "varias cosas",
        "asistencia regular",
        "aprendí mucho",
        "participación básica",
        "sin detalles"
    ]

    return [{
        "grado": random.choice(grados),
        "area": random.choice(["", "", "Informática", "Administración", ""]),
        "institucion": random.choice(instituciones),
        "fin": random.choice(["", "en curso", str(random.randint(2025, 2030)), " "]),
        "logros": random.choice(logros_malos)
    }]


def infer_base_role(titulo: str) -> str:
    """
    Devuelve la clave de rol base coherente con tus catálogos.
    Busca por substring en ROLE_SYNONYMS; si no existe, prueba con
    claves directas de ROLE_STACKS/ROLE_SKILLS_PRESETS.
    """
    t = (titulo or "").lower().strip()
    try:
        from catalogs import ROLE_SYNONYMS, ROLE_STACKS, ROLE_SKILLS_PRESETS
    except Exception:
        ROLE_SYNONYMS, ROLE_STACKS, ROLE_SKILLS_PRESETS = {}, {}, {}

    # 1) Sinónimos
    for base, syns in (ROLE_SYNONYMS or {}).items():
        if any(s in t for s in syns):
            return base

    # 2) Coincidencia por nombre de clave (Backend, Data Analyst, etc.)
    for base in list((ROLE_SKILLS_PRESETS or {}).keys()) + list((ROLE_STACKS or {}).keys()):
        if base.lower() in t:
            return base

    return ""  # desconocido

def make_skills_good(titulo: str = None, seniority_hint: str = None):
    """
    Genera skills 'buenas' alineadas al rol si hay título reconocible.
    - Cubre CORE del rol y rellena con PLUS.
    - Evita 'avoid' si está definido.
    - Mantiene tamaños razonables y 'hard_skills_detailed'.
    - Fallback: diversidad por categorías desde HARD_SKILLS_POOL.
    """
    import random
    from catalogs import (
        HARD_SKILLS_POOL, SOFT_SKILLS_POOL,
        ROLE_SKILLS_PRESETS, ROLE_STACKS
    )

    # Tamaños objetivo
    hard_k = random.randint(6, 9)
    soft_k = random.randint(5, 7)

    base_role = infer_base_role(titulo)
    if not base_role:
        # Fallback clásico (tu comportamiento anterior)
        hard = _unique(_sample_with_category_balance(HARD_SKILLS_POOL, k=hard_k))
        soft = _unique(random.sample(SOFT_SKILLS_POOL, k=min(soft_k, len(SOFT_SKILLS_POOL))))
        hard_sorted, soft_sorted = sorted(hard), sorted(soft)
        return {
            "hard_skills": hard_sorted,
            "soft_skills": soft_sorted,
            "hard_skills_detailed": _build_hard_detailed(hard_sorted)
        }

    # Construye spec (CORE/PLUS/AVOID) a partir de ROLE_SKILLS_PRESETS;
    # si no existe, deriva una spec simple desde ROLE_STACKS.
    spec = (ROLE_SKILLS_PRESETS or {}).get(base_role)
    if not spec:
        seed = list((ROLE_STACKS or {}).get(base_role, []))
        core = seed[:4]
        plus = seed[4:]
        spec = {"core": core, "plus": plus, "avoid": []}

    core = list(spec.get("core", []))
    plus = [s for s in spec.get("plus", []) if s not in core]
    avoid = set(spec.get("avoid", []))

    # Nivel (opcional) para sesgar el reparto
    lvl = (seniority_hint or "").lower()
    if not lvl and titulo:
        t = titulo.lower()
        lvl = "jr" if ("jr" in t or "junior" in t) else ("sr" if ("sr" in t or "senior" in t) else "")

    # 1) cubrir core (3–4 mínimo)
    random.shuffle(core)
    take_core = min(len(core), max(3, min(4, hard_k)))
    hard = core[:take_core]

    # 2) completar con plus (más plus si 'sr', más core si 'jr')
    random.shuffle(plus)
    need = hard_k - len(hard)
    if lvl == "sr":
        # prioriza plus
        hard.extend(plus[:max(0, need)])
    elif lvl == "jr":
        # si sobra hueco, reinyecta core adicional antes de plus
        extra_core = [c for c in core[take_core:] if c not in hard]
        to_add = min(len(extra_core), need)
        hard.extend(extra_core[:to_add])
        need = hard_k - len(hard)
        if need > 0:
            hard.extend(plus[:need])
    else:
        # neutral
        hard.extend(plus[:max(0, need)])

    # 3) si aún falta, rellena del pool general evitando 'avoid' y duplicados
    if len(hard) < hard_k:
        extras = [s for s in HARD_SKILLS_POOL if s not in hard and s not in avoid]
        random.shuffle(extras)
        hard.extend(extras[:hard_k - len(hard)])

    # 4) limpieza final
    hard = [s for s in _unique(hard) if s not in avoid][:hard_k]

    # Soft aleatorias sin duplicados
    soft = _unique(random.sample(SOFT_SKILLS_POOL, k=min(soft_k, len(SOFT_SKILLS_POOL))))

    hard_sorted = sorted(hard)
    soft_sorted = sorted(soft)
    return {
        "hard_skills": hard_sorted,
        "soft_skills": soft_sorted,
        "hard_skills_detailed": _build_hard_detailed(hard_sorted)
    }

def make_skills_bad():
    """
    Variedad de fallas:
    - 35%: completamente vacío.
    - 35%: solo soft (1–4), desordenadas.
    - 15%: hard 'redundantes' (Office/básicos) + soft mínimas.
    - 15%: hard desalineadas (pocas y superficiales) + soft mínimas.
    """
    r = random.random()
    if r < 0.35:
        return {"hard_skills": [], "soft_skills": []}

    if r < 0.70:
        # solo soft (1–4), evitando duplicados; orden aleatorio
        soft_n = random.randint(1, 4)
        soft = random.sample(SOFT_SKILLS_POOL, k=min(soft_n, len(SOFT_SKILLS_POOL)))
        random.shuffle(soft)
        return {"hard_skills": [], "soft_skills": soft}

    if r < 0.85:
        # 'hard' redundantes/básicos presentados como principales
        hard = random.sample(["Word", "PowerPoint", "Correo electrónico", "Navegación web", "Office"],
                             k=random.randint(1, 3))
        soft = random.sample(SOFT_SKILLS_POOL, k=random.randint(0, 2))
        return {"hard_skills": hard, "soft_skills": soft}

    # desalineados: 1–2 hard superficiales fuera de foco
    hard = random.sample(["HTML", "CSS"], k=random.randint(1, 2))
    soft = random.sample(SOFT_SKILLS_POOL, k=random.randint(0, 2))
    return {"hard_skills": hard, "soft_skills": soft}


def make_contact_good(fake, first, last):
    return {
        "email": make_professional_email(first, last),
        "telefono": fake.phone_number(),
        "linkedin": make_linkedin(first, last),
        "web": "" if random.random() < 0.5 else f"https://{first}{last}.dev".lower()
    }

def make_contact_bad(fake, first, last):
    correo = make_cute_email(first, last)
    return {
        "email": correo,
        "telefono": fake.phone_number(),
        "linkedin": "" if random.random() < 0.8 else make_linkedin(first, last) + random.choice(EMOJIS),
        "web": random.choice(["", "http://miwebgratis.tk", "http://blogspot-1998-example.com"])
    }

def _norm_key(s: str) -> str:
    return re.sub(r'\W+', ' ', (s or '').lower()).strip()

def _clean_spaces(s: str) -> str:
    # quita espacios antes de ; , .  y dobles espacios
    s = re.sub(r'\s+([;,:.])', r'\1', s)
    s = re.sub(r'\s{2,}', ' ', s).strip()
    # arregla "tiempos de tiempo de"
    s = re.sub(r'tiempos de tiempo de', 'tiempos de', s, flags=re.I)
    return s

def _dedup_bullets(lines: list[str]) -> list[str]:
    seen, out = set(), []
    for ln in lines:
        k = _norm_key(ln)
        if k in seen:
            continue
        out.append(_clean_spaces(ln))
        seen.add(k)
    return out


WEB_MS = {"LCP","FID","TTFB"}
WEB_PP = {"CLS"}  # puntos porcentuales

def _format_before_after(metric: str) -> str:
    m = (metric or "").upper()
    if m in WEB_MS:
        before = random.randint(2500, 5000)  # ms
        after  = random.randint(800, 1800)
        if after >= before: after = max(200, before - random.randint(400,1200))
        return f"de {before} ms a {after} ms"
    if m in WEB_PP:
        # puntos en vez de horas/%
        before = round(random.uniform(0.25, 0.35), 2)
        after  = round(max(0.01, before - random.uniform(0.05, 0.15)), 2)
        return f"de {before} a {after}"
    # cobertura/tests/time-to-report/latencia → horas por defecto
    before = random.randint(6,18)
    after  = random.randint(1,5)
    if after >= before: after = max(1, before - random.randint(2,5))
    return f"de {before} h a {after} h"


REAL_LOCS = [
    "Ciudad de México, México", "Guadalajara, México", "Monterrey, México",
    "Buenos Aires, Argentina", "Bogotá, Colombia", "Santiago, Chile",
    "Madrid, España", "Barcelona, España", "Lima, Perú",
    "Miami, Estados Unidos", "Toronto, Canadá"
]

def make_location(fake=None):
    return random.choice(REAL_LOCS)
