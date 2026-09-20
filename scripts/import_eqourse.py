#!/usr/bin/env python3
"""Import eQOURSE CC BY 4.0 JEE datasets into Study Buddy without overwriting existing data."""
from pathlib import Path
import argparse, hashlib, json, re, urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://huggingface.co/datasets/eQOURSE"
SUBJECTS = {"physics": "Physics", "chemistry": "Chemistry", "mathematics": "Mathematics"}

def get_rows(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return [json.loads(x) for x in r.read().decode().splitlines() if x.strip()]

def year(source):
    m = re.findall(r"20\\d{2}", source or "")
    if m:
        return int(m[-1])
    m = re.findall(r"(?<!\\d)(\\d{2})(?!\\d)", source or "")
    return 2000 + int(m[-1]) if m else 2000

def chapter(subject, topic, subtopic):
    t = (topic + " " + subtopic).lower()
    groups = {
      "Physics": [("kinematic motion projectile", "Kinematics"), ("newton friction laws of motion", "Laws of Motion"), ("work energy power", "Work, Energy and Power"), ("rotation rolling moment of inertia", "Rotational Motion"), ("gravitation satellite", "Gravitation"), ("thermodynamic heat", "Thermodynamics"), ("oscillation harmonic", "Oscillations"), ("wave sound", "Waves"), ("electrostatic electric field capacitor", "Electrostatics"), ("current circuit resistance", "Current Electricity"), ("magnetic magnetism", "Magnetic Effects of Current and Magnetism"), ("induction alternating", "Electromagnetic Induction and Alternating Current"), ("optics", "Optics"), ("nuclear atom", "Atoms and Nuclei")],
      "Chemistry": [("thermodynamic", "Thermodynamics"), ("equilibrium", "Equilibrium"), ("electrochem", "Electrochemistry"), ("kinetics", "Chemical Kinetics"), ("coordination", "Coordination Compounds"), ("hydrocarbon organic", "Organic Chemistry"), ("carbonyl aldehyde ketone carboxylic", "Aldehydes, Ketones and Carboxylic Acids"), ("amine nitrogen", "Amines"), ("atomic quantum", "Structure of Atom"), ("bond molecular", "Chemical Bonding and Molecular Structure"), ("periodic", "Classification of Elements and Periodicity")],
      "Mathematics": [("complex", "Complex Numbers"), ("quadratic", "Quadratic Equations"), ("sequence progression series", "Sequences and Series"), ("binomial", "Binomial Theorem"), ("permutation combination", "Permutations and Combinations"), ("probability", "Probability"), ("matrix determinant", "Matrices and Determinants"), ("circle", "Circle"), ("conic parabola ellipse hyperbola", "Conic Sections"), ("vector", "Vector Algebra"), ("three dimensional plane", "Three Dimensional Geometry"), ("limit continuity", "Limits and Continuity"), ("differenti derivative", "Differential Calculus"), ("integral", "Integral Calculus"), ("trigonometric trigonometry", "Trigonometry")]
    }
    for keys, name in groups.get(subject, []):
        if any(k in t for k in keys.split()):
            return name
    return topic.strip() or "Uncategorized"

def source_key(row):
    return str(row.get("question_id") or "").strip()

def make_id(prefix, subject, exam_year, source_id, text, used):
    code = {"Physics": "PHY", "Chemistry": "CHE", "Mathematics": "MAT"}[subject]
    digest = hashlib.sha1((source_id + "|" + text).encode("utf-8")).hexdigest()
    number = int(digest[:10], 16) % 1000000
    if number == 0:
        number = 1
    qid = f"{prefix}-{code}-{exam_year:04d}-{number:06d}"
    while qid in used:
        number = (number % 999999) + 1
        qid = f"{prefix}-{code}-{exam_year:04d}-{number:06d}"
    used.add(qid)
    return qid

def load_list(path):
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data.get("questions", [])

def merge_records(existing, imported):
    by_id = {x.get("question_id"): x for x in existing if x.get("question_id")}
    for item in imported:
        by_id.setdefault(item["question_id"], item)
    return list(by_id.values())

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--advanced", action="store_true")
    p.add_argument("--main", action="store_true")
    args = p.parse_args()
    if not (args.advanced or args.main):
        p.error("choose --advanced and/or --main")

    jobs = []
    if args.advanced:
        jobs.append(("JEE Advanced", "jee-advanced-questions", "jee_advanced", "JEEA", "Very Hard"))
    if args.main:
        jobs.append(("JEE Main", "jee-main-questions", "jee_main", "JEEM", "Hard"))

    for exam, dataset, outdir, prefix, default_difficulty in jobs:
        for slug, subject in SUBJECTS.items():
            rows_by_key = {}
            for split in ("train", "test"):
                url = f"{BASE}/{dataset}/resolve/main/{slug}/{split}.jsonl"
                for row in get_rows(url):
                    key = source_key(row)
                    if key and key not in rows_by_key:
                        rows_by_key[key] = row

            rows = sorted(rows_by_key.values(), key=lambda r: source_key(r))
            qp = ROOT / "data/questions" / outdir / f"{slug}.json"
            sp = ROOT / "data/solutions" / outdir / f"{slug}.json"
            qp.parent.mkdir(parents=True, exist_ok=True)
            sp.parent.mkdir(parents=True, exist_ok=True)
            existing_questions = load_list(qp)
            existing_solutions = load_list(sp)
            used_ids = {x.get("question_id") for x in existing_questions if x.get("question_id")}
            imported_questions = []
            imported_solutions = []

            for row in rows:
                text = str(row.get("question") or "").strip()
                raw_answer = str(row.get("numerical_answer") or row.get("answer") or "").strip()
                qt = str(row.get("question_type") or "").strip().lower()
                opts = [str(row.get(f"option_{i}") or "").strip() for i in range(1, 5)]
                opts = [x for x in opts if x]
                if qt == "single_correct" and row.get("correct_option"):
                    try:
                        idx = int(row["correct_option"]) - 1
                        answer = opts[idx] if 0 <= idx < len(opts) else raw_answer
                    except (TypeError, ValueError):
                        answer = raw_answer
                    qtype = "MCQ" if opts else "Subjective"
                else:
                    answer = raw_answer
                    qtype = "Numerical" if qt in ("numerical", "integer") else "Subjective"
                if not text or not answer:
                    continue
                exam_year = year(row.get("source_paper", ""))
                qid = make_id(prefix, subject, exam_year, source_key(row), text, used_ids)
                ref = f"{BASE}/{dataset}"
                question = {
                    "question_id": qid,
                    "exam": exam,
                    "exam_year": exam_year,
                    "subject": subject,
                    "chapter": chapter(subject, str(row.get("topic") or ""), str(row.get("subtopic") or "")),
                    "topic": str(row.get("subtopic") or row.get("topic") or "Uncategorized"),
                    "difficulty": default_difficulty,
                    "question_type": qtype,
                    "question_text": text.replace("[IMAGE]", "\\n[Diagram]\\n"),
                    "correct_answer": answer,
                    "marks": 4,
                    "negative_marks": 1 if qtype == "MCQ" else 0,
                    "source": "eQOURSE",
                    "source_reference": ref,
                    "tags": ["eQOURSE", "CC BY 4.0", f"source_question_id:{source_key(row)}", str(row.get("source_paper") or ""), str(row.get("topic") or ""), str(row.get("subtopic") or "")],
                    "content_type": "open_license",
                    "rights_status": "open_license",
                    "redistribution_allowed": True,
                    "rights_holder": "eQOURSE",
                    "license": "CC BY 4.0",
                    "license_reference": ref,
                }
                if opts:
                    question["options"] = opts
                solution = {
                    "question_id": qid,
                    "solution_type": "source_worked_solution",
                    "solution_text": str(row.get("solution") or "").replace("[IMAGE]", "\\n[Diagram]\\n").strip(),
                    "final_answer": answer,
                    "key_concepts": [x for x in [str(row.get("topic") or "").strip(), str(row.get("subtopic") or "").strip()] if x],
                    "source": "eQOURSE",
                    "source_reference": ref,
                }
                if not solution["solution_text"]:
                    continue
                imported_questions.append(question)
                imported_solutions.append(solution)

            merged_questions = merge_records(existing_questions, imported_questions)
            merged_solutions = merge_records(existing_solutions, imported_solutions)
            qp.write_text(json.dumps(merged_questions, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
            sp.write_text(json.dumps(merged_solutions, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
            print(f"{exam} {subject}: imported={len(imported_questions)} total={len(merged_questions)}")

if __name__ == "__main__":
    main()
