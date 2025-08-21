# -*- coding: utf-8 -*-
"""
Generador de CVs sintéticos con Faker
- Produce CVs "buenos" y "malos" según reglas configuradas.
- Exporta JSONL (para ML) y TXT (estilo ATS).
- Opcional: calcula encaje (fit) contra UNA O VARIAS vacantes (JSONs).
- Uso básico:
    python generador_cvs.py --n 200 --ratio_buenos 0.6 --locale es_MX --out ./salida
- Con múltiples vacantes (por rutas repetidas o glob):
    python generador_cvs.py --n 200 --locale es_MX \
      --jd vacantes/analista_datos.json \
      --jd vacantes/backend_jr.json \
      --fit_threshold 0.7 \
      --out ./salida_fit_multi
    # o
    python generador_cvs.py --n 200 --locale es_MX \
      --jd_glob "./vacantes/*.json" \
      --fit_threshold 0.7 \
      --out ./salida_fit_multi
"""
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

from faker import Faker

# ----------------------------
# Listas base y utilidades
# ----------------------------

ACCION_VERBS_ES = [
    "Lideré", "Diseñé", "Implementé", "Optimicé", "Automaticé", "Coordiné",
    "Mejoré", "Desarrollé", "Analicé", "Iteré", "Escalé", "Consolidé",
    "Reduje", "Aumenté", "Orquesté", "Integré", "Planifiqué", "Ejecuté",
    "Supervisé", "Capacité", "Gestioné", "Dirigí", "Evalué", "Monitoreé",
    "Fortalecí", "Modernicé", "Estandaricé", "Simplifiqué", "Agilicé",
    "Audité", "Reestructuré", "Validé", "Refactoricé", "Migré", "Impulsé",
    "Negocié", "Colaboré", "Documenté", "Implementé mejoras", "Estabilicé"
]

HARD_SKILLS_POOL = [
    # Lenguajes de programación
    "Python", "R", "Java", "C++", "C#", "JavaScript", "TypeScript", "Go", "Rust",
    # Bases de datos
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Cassandra", "Redis", "Elasticsearch",
    # BI y análisis
    "Power BI", "Tableau", "Qlik Sense", "Looker", "Excel avanzado",
    # Cloud & DevOps
    "Docker", "Kubernetes", "Terraform", "Ansible",
    "Linux", "Git", "CI/CD", "Jenkins", "AWS", "GCP", "Azure",
    # Ciencia de datos e IA
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "PyTorch", "TensorFlow", "Scikit-learn", "Hugging Face", "LangChain",
    # Big Data
    "Spark", "Hadoop", "Kafka",
    # Desarrollo Web / Backend
    "Django", "FastAPI", "Flask", "Spring Boot", "Node.js", "Express.js",
    # Frontend
    "React", "Angular", "Vue.js", "Next.js",
    # Seguridad
    "Ciberseguridad", "Pentesting", "OWASP", "Seguridad en la nube",
    # QA / Testing
    "Selenium", "JUnit", "PyTest", "Postman",
    # Otros
    "Scrum", "Kanban", "Agile", "Microservicios", "APIs REST", "GraphQL"
]

SOFT_SKILLS_POOL = [
    "Comunicación efectiva", "Trabajo en equipo", "Liderazgo",
    "Pensamiento crítico", "Gestión del tiempo", "Adaptabilidad",
    "Resolución de problemas", "Orientación a resultados", "Empatía",
    # Más específicas del entorno tech
    "Aprendizaje continuo", "Gestión de proyectos ágiles",
    "Colaboración en entornos remotos", "Capacidad de mentoría",
    "Documentación clara", "Atención al detalle", "Innovación",
    "Resiliencia", "Proactividad", "Gestión de conflictos",
    "Pensamiento analítico", "Creatividad en la resolución de problemas"
]

JOB_TITLES = [
    # Ciencia de datos y análisis
    "Analista de Datos", "Científico de Datos", "Ingeniero de Machine Learning",
    "Ingeniero de IA", "Especialista en NLP", "MLOps Engineer",
    # Desarrollo de software
    "Ingeniero de Software", "Desarrollador Backend", "Desarrollador Full-Stack",
    "Desarrollador Frontend", "Ingeniero DevOps", "Arquitecto de Software",
    # Cloud y sistemas
    "Cloud Engineer", "Cloud Architect", "Site Reliability Engineer (SRE)",
    "Administrador de Sistemas", "Ingeniero de Infraestructura",
    # BI y producto
    "Especialista en BI", "Ingeniero de Datos", "Data Engineer",
    "Data Architect", "Product Manager", "Product Owner",
    # QA y pruebas
    "QA Engineer", "QA Automation Engineer", "Tester de Software",
    # Ciberseguridad
    "Especialista en Ciberseguridad", "Ingeniero de Seguridad",
    "Analista SOC", "Pentester",
    # Otros
    "Scrum Master", "Agile Coach", "Consultor Tecnológico"
]
INDUSTRIAS = [
    "Fintech",              # bancos digitales, pagos, blockchain
    "E-commerce",           # marketplaces, retail digital
    "Telecomunicaciones",   # redes, 5G, IoT
    "Salud Digital",        # healthtech, telemedicina
    "EdTech",               # plataformas educativas, LMS
    "Ciberseguridad",       # seguridad informática, SOC
    "Cloud Computing",      # proveedores de nube y SaaS
    "Inteligencia Artificial", # startups y big tech IA
    "Videojuegos",          # gaming, AR/VR
    "Automotriz Tech",      # autos eléctricos, conducción autónoma
    "Smart Cities",         # IoT urbano, movilidad inteligente
    "Energía y CleanTech",  # renovables, optimización energética
    "Consultoría Tecnológica", # servicios de TI y digitalización
    "Medios Digitales",     # streaming, redes sociales
    "Logística Tech"        # última milla, optimización con datos
]



