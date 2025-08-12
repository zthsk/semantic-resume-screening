"""
Synthetic Resume Generator -> Parser -> Summarizer

What this script does:
1) Generate N synthetic resumes in a consistent, parser-friendly Markdown format.
   - Also saves .txt copies for convenience.
   - Optionally saves PDFs if reportlab is installed and --make-pdf is passed.

2) Parse the generated resumes deterministically (no ML) back into structured JSON.

3) Create a 2–3 sentence summary from the parsed structure (deterministic).
   - You can later replace summarize() with a call to your LLM.

Usage:
  python synth_resumes.py --out ./synthetic --count 12 --make-pdf
"""

import os
import re
import json
import random
import argparse
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# -------------------------------
# Optional dependency (PDF)
# -------------------------------
HAVE_REPORTLAB = False
try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    HAVE_REPORTLAB = True
except Exception:
    HAVE_REPORTLAB = False

# -------------------------------
# Data models
# -------------------------------
@dataclass
class Education:
    institution: str
    degree: str
    field_of_study: str
    year: int
    gpa: Optional[float] = None
    location: Optional[str] = None

@dataclass
class Experience:
    company: str
    title: str
    start: str  # e.g., "Jan 2021"
    end: str    # e.g., "Present" or "Jun 2023"
    location: str
    highlights: List[str]

@dataclass
class ResumeStruct:
    name: str
    title: str
    email: str
    phone: str
    location: str
    education: List[Education]
    experience: List[Experience]
    skills: Dict[str, List[str]]

# -------------------------------
# Synthetic data
# -------------------------------
FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Casey", "Robin", "Riley", "Avery", "Quinn",
    "Morgan", "Jamie", "Cameron", "Drew", "Peyton", "Skyler", "Emerson"
]
LAST_NAMES = [
    "Johnson", "Smith", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson"
]
CITIES_ST = [
    ("San Francisco", "CA"), ("Seattle", "WA"), ("Austin", "TX"),
    ("New York", "NY"), ("Boston", "MA"), ("Chicago", "IL"),
    ("Denver", "CO"), ("Atlanta", "GA"), ("San Diego", "CA"),
    ("Portland", "OR"), ("Phoenix", "AZ"), ("Miami", "FL")
]
DEGREES = [
    "Bachelor of Science", "Master of Science", "Bachelor of Engineering", "Master of Engineering"
]
FIELDS = [
    "Computer Science", "Software Engineering", "Information Systems",
    "Electrical Engineering", "Data Science"
]
COMPANIES = [
    "TechNova", "BluePeak", "InnoSoft", "CloudLoom", "DataForge",
    "Nextlytics", "BrightHub", "CodeSpring", "QuantumNest", "HyperWeave"
]
JOB_TITLES = [
    "Software Engineer", "Senior Software Engineer", "Backend Engineer",
    "Full Stack Developer", "Data Engineer", "Machine Learning Engineer"
]
HIGHLIGHT_TEMPLATES = [
    "Built {thing} using {tech} improving {metric} by {percent}%",
    "Led {count}-person team to deliver {project} on time",
    "Reduced {metric} by {percent}% via {approach}",
    "Designed and implemented {component} with {tech}",
    "Migrated legacy {system} to {cloud} with zero downtime"
]
SKILL_GROUPS = {
    "Programming": ["Python", "JavaScript", "TypeScript", "Java", "Go", "C++"],
    "Web": ["React", "Node.js", "Express", "Django", "Flask", "FastAPI"],
    "Data": ["Pandas", "NumPy", "scikit-learn", "PyTorch", "TensorFlow", "SQL"],
    "Cloud/DevOps": ["AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform"]
}

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def rand_phone() -> str:
    # US-ish
    a = random.randint(200, 999)
    b = random.randint(200, 999)
    c = random.randint(1000, 9999)
    return f"({a}) {b}-{c}"

def rand_email(first: str, last: str) -> str:
    domain = random.choice(["gmail.com", "outlook.com", "proton.me", "yahoo.com"])
    sep = random.choice([".", "_", ""])
    return f"{first.lower()}{sep}{last.lower()}@{domain}"

def rand_year_range() -> (str, str):
    start_year = random.randint(2015, 2022)
    start = f"{random.choice(MONTHS)} {start_year}"
    if random.random() < 0.3:
        end = "Present"
    else:
        end_year = random.randint(start_year, 2025)
        end = f"{random.choice(MONTHS)} {end_year}"
    return start, end

