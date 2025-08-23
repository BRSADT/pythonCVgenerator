ACCION_VERBS_ES = [
    "Lideré", "Diseñé", "Implementé", "Optimicé", "Automaticé", "Coordiné",
    "Mejoré", "Desarrollé", "Analicé", "Iteré", "Escalé", "Consolidé",
    "Reduje", "Aumenté", "Orquesté", "Integré", "Planifiqué", "Ejecuté",
    "Supervisé", "Capacité", "Gestioné", "Dirigí", "Evalué", "Monitoreé",
    "Fortalecí", "Modernicé", "Estandaricé", "Simplifiqué", "Agilicé",
    "Audité", "Reestructuré", "Validé", "Refactoricé", "Migré", "Impulsé",
    "Negocié", "Colaboré", "Documenté", "Implementé mejoras", "Estabilicé"
]

GOOD_VERBS = ["Implementé","Optimicé","Automaticé","Estandaricé","Refactoricé","Integré",
              "Desplegué","Instrumenté","Aceleré","Escalé","Migré","Consolidé",
              "Fortalecí","Estabilicé","Lideré","Coordiné","Orquesté","Dirigí",
              "Analicé","Diagnostiqué","Diseñé","Rediseñé","Iteré","Validé","Audité",
              "Aumenté","Reduje","Disminuí","Mejoré"]

# === Canonicalización de términos técnicos / aliases ===
STACK_ALIASES = {
    "py": "python", "python3": "python",
    "js": "javascript", "react.js": "react", "node": "node.js",
    "ts": "typescript",
    "postgres": "postgresql", "postgre": "postgresql",
    "gcp": "google cloud", "aws": "amazon web services",
    "azure devops": "azure",
    "ml": "machine learning", "dl": "deep learning",
    "nlp": "procesamiento del lenguaje natural",
    "cv": "computer vision",
    "tf": "tensorflow", "torch": "pytorch",
    "db": "database", "sql server": "mssql",
}