EMAIL_CUTE_PATTERNS = [
    "gatita_{num}_{nombre}@gmail.com",
    "dragon_{apellido}{num}@hotmail.com",
    "baby.{nombre}_{num}@yahoo.com",
    "rockstar_{nombre}{apellido}{num}@gmail.com",
    "dark_{nombre}{num}@hotmail.com",
    "angel_{apellido}_{num}@yahoo.com",
    "naruto_{nombre}_{num}@gmail.com",
    "party_{apellido}{num}@hotmail.com"
]

DOMINIOS_PRO = [
    "gmail.com", "outlook.com", "proton.me", "icloud.com",
    "zoho.com", "tutanota.com", "hey.com", "empresa.com"
]


EMOJIS = ["😅", "✨", "🔥", "🥳", "🤙", "💯", "😉", "🤩"]


# =========================
# Anti-reglas (errores)
# =========================

def _ensure_extras(cv):
    if "extras" not in cv:
        cv["extras"] = {}

def _strip_metrics(text):
    # quita % y números que parezcan métricas
    return re.sub(r"\b\d{1,3}%\b", "X%", re.sub(r"\b\d+\b", "N", text))

def ar_emojis_uppercase_summary(cv):
    cv["resumen"] = cv["resumen"].upper() + " " + " ".join(random.sample(EMOJIS, k=random.randint(1,3)))
    return "emojis_y_mayus_en_resumen"

def ar_include_age_marital(cv):
    extra = " Edad: {} años. Estado civil: {}.".format(random.randint(21, 42), random.choice(["Soltero/a", "Casado/a"]))
    cv["resumen"] = (cv["resumen"] + " " + extra).strip()
    return "incluye_edad_y_estado_civil"

def ar_instagram_contact(cv):
    cv["contacto"]["instagram"] = "@{}".format(re.sub(r"\s+", "", cv["identidad"]["nombre"].lower()))
    return "incluye_instagram_personal"

def ar_mentions_layoff(cv):
    if cv["experiencia"]:
        cv["experiencia"][0]["descripcion"] = (cv["experiencia"][0].get("descripcion","") +
            "\n- Motivo de salida: recorte de personal.").strip()
    return "menciona_recorte_personal"

def ar_irrelevant_hobbies(cv):
    _ensure_extras(cv)
    hobbies = cv["extras"].get("intereses", [])
    hobbies = list(set(hobbies + random.sample(["Real Madrid","Marvel","Videojuegos retro","Gatos siameses"], k=2)))
    cv["extras"]["intereses"] = hobbies
    return "hobbies_irrelevantes"

def ar_links_broken(cv):
    # rompe linkedin/web
    if cv["contacto"].get("linkedin"):
        cv["contacto"]["linkedin"] = "http://link-broken.example"
    if "web" in cv["contacto"]:
        cv["contacto"]["web"] = "http://404.example"
    return "links_rotos"

def ar_incoherent_dates(cv):
    # pone una entrada con fin < inicio
    if cv["experiencia"]:
        exp = random.choice(cv["experiencia"])
        inicio = date(2021, 5, 1)
        fin = date(2020, 12, 1)
        exp["inicio"] = inicio.strftime("%Y-%m")
        exp["fin"] = fin.strftime("%Y-%m")
    return "fechas_incoherentes"

def ar_remove_descriptions(cv):
    # borra descripciones de algunas experiencias, pero garantiza al menos una con texto
    if not cv.get("experiencia"):
        return None
    touched = False
    prev_non_empty_idx = [i for i, e in enumerate(cv["experiencia"]) if e.get("descripcion")]

    for e in cv["experiencia"]:
        if e.get("descripcion") and random.random() < 0.6:
            e["descripcion"] = ""
            touched = True

    # si accidentalmente quedaron TODAS vacías, restaura una con un bullet mínimo
    if touched:
        any_non_empty = any(e.get("descripcion") for e in cv["experiencia"])
        if not any_non_empty and prev_non_empty_idx:
            idx = random.choice(prev_non_empty_idx)
            titulo = cv.get("identidad", {}).get("titulo") or random.choice(JOB_TITLES)
            cv["experiencia"][idx]["descripcion"] = "- " + make_bullet_coherent(titulo, positive=True)
    return "experiencia_sin_descripcion" if touched else None


def ar_no_metrics(cv):
    # reemplaza números/porcentajes para quitar impacto
    for e in cv["experiencia"]:
        if e.get("descripcion"):
            e["descripcion"] = _strip_metrics(e["descripcion"])
    return "sin_metricas"

def ar_cute_email(cv):
    # correo poco profesional
    first, last = cv["identidad"]["nombre"].split(" ", 1)
    cv["contacto"]["email"] = make_cute_email(first, last)
    return "email_poco_profesional"

