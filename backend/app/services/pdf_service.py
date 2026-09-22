import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from pypdf import PdfReader

class PDFService:
    @staticmethod
    def extract_text_from_pdf(file_path: Path) -> str:
        """Extract clean plain text from all pages of a PDF file, preserving page order."""
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
        NOT_FOUND = "Author information could not be reliably extracted."
        if not lines:
            return NOT_FOUND

        # 1. Check for explicit author line prefixes in the header block
        author_patterns = [
            r'(?:By|Authors?|Author List|Authored by)[\s:]+([^\n\r]+)',
            r'(?:^|\n)(?:Authors?|Author Information)[\s:]*\n+([^\n\r]+)'
        ]
        
        for pat in author_patterns:
            m = re.search(pat, text[:2500], re.IGNORECASE)
            if m:
                candidate = m.group(1).strip()
                names = PDFService._extract_valid_names_from_text(candidate)
                if names:
                    return ", ".join(names)

        # 2. Locate the boundary where Abstract / Introduction / Keywords starts
        abstract_idx = -1
        for idx, line in enumerate(lines[:25]):
            if re.match(r'^(?:abstract|introduction|1\.?\s+introduction|keywords?|index terms?)\b', line, re.IGNORECASE):
                abstract_idx = idx
                break

        search_limit = abstract_idx if abstract_idx > 1 else min(10, len(lines))
        
        # Determine title lines to avoid treating title fragments as author names
        title_lines_count = 1
        if len(lines) > 2 and len(lines[0]) < 60 and not PDFService._extract_valid_names_from_text(lines[0]):
            if not PDFService._extract_valid_names_from_text(lines[1]):
                if not any(lines[1].lower().startswith(x) for x in ["by", "author", "dr.", "prof."]):
                    if not any(w in lines[1].lower() for w in ["university", "department", "email", "@"]):
                        if abstract_idx > 2:
                            title_lines_count = 2

        candidate_lines = []
        for line in lines[title_lines_count:search_limit]:
            sanitized = PDFService._sanitize_author_line(line)
            if sanitized:
                candidate_lines.append(sanitized)

        if candidate_lines:
            # Check individual candidate lines first for high-confidence person names
            for cand in candidate_lines:
                names = PDFService._extract_valid_names_from_text(cand)
                if names:
                    return ", ".join(names)

            # Otherwise test combined string
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

        # Remove academic titles and prefixes before splitting
        cleaned_text = re.sub(
            r'\b(?:Dr\.|Prof\.|Professor|Doctor|Mr\.|Ms\.|Mrs\.|Ph\.D\.|M\.Sc\.|B\.Sc\.|MD|IEEE Fellow|Senior Member|Member IEEE|Fellow IEEE)\b',
            '',
            sanitized,
            flags=re.IGNORECASE
        )

        # Split on commas, semicolons, 'and', or '&'
        raw_parts = [p.strip() for p in re.split(r'[,;]|\band\b|&', cleaned_text) if p.strip()]
        valid_names = []

        for part in raw_parts:
            # Clean inner spaces and symbols
            clean_part = re.sub(r'[\d\*\†\‡\§\^\¹\²\³\⁴\⁵\⁶\⁷\⁸\⁹\⁰]', '', part).strip()
            clean_part = re.sub(r'\s+', ' ', clean_part)
            
            if PDFService._is_valid_person_name(clean_part):
                if clean_part not in valid_names:
                    valid_names.append(clean_part)

        return valid_names[:12]

    @staticmethod
    def _sanitize_author_line(line: str) -> Optional[str]:
        """Strip affiliations, emails, numbers, and symbols from an author string."""
        if not line or len(line.strip()) < 2:
            return None

        lower = line.lower()
        exclude_phrases = [
            "school of", "research center", "index terms", "published in",
            "all rights reserved", "center for", "tech report", "under review",
            "university of", "department of", "faculty of", "institute of"
        ]
        if any(p in lower for p in exclude_phrases):
            return None

        exclude_words = {
            "university", "department", "institute", "faculty", "laboratory", "school",
            "college", "google", "deepmind", "microsoft", "meta", "openai",
            "stanford", "mit", "berkeley", "cambridge", "oxford", "ieee", "acm", "springer",
            "elsevier", "arxiv", "abstract", "introduction", "keywords",
            "proceedings", "conference", "journal", "volume", "vol.", "no.",
            "pp.", "doi:", "http", "www.", "copyright", "received", "accepted",
            "acknowledgement", "reference", "citation", "editor", "press", "inc.", "ltd", "corp",
            "usa", "uk", "china", "germany", "france", "canada", "india", "japan", "poland",
            "lab", "division", "preprint", "zielona", "zgora", "philology"
        }
        
        # Tokenize line words to check word boundaries accurately without false substring hits
        line_tokens = set(re.findall(r'\b[a-z0-9\.\:]+\b', lower))
        if any(w in line_tokens for w in exclude_words):
            return None

        # Remove email addresses like name@domain.com or {name1, name2}@domain.com
        line = re.sub(r'\{[^\}]+\}@\S+', '', line)
        line = re.sub(r'\S+@\S+', '', line)
        
        # Remove footnote markers & superscripts (1, 2, *, †, ‡, §, ^, ¹, ², ³, etc.)
        line = re.sub(r'[\d\*\†\‡\§\^\¹\²\³\⁴\⁵\⁶\⁷\⁸\⁹\⁰]', '', line)
        
        # Remove brackets, parentheses, curly braces
        line = re.sub(r'[\(\)\[\]\{\}]', '', line)
        
        # Normalize whitespace
        line = re.sub(r'[\t\r\n]', ' ', line)
        line = re.sub(r'\s+', ' ', line).strip()

        words = line.split()
        if 1 <= len(words) <= 18 and any(c.isalpha() for c in line):
            return line

        return None

    @staticmethod
    def _is_valid_person_name(name: str) -> bool:
        """Check if candidate string is a plausible person name supporting Unicode characters."""
        name = name.strip()
        if len(name) < 3 or len(name) > 60:
            return False
        
        words = name.split()
        if len(words) < 1 or len(words) > 5:
            return False
            
        # Must only contain Unicode letters, periods, apostrophes, hyphens, or spaces
        if not re.match(r"^[\w\.\'\-\s]+$", name, re.UNICODE) or any(c.isdigit() for c in name):
            return False
            
        # Exclude non-name stop words, research terms, and institutional words
        stopwords = {
            "the", "and", "for", "with", "from", "paper", "study", "analysis", "system", "model",
            "deep", "learning", "residual", "attention", "transformer", "network", "overview",
            "report", "survey", "method", "results", "table", "figure", "page", "section",
            "quantum", "neural", "framework", "architecture", "dataset", "empirical", "evaluation",
            "abstract", "introduction", "conclusion", "state", "estimation", "algorithm",
            "advanced", "learners", "mobile", "devices", "english", "language", "insights",
            "interview", "data", "qualitative", "quantitative", "investigation",
            "university", "department", "institute", "faculty", "laboratory", "school", "college",
            "zielona", "zgora", "philology", "poland"
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
        if has_abstract or has_refs:
            return "Research Paper"

        # Default fallback
        return "Academic Document"

    @staticmethod
    def segment_sections(text: str) -> Dict[str, str]:
        """
        Segment academic paper into recognized sections using robust heading patterns.
        Falls back to 'Not explicitly mentioned in the paper.' for missing sections.
        """
        NOT_FOUND = "Not explicitly mentioned in the paper."
        NOT_FOUND_DATASET = "Dataset information is not explicitly mentioned in the paper."
        NOT_FOUND_AUTHORS = "Author information could not be reliably extracted."
        
        if not text:
            return {
                "title": NOT_FOUND,
                "authors": NOT_FOUND_AUTHORS,
                "abstract": NOT_FOUND,
                "introduction": NOT_FOUND,
                "problem": NOT_FOUND,
                "motivation": NOT_FOUND,
                "objective": NOT_FOUND,
                "methodology": NOT_FOUND,
                "participants": NOT_FOUND,
                "data_collection": NOT_FOUND,
                "algorithms": NOT_FOUND,
                "technologies": NOT_FOUND,
                "dataset": NOT_FOUND_DATASET,
                "experimental_setup": NOT_FOUND,
                "results": NOT_FOUND,
                "findings": NOT_FOUND,
                "discussion": NOT_FOUND,
                "conclusion": NOT_FOUND,
                "limitations": NOT_FOUND,
                "future_work": NOT_FOUND,
                "references": NOT_FOUND
            }

        sections = {}
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 1. Extract Title
        title = NOT_FOUND
        if lines:
            first_line = lines[0]
            if len(first_line) > 10 and not first_line.lower().startswith("abstract"):
                title = first_line
                if len(title) < 45 and len(lines) > 1 and not lines[1].lower().startswith("abstract"):
                    title = f"{title} {lines[1]}"
            else:
                title = lines[0]
        sections["title"] = title[:250].strip()

        # 2. Extract Authors cleanly
        sections["authors"] = PDFService.extract_clean_authors(text, lines)

        # 3. Heading boundaries for multi-disciplinary academic papers and documents
        heading_patterns = [
            ("abstract", r'(?:^|\n)(?:[\d\.]+\s+)?(?:ABSTRACT|Abstract)\b[:\s]*\n?'),
            ("introduction", r'(?:^|\n)(?:[\d\.]+\s+)?(?:INTRODUCTION|Introduction|Background|Theoretical Background)\b[:\s]*\n?'),
            ("problem", r'(?:^|\n)(?:[\d\.]+\s+)?(?:PROBLEM STATEMENT|Problem Statement|Problem Formulation|Research Problem|The Problem)\b[:\s]*\n?'),
            ("motivation", r'(?:^|\n)(?:[\d\.]+\s+)?(?:MOTIVATION|Motivation|Background and Motivation|Rationale)\b[:\s]*\n?'),
            ("objective", r'(?:^|\n)(?:[\d\.]+\s+)?(?:OBJECTIVES?|Objectives?|Research Goals?|Aim of the Study|Aims? of the Research|Research Questions?|Purpose of the Study)\b[:\s]*\n?'),
            ("methodology", r'(?:^|\n)(?:[\d\.]+\s+)?(?:METHODOLOGY|Methodology|PROPOSED METHOD|Proposed Method|APPROACH|Approach|SYSTEM ARCHITECTURE|Architecture|System Design|Research Design|Method of Investigation|Procedure|Instrumentation|Methods)\b[:\s]*\n?'),
            ("participants", r'(?:^|\n)(?:[\d\.]+\s+)?(?:PARTICIPANTS|Participants|Subjects?|Sample|Informants|Respondents?|Participants and Setting)\b[:\s]*\n?'),
            ("data_collection", r'(?:^|\n)(?:[\d\.]+\s+)?(?:DATA COLLECTION(?: AND ANALYSIS)?|Data Collection(?: and Analysis)?|Instruments?|Interviews?|Questionnaires?|Data Sources?)\b[:\s]*\n?'),
            ("algorithms", r'(?:^|\n)(?:[\d\.]+\s+)?(?:ALGORITHMS?|Algorithms?|Model Architecture|Mathematical Formulation|Data Analysis Procedures?)\b[:\s]*\n?'),
            ("technologies", r'(?:^|\n)(?:[\d\.]+\s+)?(?:TECHNOLOGY STACK|Tools and Technologies|Implementation Details|Frameworks|Hardware and Software|Mobile Devices and Tools|Resources and Tools)\b[:\s]*\n?'),
            ("dataset", r'(?:^|\n)(?:[\d\.]+\s+)?(?:DATASET|Datasets?|Benchmark Datasets?|Corpus|Corpora)\b[:\s]*\n?'),
            ("experimental_setup", r'(?:^|\n)(?:[\d\.]+\s+)?(?:EXPERIMENTAL SETUP|Experimental Setup|Experiments|Evaluation Setup|Training Details|Context and Setting)\b[:\s]*\n?'),
            ("results", r'(?:^|\n)(?:[\d\.]+\s+)?(?:RESULTS|Results|EXPERIMENTAL RESULTS|Experimental Results|EVALUATION|Evaluation|Performance Analysis)\b[:\s]*\n?'),
            ("findings", r'(?:^|\n)(?:[\d\.]+\s+)?(?:FINDINGS(?: AND DISCUSSION)?|Findings(?: and Discussion)?|Key Findings|Observations?|Empirical Findings)\b[:\s]*\n?'),
            ("discussion", r'(?:^|\n)(?:[\d\.]+\s+)?(?:DISCUSSION(?: OF FINDINGS)?|Discussion(?: of Findings)?|Analysis of Results)\b[:\s]*\n?'),
            ("limitations", r'(?:^|\n)(?:[\d\.]+\s+)?(?:LIMITATIONS?(?: AND FUTURE (?:RESEARCH|WORK))?|Limitations?(?: and Future (?:Research|Work))?|Threats to Validity|Limitations of the Study)\b[:\s]*\n?'),
            ("future_work", r'(?:^|\n)(?:[\d\.]+\s+)?(?:FUTURE WORK|Future Work|Future Directions?|Future Research|Directions for Future Research)\b[:\s]*\n?'),
            ("conclusion", r'(?:^|\n)(?:[\d\.]+\s+)?(?:CONCLUSIONS?(?: AND PEDAGOGICAL IMPLICATIONS)?|Conclusions?(?: and Pedagogical Implications)?|Concluding Remarks|Pedagogical Implications|Implications for Teaching)\b[:\s]*\n?'),
            ("references", r'(?:^|\n)(?:[\d\.]+\s+)?(?:REFERENCES|References|BIBLIOGRAPHY|Bibliography)\b[:\s]*\n?')
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
            if name == "dataset":
                sections[name] = extracted_blocks.get(name, NOT_FOUND_DATASET)
            else:
                sections[name] = extracted_blocks.get(name, NOT_FOUND)

        return sections
