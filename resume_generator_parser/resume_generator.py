"""
Synthetic resume generator module.
Generates consistent, parser-friendly resumes in markdown format.
"""
import random
import logging
from pathlib import Path
from typing import List, Dict

from models import ResumeStruct, Education, Experience

logger = logging.getLogger(__name__)

# -------------------------------
# Synthetic data constants
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

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

class ResumeGenerator:
    """Generates synthetic resumes for testing and development."""
    
    def __init__(self, seed: int = 42):
        """Initialize generator with optional seed for reproducibility."""
        random.seed(seed)
    
    def generate_resume(self) -> ResumeStruct:
        """Generate a single synthetic resume."""
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        title = random.choice(JOB_TITLES)
        email = self._generate_email(first, last)
        phone = self._generate_phone()
        city, st = random.choice(CITIES_ST)
        location = f"{city}, {st}"
        
        # Generate education
        education = self._generate_education(location)
        
        # Generate experience
        experience = self._generate_experience()
        
        # Generate skills
        skills = self._generate_skills()
        
        return ResumeStruct(
            name=name,
            title=title,
            email=email,
            phone=phone,
            location=location,
            education=education,
            experience=experience,
            skills=skills
        )
    
    def generate_multiple(self, count: int) -> List[ResumeStruct]:
        """Generate multiple synthetic resumes."""
        return [self.generate_resume() for _ in range(count)]
    
    def _generate_email(self, first: str, last: str) -> str:
        """Generate a realistic email address."""
        domain = random.choice(["gmail.com", "outlook.com", "proton.me", "yahoo.com"])
        sep = random.choice([".", "_", ""])
        return f"{first.lower()}{sep}{last.lower()}@{domain}"
    
    def _generate_phone(self) -> str:
        """Generate a realistic US phone number."""
        a = random.randint(200, 999)
        b = random.randint(200, 999)
        c = random.randint(1000, 9999)
        return f"({a}) {b}-{c}"
    
    def _generate_education(self, location: str) -> List[Education]:
        """Generate education entries."""
        edu_count = random.choice([1, 1, 2])  # Bias towards 1
        educations = []
        grad_year = random.randint(2016, 2023)
        institutions = ["State University", "Tech University", "City College", "Institute of Technology"]
        
        for i in range(edu_count):
            degree = random.choice(DEGREES)
            field = random.choice(FIELDS)
            inst = f"{random.choice(institutions)} of {random.choice(['North','West','East','Central',''])}".strip()
            year = grad_year - i
            gpa = round(random.uniform(3.2, 4.0), 2)
            
            educations.append(Education(
                institution=inst,
                degree=degree,
                field_of_study=field,
                year=year,
                gpa=gpa,
                location=location
            ))
        
        return educations
    
    def _generate_experience(self) -> List[Experience]:
        """Generate work experience entries."""
        exp_count = random.randint(2, 4)
        experiences = []
        
        for _ in range(exp_count):
            company = random.choice(COMPANIES)
            job = random.choice(JOB_TITLES)
            start, end = self._generate_date_range()
            exp_loc = f"{random.choice([city for city,_ in CITIES_ST])}, {random.choice([st for _,st in CITIES_ST])}"
            highlights = [self._generate_highlight() for _ in range(random.randint(2, 4))]
            
            experiences.append(Experience(
                company=company,
                title=job,
                start=start,
                end=end,
                location=exp_loc,
                highlights=highlights
            ))
        
        return experiences
    
    def _generate_date_range(self) -> tuple[str, str]:
        """Generate a realistic date range."""
        start_year = random.randint(2015, 2022)
        start = f"{random.choice(MONTHS)} {start_year}"
        
        if random.random() < 0.3:
            end = "Present"
        else:
            end_year = random.randint(start_year, 2025)
            end = f"{random.choice(MONTHS)} {end_year}"
        
        return start, end
    
    def _generate_highlight(self) -> str:
        """Generate a realistic work highlight."""
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
    
    def _generate_skills(self) -> Dict[str, List[str]]:
        """Generate skills organized by category."""
        skills = {}
        for group, items in SKILL_GROUPS.items():
            n = random.randint(3, min(5, len(items)))
            skills[group] = random.sample(items, n)
        return skills