def ar_missing_hard_skills(cv):
    cv["skills"]["hard_skills"] = []
    return "faltan_hard_skills"

def ar_contact_block_huge(cv):
    # simula bloque de contacto "pesado" con muchos canales
    cv["contacto"]["telefono_alterno"] = cv["contacto"]["telefono"] if "telefono" in cv["contacto"] else "+52 55 0000 0000"
    cv["contacto"]["tiktok"] = "@{}".format(cv["identidad"]["nombre"].split()[0].lower())
    cv["contacto"]["facebook"] = "fb.com/{}".format(cv["identidad"]["nombre"].replace(" ",".").lower())
    return "contacto_demasiado_grande"

ANTI_RULE_FUNCS = [
    ar_emojis_uppercase_summary,
    ar_include_age_marital,
    ar_instagram_contact,
    ar_mentions_layoff,
    ar_irrelevant_hobbies,
    ar_links_broken,
    ar_incoherent_dates,
    ar_remove_descriptions,
    ar_no_metrics,
    ar_cute_email,
    ar_missing_hard_skills,
    ar_contact_block_huge,
]



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

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# ----------------------------
# Generadores de componentes
# ----------------------------

def make_professional_email(first, last):
    dom = random.choice(DOMINIOS_PRO)
    base = f"{first}.{last}".lower().replace(" ", "")
    return f"{base}@{dom}"

def make_cute_email(first, last):
    pattern = random.choice(EMAIL_CUTE_PATTERNS)
    return pattern.format(nombre=first.lower(), apellido=last.lower(), num=random.randint(7, 999))

def make_linkedin(first, last):
    handle = f"{first}-{last}".lower().replace(" ", "-")
    return f"https://www.linkedin.com/in/{handle}{random.randint(10,99)}"

def make_summary_good(fake, titulo):
    """
    Resumen 'bueno' más elaborado y variado para perfiles tech.
    - Incluye industria, stack, métricas y horizonte temporal.
    - Alterna plantillas (impacto, plataforma, datos/ML, producto, confiabilidad/DevOps).
    """
    verb = random.choice(ACCION_VERBS_ES)
    industria = random.choice(INDUSTRIAS)
    stack = random.sample(HARD_SKILLS_POOL, k=min(3, max(2, random.randint(2, 4))))
    metric = _pick_metric_for_role(titulo)
    delta = random.randint(8, 45)
    timeframe = random.choice(["en 3 meses", "en 6 meses", "en 1 trimestre", "en 2 trimestres"])
    eff = _effect_verb(metric, positive=True)
    senior = random.choice([
        "", "con trayectoria en entornos de alto crecimiento",
        "con experiencia en productos de misión crítica",
        "enfocado en calidad y entrega continua"
    ])
    alcance = random.choice([
        "impactando a +1M de usuarios",
        "soportando cargas pico estacionales",
        "cumpliendo SLOs exigentes",
        "alineado a OKRs de negocio"
    ])
    gobierno = random.choice([
        "bajo prácticas Agile/Scrum", "con CI/CD y pruebas automatizadas",
        "apegado a seguridad y compliance en nube", "con observabilidad end‑to‑end"
    ])
    # Opcional liderazgo/equipo
    equipo = random.choice([
        "", "Colaboración con equipos multidisciplinarios (Producto, Diseño, Datos).",
        "Mentoría a perfiles junior y coordinación con stakeholders técnicos y de negocio.",
        "Trabajo transversal con SRE/DevOps y Data para acelerar entregas."
    ])

    # Plantillas temáticas
    templates = [
        # 1) Impacto y optimización
        "Profesional {titulo_l} {senior}. {verb} soluciones en {industria} que {eff} {metric} en {delta}% {timeframe}, "
        "mediante {stack}. {alcance}; {gobierno}. {equipo}",

        # 2) Plataforma/arquitectura
        "{titulo} {senior}. {verb} una arquitectura modular y escalable en {industria}, "
        "habilitando nuevas capacidades con {stack}. Resultado: {eff} {metric} en {delta}% {timeframe} y reducción de deuda técnica; {gobierno}. {equipo}",

        # 3) Datos/ML
        "Especialista en soluciones de datos/ML para {industria}. {verb} pipelines y modelos productivos con {stack}, "
        "logrando {eff} {metric} en {delta}% {timeframe}. Enfoque en trazabilidad, reproducibilidad y monitoreo de modelos; {gobierno}. {equipo}",

        # 4) Producto/entregables
        "{titulo} orientado a impacto. {verb} iniciativas clave en {industria} con {stack}, "
        "priorizando valor de negocio y time-to-market. Se {eff} {metric} en {delta}% {timeframe}; {alcance}. {gobierno}. {equipo}",

        # 5) Confiabilidad/DevOps
        "{titulo} {senior} en plataformas cloud. {verb} servicios críticos en {industria} con {stack}, "
        "mejorando confiabilidad y velocidad de despliegue: {eff} {metric} en {delta}% {timeframe}. Observabilidad y rollback seguro; {gobierno}. {equipo}",

        # --- Plantillas expandidas ---
        "Profesional en {titulo} con sólida experiencia en {industria}. {verb} soluciones basadas en datos que generaron un {delta}% de mejora en eficiencia operativa.",
        "Especialista en {titulo} enfocado en el uso de {stack} para resolver problemas complejos de negocio. {verb} proyectos con impacto medible en productividad.",
        "Ingeniero con trayectoria en {industria} aplicando {stack} y metodologías ágiles. Experiencia en proyectos de alcance internacional.",
        "{verb} iniciativas de Inteligencia Artificial en {industria}, integrando modelos de {stack} para optimizar procesos clave.",
        "Profesional con dominio de {stack} y enfoque en analítica avanzada. {verb} estrategias de datos que redujeron costos en un {delta}%.",
        "Orientado a resultados en {titulo}, con experiencia en {industria}. {verb} soluciones escalables en la nube ({stack}) logrando mejoras en disponibilidad.",
        "Experto en {stack} con práctica en equipos multidisciplinarios. {verb} proyectos de innovación tecnológica para empresas líderes del sector.",
        "Candidato con experiencia comprobada en {titulo}. {verb} sistemas inteligentes que impactaron en la toma de decisiones estratégicas.",
        "Perfil orientado a {stack} con conocimientos en analítica avanzada. {verb} proyectos de transformación digital en {industria}.",
        "{verb} proyectos aplicando {stack} y {soft} para lograr un impacto organizacional positivo en {industria}.",
        "Ingeniero con visión innovadora en {industria}. Experiencia en {stack} y metodologías ágiles como Scrum/Kanban.",
        "Profesional en {titulo} que combina experiencia técnica con {soft}. {verb} iniciativas que fortalecieron la competitividad empresarial en un {delta}%.",
        "{verb} proyectos de Inteligencia Artificial aplicados a {stack} con impacto en {industria}.",
        "Trayectoria en {titulo} con énfasis en {stack}. Capacidad demostrada para integrar datos, modelos y procesos de negocio.",
        "Candidato con experiencia en {industria} aplicando {stack}. {verb} proyectos de alto impacto con métricas de mejora superiores al {delta}%."
    ]

    tmpl = random.choice(templates)
    soft = random.choice(SOFT_SKILLS_POOL)
    summary = tmpl.format(
        titulo=titulo,
        titulo_l=titulo.lower(),
        senior=senior if senior else "",
        verb=verb,
        industria=industria,
        eff=eff,
        metric=metric,
        delta=delta,
        timeframe=timeframe,
        stack=", ".join(stack),
        alcance=alcance,
        gobierno=gobierno,
        equipo=equipo,
        soft = soft
    )

    # Pulido ligero: espacios dobles y puntos finales
    summary = re.sub(r"\s{2,}", " ", summary).strip()
    if not summary.endswith("."):
        summary += "."
    return summary

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



