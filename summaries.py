# summaries.py
import random
from typing import Optional
from typing import Dict, Callable, Optional, List, Tuple

# ---- Dependencias que YA tienes en tu proyecto ----
# from catalogs import ROLE_KEYWORDS, ROLE_STACKS
# from gen import infer_base_role, _pick_metric_for_role, _effect_verb

# --- NUEVO: sinónimos y frases a evitar/variar ---
_AVOID_PHRASES = {
    "buenas prácticas y diseño simple": [
        "patrones claros y código legible",
        "simplicidad y mantenibilidad",
        "calidad de software y claridad técnica",
        "arquitecturas limpias y DX sólida"
    ],
    "orientado/a a": ["enfocado/a en", "con foco en", "con énfasis en", "centrado/a en"],
}

def _degen(s: str) -> str:
    """Reescribe clichés con sinónimos para evitar plantillas repetidas."""
    for base, alts in _AVOID_PHRASES.items():
        if base in s:
            s = s.replace(base, random.choice(alts))
    # reemplaza conectores que suenan igual siempre
    s = s.replace("Me motiva", random.choice(["Me entusiasma", "Me mueve", "Me interesa"]))
    s = s.replace("Se caracteriza por", random.choice(["Destaca por", "Suele mostrar", "Sobresale por"]))
    return s