class ResumeRenderer:
    """Renders resume structures to various formats."""
    
    @staticmethod
    def to_markdown(resume: ResumeStruct) -> str:
        """Convert resume to markdown format."""
        lines = []
        lines.append(f"# {resume.name}")
        lines.append(f"Title: {resume.title}")
        lines.append("")
        lines.append("## Contact")
        lines.append(f"Email: {resume.email}")
        lines.append(f"Phone: {resume.phone}")
        lines.append(f"Location: {resume.location}")
        lines.append("")
        lines.append("## Education")
        for edu in resume.education:
            lines.append(f"- Institution: {edu.institution} | Degree: {edu.degree} | Field: {edu.field_of_study} | Year: {edu.year} | GPA: {edu.gpa} | Location: {edu.location}")
        lines.append("")
        lines.append("## Experience")
        for exp in resume.experience:
            lines.append(f"- Company: {exp.company} | Title: {exp.title} | Dates: {exp.start} - {exp.end} | Location: {exp.location}")
            lines.append(f"  Highlights:")
            for highlight in exp.highlights:
                lines.append(f"    - {highlight}")
        lines.append("")
        lines.append("## Skills")
        for group, items in resume.skills.items():
            lines.append(f"- {group}: {', '.join(items)}")
        lines.append("")
        return "\n".join(lines)
    
    @staticmethod
    def to_text(resume: ResumeStruct) -> str:
        """Convert resume to plain text format."""
        return ResumeRenderer.to_markdown(resume)
    
    @staticmethod
    def to_pdf(resume: ResumeStruct, output_path: Path) -> bool:
        """Convert resume to PDF format (requires reportlab)."""
        try:
            from reportlab.lib.pagesizes import LETTER
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import inch
            
            text = ResumeRenderer.to_text(resume)
            
            c = canvas.Canvas(str(output_path), pagesize=LETTER)
            width, height = LETTER
            left = 0.75 * inch
            top = height - 0.75 * inch
            line_height = 12
            x, y = left, top
            
            for raw_line in text.splitlines():
                line = raw_line.expandtabs(2)
                while len(line) > 0:
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
                return True
                
        except ImportError:
            logger.warning("reportlab not installed; cannot generate PDF")
            return False
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return False

def generate_resumes(output_dir: Path, count: int, make_pdf: bool = False) -> List[ResumeStruct]:
    """Generate multiple resumes and save them to the output directory."""
    generator = ResumeGenerator()
    renderer = ResumeRenderer()
    
    # Create output directories
    md_dir = output_dir / "markdown"
    txt_dir = output_dir / "text"
    pdf_dir = output_dir / "pdf"
    
    md_dir.mkdir(parents=True, exist_ok=True)
    txt_dir.mkdir(parents=True, exist_ok=True)
    
    if make_pdf:
        pdf_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate resumes
    resumes = generator.generate_multiple(count)
    
    for i, resume in enumerate(resumes):
        stem = f"resume_{i+1:02d}"
        
        # Save markdown
        md_path = md_dir / f"{stem}.md"
        md_path.write_text(renderer.to_markdown(resume), encoding="utf-8")
        
        # Save text
        txt_path = txt_dir / f"{stem}.txt"
        txt_path.write_text(renderer.to_text(resume), encoding="utf-8")
        
        # Save PDF if requested
        if make_pdf:
            pdf_path = pdf_dir / f"{stem}.pdf"
            if not renderer.to_pdf(resume, pdf_path):
                logger.warning(f"Failed to generate PDF for {stem}")
    
    logger.info(f"Generated {count} resumes in {output_dir}")
    return resumes