LOWER_IS_BETTER = [
    "costos", "costo unitario", "CAC", "tiempo de ciclo", "tiempo de respuesta",
    "latencia", "defectos", "bugs", "retrabajo", "incidentes", "tasa de rebote",
    "onboarding (tiempo)", "lead time", "churn", "MTTR", "abandono de carrito", "fallas"
]
HIGHER_IS_BETTER = [
    "ventas", "ingresos", "MRR", "ARPU", "conversión", "retención", "NPS",
    "satisfacción", "disponibilidad", "uptime", "throughput", "cobertura de tests",
    "precisión", "recall", "F1", "adopción", "uso activo", "tráfico calificado",
    "éxito de entrega", "productividad", "velocidad de despliegue"
]

# Mapas por rol para elegir métricas plausibles
ROLE_METRICS = {
    "Desarrollador Backend": (["latencia","tiempo de respuesta","MTTR","throughput","disponibilidad"], []),
    "Ingeniero de Software": (["defectos","cobertura de tests","latencia","tiempo de ciclo","productividad"], []),
    "Científico de Datos": (["precisión","F1","tiempo de corrida","adopción"], []),
    "Analista de Datos": (["tiempo de reporte","precisión del forecast","adopción de dashboards"], []),
    "Product Manager": (["conversión","retención","NPS","MRR"], []),
    "Especialista en BI": (["tiempo de reporte","adopción","exactitud de datos"], []),
}
# fallback si no está el rol
DEFAULT_METRICS = ["costos","latencia","conversión","ventas","precisión","defectos"]

GOOD_VERBS = ["Implementé","Optimicé","Automaticé","Estandaricé","Refactoricé","Integré",
              "Desplegué","Instrumenté","Aceleré","Escalé","Migré","Consolidé",
              "Fortalecí","Estabilicé","Lideré","Coordiné","Orquesté","Dirigí",
              "Analicé","Diagnostiqué","Diseñé","Rediseñé","Iteré","Validé","Audité",
              "Aumenté","Reduje","Disminuí","Mejoré"]

def _pick_metric_for_role(titulo):
    pool = ROLE_METRICS.get(titulo, (DEFAULT_METRICS, []))[0]
    return random.choice(pool)

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