def make_highlight() -> str:
    return random.choice(HIGHLIGHT_TEMPLATES).format(
        thing=random.choice(["a microservice", "a data pipeline", "a CI/CD system", "an internal SDK", "a real-time API"]),
        tech=random.choice(["Python", "Go", "TypeScript", "Kubernetes", "AWS", "PostgreSQL"]),
        metric=random.choice(["latency", "cost", "CPU usage", "error rate", "MTTR"]),
        percent=random.choice([15, 20, 25, 30, 40]),
        count=random.randint(3, 8),
        project=random.choice(["a payments module", "recommendation engine", "feature store", "ETL replatform"]),
        approach=random.choice(["caching", "asynchronous processing", "schema optimization", "observability tooling"]),
        component=random.choice(["auth gateway", "ingestion pipeline", "model serving layer", "monitoring stack"]),
        system=random.choice(["monolith", "cron farm", "VM cluster"]),
        cloud=random.choice(["AWS", "GCP", "Azure"])
    )

def pick_skills() -> Dict[str, List[str]]:
    out = {}
    for group, items in SKILL_GROUPS.items():
        n = random.randint(3, min(5, len(items)))
        out[group] = random.sample(items, n)
    return out

def generate_resume() -> ResumeStruct:
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    title = random.choice(JOB_TITLES)
    email = rand_email(first, last)
    phone = rand_phone()
    city, st = random.choice(CITIES_ST)
    location = f"{city}, {st}"

    # Education (1–2 entries)
    edu_count = random.choice([1, 1, 2])
    edus: List[Education] = []
    grad_year = random.randint(2016, 2023)
    institutions = ["State University", "Tech University", "City College", "Institute of Technology"]
    for i in range(edu_count):
        degree = random.choice(DEGREES)
        field = random.choice(FIELDS)
        inst = f"{random.choice(institutions)} of {random.choice(['North','West','East','Central',''])}".strip()
        year = grad_year - i
        gpa = round(random.uniform(3.2, 4.0), 2)
        edus.append(Education(institution=inst, degree=degree, field_of_study=field, year=year, gpa=gpa, location=location))

    # Experience (2–4 entries)
    exps: List[Experience] = []
    for _ in range(random.randint(2, 4)):
        company = random.choice(COMPANIES)
        job = random.choice(JOB_TITLES)
        start, end = rand_year_range()
        exp_loc = f"{random.choice([city for city,_ in CITIES_ST])}, {random.choice([st for _,st in CITIES_ST])}"
        highs = [make_highlight() for _ in range(random.randint(2, 4))]
        exps.append(Experience(company=company, title=job, start=start, end=end, location=exp_loc, highlights=highs))

    skills = pick_skills()

    return ResumeStruct(
        name=name, title=title, email=email, phone=phone, location=location,
        education=edus, experience=exps, skills=skills
    )

# -------------------------------
# Rendering (Markdown + TXT + PDF)
# -------------------------------
def render_markdown(r: ResumeStruct) -> str:
    # A stable, parser-friendly layout with explicit keys and separators
    lines = []
    lines.append(f"# {r.name}")
    lines.append(f"Title: {r.title}")
    lines.append("")
    lines.append("## Contact")
    lines.append(f"Email: {r.email}")
    lines.append(f"Phone: {r.phone}")
    lines.append(f"Location: {r.location}")
    lines.append("")
    lines.append("## Education")
    for e in r.education:
        # One-per-line with pipe-separated fields (easy parse)
        lines.append(f"- Institution: {e.institution} | Degree: {e.degree} | Field: {e.field_of_study} | Year: {e.year} | GPA: {e.gpa} | Location: {e.location}")
    lines.append("")
    lines.append("## Experience")
    for x in r.experience:
        lines.append(f"- Company: {x.company} | Title: {x.title} | Dates: {x.start} - {x.end} | Location: {x.location}")
        lines.append(f"  Highlights:")
        for h in x.highlights:
            lines.append(f"    - {h}")
    lines.append("")
    lines.append("## Skills")
    for group, items in r.skills.items():
        lines.append(f"- {group}: {', '.join(items)}")
    lines.append("")
    return "\n".join(lines)

