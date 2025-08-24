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
                 make_education_good, make_skills_good,_choose_k_bad,make_location)
from catalogs import JOB_TITLES
from rules import weighted_sample_rules
from fit import score_fit,load_vacantes
from rules import weighted_sample_rules, apply_rules_with_exclusivity, RULES
from CVCleaner import CVPostCleaner
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)





def generar_cv(fake, bueno=True, locale="es_MX", seed=None, args=None):
    if random.random() < 0.5:
        first = fake.first_name_male()
        last = fake.last_name_male()
        genero = "m"
    else:
        first = fake.first_name_female()
        last = fake.last_name_female()
        genero = "f"
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
        if random.random() < 0.5:
            first = fake.first_name_male()
            last = fake.last_name_male()
            genero = "m"
        else:
            first = fake.first_name_female()
            last = fake.last_name_female()
            genero = "f"

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
                          "ubicacion": make_location(fake)},
            "contacto": contacto, "resumen": resumen,
            "experiencia": experiencia, "educacion": educacion, "skills": skills,"genero": genero
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
            "reglas_aplicadas": reglas_aplicadas,
            "genero": genero
        },
        "identidad": {
            "nombre": f"{first} {last}",
            "titulo": titulo,
            "ubicacion": make_location(fake)
        },
        "contacto": contacto,
        "resumen": resumen,
        "experiencia": experiencia,
        "educacion": educacion,
        "skills": skills
    }
    cleaner = CVPostCleaner()
    estructura = cleaner.clean_cv_dict(estructura)
    return estructura

def write_label_jsonl(cv, fname, out_dir):
    record = {
        "id": fname,
        "label": cv["meta"]["label"],
        "reglas": cv["meta"].get("reglas_aplicadas", [])
    }
    with open(os.path.join(out_dir, "labels.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def build_affinity_record_all(cv: dict, fname: str) -> dict:
    """
    Construye un registro con TODAS las vacantes ordenadas por score desc.
    Incluye 'rol_cv' tomado de cv['identidad']['titulo'] y el mejor match.
    """
    fits = (cv.get("meta", {}) or {}).get("fits", [])
    ordered = sorted(fits, key=lambda x: x["fit_score"], reverse=True)

    vacantes = [
        {
            "jd": it["jd_name"],
            "score": round(float(it["fit_score"]), 4),
            "label": it["fit_label"]
        }
        for it in ordered
    ]

    mejor = None
    if ordered:
        top = ordered[0]
        mejor = {
            "jd": top["jd_name"],
            "score": round(float(top["fit_score"]), 4),
            "label": top["fit_label"]
        }

    return {
        "id": fname,
        "rol_cv": cv.get("identidad", {}).get("titulo", ""),
        "vacantes": vacantes,
        "mejor": mejor
    }


def write_affinity_jsonl(record: dict, out_dir: str, jsonl_name: str = "afinidades.jsonl"):
    """
    Escribe (append) una línea JSON con afinidad por CV: id, top3 y mejor.
    """
    path = os.path.join(out_dir, jsonl_name)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")



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
    """if cv["meta"].get("fits"):
        lines.append("Encaje con vacantes")
        lines.append("-------------------")
        top = sorted(cv["meta"]["fits"], key=lambda x: x["fit_score"], reverse=True)[:3]
        for f in top:
            lines.append(f"- {f['jd_name']}: {f['fit_score']:.2f} ({f['fit_label']})")
        lines.append("")"""
    # Marcas de reglas (útil para depurar dataset)
    #lines.append(f"[Label: {cv['meta']['label']}] Reglas: {', '.join(cv['meta']['reglas_aplicadas'])}")
    label_info = {
        "id": cv.get("meta", {}).get("id", "unknown"),  # si quieres guardar el id/nombre aquí
        "label": cv["meta"]["label"],
        "reglas": cv["meta"].get("reglas_aplicadas", [])
    }
    #ines.append(json.dumps(label_info, ensure_ascii=False))

    raw_txt = "\n".join(lines)
    # Limpieza post-render ATS
    cleaner = CVPostCleaner()
    return cleaner.clean_txt(raw_txt)


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
    afinidades_acumuladas = []
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
            write_label_jsonl(cv, fname, args.out)
            # Afinidad con vacantes: JSONL por CV (usa el mismo orden y top3 que el snippet)
            if cv.get("meta", {}).get("fits"):
                rec = build_affinity_record_all(cv, fname)
                write_affinity_jsonl(rec, args.out, jsonl_name="afinidades.jsonl")
                afinidades_acumuladas.append(rec)
                write_affinity_jsonl(rec, args.out, jsonl_name="afinidades.jsonl")
                afinidades_acumuladas.append(rec)

    # JSON agregado con todas las afinidades de la corrida
    if afinidades_acumuladas:
        with open(os.path.join(args.out, "afinidades.json"), "w", encoding="utf-8") as fa:
            json.dump(afinidades_acumuladas, fa, ensure_ascii=False, indent=2)


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