def make_bullet_coherent(titulo, positive=True, include_version=False, stack=None):
    verb = random.choice(GOOD_VERBS[:-4])  # evita usar directamente Aumenté/Reduje al inicio
    metric = _pick_metric_for_role(titulo)
    eff = _effect_verb(metric, positive=positive)
    delta = random.randint(8, 45)  # rango razonable
    timeframe = random.choice(["en 3 meses","en 6 meses","en 1 trimestre",""])
    stack_txt = ""
    if include_version and stack:
        stack_txt = f" Usando {', '.join(stack)}."
    core = f"{verb} {random.choice(['el','la'])} {random.choice(['pipeline','proceso','servicio','módulo','estrategia'])} clave, {eff} {metric} en {delta}%"
    if timeframe:
        core += f" {timeframe}"
    return core + "." + stack_txt


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
            bullets.append("- " + make_bullet_coherent(titulo, positive=True, include_version=False))
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
    return [{
        "grado": "Licenciatura",
        "area": random.choice(["Ingeniería en Computación", "Matemáticas", "Informática", "Sistemas"]),
        "institucion": fake.company() + " University",
        "fin": str(grad_year),
        "logros": "Graduación con promedio destacado. Participación en proyectos aplicados."
    }]

def make_education_bad(fake):
    # Campos faltantes / vagos
    return [{
        "grado": random.choice(["Curso", "Diploma", "Licenciatura"]),
        "area": "",
        "institucion": "Escuela X",
        "fin": "",
        "logros": "" if random.random() < 0.6 else "varias cosas"
    }]


EDU_DEGREES = ["Licenciatura", "Ingeniería", "Maestría", "Especialización", "Diplomado"]
EDU_FIELDS_TECH = [
    "Ingeniería en Computación", "Ciencia de Datos", "Sistemas", "Informática",
    "Software", "Ciberseguridad", "Inteligencia Artificial", "Telemática",
    "Tecnologías de la Información", "Matemáticas Aplicadas"
]
EDU_INSTITUTIONS_GENERIC = [
    "Universidad Estatal", "Instituto Tecnológico Metropolitano",
    "Universidad Politécnica", "Centro de Estudios Superiores",
    "Universidad Virtual de Tecnología"
]

CERT_CATALOG = [
    "AWS Certified Cloud Practitioner",
    "AWS Solutions Architect – Associate",
    "Microsoft Azure Fundamentals (AZ-900)",
    "Google Cloud Digital Leader",
    "Google Data Analytics Certificate",
    "TensorFlow Developer Certificate",
    "Scrum Master (PSM I)",
    "dbt Fundamentals",
    "Snowflake SnowPro Core",
    "Databricks Lakehouse Fundamentals"
]

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

# Catálogos neutrales para enriquecer sin sesgo
PROF_LEVELS = ["Básico", "Intermedio", "Avanzado"]

# Para asegurar variedad técnica real (no sesgo demográfico; solo categorías tech)
HARD_CATEGORIES = {
    "lenguajes": {"Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Go", "Rust", "R"},
    "cloud_devops": {"AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform", "Linux", "Git", "CI/CD"},
    "datos_ml": {"SQL", "PostgreSQL", "MySQL", "MongoDB", "Cassandra", "Elasticsearch",
                 "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
                 "PyTorch", "TensorFlow", "Scikit-learn"},
    "bigdata_stream": {"Spark", "Hadoop", "Kafka"},
    "backend_front": {"Django", "FastAPI", "Flask", "Spring Boot", "Node.js", "Express.js",
                      "React", "Angular", "Vue.js", "Next.js"},
    "bi_analytics": {"Power BI", "Tableau", "Looker", "Qlik Sense", "Excel avanzado"}
}

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

def make_skills_good():
    """
    - Garantiza diversidad técnica (categorías) y elimina duplicados.
    - Tamaños razonables y orden estable (legible).
    - Añade 'hard_skills_detailed' (opcional, no rompe compatibilidad).
    """
    # hard: 6–9 con diversidad
    hard_k = random.randint(6, 9)
    hard = _sample_with_category_balance(HARD_SKILLS_POOL, k=hard_k)
    hard = _unique(hard)

    # soft: 5–7 sin duplicados
    soft_k = random.randint(5, 7)
    soft = _unique(random.sample(SOFT_SKILLS_POOL, k=min(soft_k, len(SOFT_SKILLS_POOL))))

    # orden alfabético para legibilidad (no sesga; facilita comparar CVs)
    hard_sorted = sorted(hard)
    soft_sorted = sorted(soft)

    skills = {"hard_skills": hard_sorted, "soft_skills": soft_sorted}

    # enriquecido opcional (útil para features del modelo, pero no obligatorio)
    skills["hard_skills_detailed"] = _build_hard_detailed(hard_sorted)

    return skills


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



# =========================
# Scoring de encaje CV ↔ Vacante (multi-JD)
# =========================

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
    return bool(re.search(r"\b\d{1,3}\s?%|\b\d+\s+(mes|meses|semanas|d[ií]as)\b|\bpp\b", txt))

def _soft_evidence(cv, soft_terms):
    exp_txt = _norm("\n".join(e.get("descripcion","") for e in cv.get("experiencia", [])))
    return [s for s in soft_terms if _contains_phrase(exp_txt, s)]

