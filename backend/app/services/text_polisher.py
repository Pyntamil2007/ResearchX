import re
from typing import List, Optional

class TextPolisher:
    @staticmethod
    def clean_text_artifacts(text: str) -> str:
        """
        Remove OCR artifacts, citation brackets, broken hyphens, and normalize whitespace.
        """
        if not text:
            return ""
        
        # Remove citation brackets like [1], [2, 3], [4-7], [12]
        t = re.sub(r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]', '', text)
        t = re.sub(r'\[\s*\d+\s*[-–—]\s*\d+\s*\]', '', t)
        
        # Remove parenthetical author citations like (Smith et al., 2020)
        t = re.sub(r'\([A-Z][a-zA-Z\s]+(?:et al\.?)?,?\s*\d{4}\)', '', t)
        
        # Fix hyphenated words broken across line breaks: "algo-\n rithm" -> "algorithm"
        t = re.sub(r'(\b[a-zA-Z]+)-\s*\n\s*([a-zA-Z]+\b)', r'\1\2', t)
        
        # Replace newlines with spaces
        t = re.sub(r'[\r\n\t]+', ' ', t)
        
        # Remove orphan punctuation or isolated symbols
        t = re.sub(r'\s+([,.:;?!])', r'\1', t)
        t = re.sub(r'([,.:;?!])\1+', r'\1', t)
        
        # Normalize multiple spaces
        t = re.sub(r'\s{2,}', ' ', t)
        
        return t.strip()

    @staticmethod
    def polish_sentence(sentence: str) -> str:
        """
        Ensure a single sentence is capitalized, clean, and properly punctuated with a terminal period.
        """
        s = sentence.strip()
        if not s:
            return "Not explicitly mentioned in the paper."
        if s in [
            "Not explicitly mentioned in the paper.",
            "Dataset information is not explicitly mentioned in the paper.",
            "Author information could not be reliably extracted.",
            "No suitable numerical data was found in the paper for this visualization.",
            "Information not available in the document.",
            "Information not available in the paper."
        ]:
            return s
        
        # Capitalize first character
        if len(s) > 0:
            s = s[0].upper() + s[1:]
        
        # Ensure terminal punctuation
        if not s.endswith(('.', '!', '?')):
            s = s + '.'
            
        return s

    @staticmethod
    def format_neat_paragraph(text: str, max_sentences: int = 4) -> str:
        """
        Transform raw extracted text into neat, readable, academic-grade sentences.
        """
        if not text:
            return "Not explicitly mentioned in the paper."
            
        text_str = text.strip()
        if text_str in [
            "Not explicitly mentioned in the paper.",
            "Dataset information is not explicitly mentioned in the paper.",
            "Author information could not be reliably extracted.",
            "No suitable numerical data was found in the paper for this visualization.",
            "Information not available in the document.",
            "Information not available in the paper.",
            "Not specified in the document."
        ]:
            return text_str

        cleaned = TextPolisher.clean_text_artifacts(text)
        
        # Protect common abbreviations from premature sentence splitting
        abbrevs = {
            r'\be\.g\.': 'e_g_temp',
            r'\bi\.e\.': 'i_e_temp',
            r'\bet al\.': 'et_al_temp',
            r'\bDr\.': 'Dr_temp',
            r'\bProf\.': 'Prof_temp',
            r'\bFig\.': 'Fig_temp',
            r'\bTab\.': 'Tab_temp',
            r'\bvs\.': 'vs_temp',
            r'\bVol\.': 'Vol_temp',
            r'\bNo\.': 'No_temp'
        }
        for pattern, replacement in abbrevs.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

        # Split on sentence boundaries
        raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned) if len(s.strip()) > 10]

        # Restore abbreviations
        rev_abbrevs = {
            'e_g_temp': 'e.g.',
            'i_e_temp': 'i.e.',
            'et_al_temp': 'et al.',
            'Dr_temp': 'Dr.',
            'Prof_temp': 'Prof.',
            'Fig_temp': 'Fig.',
            'Tab_temp': 'Tab.',
            'vs_temp': 'vs.',
            'Vol_temp': 'Vol.',
            'No_temp': 'No.'
        }

        polished_sentences: List[str] = []
        for s in raw_sentences:
            for temp, orig in rev_abbrevs.items():
                s = s.replace(temp, orig)
            
            # Filter out noisy formula fragments or orphan headers
            if len(s.split()) < 3 and not s.endswith('.'):
                continue
            
            polished = TextPolisher.polish_sentence(s)
            if polished not in polished_sentences:
                polished_sentences.append(polished)
            
            if len(polished_sentences) >= max_sentences:
                break

        if not polished_sentences:
            cleaned_single = TextPolisher.polish_sentence(cleaned[:300])
            return cleaned_single

        return " ".join(polished_sentences)