def save_pdf_from_text(pdf_path: Path, text: str):
    if not HAVE_REPORTLAB:
        raise RuntimeError("reportlab not installed.")
    c = canvas.Canvas(str(pdf_path), pagesize=LETTER)
    width, height = LETTER
    left = 0.75 * inch
    top = height - 0.75 * inch
    line_height = 12
    x, y = left, top

    for raw_line in text.splitlines():
        # naive word wrap
        line = raw_line.expandtabs(2)
        while len(line) > 0:
            # wrap around ~100 chars based on width; simple heuristic
            if len(line) <= 110:
                draw = line
                line = ""
            else:
                break_at = line.rfind(" ", 0, 110)
                if break_at == -1:
                    break_at = 110
                draw = line[:break_at]
                line = line[break_at:].lstrip()
            c.drawString(x, y, draw)
            y -= line_height
            if y < 0.75 * inch:
                c.showPage()
                y = top
    c.showPage()
    c.save()

# -------------------------------
# Parser (deterministic)
# -------------------------------
def parse_markdown(md: str) -> ResumeStruct:
    # Extract simple sections based on headers and field prefixes
    # Assumes the template produced by render_markdown()
    def get(header: str) -> Optional[str]:
        m = re.search(rf"^{re.escape(header)}:\s*(.+)$", md, flags=re.M)
        return m.group(1).strip() if m else None

    name_m = re.search(r"^#\s+(.+)$", md, flags=re.M)
    name = name_m.group(1).strip() if name_m else ""
    title = get("Title") or ""
    email = get("Email") or ""
    phone = get("Phone") or ""
    location = get("Location") or ""

    # Education lines
    edu_sec = re.search(r"(?ms)^## Education\s*(.+?)^\s*## ", md + "\n## ", flags=0)
    edu_lines = []
    if edu_sec:
        for line in edu_sec.group(1).splitlines():
            line = line.strip()
            if line.startswith("- Institution:"):
                edu_lines.append(line)

    educations: List[Education] = []
    for line in edu_lines:
        # Parse fields by " | " delimiters and "key: value"
        fields = [kv.strip() for kv in line[1:].split("|")]  # remove leading '-'
        kvmap = {}
        for kv in fields:
            if ":" in kv:
                k, v = kv.split(":", 1)
                kvmap[k.strip().lower()] = v.strip()
        educations.append(Education(
            institution=kvmap.get("institution", ""),
            degree=kvmap.get("degree", ""),
            field_of_study=kvmap.get("field", ""),
            year=int(kvmap.get("year", "0") or 0),
            gpa=float(kvmap.get("gpa", "0") or 0),
            location=kvmap.get("location", "")
        ))

    # Experience
    exp_sec = re.search(r"(?ms)^## Experience\s*(.+?)^\s*## ", md + "\n## ", flags=0)
    exp_lines = []
    exp_high_map = {}  # index -> highlights
    if exp_sec:
        lines = exp_sec.group(1).splitlines()
        current_idx = -1
        for ln in lines:
            s = ln.rstrip()
            if s.strip().startswith("- Company:"):
                current_idx += 1
                exp_lines.append(s.strip())
                exp_high_map[current_idx] = []
            elif s.strip().startswith("- "):  # another job bullet immediately
                current_idx += 1
                exp_lines.append(s.strip())
                exp_high_map[current_idx] = []
            elif s.strip().startswith("Highlights:"):
                # nothing to store directly
                pass
            elif s.strip().startswith("-") and s.startswith("    -"):
                # nested highlight bullet
                exp_high_map[current_idx].append(s.strip()[2:].strip())
            elif s.strip().startswith("    - "):
                exp_high_map[current_idx].append(s.strip()[4:].strip())

    experiences: List[Experience] = []
    for idx, line in enumerate(exp_lines):
        fields = [kv.strip() for kv in line[1:].split("|")]  # remove leading '-'
        kvmap = {}
        for kv in fields:
            if ":" in kv:
                k, v = kv.split(":", 1)
                kvmap[k.strip().lower()] = v.strip()
        # Dates of form "Jan 2020 - Present"
        dates = kvmap.get("dates", "")
        start, end = "", ""
        if " - " in dates:
            start, end = [x.strip() for x in dates.split(" - ", 1)]
        experiences.append(Experience(
            company=kvmap.get("company", ""),
            title=kvmap.get("title", ""),
            start=start,
            end=end,
            location=kvmap.get("location", ""),
            highlights=exp_high_map.get(idx, [])
        ))

    # Skills
    skills_sec = re.search(r"(?ms)^## Skills\s*(.+)$", md)
    skills: Dict[str, List[str]] = {}
    if skills_sec:
        for line in skills_sec.group(1).splitlines():
            line = line.strip()
            if line.startswith("- ") and ":" in line:
                k, v = line[2:].split(":", 1)
                group = k.strip()
                items = [x.strip() for x in v.split(",") if x.strip()]
                skills[group] = items

    return ResumeStruct(
        name=name, title=title, email=email, phone=phone, location=location,
        education=educations, experience=experiences, skills=skills
    )