def score_fit(cv, jd, weights=None, threshold=0.65):
    """
    Calcula encaje CV↔vacante (0–1) y razones.
    Pesos por defecto (suman 1.0):
      keywords 0.35, stack 0.35, exp 0.10, metrics 0.10, soft 0.05, nice_to_have 0.05
    """
    W = weights or {"keywords":0.35,"stack":0.35,"exp":0.10,"metrics":0.10,"soft":0.05,"nice":0.05}
    txt = cv_plain_text(cv)
    pos, neg = [], []

    # 1) Keywords obligatorias
    must = jd.get("must_keywords", [])
    if must:
        k_hits = sum(_contains_phrase(txt, k) for k in must)
        kw_score = k_hits / len(must)
        if k_hits < len(must):
            neg.append({"missing_keywords":[k for k in must if not _contains_phrase(txt,k)]})
        else:
            pos.append({"keywords_match": must})
    else:
        kw_score = 1.0

    # 2) Stack requerido
    req = [s.lower() for s in jd.get("required_stack", [])]
    if req:
        s_hits = _stack_hits(txt, req)
        stack_score = len(s_hits) / len(req)
        if len(s_hits) < len(req):
            neg.append({"missing_stack":[s for s in req if s not in [h.lower() for h in s_hits]]})
        else:
            pos.append({"stack_match": s_hits})
    else:
        stack_score = 1.0

    # 3) Nice-to-have (bono)
    nth = [s.lower() for s in jd.get("nice_to_have", [])]
    nice_score = 0.0
    if nth:
        nice_hits = _stack_hits(txt, nth)
        nice_score = len(nice_hits) / len(nth)
        if nice_hits:
            pos.append({"nice_to_have_hits": nice_hits})

    # 4) Años de experiencia mínimos
    years = _count_years_experience(cv)
    miny = jd.get("min_years_exp", 0)
    exp_score = 1.0 if years >= miny else max(0.0, years / max(0.5, miny))
    if years < miny:
        neg.append({"experience_years": f"{years} < {miny}"})
    else:
        pos.append({"experience_years": f"{years} >= {miny}"})

    # 5) Métricas (impacto)
    m = _has_metrics(cv)
    metrics_score = 1.0 if m else 0.0
    if not m:
        neg.append({"no_metrics": True})
    else:
        pos.append({"metrics_present": True})

    # 6) Soft skills evidenciadas en experiencia
    soft_req = jd.get("soft_required", [])
    soft_score = 1.0
    if soft_req:
        evid = _soft_evidence(cv, soft_req)
        soft_score = min(1.0, len(evid)/len(soft_req)) if soft_req else 1.0
        if evid:
            pos.append({"soft_evidence": evid})

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
        "reasons_pos": pos,
        "reasons_neg": neg
    }


# ----------------------------
# Ensambladores CV
# ----------------------------


# --- Degraders como anti‑reglas (siguen la misma interfaz) ---
def ar_degrade_summary(cv):
    ctx = cv.get("meta", {}).get("ctx", {})
    fake = ctx.get("fake"); titulo = ctx.get("titulo")
    if fake and titulo:
        cv["resumen"] = make_summary_bad(fake)
        return "resumen_debil"

def ar_degrade_education(cv):
    ctx = cv.get("meta", {}).get("ctx", {})
    fake = ctx.get("fake")
    if fake:
        cv["educacion"] = make_education_bad(fake)
        return "educacion_pobre"

def ar_degrade_skills(cv):
    cv["skills"] = make_skills_bad()
    return "skills_debil"

def ar_degrade_experience(cv):
    ctx = cv.get("meta", {}).get("ctx", {})
    fake = ctx.get("fake"); titulo = ctx.get("titulo")
    if fake:
        cv["experiencia"] = make_experience_bad(fake)
        return "experiencia_vaga"

def ar_degrade_contact(cv):
    ctx = cv.get("meta", {}).get("ctx", {})
    fake = ctx.get("fake"); first = ctx.get("first"); last = ctx.get("last")
    if fake and first:
        cv["contacto"] = make_contact_bad(fake, first, last or "")
        return "contacto_poco_profesional"

# Elimina de ANTI_RULE_FUNCS las que descartaste por sesgo previamente.
ANTI_RULE_FUNCS_SAFE = [
    ar_emojis_uppercase_summary,
    ar_instagram_contact,
    ar_links_broken,
    ar_remove_descriptions,
    ar_no_metrics,
    ar_cute_email,
    ar_missing_hard_skills,
    ar_contact_block_huge,
]

EXCLUSIVE_GROUPS = {
    "summary": {ar_degrade_summary, ar_emojis_uppercase_summary},
    "skills": {ar_degrade_skills, ar_missing_hard_skills},
    "experience": {ar_degrade_experience, ar_remove_descriptions, ar_no_metrics},
    "contact": {ar_degrade_contact, ar_contact_block_huge, ar_links_broken},
    "education": {ar_degrade_education},
}
FUNC2GROUP = {f: g for g, fs in EXCLUSIVE_GROUPS.items() for f in fs}

def _apply_rules_with_exclusivity(cv_tmp, funcs):
    used_groups = set()
    applied = []
    for func in funcs:
        group = FUNC2GROUP.get(func)
        if group and group in used_groups:
            continue  # ya degradamos esa sección
        tag = func(cv_tmp)
        if tag:
            applied.append(tag)
            if group:
                used_groups.add(group)
    return applied


