import re
from typing import Dict, Any, Optional
from app.services.text_polisher import TextPolisher

class SummaryService:
    @staticmethod
    def generate_easy_summary(sections: Dict[str, str], domain: str) -> Dict[str, str]:
        """
        Generate a clear, beginner-friendly 6-point summary strictly grounded
        in the extracted research sections without inventing facts, formatted in neat sentences.
        """
        NOT_FOUND = "Not explicitly mentioned in the paper."
        
        def is_valid_section(val: Optional[str]) -> bool:
            if not val or not isinstance(val, str):
                return False
            low = val.strip().lower()
            return low not in [
                "not explicitly mentioned in the paper.",
                "dataset information is not explicitly mentioned in the paper.",
                "information not available in the paper.",
                "information not available in the document.",
                "information not available",
                ""
            ]

        abstract = sections.get("abstract") if is_valid_section(sections.get("abstract")) else None
        intro = sections.get("introduction") if is_valid_section(sections.get("introduction")) else None
        problem = sections.get("problem") if is_valid_section(sections.get("problem")) else None
        motivation = sections.get("motivation") if is_valid_section(sections.get("motivation")) else None
        objective = sections.get("objective") if is_valid_section(sections.get("objective")) else None
        methodology = sections.get("methodology") if is_valid_section(sections.get("methodology")) else None
        results = sections.get("results") if is_valid_section(sections.get("results")) else None
        conclusion = sections.get("conclusion") if is_valid_section(sections.get("conclusion")) else None
        
        # 1. What is this paper about?
        about = NOT_FOUND
        if abstract:
            about = TextPolisher.format_neat_paragraph(abstract, max_sentences=2)
        elif intro:
            about = TextPolisher.format_neat_paragraph(intro, max_sentences=2)

        # 2. What problem does it solve?
        problem_solved = NOT_FOUND
        if problem:
            problem_solved = TextPolisher.format_neat_paragraph(problem, max_sentences=2)
        elif intro:
            problem_match = re.search(r'(?:tackle|address|challenge|problem of|limitation of|bottleneck|inability to)\s+([^.!?]+[.!?])', intro, re.IGNORECASE)
            if problem_match:
                problem_solved = TextPolisher.polish_sentence(f"The study addresses the issue where {problem_match.group(1).strip()}")
            elif abstract:
                problem_solved = TextPolisher.format_neat_paragraph(abstract, max_sentences=2)
        elif abstract:
            problem_solved = TextPolisher.format_neat_paragraph(abstract, max_sentences=2)

        # 3. Why was the research conducted?
        why_conducted = NOT_FOUND
        if motivation:
            why_conducted = TextPolisher.format_neat_paragraph(motivation, max_sentences=2)
        elif objective:
            why_conducted = TextPolisher.format_neat_paragraph(objective, max_sentences=2)
        elif intro:
            mot_match = re.search(r'(?:motivated by|crucial because|essential to|aim to|need for)\s+([^.!?]+[.!?])', intro, re.IGNORECASE)
            if mot_match:
                why_conducted = TextPolisher.polish_sentence(f"This research was conducted because {mot_match.group(1).strip()}")

        # 4. How was it performed?
        how_performed = NOT_FOUND
        if methodology:
            how_performed = TextPolisher.format_neat_paragraph(methodology, max_sentences=2)
        elif is_valid_section(sections.get("participants")) or is_valid_section(sections.get("data_collection")):
            parts = []
            if is_valid_section(sections.get("participants")):
                parts.append(f"Study sample: {sections['participants']}")
            if is_valid_section(sections.get("data_collection")):
                parts.append(f"Data collection & analysis: {sections['data_collection']}")
            how_performed = TextPolisher.format_neat_paragraph(" ".join(parts), max_sentences=2)
        elif abstract:
            method_match = re.search(r'(?:we propose|we introduce|we design|by using|via|our approach|the study (?:involved|employed|investigated))\s+([^.!?]+[.!?])', abstract, re.IGNORECASE)
            if method_match:
                how_performed = TextPolisher.polish_sentence(f"The authors note that {method_match.group(0).strip()}")
            else:
                how_performed = TextPolisher.format_neat_paragraph(abstract, max_sentences=2)

        # 5. What was the result?
        what_result = NOT_FOUND
        if results:
            what_result = TextPolisher.format_neat_paragraph(results, max_sentences=2)
        elif is_valid_section(sections.get("findings")):
            what_result = TextPolisher.format_neat_paragraph(sections["findings"], max_sentences=2)
        elif is_valid_section(sections.get("discussion")):
            what_result = TextPolisher.format_neat_paragraph(sections["discussion"], max_sentences=2)
        elif conclusion:
            res_match = re.search(r'(?:results show|findings demonstrate|demonstrates that|achieves|outperforms|evaluated on|findings highlight)\s+([^.!?]+[.!?])', conclusion, re.IGNORECASE)
            if res_match:
                what_result = TextPolisher.polish_sentence(f"Experimental outcomes show that {res_match.group(0).strip()}")
            else:
                what_result = TextPolisher.format_neat_paragraph(conclusion, max_sentences=2)
        elif abstract:
            res_match = re.search(r'(?:results show|findings demonstrate|demonstrates that|achieves|outperforms|revealed that)\s+([^.!?]+[.!?])', abstract, re.IGNORECASE)
            if res_match:
                what_result = TextPolisher.polish_sentence(f"The paper reports that {res_match.group(0).strip()}")

        # 6. What is the main contribution?
        contribution = NOT_FOUND
        if conclusion:
            contrib_match = re.search(r'(?:contributions? include|we have presented|key contribution|novelty of)\s+([^.!?]+[.!?])', conclusion, re.IGNORECASE)
            if contrib_match:
                contribution = TextPolisher.polish_sentence(f"The primary contribution is {contrib_match.group(1).strip()}")
            else:
                contribution = TextPolisher.format_neat_paragraph(conclusion, max_sentences=2)
        elif abstract:
            contribution = TextPolisher.format_neat_paragraph(abstract, max_sentences=2)

        return {
            "what_is_this_paper_about": about,
            "what_problem_does_it_solve": problem_solved,
            "why_was_the_research_conducted": why_conducted,
            "how_was_it_performed": how_performed,
            "what_was_the_result": what_result,
            "what_is_the_main_contribution": contribution
        }
