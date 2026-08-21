import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from pypdf import PdfReader

class PDFService:
    @staticmethod
    def extract_text_from_pdf(file_path: Path) -> str:
        """Extract clean plain text from a PDF file."""
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        reader = PdfReader(str(file_path))
        extracted_pages = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_pages.append(text)
                
        full_text = "\n\n".join(extracted_pages)
        return PDFService.clean_text(full_text)

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalize whitespace, remove line hyphens, and strip excessive blank lines."""
        if not text:
            return ""
        
        # Replace non-breaking spaces and unusual whitespace
        text = text.replace('\xa0', ' ').replace('\r\n', '\n').replace('\r', '\n')
        
        # Fix hyphenated line breaks (e.g. "approxi-\nmation" -> "approximation")
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        
        # Remove standalone page numbers or headers like "Page 1 of 12"
        text = re.sub(r'(?i)\bpage\s+\d+(\s+of\s+\d+)?\b', '', text)
        
        # Collapse multiple spaces into one, keeping newlines
        lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]
        
        # Collapse multiple empty lines
        cleaned_lines = []
        empty_count = 0
        for line in lines:
            if not line:
                empty_count += 1
                if empty_count <= 2:
                    cleaned_lines.append("")
            else:
                empty_count = 0
                cleaned_lines.append(line)
                
        return "\n".join(cleaned_lines).strip()

    @staticmethod
    def extract_clean_authors(text: str, lines: List[str]) -> str:
        """
        Accurately extract author names from the paper's first page / title section.
        Strictly excludes emails, affiliations, universities, citations, footnotes,
        acknowledgements, references, and institution names.
        """
        NOT_FOUND = "Information not available"
        if not lines:
            return NOT_FOUND

        # 1. Check for explicit author line prefixes in the header block
        author_patterns = [
            r'(?:By|Authors?|Author List|Authored by)[\s:]+([^\n\r]+)',
            r'(?:^|\n)(?:Authors?|Author Information)[\s:]*\n+([^\n\r]+)'
        ]
        
        for pat in author_patterns:
            m = re.search(pat, text[:1500], re.IGNORECASE)
            if m:
                candidate = m.group(1).strip()
                names = PDFService._extract_valid_names_from_text(candidate)
                if names:
                    return ", ".join(names)

        # 2. Look exclusively in the candidate block between Title and Abstract / Introduction
        abstract_idx = -1
        for idx, line in enumerate(lines[:15]):
            if re.match(r'^(?:abstract|introduction|1\.?\s+introduction)\b', line, re.IGNORECASE):
                abstract_idx = idx
                break

        search_limit = abstract_idx if abstract_idx > 1 else min(6, len(lines))
        candidate_lines = []
        for line in lines[1:search_limit]:
            sanitized = PDFService._sanitize_author_line(line)
            if sanitized:
                candidate_lines.append(sanitized)

        if candidate_lines:
            combined = " ".join(candidate_lines)
            names = PDFService._extract_valid_names_from_text(combined)
            if names:
                return ", ".join(names)

        return NOT_FOUND

    @staticmethod
    def _extract_valid_names_from_text(text: str) -> List[str]:
        """Extract individual person names from candidate author text."""
        sanitized = PDFService._sanitize_author_line(text)
        if not sanitized:
            return []

        # Split on commas, semicolons, or 'and'
        raw_parts = [p.strip() for p in re.split(r'[,;]|\band\b|&', sanitized) if p.strip()]
        valid_names = []

        for part in raw_parts:
            # Clean inner spaces and symbols
            clean_part = re.sub(r'[\d\*\†\‡\§\^]', '', part).strip()
            clean_part = re.sub(r'\s+', ' ', clean_part)
            
            if PDFService._is_valid_person_name(clean_part):
                if clean_part not in valid_names:
                    valid_names.append(clean_part)

        return valid_names[:10]

    @staticmethod
    def _sanitize_author_line(line: str) -> Optional[str]:
        """Strip affiliations, emails, numbers, and symbols from an author string."""
        if not line or len(line.strip()) < 2:
            return None

        lower = line.lower()
        exclude_words = [
            "university", "department", "institute", "faculty", "laboratory", "school of",
            "college", "research center", "google", "deepmind", "microsoft", "meta", "openai",
            "stanford", "mit", "berkeley", "cambridge", "oxford", "ieee", "acm", "springer",
            "elsevier", "arxiv", "abstract", "introduction", "keywords", "index terms",
            "published in", "proceedings", "conference", "journal", "volume", "vol.", "no.",
            "pp.", "doi:", "http", "www.", "copyright", "all rights reserved", "received", "accepted",
            "acknowledgement", "reference", "citation", "editor", "press", "inc.", "ltd", "corp",
            "usa", "uk", "china", "germany", "france", "canada", "india", "japan", "center for"
        ]
        
        if any(w in lower for w in exclude_words):
            return None

        # Remove email addresses like name@domain.com or {name1, name2}@domain.com
        line = re.sub(r'\{[^\}]+\}@\S+', '', line)
        line = re.sub(r'\S+@\S+', '', line)
        
        # Remove footnote markers & superscripts (1, 2, *, †, ‡, §, ^)
        line = re.sub(r'[\d\*\†\‡\§\^]', '', line)
        
        # Remove brackets, parentheses, curly braces
        line = re.sub(r'[\(\)\[\]\{\}]', '', line)
        
        # Normalize whitespace
        line = re.sub(r'[\t\r\n]', ' ', line)
        line = re.sub(r'\s+', ' ', line).strip()

        words = line.split()
        if 1 <= len(words) <= 15 and any(c.isalpha() for c in line):
            return line

        return None

    @staticmethod
    def _is_valid_person_name(name: str) -> bool:
        """Check if candidate string is a plausible person name."""
        name = name.strip()
        if len(name) < 3 or len(name) > 50:
            return False
        
        words = name.split()
        if len(words) < 1 or len(words) > 5:
            return False
            
        # Must only contain alphabetical characters, hyphens, periods, or apostrophes
        if not re.match(r"^[A-Za-z\.\'\-\s]+$", name):
            return False
            
        # Exclude non-name stop words and domain words
        stopwords = {
            "the", "and", "for", "with", "from", "paper", "study", "analysis", "system", "model",
            "deep", "learning", "residual", "attention", "transformer", "network", "overview",
            "report", "survey", "method", "results", "table", "figure", "page", "section"
        }
        if any(w.lower() in stopwords for w in words):
            return False
            
        # At least one word should start with a capital letter
        if not any(w[0].isupper() for w in words if w):
            return False

        return True

    @staticmethod
    def detect_document_type(text: str, total_pages: int = 1) -> str:
        """
        Accurately detect whether document is a Research Paper, Review Paper, Conference Paper,
        Journal Paper, Academic Book, Book Chapter, Technical Report, or Academic Document.
        """
        lower = text[:4000].lower()

        # 1. Academic Book / Book Chapter
        if "isbn" in lower or re.search(r'\bchapter\s+\d+\b', lower) or "table of contents" in lower or total_pages > 45:
            if re.search(r'\bchapter\s+\d+\b', lower):
                return "Book Chapter"
            return "Academic Book"

        # 2. Review / Survey Paper
        if "a survey of" in lower or "a comprehensive survey" in lower or "a review of" in lower or "systematic review" in lower or "literature review" in lower:
            return "Review Paper"

        # 3. Conference Paper
        if "proceedings of" in lower or "conference on" in lower or "international conference" in lower or "symposium on" in lower or "cvpr" in lower or "neurips" in lower or "icml" in lower or "iclr" in lower:
            return "Conference Paper"

        # 4. Journal Paper
        if "journal of" in lower or "transactions on" in lower or "ieee transactions" in lower or "acm transactions" in lower:
            return "Journal Paper"

        # 5. Technical Report
        if "technical report" in lower or "white paper" in lower or "tr-" in lower:
            return "Technical Report"

        # 6. Standard Research Paper (Has Abstract + Methodology / Results / References)
        has_abstract = "abstract" in lower
        has_refs = "references" in lower or "bibliography" in lower
        if has_abstract and has_refs:
            return "Research Paper"

        # Default fallback
        return "Academic Document"

    @staticmethod
    def segment_sections(text: str) -> Dict[str, str]:
        """
        Segment academic paper into recognized sections using robust heading patterns.
        Falls back to 'Information not available in the paper.' for missing sections.
        """
        NOT_FOUND = "Information not available in the paper."
        
        if not text:
            return {sec: NOT_FOUND for sec in [
                "title", "authors", "abstract", "introduction", "problem", "motivation",
                "objective", "methodology", "algorithms", "technologies", "dataset",
                "experimental_setup", "results", "discussion", "conclusion",
                "limitations", "future_work", "references"
            ]}

        sections = {}
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 1. Extract Title
        title = NOT_FOUND
        if lines:
            first_line = lines[0]
            if len(first_line) > 10 and not first_line.lower().startswith("abstract"):
                title = first_line
                if len(title) < 35 and len(lines) > 1 and not lines[1].lower().startswith("abstract"):
                    title = f"{title} {lines[1]}"
            else:
                title = lines[0]
        sections["title"] = title[:250].strip()

        # 2. Extract Authors cleanly
        sections["authors"] = PDFService.extract_clean_authors(text, lines)

        # 3. Heading boundaries for academic papers and documents
        heading_patterns = [
            ("abstract", r'(?:^|\n)(?:[\d\.]+\s+)?(?:ABSTRACT|Abstract)\b[:\s]*'),
            ("introduction", r'(?:^|\n)(?:[\d\.]+\s+)?(?:INTRODUCTION|Introduction|1\.?\s+Introduction)\b[:\s]*'),
            ("problem", r'(?:^|\n)(?:[\d\.]+\s+)?(?:PROBLEM STATEMENT|Problem Statement|Problem Formulation|Research Problem)\b[:\s]*'),
            ("motivation", r'(?:^|\n)(?:[\d\.]+\s+)?(?:MOTIVATION|Motivation|Background and Motivation)\b[:\s]*'),
            ("objective", r'(?:^|\n)(?:[\d\.]+\s+)?(?:OBJECTIVES?|Objectives?|Research Goals?)\b[:\s]*'),
            ("methodology", r'(?:^|\n)(?:[\d\.]+\s+)?(?:METHODOLOGY|Methodology|PROPOSED METHOD|Proposed Method|APPROACH|Approach|SYSTEM ARCHITECTURE|Architecture|System Design)\b[:\s]*'),
            ("algorithms", r'(?:^|\n)(?:[\d\.]+\s+)?(?:ALGORITHMS?|Algorithms?|Model Architecture|Mathematical Formulation)\b[:\s]*'),
            ("technologies", r'(?:^|\n)(?:[\d\.]+\s+)?(?:TECHNOLOGY STACK|Tools and Technologies|Implementation Details|Frameworks)\b[:\s]*'),
            ("dataset", r'(?:^|\n)(?:[\d\.]+\s+)?(?:DATASET|Datasets?|Data Collection|Benchmark Datasets?)\b[:\s]*'),
            ("experimental_setup", r'(?:^|\n)(?:[\d\.]+\s+)?(?:EXPERIMENTAL SETUP|Experimental Setup|Experiments|Evaluation Setup|Training Details)\b[:\s]*'),
            ("results", r'(?:^|\n)(?:[\d\.]+\s+)?(?:RESULTS|Results|EXPERIMENTAL RESULTS|Experimental Results|EVALUATION|Evaluation|Performance Analysis)\b[:\s]*'),
            ("discussion", r'(?:^|\n)(?:[\d\.]+\s+)?(?:DISCUSSION|Discussion|Analysis of Results)\b[:\s]*'),
            ("limitations", r'(?:^|\n)(?:[\d\.]+\s+)?(?:LIMITATIONS?|Limitations?|Threats to Validity)\b[:\s]*'),
            ("future_work", r'(?:^|\n)(?:[\d\.]+\s+)?(?:FUTURE WORK|Future Work|Future Directions?)\b[:\s]*'),
            ("conclusion", r'(?:^|\n)(?:[\d\.]+\s+)?(?:CONCLUSION|Conclusion|Conclusions and Future Work|Concluding Remarks)\b[:\s]*'),
            ("references", r'(?:^|\n)(?:[\d\.]+\s+)?(?:REFERENCES|References|BIBLIOGRAPHY|Bibliography)\b[:\s]*')
        ]

        # Find match indices
        matches = []
        for name, pattern in heading_patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                matches.append((m.start(), m.end(), name))

        # Sort matches by start position
        matches.sort(key=lambda x: x[0])

        # Extract content between headings
        extracted_blocks = {}
        for i, (start, end, name) in enumerate(matches):
            next_start = matches[i + 1][0] if i + 1 < len(matches) else len(text)
            content = text[end:next_start].strip()
            if name not in extracted_blocks or len(content) > len(extracted_blocks[name]):
                extracted_blocks[name] = content

        for name, _ in heading_patterns:
            sections[name] = extracted_blocks.get(name, NOT_FOUND)

        return sections