# Catálogo unificado (función, peso). Incluye degraders como si fueran anti‑reglas.
BAD_RULE_FUNCS = [
    # Degraders por sección
    (ar_degrade_summary,    0.22),
    (ar_degrade_education,  0.25),
    (ar_degrade_skills,     0.25),
    (ar_degrade_experience, 0.22),
    (ar_degrade_contact,    0.20),
    # Anti‑reglas “clásicas” seguras
    (ar_missing_hard_skills,      0.30),
    (ar_no_metrics,               0.25),
    (ar_remove_descriptions,      0.25),
    (ar_instagram_contact,        0.25),
    (ar_cute_email,               0.25),
    (ar_contact_block_huge,       0.20),
    (ar_links_broken,             0.15),
    (ar_emojis_uppercase_summary, 0.15),
]

def _weighted_sample_rules(rules_with_weights, k):
    # rules_with_weights: [(func, weight), ...]
    selected = []
    pool = list(rules_with_weights)
    for _ in range(min(k, len(pool))):
        weights = [w for _, w in pool]
        idx = random.choices(range(len(pool)), weights=weights, k=1)[0]
        selected.append(pool.pop(idx)[0])  # agrega func y lo saca del pool
    return selected

def generar_cv(fake, bueno=True, locale="es_MX", seed=None, args=None):
    first = fake.first_name()
    last = fake.last_name()
    titulo = random.choice(JOB_TITLES)

    if bueno:
        contacto = make_contact_good(fake, first, last)
        resumen = make_summary_good(fake, titulo)
        experiencia = make_experience_good(fake, titulo)
        educacion = make_education_good(fake)
        skills = make_skills_good()
        reglas_aplicadas = [
            "email_profesional", "linkedin_incluido", "resumen_con_verbos_accion_y_metricas",
            "experiencia_con_logros_cuantificados", "skills_separadas_hard_soft",
            "fechas_consistentes", "headshot_profesional"
        ]
    else:
        # 1) Partimos de un CV "bueno-neutral"
        contacto = make_contact_good(fake, first, last)
        resumen = make_summary_good(fake, titulo)
        experiencia = make_experience_good(fake, titulo)
        educacion = make_education_good(fake)
        skills = make_skills_good()

        cv_tmp = {
            "meta": {
                "ctx": {"fake": fake, "titulo": titulo, "first": first, "last": last}
            },
            "identidad": {"nombre": f"{first} {last}", "titulo": titulo,
                          "ubicacion": fake.city() + ", " + fake.country()},
            "contacto": contacto, "resumen": resumen,
            "experiencia": experiencia, "educacion": educacion, "skills": skills
        }

        # 2) Número total de reglas a aplicar (misma lógica que ya tienes)
        k_total = _choose_k_bad(args or argparse.Namespace(bad_severity="med", bad_min=None, bad_max=None))

        # 3) Selecciona anti‑reglas (incluye degraders) por pesos, sin repetir
        picked_funcs = _weighted_sample_rules(BAD_RULE_FUNCS, k_total)

        # 4) Aplica en orden y registra tags
        reglas_aplicadas = []
        # 4) Aplica en orden con exclusividad y registra tags
        reglas_aplicadas = _apply_rules_with_exclusivity(cv_tmp, picked_funcs)

        # 5) Vuelca de regreso
        contacto = cv_tmp["contacto"]
        resumen = cv_tmp["resumen"]
        experiencia = cv_tmp["experiencia"]
        educacion = cv_tmp["educacion"]
        skills = cv_tmp["skills"]

    estructura = {
        "meta": {
            "label": "exito" if bueno else "fracaso",
            "locale": locale,
            "seed": seed,
            "reglas_aplicadas": reglas_aplicadas
        },
        "identidad": {
            "nombre": f"{first} {last}",
            "titulo": titulo,
            "ubicacion": fake.city() + ", " + fake.country()
        },
        "contacto": contacto,
        "resumen": resumen,
        "experiencia": experiencia,
        "educacion": educacion,
        "skills": skills
    }
    return estructura


def cv_txt_ats(cv):
    """Representación ATS-friendly en texto plano."""
    lines = []
    lines.append(f"{cv['identidad']['nombre']} — {cv['identidad']['titulo']}")
    lines.append(cv['identidad']['ubicacion'])
    c = cv["contacto"]
    lines.append(f"Email: {c.get('email','')}")
    if c.get("linkedin"):
        lines.append(f"LinkedIn: {c['linkedin']}")
    if c.get("web"):
        lines.append(f"Web: {c['web']}")
    lines.append("")

    lines.append("Resumen")
    lines.append("-------")
    lines.append(cv["resumen"])
    lines.append("")

    lines.append("Experiencia")
    lines.append("-----------")
    for exp in cv["experiencia"]:
        lines.append(f"{exp['puesto']} | {exp['empresa']} | {exp['inicio']} — {exp['fin']}")
        if exp["descripcion"]:
            for ln in exp["descripcion"].splitlines():
                lines.append(ln)
        else:
            lines.append("(Sin descripción)")
        lines.append("")
    lines.append("Educación")
    lines.append("---------")
    for ed in cv["educacion"]:
        lines.append(f"{ed['grado']} en {ed['area'] or '(s/d)'} — {ed['institucion']} ({ed['fin'] or 's/f'})")
        if ed["logros"]:
            lines.append(f"- {ed['logros']}")
        lines.append("")
    lines.append("Skills")
    lines.append("------")
    hard = ", ".join(cv["skills"]["hard_skills"]) if cv["skills"]["hard_skills"] else "(vacías)"
    soft = ", ".join(cv["skills"]["soft_skills"]) if cv["skills"]["soft_skills"] else "(vacías)"
    lines.append(f"Hard skills: {hard}")
    lines.append(f"Soft skills: {soft}")
    lines.append("")
    # Encaje con vacantes (si existe)
    if cv["meta"].get("fits"):
        lines.append("Encaje con vacantes")
        lines.append("-------------------")
        top = sorted(cv["meta"]["fits"], key=lambda x: x["fit_score"], reverse=True)[:3]
        for f in top:
            lines.append(f"- {f['jd_name']}: {f['fit_score']:.2f} ({f['fit_label']})")
        lines.append("")
    # Marcas de reglas (útil para depurar dataset)
    lines.append(f"[Label: {cv['meta']['label']}] Reglas: {', '.join(cv['meta']['reglas_aplicadas'])}")
    return "\n".join(lines)