# -------------------------------
# Summarizer (2–3 sentences, deterministic)
# Replace this later with your LLM if desired.
# -------------------------------
def summarize(data: ResumeStruct) -> str:
    yrs = set()
    for x in data.experience:
        # crude year pull from "Mon YYYY" or "YYYY"
        for token in (x.start, x.end):
            if token and token.strip() and token.strip() != "Present":
                m = re.search(r"(19|20)\d{2}", token)
                if m:
                    yrs.add(int(m.group(0)))
    if yrs:
        span = f"{min(yrs)}–{max(yrs)}"
    else:
        span = "recent years"

    top_role = data.title or (data.experience[0].title if data.experience else "Engineer")
    top_company = data.experience[0].company if data.experience else ""
    skill_flat = [s for group in data.skills.values() for s in group]
    top_skills = ", ".join(sorted(skill_flat)[:5]) if skill_flat else None

    s1 = f"{data.name} is a {top_role} based in {data.location} with experience spanning {span}."
    s2 = f"Recent work includes roles at {top_company} delivering impact across multiple projects." if top_company else ""
    s3 = f"Core skills include {top_skills}." if top_skills else ""

    # Return 2–3 concise sentences
    return " ".join([x for x in [s1, s2, s3] if x]).strip()

# -------------------------------
# Main flow
# -------------------------------
def generate_resumes(out_dir: Path, count: int, make_pdf: bool):
    md_dir = out_dir / "md"
    txt_dir = out_dir / "txt"
    pdf_dir = out_dir / "pdf"
    md_dir.mkdir(parents=True, exist_ok=True)
    txt_dir.mkdir(parents=True, exist_ok=True)
    if make_pdf:
        if not HAVE_REPORTLAB:
            print("⚠️  reportlab not installed; skipping PDF generation.")
            make_pdf = False
        else:
            pdf_dir.mkdir(parents=True, exist_ok=True)

    structs: List[ResumeStruct] = []

    for i in range(count):
        r = generate_resume()
        structs.append(r)
        md = render_markdown(r)
        stem = f"resume_{i+1:02d}"

        (md_dir / f"{stem}.md").write_text(md, encoding="utf-8")
        (txt_dir / f"{stem}.txt").write_text(md, encoding="utf-8")

        if make_pdf:
            try:
                save_pdf_from_text(pdf_dir / f"{stem}.pdf", md)
            except Exception as e:
                print(f"PDF failed for {stem}: {e}")

    return structs

def parse_generated(out_dir: Path, use_md: bool = True):
    src_dir = out_dir / ("md" if use_md else "txt")
    parsed_dir = out_dir / "parsed"
    parsed_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for p in sorted(src_dir.glob("*.md" if use_md else "*.txt")):
        md = p.read_text(encoding="utf-8")
        struct = parse_markdown(md)
        summary = summarize(struct)
        rec = {
            "filename": p.name,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "data": asdict(struct),
            "summary": summary
        }
        results.append(rec)
        (parsed_dir / f"{p.stem}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")

    combined = {
        "count": len(results),
        "results": results
    }
    (parsed_dir / "combined.json").write_text(json.dumps(combined, indent=2), encoding="utf-8")
    return results

def main():
    ap = argparse.ArgumentParser(description="Synthetic resume generator + parser + summarizer")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--count", type=int, default=12, help="How many resumes to generate (10–15 recommended)")
    ap.add_argument("--make-pdf", action="store_true", help="Also generate PDFs (requires reportlab)")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"🛠️  Generating {args.count} synthetic resumes -> {out_dir}")
    generate_resumes(out_dir, args.count, args.make_pdf)

    print("🔎 Parsing generated resumes (Markdown)...")
    results = parse_generated(out_dir, use_md=True)

    print(f"✅ Done. Folders created:")
    print(f"   - {out_dir / 'md'} (Markdown)")
    print(f"   - {out_dir / 'txt'} (Plain text)")
    if args.make_pdf and HAVE_REPORTLAB:
        print(f"   - {out_dir / 'pdf'} (PDF)")
    print(f"   - {out_dir / 'parsed'} (Parsed JSON + combined.json)")

if __name__ == "__main__":
    random.seed(42)  # reproducible-ish
    main()
