import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from models import JobDescription, CandidateMatch

# -------------------------
# Text + skills utilities
# -------------------------
_STOP = set("""
the a an and or with to in of for on at by from your our you we they is are be this that will as
""".split())

_TOKEN_RE = re.compile(r"[a-z0-9+#.\-]+")

def _norm(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    return re.sub(r"\s+", " ", s).strip()

def _tokenize(s: str) -> List[str]:
    return _TOKEN_RE.findall(_norm(s))

def _cosine(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    # A: (n, d), B: (m, d) -> (n, m)
    A = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-9)
    B = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-9)
    return A @ B.T

def _skills_from_resume_data(data: Dict[str, Any]) -> List[str]:
    skills = data.get("skills") or {}
    out: List[str] = []
    if isinstance(skills, dict):
        for _, arr in skills.items():
            if isinstance(arr, list):
                out.extend(arr)
    elif isinstance(skills, list):
        out.extend(skills)
    # normalize
    return [t for t in (_norm(x) for x in out) if t]

def _skills_from_jd(job: JobDescription) -> List[str]:
    # lightweight extractor; replace with curated skill list if you have one
    text = "\n".join([
        job.title or "",
        job.company or "",
        job.description or "",
        "\n".join(job.requirements or []),
        "\n".join(job.preferred_skills or []),
    ])
    toks = [t for t in _tokenize(text) if t not in _STOP and not t.isdigit()]
    return sorted(set(toks))

def _jaccard(a: List[str], b: List[str]) -> float:
    A, B = set(a), set(b)
    if not A and not B:
        return 0.0
    return len(A & B) / max(1, len(A | B))

def _title_align(jd_title: str, cand_title: str) -> float:
    if not jd_title or not cand_title:
        return 0.0
    a = set(_tokenize(jd_title))
    b = set(_tokenize(cand_title))
    if not a or not b:
        return 0.0
    return len(a & b) / max(3, len(a))

# -------------------------
# File loading
# -------------------------
def _load_resume_jsons(parsed_path: Path) -> List[Dict[str, Any]]:
    """
    Accepts a directory of per-resume JSONs (e.g., llm_parsed_resumes/*.json)
    or a single combined.json. Skips *.error.json.
    """
    out: List[Dict[str, Any]] = []

    if parsed_path.is_file():
        data = json.loads(parsed_path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "results" in data:
            out = data["results"]
        else:
            out = [data]
        return out

    for jf in sorted(parsed_path.glob("*.json")):
        if jf.name.endswith(".error.json") or jf.name == "combined.json":
            continue
        try:
            out.append(json.loads(jf.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out

# -------------------------
# Candidate text builder
# -------------------------
def _candidate_summary_text(res: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Prefer model-generated summary; if missing, build a surrogate from title/experience/skills.
    Returns (text, data_dict).
    
    This function handles both data formats:
    - Direct resume data (legacy format)
    - Nested data under 'data' key (ParsedResume format from resume_generator_parser)
    """
    # Handle both data formats: direct resume data or nested under 'data' key
    # This makes it compatible with resume_generator_parser output
    data = res.get("data", res)  # support either schema
    summary = data.get("summary") or ""
    title = data.get("title") or ""

    if not summary:
        parts = [title]
        # fold in a bit of experience if needed
        exps = data.get("experience", [])
        if isinstance(exps, list) and exps:
            parts.append("; ".join([f"{x.get('title','')} at {x.get('company','')}" for x in exps[:3]]))
        sk = _skills_from_resume_data(data)
        if sk:
            parts.append("Skills: " + ", ".join(sk[:20]))
        summary = ". ".join([p for p in parts if p]).strip()

    return summary, data

# -------------------------
# SemanticMatcher
# -------------------------
class SemanticMatcher:
    """
    Sentence-BERT based matcher with an optional skill-blended + title score.
    """
    def __init__(
        self,
        sbert_model: str = "sentence-transformers/all-mpnet-base-v2",
        device: Optional[str] = None,
        blend_alpha: float = 0.25,     # weight for skills Jaccard vs embedding similarity
        title_weight: float = 0.10,    # small extra weight for title alignment
    ):
        self.model_name = sbert_model
        self.model = SentenceTransformer(self.model_name, device=device or None)
        self.blend_alpha = float(blend_alpha)
        self.title_weight = float(title_weight)

    def match_candidates(
        self,
        job: JobDescription,
        parsed_resumes_dir: str,
        top_n: int = 10,
    ) -> List[CandidateMatch]:
        """
        Rank candidates from a directory (or combined.json) against the job.
        Returns a list[CandidateMatch] sorted by score desc.
        """
        root = Path(parsed_resumes_dir)
        items = _load_resume_jsons(root)
        if not items:
            return []

        # Build JD text + skills
        jd_text = "\n".join([
            job.title or "",
            job.company or "",
            job.description or "",
            "Requirements:\n" + "\n".join(job.requirements or []),
            "Preferred:\n" + "\n".join(job.preferred_skills or []),
        ]).strip()
        jd_skills = _skills_from_jd(job)

        # Candidate texts and metadata
        cand_texts: List[str] = []
        metas: List[Dict[str, Any]] = []
        filenames: List[str] = []
        for res in items:
            text, data = _candidate_summary_text(res)
            if not text:
                continue
            cand_texts.append(text)
            metas.append(data)
            src = res.get("source_pdf") or res.get("filename") or ""
            filenames.append(Path(src).name if src else "")

        if not cand_texts:
            return []

        # Embeddings
        jd_emb = self.model.encode([jd_text], show_progress_bar=False)
        cand_embs = self.model.encode(cand_texts, batch_size=64, show_progress_bar=False)

        # Cosine similarity
        sims = _cosine(cand_embs, jd_emb)[:, 0]  # shape (N,)

        # Skills Jaccard + Title alignment
        skill_sims = np.zeros(len(metas), dtype=float)
        title_sims = np.zeros(len(metas), dtype=float)
        for i, meta in enumerate(metas):
            rskills = _skills_from_resume_data(meta)
            skill_sims[i] = _jaccard(jd_skills, rskills)
            title_sims[i] = _title_align(job.title, meta.get("title", ""))

        # Final blended score
        final = (1.0 - self.blend_alpha) * sims + self.blend_alpha * skill_sims + self.title_weight * title_sims

        # Package results
        ordered_idx = np.argsort(-final)
        results: List[CandidateMatch] = []
        for idx in ordered_idx[:top_n]:
            meta = metas[idx]
            results.append(
                CandidateMatch(
                    name=meta.get("name", ""),
                    filename=filenames[idx],
                    title=meta.get("title", ""),
                    match_score=float(final[idx]),
                    skills_match=sorted(set(_skills_from_resume_data(meta)))[:25],
                    summary=meta.get("summary", cand_texts[idx]),
                )
            )
        return results