# === HARD_SKILLS_POOL (REEMPLAZA) ===
HARD_SKILLS_POOL = [
    # Lenguajes
    "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Go", "Rust", "R",

    # Backend / Web
    "APIs REST", "GraphQL", "Microservicios",
    "FastAPI", "Flask", "Django", "Spring Boot", "Node.js", "Express.js",
    "gRPC", "OpenAPI", "JWT",

    # Frontend
    "HTML", "CSS", "React", "Angular", "Vue.js", "Next.js", "Redux", "Tailwind", "Webpack",

    # Datos / BI / Analytics
    "SQL", "PostgreSQL", "MySQL", "SQL Server", "MongoDB", "Cassandra", "Redis", "Elasticsearch",
    "Power BI", "Tableau", "Looker", "Excel avanzado", "ETL", "Modelado de datos", "KPIs",

    # Big Data / Streaming
    "Spark", "Hadoop", "Kafka", "RabbitMQ",

    # Cloud / DevOps / Infra
    "Linux", "Docker", "Kubernetes", "Helm", "Terraform", "Ansible",
    "CI/CD", "Git", "GitHub Actions", "GitLab CI",
    "Amazon Web Services", "Google Cloud", "Azure",

    # Observabilidad / SRE
    "Prometheus", "Grafana", "Loki", "ELK",

    # QA / Testing
    "Selenium", "Cypress", "Playwright", "JUnit", "PyTest", "Postman", "Contract testing", "TDD", "BDD", "Coverage",

    # Ciencia de datos / IA
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "PyTorch", "TensorFlow", "Scikit-learn",

    # Otros
    "Seguridad en la nube", "OWASP"
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
    # Backend
    "Desarrollador Backend", "Backend Engineer",

    # Frontend
    "Desarrollador Frontend", "Frontend Developer",

    # Datos / BI
    "Analista de Datos", "Data Analyst",
    "Ingeniero de Datos", "Data Engineer",
    "Especialista en BI",

    # QA / Testing
    "QA Engineer", "QA Automation Engineer", "Tester de Software",

    # DevOps / SRE / Cloud
    "Ingeniero DevOps", "Site Reliability Engineer (SRE)", "Cloud Engineer",

    # Software general / ML
    "Ingeniero de Software", "Científico de Datos", "Ingeniero de Machine Learning"
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


# ----------------------------
# Generadores de componentes
# ----------------------------


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
# === ROLE_METRICS (REEMPLAZA) ===
ROLE_METRICS = {
    # Backend
    "Desarrollador Backend": (["latencia","tiempo de respuesta","MTTR","throughput","disponibilidad"], []),
    "Backend Engineer":      (["latencia","tiempo de respuesta","MTTR","throughput","disponibilidad"], []),

    # Frontend
    "Desarrollador Frontend": (["LCP","CLS","FID","tiempo de carga","conversion en UI"], []),
    "Frontend Developer":     (["LCP","CLS","FID","tiempo de carga","conversion en UI"], []),

    # Datos / BI
    "Analista de Datos": (["tiempo de reporte","adopción de dashboards","exactitud de datos"], []),
    "Data Analyst":      (["tiempo de reporte","adopción de dashboards","exactitud de datos"], []),
    "Ingeniero de Datos":(["freshness de datos","SLA de pipelines","costos de cómputo"], []),
    "Data Engineer":     (["freshness de datos","SLA de pipelines","costos de cómputo"], []),
    "Especialista en BI":(["tiempo de reporte","adopción","exactitud de datos"], []),

    # QA / Testing
    "QA Engineer":            (["defectos","cobertura de tests","tiempo de ciclo","tasa de regresión"], []),
    "QA Automation Engineer": (["defectos","cobertura de tests","tiempo de ciclo","tasa de regresión"], []),
    "Tester de Software":     (["defectos","cobertura de tests","tiempo de ciclo","tasa de regresión"], []),

    # DevOps / SRE / Cloud
    "Ingeniero DevOps":              (["tiempo de despliegue","frecuencia de releases","tasa de fallos"], []),
    "Site Reliability Engineer (SRE)":(["SLO","SLA","MTTR","uptime"], []),
    "Cloud Engineer":                 (["costos","disponibilidad","tiempo de aprovisionamiento"], []),

    # Software general / ML
    "Ingeniero de Software":     (["defectos","cobertura de tests","tiempo de ciclo","productividad"], []),
    "Científico de Datos":       (["precisión","F1","tiempo de corrida","adopción"], []),
    "Ingeniero de Machine Learning": (["latencia de inferencia","throughput de modelos","drift"], []),
}
# fallback si no está el rol
DEFAULT_METRICS = ["costos","latencia","conversión","ventas","precisión","defectos"]

# fallback si no está el rol
DEFAULT_METRICS = ["costos","latencia","conversión","ventas","precisión","defectos"]




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


# --- Helpers para degradar skills sin sesgo demográfico ---
BASIC_OFFICE_SKILLS = ["Word", "PowerPoint", "Correo electrónico", "Office", "Navegación web"]
OUT_OF_FOCUS_HARD = ["HTML", "CSS"]  # superficiales fuera de foco para roles de datos/ML/backend

# --- NUEVO: arquetipos por rol base ---
ROLE_SYNONYMS = {
    "Backend":        ["backend engineer","desarrollador backend","backend developer"],
    "Frontend":       ["frontend developer","desarrollador frontend","ui developer"],
    "Data Analyst":   ["analista de datos","data analyst"],
    "Data Engineer":  ["ingeniero de datos","data engineer"],
    "QA":             ["qa","tester","quality assurance","qa engineer","qa automation"],
    "DevOps/SRE":     ["devops","site reliability engineer","sre","platform engineer"],
    "BI":             ["especialista en bi","bi analyst","business intelligence"],
    "Software":       ["ingeniero de software","software engineer"],
    "ML":             ["ingeniero de machine learning","ml engineer","mlops"],
    "data_scientist": ["cientifico de datos", "data scientist", "ml scientist", "investigador de datos"],
    "data_analyst": ["analista de datos", "data analyst", "analista datos", "bi analyst"],
    "data_engineer": ["ingeniero de datos", "data engineer"],
    "backend": ["backend", "back-end", "desarrollador backend", "backend engineer", "backend developer",
                "ingeniero de software backend"],
    "frontend": ["frontend", "front-end", "desarrollador frontend", "ui developer"],
    "devops": ["devops", "sre", "site reliability", "site reliability engineer", "platform engineer"],
}

ROLE_STACKS = {
    "Backend": [
        "APIs REST","Microservicios","GraphQL","JWT",
        "Python","FastAPI","Flask","Django",
        "Java","Spring Boot",
        "Node.js","Express.js",
        "PostgreSQL","MySQL","SQL Server","MongoDB","Redis","Elasticsearch",
        "Docker","Kubernetes","CI/CD",
        "Kafka","RabbitMQ","gRPC","OpenAPI","Git","Linux"
    ],
    "Frontend": [
        "JavaScript","TypeScript","HTML","CSS",
        "React","Next.js","Angular","Vue.js","Redux","Tailwind","Webpack",
        "REST","GraphQL","Axios","Cypress","Playwright","Jest","Figma","A11y","Git"
    ],
    "Data Analyst": [
        "SQL","Excel avanzado","Power BI","Tableau","Looker",
        "ETL","Modelado de datos","KPIs","AB testing","Storytelling de datos",
        "Python","Scikit-learn","pandas","seaborn","Git"
    ],
    "Data Engineer": [
        "Python","Spark","Airflow","ETL","Data Lake","Lakehouse",
        "Databricks","Kafka","Snowflake","BigQuery","Redshift",
        "DBT","Parquet","Delta Lake","S3","GCS","CI/CD","Terraform","Git"
    ],
    "QA": [
        "E2E","Testing automatizado","Selenium","Cypress","Playwright",
        "JUnit","PyTest","Postman","Contract testing","TDD","BDD",
        "CI/CD","Coverage","Git","Linux","Docker"
    ],
    "DevOps/SRE": [
        "Linux","Bash","Docker","Kubernetes","Helm","Terraform","Ansible",
        "Prometheus","Grafana","Loki","ELK",
        "CI/CD","GitHub Actions","GitLab CI",
        "SLO","SLA","On-call","Autoscaling","CDN","Observabilidad","Git"
    ],
    "BI": [
        "Power BI","Tableau","Looker","SQL","Excel avanzado",
        "ETL","Modelado de datos","KPIs","Git"
    ],
    "Software": [
        "Python","Java","C#","C++","JavaScript","TypeScript",
        "APIs REST","SQL","Docker","Git","CI/CD","Linux","Testing automatizado"
    ],
    "ML": [
        "Python","Scikit-learn","PyTorch","TensorFlow",
        "MLOps","CI/CD","Docker","Kubernetes","MLflow","Feature Store"
    ]
}

ROLE_KEYWORDS = {
    "Backend":      ["backend","microservicios","api","rest","endpoints"],
    "Frontend":     ["frontend","ui","ux","componentes","responsive"],
    "Data Analyst": ["analista de datos","dashboard","kpi","etl","modelado de datos"],
    "Data Engineer":["data pipeline","etl","orquestación","ingesta","batch","streaming"],
    "QA":           ["calidad","automatización de pruebas","regresión","e2e","cobertura"],
    "DevOps/SRE":   ["devops","observabilidad","infraestructura","resiliencia","slo","on-call"],
    "BI":           ["business intelligence","dashboard","kpi","etl"],
    "Software":     ["ingeniería de software","arquitectura","patrones de diseño"],
    "ML":           ["machine learning","mlops","modelo","inferencias"]
}


# Patrones de bullets con métrica (usa {tech} / {impact} placeholders)
ROLE_BULLETS = {
    "Backend": [
        "Diseñé endpoints REST para microservicios con {tech}; reduje latencia {impact}.",
        "Implementé {tech} y caché en {tech} mejorando throughput {impact}.",
    ],
    "Frontend": [
        "Migre UI a {tech} con SSR; mejoré LCP/FID {impact}.",
        "Construí diseño responsive con {tech}; reduje CLS {impact}.",
    ],
    "Data Analyst": [
        "Modelé KPIs y dashboard en {tech}; habilité decisiones con ahorro {impact}.",
        "Optimicé queries {tech}; reduje TTI de reportes {impact}.",
    ],
    "Data Engineer": [
        "Orquesté pipelines ETL en {tech}; bajé costos/SLAs {impact}.",
        "Implementé ingesta streaming con {tech}; mejoré frescura {impact}.",
    ],
    "QA": [
        "Automatizé pruebas E2E con {tech}; elevé cobertura {impact}.",
        "Implementé contract testing con {tech}; reduje defectos post-release {impact}.",
    ],
    "DevOps/SRE": [
        "Containericé servicios con {tech}; mejoré despliegues {impact}.",
        "Observabilidad con {tech}; bajé MTTR {impact}.",
    ],
}

# Alias útiles para el scorer (normalización)
STACK_ALIASES = {
    "k8s": "kubernetes",
    "restful": "apis rest",
    "rest api": "apis rest",
    "postgres": "postgresql",
    "js": "javascript",
    "gh actions": "github actions",
    "gcp": "google cloud",
    "ms sql": "sql server",
}
# --- Canonicalización de roles y presets de skills por rol ---
ROLE_SYNONYMS = {
    "backend": [
        "backend", "back-end", "desarrollador backend", "ingeniero backend",
        "ingeniero de software backend"
    ],
    "data_analyst": [
        "analista de datos", "data analyst", "analista datos"
    ],
    "frontend": [
        "frontend", "front-end", "desarrollador frontend", "ui developer"
    ],
    "qa": [
        "qa", "tester", "qa engineer", "qa automation", "quality assurance"
    ],
    "devops": [
        "devops", "sre", "site reliability", "platform engineer"
    ],
}

def _canon_role(title: str) -> str:
    t = (title or "").lower()
    # quita acentos simples
    import unicodedata
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    for canon, words in ROLE_SYNONYMS.items():
        if any(w in t for w in words):
            return canon
    return ""  # desconocido

# Presets: 'core' (=debe cubrirse), 'plus' (=relleno relevante), 'avoid' (=ruido para ese rol)
ROLE_SKILLS_PRESETS = {
    "backend": {
        "core": ["Python", "APIs REST", "SQL", "Git"],  # 3–4 caerán sí o sí
        "plus": ["FastAPI", "Flask", "Django", "PostgreSQL", "MySQL",
                 "Docker", "CI/CD", "Linux", "Kafka", "Microservicios", "Elasticsearch"],
        "avoid": ["Power BI", "Tableau", "Qlik Sense", "Excel avanzado", "React", "Angular", "Vue.js"]
    },
    "data_analyst": {
        "core": ["SQL", "Excel avanzado"],
        "plus": ["Power BI", "Tableau", "Looker", "Qlik Sense", "Python", "Scikit-learn"],
        "avoid": ["Kubernetes", "Terraform", "Spring Boot", "Node.js", "React", "Kafka"]
    },
    "frontend": {
        "core": ["JavaScript", "React"],  # puedes alternar por Angular/Vue en gen si quieres variedad
        "plus": ["TypeScript", "Next.js", "Node.js", "APIs REST", "Git", "CI/CD"],
        "avoid": ["Power BI", "Tableau", "Qlik Sense", "Excel avanzado", "Hadoop", "Spark"]
    },
    "qa": {
        "core": ["Selenium", "Postman", "PyTest"],
        "plus": ["JUnit", "CI/CD", "Git", "Linux", "Docker"],
        "avoid": ["Power BI", "Tableau", "React", "Angular", "Hadoop", "Spark"]
    },
    "devops": {
        "core": ["Linux", "Docker", "Kubernetes", "CI/CD"],
        "plus": ["AWS", "GCP", "Azure", "Terraform", "Git"],
        "avoid": ["Power BI", "Tableau", "Qlik Sense", "Excel avanzado", "React", "Angular"]
    },
    "data_scientist": {
        "core": ["Python", "Scikit-learn", "Pandas", "NumPy", "Machine Learning"],
        "plus": ["PyTorch", "TensorFlow", "NLP", "Computer Vision", "SQL", "Jupyter", "AB testing",
                 "Modelado estadístico", "Feature engineering", "MLOps", "MLflow"]
    },

    "data_engineer": {
        "core": ["Python", "Spark", "Airflow"],
        "plus": ["Kafka", "ETL", "Data Lake", "Lakehouse", "Databricks", "DBT", "Snowflake", "BigQuery", "Redshift",
                 "S3", "GCS"]
    },
}

HARD_CATEGORIES.update({
    "qa_testing": {"Selenium","Cypress","Playwright","JUnit","PyTest","Postman","Contract testing","TDD","BDD","Coverage"},
    "frontend_ui": {"HTML","CSS","React","Angular","Vue.js","Next.js","Redux","Tailwind","Webpack"}
})

ROLE_SUMMARY_KEYWORDS = {
    "data_scientist": ["modelos de machine learning", "validación y experimentación", "pipeline de datos y feature store"],
    "data_analyst": ["dashboards ejecutivos", "modelado de KPIs", "automatización de reportes"],
    "data_engineer": ["orquestación de pipelines", "ingesta batch/streaming", "data lake/lakehouse"],
    "backend": ["microservicios y APIs REST", "cachés y colas de mensajes", "observabilidad y performance"],
    "frontend": ["componentes reutilizables", "SSR/ISR", "accesibilidad (A11y)"],
    "devops": ["infraestructura como código", "observabilidad end-to-end", "SLO/SLA y on-call"]
}

HARD_SKILLS_POOL += [
    "Pandas", "NumPy", "Jupyter", "MLflow",
    "Airflow", "DBT", "Snowflake", "BigQuery", "Redshift",
    "Databricks", "PySpark"
]

STACK_ALIASES.update({
    "sklearn": "scikit-learn",
    "numpy": "numpy",           # normalizado
    "pyspark": "spark",
    "ml flow": "mlflow",
    "ab testing": "ab testing",
    "looker studio": "looker",
})