def _cap(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s

def _weighted_pick(d: dict) -> str:
    r, acc = random.random(), 0.0
    for k, w in d.items():
        acc += w
        if r <= acc: return k
    return next(iter(d))  # fallback

def _assemble(frases, length: str, min_sentences: int) -> str:
    frases = [f for f in frases if f]
    if not frases: return ""
    # asegura mínimo
    if len(frases) < min_sentences:
        # intenta duplicar con variantes suaves
        while len(frases) < min_sentences:
            frases.append(random.choice(frases))
    if length == "short":
        out = " ".join(frases[:max(1, min_sentences)])
    elif length == "medium":
        out = " ".join(frases[:max(2, min_sentences)])
    else:
        out = " ".join(frases)
    return _degen(out).strip().rstrip(".") + "."

class SummaryGenerator:
    DEFAULT_FAMILY_WEIGHTS = {
        "perfil_personal":           0.14,
        "tecnico_especialista":      0.11,
        "liderazgo_entrega":         0.09,
        "producto_valor":            0.08,
        "investigacion_aprendiz":    0.06,
        "data_driven":               0.10,  # sube para tener más métricas en parte del mix
        "customer_centric":          0.06,
        "consultoria_freelance":     0.05,
        "remoto_distribuido":        0.05,
        "startup_scale":             0.06,
        "compliance_seguridad":      0.05,
        "craft_calidad":             0.07,
        "community_mentoria":        0.04,
        "operacion_procesos":        0.08,  # también con posibles métricas cualitativas
        "internacional_multilingue": 0.06,
    }
    DEFAULT_LENGTH_WEIGHTS = {"short": 0.10, "medium": 0.10, "long": 0.80}  # más medianos y largos
    DEFAULT_PERSONA_WEIGHTS = {"primera": 0.65, "tercera": 0.35}

    def __init__(
        self,
        family_weights=None,
        length_weights=None,
        persona_weights=None,
        global_metrics_prob: float = 0.30,      # antes 0.18 – reintroducimos métricas
        metrics_ratio_by_family: dict | None = None,
        min_sentences: int = 2,                 # asegura que “short” no sea una sola línea plana
        role_keywords=None, role_stacks=None,
        infer_base_role_fn=None, pick_metric_fn=None, effect_verb_fn=None,
    ):
        self.family_weights = family_weights or self.DEFAULT_FAMILY_WEIGHTS
        self.length_weights = length_weights or self.DEFAULT_LENGTH_WEIGHTS
        self.persona_weights = persona_weights or self.DEFAULT_PERSONA_WEIGHTS
        self.global_metrics_prob = global_metrics_prob
        self.metrics_ratio_by_family = metrics_ratio_by_family or {
            "data_driven": 0.55,
            "operacion_procesos": 0.40,
            "liderazgo_entrega": 0.30,
            "producto_valor": 0.25,
        }
        self.min_sentences = min_sentences

        self.ROLE_KEYWORDS = role_keywords or {}
        self.ROLE_STACKS = role_stacks or {}
        self.infer_base_role = infer_base_role_fn or (lambda t: "")
        self._pick_metric_for_role = pick_metric_fn or (lambda t: "rendimiento")
        self._effect_verb = effect_verb_fn or (lambda m, pos=True: "mejoré")

        self.families = {
            "perfil_personal":           self._f_perfil_personal,
            "tecnico_especialista":      self._f_tecnico_especialista,
            "liderazgo_entrega":         self._f_liderazgo_entrega,
            "producto_valor":            self._f_producto_valor,
            "investigacion_aprendiz":    self._f_investigacion_aprendiz,
            "data_driven":               self._f_data_driven,
            "customer_centric":          self._f_customer_centric,
            "consultoria_freelance":     self._f_consultoria_freelance,
            "remoto_distribuido":        self._f_remoto_distribuido,
            "startup_scale":             self._f_startup_scale,
            "compliance_seguridad":      self._f_compliance_seguridad,
            "craft_calidad":             self._f_craft_calidad,
            "community_mentoria":        self._f_community_mentoria,
            "operacion_procesos":        self._f_operacion_procesos,
            "internacional_multilingue": self._f_internacional_multilingue,
        }

    def generate(self, titulo: str, force_family: str = None, force_len: str = None, force_persona: str = None) -> str:
        family  = force_family  or _weighted_pick(self.family_weights)
        length  = force_len     or _weighted_pick(self.length_weights)
        persona = force_persona or _weighted_pick(self.persona_weights)
        fn = self.families.get(family, self._f_perfil_personal)
        return fn(titulo, length, persona, family)

    # ---------- utilidades ----------
    def _role_condiments(self, titulo: str):
        base = self.infer_base_role(titulo)
        kws  = list(self.ROLE_KEYWORDS.get(base, [])) if base else []
        tech = list(self.ROLE_STACKS.get(base, []))   if base else []
        return (", ".join(kws[:2]) if kws else ""), (", ".join(tech[:2]) if tech else "")

    def _maybe_metric_sentence(self, titulo: str, family: str) -> str:
        # mezcla prob. global con refuerzo por familia
        p = self.global_metrics_prob
        if family in self.metrics_ratio_by_family:
            # combina suavemente (no 100% para evitar monotonía)
            p = 1 - (1 - p) * (1 - self.metrics_ratio_by_family[family])
        if random.random() > p:
            return ""
        metric = self._pick_metric_for_role(titulo)
        eff = self._effect_verb(metric, positive=True)
        delta = random.randint(8, 45)
        timeframe = random.choice(["en 3 meses", "en 6 meses", "en 1 trimestre"])
        # aparte de %, permite antes→después ocasional
        if random.random() < 0.35:
            before = f"{random.randint(6,18)} h"
            after = f"{random.randint(1,5)} h"
            return f" {eff} tiempos de {metric} de {before} a {after}."
        return f" {eff} {metric} en {delta}% {timeframe}."

    # ---------- familias (actualizadas para usar min_sentences y métricas por familia) ----------
    def _f_perfil_personal(self, titulo, length, persona, family):
        kw, tech = self._role_condiments(titulo)
        foco = kw or random.choice([
            "patrones claros y código legible",
            "simplicidad y mantenibilidad",
            "arquitecturas limpias y APIs consistentes",
            "documentación útil y colaboración"
        ])
        valores = ", ".join(random.sample([
            "calidad", "claridad", "colaboración",
            "aprendizaje continuo", "observabilidad", "autonomía", "responsabilidad"
        ], k=3))
        if persona == "primera":
            frases = [
                f"Soy {titulo.lower()} {random.choice(['práctico/a','con criterio técnico','orientado/a al valor'])}, {random.choice(_AVOID_PHRASES['orientado/a a'])} {foco}.",
                f"Disfruto {random.choice(['resolver problemas reales','mejorar la DX','alinear técnica y producto'])}.",
                f"Cuido {valores}." + (f" Experiencia con {tech}." if tech and random.random()<0.5 else "")
            ]
        else:
            frases = [
                f"{_cap(titulo)} con foco en {foco}.",
                f"{random.choice(['Destaca por','Sobresale por'])} {random.choice(['pensamiento claro','colaboración','comunicación abierta'])}.",
                f"Atención a {valores}." + (f" Familiaridad con {tech}." if tech and random.random()<0.5 else "")
            ]
        return _assemble(frases, length, self.min_sentences)

    def _f_tecnico_especialista(self, titulo, length, persona, family):
        kw, tech = self._role_condiments(titulo)
        foco = kw or random.choice(["arquitecturas limpias", "APIs claras", "pruebas y CI/CD"])
        frases = [
            (f"Como {titulo.lower()}, trabajo en {foco}." if persona=="primera" else f"{_cap(titulo)} con enfoque en {foco}."),
            f"{'Exploro' if persona=='primera' else 'Explora'} patrones, pruebas y automatización para mantenibilidad.",
            (f"{'Suelo usar' if persona=='primera' else 'Stack habitual'}: {tech}." if tech and random.random()<0.6 else "")
        ]
        return _assemble(frases, length, self.min_sentences) + self._maybe_metric_sentence(titulo, family)

    def _f_liderazgo_entrega(self, titulo, length, persona, family):
        frases = [
            f"{_cap('lidero' if persona=='primera' else 'Lidera')} entregas iterativas con foco en valor y calidad.",
            f"{'Alineo' if persona=='primera' else 'Alinea'} objetivos con Producto y Datos.",
            f"{'Impulso' if persona=='primera' else 'Impulsa'} revisión entre pares y documentación."
        ]
        return _assemble(frases, length, self.min_sentences) + self._maybe_metric_sentence(titulo, family)

    def _f_producto_valor(self, titulo, length, persona, family):
        kw, tech = self._role_condiments(titulo)
        foco = random.choice(["impacto en usuario", "time‑to‑value", "casos de uso claros"])
        frases = [
            f"{_cap('me interesa' if persona=='primera' else 'Le interesa')} conectar decisiones técnicas con {foco}.",
            "Priorización guiada por objetivos y feedback continuo.",
            (f"Stack frecuente: {tech}." if tech and random.random()<0.5 else "")
        ]
        return _assemble(frases, length, self.min_sentences) + self._maybe_metric_sentence(titulo, family)

    def _f_investigacion_aprendiz(self, titulo, length, persona, family):
        temas = random.sample(["PLN", "sistemas distribuidos", "observabilidad", "data quality", "ML aplicado"], k=3)
        frases = [
            f"Aprendizaje continuo en {', '.join(temas)}.",
            "Experimentación, medición y documentación de hallazgos."
        ]
        return _assemble(frases, length, self.min_sentences)

    def _f_data_driven(self, titulo, length, persona, family):
        kw, tech = self._role_condiments(titulo)
        frases = [
            f"{_cap('tomo' if persona=='primera' else 'Toma')} decisiones basadas en métricas y telemetría.",
            "Definición de tableros útiles y alertas accionables.",
            (f"Herramientas: {tech}." if tech and random.random()<0.5 else "")
        ]
        return _assemble(frases, length, self.min_sentences) + self._maybe_metric_sentence(titulo, family)

    def _f_customer_centric(self, titulo, length, persona, family):
        frases = [
            f"{_cap('empatizo' if persona=='primera' else 'Empatiza')} con el usuario final para priorizar mejoras.",
            "Reducción de fricción y elevación de la experiencia.",
            "Comunicación clara con stakeholders."
        ]
        return _assemble(frases, length, self.min_sentences)

    def _f_consultoria_freelance(self, titulo, length, persona, family):
        kw, tech = self._role_condiments(titulo)
        frases = [
            "Experiencia en contextos cambiantes y alcance ambiguo.",
            "Traducción de requerimientos en soluciones concretas.",
            (f"Proyectos recientes con {tech}." if tech and random.random()<0.5 else "")
        ]
        return _assemble(frases, length, self.min_sentences)

    def _f_remoto_distribuido(self, titulo, length, persona, family):
        frases = [
            "Trabajo fluido en equipos remotos y zonas horarias distintas.",
            "Disciplina en comunicación asincrónica y documentación."
        ]
        return _assemble(frases, length, self.min_sentences)

    def _f_startup_scale(self, titulo, length, persona, family):
        kw, tech = self._role_condiments(titulo)
        frases = [
            "Ritmo startup: iteración rápida con criterio de calidad.",
            "Equilibrio entre deuda técnica y velocidad de entrega.",
            (f"Stack: {tech}." if tech and random.random()<0.5 else "")
        ]
        return _assemble(frases, length, self.min_sentences)

    def _f_compliance_seguridad(self, titulo, length, persona, family):
        frases = [
            "Atención a seguridad, privacidad y cumplimiento.",
            "Automatización de controles y trazabilidad."
        ]
        return _assemble(frases, length, self.min_sentences)

    def _f_craft_calidad(self, titulo, length, persona, family):
        kw, tech = self._role_condiments(titulo)
        frases = [
            "Cuidado por legibilidad, pruebas y patrones claros.",
            "Prefiero decisiones simples frente a complejidad innecesaria.",
            (f"Entorno habitual: {tech}." if tech and random.random()<0.5 else "")
        ]
        return _assemble(frases, length, self.min_sentences)

    def _f_community_mentoria(self, titulo, length, persona, family):
        frases = [
            "Promuevo intercambio de conocimiento y mentoría.",
            "Uso ejemplos y documentación para alinear equipos."
        ]
        return _assemble(frases, length, self.min_sentences)

    def _f_operacion_procesos(self, titulo, length, persona, family):
        kw, tech = self._role_condiments(titulo)
        frases = [
            "Mejoras en SLIs/SLOs y postmortems accionables.",
            "Prevención antes que corrección.",
            (f"Tooling: {tech}." if tech and random.random()<0.5 else "")
        ]
        return _assemble(frases, length, self.min_sentences) + self._maybe_metric_sentence(titulo, family)

    def _f_internacional_multilingue(self, titulo, length, persona, family):
        idiomas = random.sample(["español", "inglés", "francés", "portugués"], k=2)
        frases = [
            f"Contexto multicultural; comunicación en {', '.join(idiomas)}.",
            "Adaptabilidad y sensibilidad intercultural."
        ]
        return _assemble(frases, length, self.min_sentences)

    # ---------- NUEVO: generación por lotes con cobertura y control de repetición ----------
    def generate_batch(self, titulo: str, n: int = 50, max_dupes: int = 2) -> list[str]:
        families = list(self.families.keys())
        # objetivo: cubrir familias y longitudes de forma estratificada
        lengths = ["short","medium","long"]
        out, seen = [], {}
        for i in range(n):
            fam = random.choice(families)
            ln = _weighted_pick(self.length_weights)
            per = _weighted_pick(self.persona_weights)
            s = self.families[fam](titulo, ln, per, fam)
            # control de duplicados (misma cadena exacta)
            k = (s,)
            seen[k] = seen.get(k, 0) + 1
            if seen[k] > max_dupes:
                # intenta otra familia
                fam2 = random.choice([f for f in families if f != fam])
                s = self.families[fam2](titulo, ln, per, fam2)
            out.append(s)
        return out