# ----------------------------
# Main CLI
# ----------------------------

def main():
    parser = argparse.ArgumentParser(description="Generador de CVs sintéticos (buenos/malos)")
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--ratio_buenos", type=float, default=0.5)
    parser.add_argument("--locale", type=str, default="es_MX")
    parser.add_argument("--out", type=str, default="./salida")
    parser.add_argument("--seed", type=int, default=42)
    # NUEVO: control de severidad/variedad en CVs malos
    parser.add_argument("--bad_severity", choices=["soft","med","hard"], default="med",
                        help="Cantidad típica de errores en CVs malos (soft 1–2, med 2–4, hard 4–7)")
    parser.add_argument("--bad_min", type=int, default=None, help="Mínimo de errores a inyectar en CVs malos (override)")
    parser.add_argument("--bad_max", type=int, default=None, help="Máximo de errores a inyectar en CVs malos (override)")
    # NUEVO: múltiples vacantes y umbral de encaje
    parser.add_argument("--jd", action="append", default=None,
                        help="Ruta(s) a JSON de vacante; puedes repetir --jd varias veces")
    parser.add_argument("--jd_glob", type=str, default=None,
                        help="Patrón glob para cargar múltiples vacantes, ej: './vacantes/*.json'")
    parser.add_argument("--fit_threshold", type=float, default=0.65,
                        help="Umbral para considerar 'fit' una vacante")

    args = parser.parse_args()

    random.seed(args.seed)
    fake = Faker(args.locale)
    Faker.seed(args.seed)

    ensure_dir(args.out)
    ensure_dir(os.path.join(args.out, "txt"))
    jsonl_path = os.path.join(args.out, "cvs.jsonl")

    # Carga de vacantes (opcional)
    vacantes = load_vacantes(args.jd, args.jd_glob)
    if vacantes:
        print(f"[INFO] Vacantes cargadas: {len(vacantes)}")

    n_buenos = int(round(args.n * args.ratio_buenos))
    n_malos = args.n - n_buenos
    indices = (["exito"] * n_buenos) + (["fracaso"] * n_malos)
    random.shuffle(indices)

    with open(jsonl_path, "w", encoding="utf-8") as fjsonl:
        for i, etiqueta in enumerate(indices, start=1):
            bueno = etiqueta == "exito"
            cv = generar_cv(fake, bueno=bueno, locale=args.locale, seed=args.seed, args=args)

            # Si hay vacantes, calcular encaje por cada una
            if vacantes:
                fits = []
                for jd in vacantes:
                    fit = score_fit(cv, jd, threshold=args.fit_threshold)
                    jd_name = jd.get("name") or jd.get("role_title") or jd.get("_source") or "vacante"
                    fits.append({
                        "jd_name": jd_name,
                        "fit_score": fit["score"],
                        "fit_label": "fit" if fit["label_fit"] else "no_fit",
                        "fit_subscores": fit["subscores"],
                        "fit_reasons_pos": fit["reasons_pos"],
                        "fit_reasons_neg": fit["reasons_neg"]
                    })
                # guarda todos los encajes y el mejor
                cv.setdefault("meta", {})
                cv["meta"]["fits"] = fits
                best = max(fits, key=lambda x: x["fit_score"])
                cv["meta"]["best_fit"] = {
                    "jd_name": best["jd_name"],
                    "fit_score": best["fit_score"],
                    "fit_label": best["fit_label"]
                }

            # Escribe JSONL y TXT
            fjsonl.write(json.dumps(cv, ensure_ascii=False) + "\n")
            txt = cv_txt_ats(cv)
            fname = f"{i:04d}_{etiqueta}.txt"
            with open(os.path.join(args.out, "txt", fname), "w", encoding="utf-8") as ft:
                ft.write(txt)

    print("==== RESUMEN DE GENERACIÓN ====")
    print(f"Total: {args.n}")
    print(f"Buenos (éxito): {n_buenos}")
    print(f"Malos (fracaso): {n_malos}")
    print(f"Locale: {args.locale}")
    print(f"Severidad malos: {args.bad_severity} (min={args.bad_min} max={args.bad_max})")
    if vacantes:
        print(f"Vacantes evaluadas: {len(vacantes)} (umbral fit={args.fit_threshold})")
    print(f"Salida JSONL: {jsonl_path}")
    print(f"TXT: {os.path.join(args.out, 'txt')}")


if __name__ == "__main__":
    main()
