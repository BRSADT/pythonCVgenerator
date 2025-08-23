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



import os


import argparse
import random
from faker import Faker


import json, os, random
from faker import Faker
from gen import (make_contact_good, make_summary_good, make_experience_good,
                 make_education_good, make_skills_good,_choose_k_bad)
from catalogs import JOB_TITLES
from rules import weighted_sample_rules
from fit import score_fit,load_vacantes
from rules import weighted_sample_rules, apply_rules_with_exclusivity, RULES

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)





def generar_cv(fake, bueno=True, locale="es_MX", seed=None, args=None):
    first = fake.first_name()
    last = fake.last_name()
    titulo = random.choice(JOB_TITLES)

    if bueno:
        contacto = make_contact_good(fake, first, last)
        resumen = make_summary_good(fake, titulo)
        experiencia = make_experience_good(fake, titulo)
        educacion = make_education_good(fake)
        skills = make_skills_good(titulo)
        reglas_aplicadas = [
            "email_profesional", "linkedin_incluido",
            "resumen_bien_escrito",  # << en vez de “..._metricas”
            "experiencia_con_logros_varios",  # ya mezclas bullets con/sin métricas
            "skills_separadas_hard_soft",
            "fechas_consistentes", "headshot_profesional"
        ]
    else:
        # 1) Partimos de un CV "bueno-neutral"
        contacto = make_contact_good(fake, first, last)
        resumen = make_summary_good(fake, titulo)
        experiencia = make_experience_good(fake, titulo)
        educacion = make_education_good(fake)
        skills = make_skills_good(titulo)

        cv_tmp = {
            "meta": {
                "ctx": {"fake": fake, "titulo": titulo, "first": first, "last": last}
            },
            "identidad": {"nombre": f"{first} {last}", "titulo": titulo,
                          "ubicacion": fake.city() + ", " + fake.country()},
            "contacto": contacto, "resumen": resumen,
            "experiencia": experiencia, "educacion": educacion, "skills": skills
        }

        k_total = _choose_k_bad(args or argparse.Namespace(bad_severity="med", bad_min=None, bad_max=None))
        picked_rules = weighted_sample_rules(k_total)
        reglas_aplicadas = apply_rules_with_exclusivity(cv_tmp, [r.func for r in picked_rules])

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
