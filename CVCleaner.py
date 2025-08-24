# --- Limpieza post-generación (dedup, fechas, gramática mínima, etc.) ---
import re
from datetime import datetime
import json, os, random
import re
class CVPostCleaner:
    import re

    DE_EL_RE = re.compile(r"\bde\s+el\b", flags=re.IGNORECASE)
    A_EL_RE = re.compile(r"\ba\s+el\b", flags=re.IGNORECASE)
    ART_DUP_RE = re.compile(r"\b(el|la)\s+(el|la)\b", flags=re.IGNORECASE)
    PLACEHOLDER_RE = re.compile(r"\bN(?:\.\d+)?%?\b", flags=re.IGNORECASE)
    SPACE_RE = re.compile(r"\s{2,}")
    TRAIL_CONNECTOR_RE = re.compile(r"(?:\s|\b)(Además|Asimismo|En paralelo|A la par|Por otro lado)\.?$")

    def _fix_spanish_grammar(self, s: str) -> str:
        s = DE_EL_RE.sub("del", s)
        s = A_EL_RE.sub("al", s)
        s = ART_DUP_RE.sub(lambda m: m.group(1), s)
        s = SPACE_RE.sub(" ", s)
        return s.strip()

    def _strip_trailing_connector(self, s: str) -> str:
        return TRAIL_CONNECTOR_RE.sub("", s).strip()

    def _is_bad_placeholder_line(self, s: str) -> bool:
        return bool(PLACEHOLDER_RE.search(s) or " N h" in s or "N h " in s)

    TODAY = datetime.today()
    DATE_RE = re.compile(r"(\d{4})-(\d{2})")
    ROLE_HEADER_RE = re.compile(r"^(.+?)\s*\|\s*(.+?)\s*\|\s*(\d{4}-\d{2})\s*—\s*(Actual|\d{4}-\d{2})\s*$")
    BULLET_RE = re.compile(r"^\s*-\s+")
    SENT_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')


    def _strip_trailing_connector(self, s: str) -> str:
        # Quita conectores si quedaron "colgando" al final del bullet
        tail_re = re.compile(r'\s*(Además|Asimismo|En paralelo|A la par|Por otro lado)\.?$', re.I)
        return tail_re.sub('', s).strip()

    def _normalize_bullet_text(self, s: str) -> str:
        # Arreglos gramaticales rápidos y espacios / artículos
        s = self._fix_line(s)
        # “en para” → “para”, “a a” → “a”
        s = re.sub(r'\ben\s+para\b', 'para', s, flags=re.I)
        s = re.sub(r'\ba\s+a\b', 'a', s, flags=re.I)
        # “el el / la la” ya lo corrige _fix_redundancies, reforzamos artículos con sustantivo neutro
        s = re.sub(r'\b(el|la)\s+(el|la)\b', r'\1', s, flags=re.I)
        # Evita "el la API", "el la estrategia" (cuando _art_noun generó discordancia)
        s = re.sub(r'\b(el|la)\s+(la|el)\s+(\bapi\b|\bestrategia\b|\bplataforma\b|\binterfaz\b|\balerta\b)',
                   r'\2 \3', s, flags=re.I)
        # Quita conectores sueltos al final
        s = self._strip_trailing_connector(s)
        return s




    def _norm_key(self, s: str) -> str:
        return re.sub(r'\W+', ' ', (s or '').lower()).strip()

    def _clean_spaces_punct(self, s: str) -> str:
        s = re.sub(r'\s+([;,:.])', r'\1', s)
        s = re.sub(r'\s{2,}', ' ', s)
        s = re.sub(r'\s+—\s+', ' — ', s)
        return s.strip()

    def _fix_double_article(self, s: str) -> str:
        s = re.sub(r'\b(el|la)\s+(el|la)\b', r'\1', s, flags=re.I)
        s = re.sub(r'\bdel\s+el\b', 'del', s, flags=re.I)
        s = re.sub(r'\bal\s+el\b', 'al', s, flags=re.I)
        return s

    def _fix_redundancies(self, s: str) -> str:
        # repeticiones obvias
        s = re.sub(r'\b(\w+)\s+\1\b', r'\1', s, flags=re.I)  # de de, el el, etc.
        s = re.sub(r'\btimes? de tiempo de\b', 'tiempos de', s, flags=re.I)

        # errores de acentuación comunes en verbos de acción del pool
        s = re.sub(r'\bAutomatizé\b', 'Automaticé', s)
        s = re.sub(r'\bHabilités\b', 'Habilité', s)
        s = re.sub(r'\bAlineé\b', 'Alineé', s)  # por si acaso en min/mayus
        s = re.sub(r'\bOrquesté\b', 'Orquesté', s)

        # conectores duplicados
        s = re.sub(r'\b(Además|Asimismo|En paralelo|A la par|Por otro lado)(\s+\1)+', r'\1', s, flags=re.I)

        # espacios y puntuación redundante tipo " ,", " ;"
        s = re.sub(r'\s+([;,:.])', r'\1', s)
        s = re.sub(r'\s{2,}', ' ', s)
        return s

        return s

    def _fix_line(self, s: str) -> str:
        return self._clean_spaces_punct(self._fix_double_article(self._fix_redundancies(s)))

    # ---------------- Diccionario (JSON) ----------------

    def _cap_future_ym(self, ym: str) -> str:
        m = self.DATE_RE.search(ym or "")
        if not m:
            return ym
        y, mo = int(m.group(1)), int(m.group(2))
        if (y, mo) > (self.TODAY.year, self.TODAY.month):
            return f"{self.TODAY.year}-{self.TODAY.month:02d}"
        return ym

    def _dedup_bullets_list(self, bullets: list[str]) -> list[str]:
        out, seen = [], set()
        for b in bullets or []:
            b2 = self._fix_line(b)
            k = self._norm_key(b2)
            if k in seen:
                continue
            seen.add(k)
            out.append(b2)
        return out

    def _dedup_education_entries(self, entries: list[dict]) -> list[dict]:
        """
        Dedup por (grado, area, institucion). Si es misma cert con diferente año => (Recertificación).
        """
        out, seen = [], {}
        for e in entries or []:
            grado = (e.get("grado") or "").strip()
            area  = (e.get("area") or "").strip()
            inst  = (e.get("institucion") or "").strip()
            fin   = (e.get("fin") or "").strip()
            k = (grado.lower(), area.lower(), inst.lower())

            if k not in seen:
                seen[k] = fin
                out.append(e)
                continue

            prev_fin = seen[k]
            if grado.lower().startswith("cert") and fin and prev_fin and fin != prev_fin:
                # recertificación (dup parcial por año distinto)
                e2 = e.copy()
                if " (Recertificación)" not in area:
                    e2["area"] = f"{area} (Recertificación)"
                out.append(e2)
                seen[k] = fin
            # si es duplicado exacto, lo omitimos
        return out

    def _fix_experience_dates(self, exp_list: list[dict]) -> list[dict]:
        fixed = []
        for e in exp_list or []:
            ini = self._cap_future_ym(e.get("inicio") or "")
            fin = e.get("fin")
            if fin and fin != "Actual":
                fin = self._cap_future_ym(fin)
                # si por recorte fin < inicio, colapsa en inicio
                try:
                    ys, ms = map(int, ini.split("-"))
                    ye, me = map(int, fin.split("-"))
                    if (ye, me) < (ys, ms):
                        fin = ini
                except Exception:
                    pass
            fixed.append({**e, "inicio": ini, "fin": fin})
        return fixed

    def clean_cv_dict(self, cv: dict) -> dict:
        """
        Limpia el dict del CV en:
        - experiencia.descripcion (dedup y fix líneas)
        - experiencia fechas futuras
        - educación (dedup + recertificación)
        - resumen (marca meta si es muy corto)
        """
        cv2 = json.loads(json.dumps(cv, ensure_ascii=False))  # copia profunda segura
        # Experiencia
        exp_list = cv2.get("experiencia") or []
        exp_fixed = []
        for e in exp_list:
            desc = e.get("descripcion") or ""
            bullets = [ln for ln in desc.splitlines() if ln.strip()]
            bullets = self._dedup_bullets_list(bullets)
            e2 = e.copy()
            e2["descripcion"] = "\n".join(bullets)
            exp_fixed.append(e2)

        # 1) Fechas realistas
        exp_fixed = self._fix_experience_dates(exp_fixed)
        # 2) Solo un 'Actual'
        exp_fixed = self._limit_current_roles(exp_fixed, max_current=1)
        cv2["experiencia"] = exp_fixed


        # Educación
        cv2["educacion"] = self._dedup_education_entries(cv2.get("educacion") or [])

        # Resumen: aviso si < 3 oraciones (no lo reescribo)
        resumen = (cv2.get("resumen") or "").strip()
        if resumen:
            num = len([s for s in self.SENT_SPLIT_RE.split(resumen) if s.strip()])
            if num < 3:
                cv2.setdefault("meta", {})
                cv2["meta"]["warn_resumen_corto"] = True

        return cv2

    # ---------------- TXT (render ATS) ----------------

    def _dedup_education_txt(self, lines: list[str]) -> list[str]:
        out, seen = [], {}
        EDU_ITEM_RE = re.compile(
            r"^(Certificación|Certificacion|Licenciatura|Ingeniería|Ingenieria|Diplomado|Maestría|Maestria)\s+en\s+(.+?)\s+—\s+(.+?)\s+\((Actual|\d{4})\)\s*$",
            re.I
        )
        for ln in lines:
            m = EDU_ITEM_RE.match(ln.strip())
            if not m:
                out.append(self._fix_line(ln))
                continue
            grado, area, inst, fin = m.groups()
            key = (grado.lower(), area.lower(), inst.lower())
            if key not in seen:
                seen[key] = fin
                out.append(self._fix_line(ln))
            else:
                prev_fin = seen[key]
                if fin != prev_fin and grado.lower().startswith("cert"):
                    ln2 = re.sub(rf"(\s+en\s+){re.escape(area)}", rf"\1{area} (Recertificación)", ln, flags=re.I)
                    out.append(self._fix_line(ln2))
                    seen[key] = fin
                # duplicado exacto => omitir
        return out

    def _dedup_bullets_block_txt(self, lines: list[str]) -> list[str]:
        out, seen = [], set()
        for ln in lines:
            if self.BULLET_RE.match(ln):
                fixed = self._normalize_bullet_text(ln)
                k = self._norm_key(fixed)
                if k in seen:
                    continue
                seen.add(k)
                out.append(fixed)
            else:
                out.append(self._fix_line(ln))
        return out

    def _limit_current_roles(self, exp_list: list[dict], max_current: int = 1) -> list[dict]:
        """
        Deja como 'Actual' solo la experiencia más reciente (por 'inicio').
        Las demás 'Actual' se cierran en su 'inicio' (conservador y coherente).
        """
        def parse_ym(s: str):
            try:
                y, m = map(int, (s or "0000-01").split("-"))
                return (y, m)
            except Exception:
                return (0, 0)

        idx_current = [(i, e) for i, e in enumerate(exp_list or []) if (e.get("fin") or "").strip() == "Actual"]
        if len(idx_current) <= max_current:
            return exp_list

        # mantén como Actual la más reciente por 'inicio'
        idx_current_sorted = sorted(idx_current, key=lambda t: parse_ym(t[1].get("inicio")), reverse=True)
        keep_idx = idx_current_sorted[0][0]

        for idx, e in idx_current_sorted[1:]:
            ini = e.get("inicio") or ""
            # cerramos en su 'inicio' (evita inconsistencias)
            e2 = e.copy()
            e2["fin"] = self._cap_future_ym(ini)
            exp_list[idx] = e2

        return exp_list


    def _cap_future_in_header(self, line: str) -> str:
        m = self.ROLE_HEADER_RE.match(line.strip())
        if not m:
            return self._fix_line(line)
        role, company, start, end = m.groups()
        start_fix = self._cap_future_ym(start)
        if end != "Actual":
            end_fix = self._cap_future_ym(end)
            try:
                ys, ms = map(int, start_fix.split("-"))
                ye, me = map(int, end_fix.split("-"))
                if (ye, me) < (ys, ms):
                    end_fix = start_fix
            except Exception:
                pass
        else:
            end_fix = end
        return self._fix_line(f"{role} | {company} | {start_fix} — {end_fix}")

    def clean_txt(self, txt: str) -> str:
        lines = txt.splitlines()
        out = []
        in_exp = False
        in_edu = False
        block = []
        edu_block = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Sección experiencia
            if stripped == "Experiencia" or stripped.startswith("Experiencia"):
                if block:
                    out.extend(self._dedup_bullets_block_txt(block)); block = []
                if edu_block:
                    out.extend(self._dedup_education_txt(edu_block)); edu_block = []
                in_exp, in_edu = True, False
                out.append(self._fix_line(line))
                continue

            # Sección educación
            if stripped == "Educación" or stripped == "Educacion" or stripped.startswith("Educación"):
                if block:
                    out.extend(self._dedup_bullets_block_txt(block)); block = []
                if edu_block:
                    out.extend(self._dedup_education_txt(edu_block)); edu_block = []
                in_exp, in_edu = False, True
                out.append(self._fix_line(line))
                continue

            if in_exp:
                if self.ROLE_HEADER_RE.match(stripped):
                    if block:
                        out.extend(self._dedup_bullets_block_txt(block)); block = []
                    out.append(self._cap_future_in_header(line))
                else:
                    block.append(line)
                continue

            if in_edu:
                # fin implícito de bloque educación si línea en blanco separa
                if stripped == "":
                    out.extend(self._dedup_education_txt(edu_block)); edu_block = []
                    out.append(line)
                    in_edu = False
                else:
                    edu_block.append(line)
                continue

            # resto
            out.append(self._fix_line(line))

        if block:
            out.extend(self._dedup_bullets_block_txt(block))
        if edu_block:
            out.extend(self._dedup_education_txt(edu_block))

        # limpiar líneas en blanco duplicadas
        final, last_blank = [], False
        for ln in out:
            if not ln.strip():
                if not last_blank:
                    final.append(ln)
                last_blank = True
            else:
                final.append(ln); last_blank = False

        txt = "\n".join(final).strip() + "\n"
        # barrido final de conectores al final de línea
        fixed_lines = []
        for ln in txt.splitlines():
            if self.BULLET_RE.match(ln):
                ln = self._strip_trailing_connector(ln)
            fixed_lines.append(self._fix_line(ln))
        return "\n".join(fixed_lines).strip() + "\n"

