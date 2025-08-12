"""
Resume parser module for extracting structured data from resume files.
Supports markdown and text formats that follow the provided sample layout.
"""

import re
import logging
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from models import ResumeStruct, Education, Experience

logger = logging.getLogger(__name__)


class ResumeParser:
    """Parser for resume files in markdown and text formats (sample-compatible)."""

    def __init__(self):
        # Headings (tolerate ## or ###)
        self.h_contact = re.compile(r"^#{2,3}\s*Contact\s*$", re.I)
        self.h_education = re.compile(r"^#{2,3}\s*Education\s*$", re.I)
        self.h_experience = re.compile(r"^#{2,3}\s*Experience\s*$", re.I)
        self.h_skills = re.compile(r"^#{2,3}\s*Skills\s*$", re.I)

        # Top matter
        self.rx_name = re.compile(r"^#\s*(.+)$")                       # e.g., "# Emerson Wilson"
        self.rx_title = re.compile(r"^Title:\s*(.+)$", re.I)           # e.g., "Title: Backend Engineer"

        # Contact lines inside Contact section
        self.rx_kv = re.compile(r"^(\w+):\s*(.+)$")                    # e.g., "Email: foo@bar.com"

        # Education / Experience / Skills line shapes
        # Education item line: "- Institution: ... | Degree: ... | Field: ... | Year: 2023 | GPA: 3.9 | Location: ..."
        self.rx_edu_item = re.compile(r"^-\s*(.+)$")
        # Experience header line: "- Company: ... | Title: ... | Dates: Mon YYYY - Mon YYYY|Present | Location: ..."
        self.rx_exp_item = re.compile(r"^-\s*(.+)$")
        self.rx_highlights_header = re.compile(r"^\s*Highlights:\s*$", re.I)
        self.rx_bullet = re.compile(r"^\s*-\s+(.*\S)\s*$")             # indented "- " bullets

        # Skills line: "- Group: A, B, C"
        self.rx_skill_line = re.compile(r"^-\s*([^:]+):\s*(.+)$")

    # ---------- Public API ----------

    def parse_file(self, file_path: Path) -> ResumeStruct:
        try:
            content = file_path.read_text(encoding="utf-8")
            return self.parse_content(content)
        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            raise RuntimeError(f"Failed to parse resume file: {e}")

    def parse_markdown(self, content: str) -> ResumeStruct:
        return self.parse_content(content)

    def parse_content(self, content: str) -> ResumeStruct:
        lines = content.splitlines()

        name = self._extract_name(lines)
        title = self._extract_title(lines)

        email, phone, location = self._extract_contact(lines)
        education = self._extract_education(lines)
        experience = self._extract_experience(lines)
        skills = self._extract_skills(lines)

        return ResumeStruct(
            name=name or "Unknown",
            title=title or "Professional",
            email=email or "",
            phone=phone or "",
            location=location or "",
            education=education,
            experience=experience,
            skills=skills,
        )

    # ---------- Extractors ----------

    def _extract_name(self, lines: List[str]) -> Optional[str]:
        for line in lines:
            m = self.rx_name.match(line.strip())
            if m:
                return m.group(1).strip()
        return None

    def _extract_title(self, lines: List[str]) -> Optional[str]:
        for line in lines:
            m = self.rx_title.match(line.strip())
            if m:
                return m.group(1).strip()
        return None

    def _section_bounds(self, lines: List[str], header_rx: re.Pattern) -> Optional[range]:
        """Return range(start, end) of a section body (between this header and the next header)."""
        start = end = None
        for i, line in enumerate(lines):
            if header_rx.match(line.strip()):
                start = i + 1
                break
        if start is None:
            return None
        # find next top-level section header
        for j in range(start, len(lines)):
            if (
                self.h_contact.match(lines[j].strip())
                or self.h_education.match(lines[j].strip())
                or self.h_experience.match(lines[j].strip())
                or self.h_skills.match(lines[j].strip())
            ):
                end = j
                break
        if end is None:
            end = len(lines)
        return range(start, end)

    def _extract_contact(self, lines: List[str]) -> (Optional[str], Optional[str], Optional[str]):
        email = phone = location = None
        rng = self._section_bounds(lines, self.h_contact)
        if rng is None:
            # fall back: scan all lines (lenient)
            for line in lines:
                m = self.rx_kv.match(line.strip())
                if not m:
                    continue
                k, v = m.group(1).lower(), m.group(2).strip()
                if k == "email":
                    email = v
                elif k == "phone":
                    phone = v
                elif k == "location":
                    location = v
            return email, phone, location

        for i in rng:
            s = lines[i].strip()
            m = self.rx_kv.match(s)
            if not m:
                continue
            k, v = m.group(1).lower(), m.group(2).strip()
            if k == "email":
                email = v
            elif k == "phone":
                phone = v
            elif k == "location":
                location = v
        return email, phone, location

    def _parse_pipe_kv(self, text: str) -> Dict[str, str]:
        """Parse 'Key: Val | Key2: Val2 | ...' into a dict (keys lowercased)."""
        parts = [p.strip() for p in text.split("|")]
        out = {}
        for part in parts:
            if ":" in part:
                k, v = part.split(":", 1)
                out[k.strip().lower()] = v.strip()
        return out

    def _extract_education(self, lines: List[str]) -> List[Education]:
        result: List[Education] = []
        rng = self._section_bounds(lines, self.h_education)
        if rng is None:
            return result

        for i in rng:
            s = lines[i].rstrip()
            m = self.rx_edu_item.match(s)
            if not m:
                continue
            text = m.group(1).strip()  # everything after "- "
            kv = self._parse_pipe_kv(text)
            inst = kv.get("institution", "")
            degree = kv.get("degree", "")
            field = kv.get("field", "")
            year = self._to_int(kv.get("year"))
            gpa = self._to_float(kv.get("gpa"))
            loc = kv.get("location", "")
            result.append(
                Education(
                    institution=inst,
                    degree=degree,
                    field_of_study=field,
                    year=year if year is not None else 0,
                    gpa=gpa,
                    location=loc,
                )
            )
        return result

    def _extract_experience(self, lines: List[str]) -> List[Experience]:
        result: List[Experience] = []
        rng = self._section_bounds(lines, self.h_experience)
        if rng is None:
            return result

        current: Optional[Experience] = None
        collecting_highlights = False

        for i in rng:
            raw = lines[i].rstrip()
            s = raw.strip()

            # New experience item line?
            m_item = self.rx_exp_item.match(s)
            if m_item and ("Company:" in s or "Title:" in s) and ("Dates:" in s or "Location:" in s):
                # stash previous
                if current:
                    result.append(current)
                kv = self._parse_pipe_kv(m_item.group(1).strip())
                company = kv.get("company", "")
                title = kv.get("title", "")
                dates = kv.get("dates", "")
                loc = kv.get("location", "")

                start, end = "", ""
                if dates:
                    if " - " in dates:
                        start, end = [x.strip() for x in dates.split(" - ", 1)]
                    else:
                        start = dates.strip()

                current = Experience(
                    company=company,
                    title=title,
                    start=start,
                    end=end,
                    location=loc,
                    highlights=[],
                )
                collecting_highlights = False
                continue

            # Highlights header?
            if self.rx_highlights_header.match(s):
                collecting_highlights = True
                continue

            # Collect highlight bullets (indented "- ")
            if collecting_highlights and current:
                m_b = self.rx_bullet.match(raw)
                if m_b:
                    current.highlights.append(m_b.group(1).strip())
                else:
                    # stop collecting when a non-bullet non-empty line appears
                    if s and not s.startswith("-"):
                        collecting_highlights = False

        if current:
            result.append(current)
        return result

    def _extract_skills(self, lines: List[str]) -> Dict[str, List[str]]:
        skills: Dict[str, List[str]] = {}
        rng = self._section_bounds(lines, self.h_skills)
        if rng is None:
            return skills

        for i in rng:
            s = lines[i].strip()
            if not s:
                continue
            m = self.rx_skill_line.match(s)
            if not m:
                continue
            group, items = m.group(1).strip(), m.group(2).strip()
            skills[group] = [x.strip() for x in items.split(",") if x.strip()]
        return skills

    # ---------- helpers ----------

    @staticmethod
    def _to_int(s: Optional[str]) -> Optional[int]:
        if s is None:
            return None
        s = s.strip()
        if not s:
            return None
        try:
            return int(s)
        except Exception:
            return None

    @staticmethod
    def _to_float(s: Optional[str]) -> Optional[float]:
        if s is None:
            return None
        s = s.strip()
        if not s:
            return None
        try:
            return float(s)
        except Exception:
            return None


# Global parser instance
_parser = None

def get_parser() -> ResumeParser:
    global _parser
    if _parser is None:
        _parser = ResumeParser()
    return _parser
