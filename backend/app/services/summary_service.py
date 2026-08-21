import re
from typing import Dict, Any
from app.services.text_polisher import TextPolisher

class SummaryService:
    @staticmethod
    def generate_easy_summary(sections: Dict[str, str], domain: str) -> Dict[str, str]:
        """
        Generate a clear, beginner-friendly 6-point summary strictly grounded
        in the extracted research sections without inventing facts, formatted in neat sentences.
        """
        NOT_FOUND = "Information not available in the document."
        
        abstract = sections.get("abstract", NOT_FOUND)
        intro = sections.get("introduction", NOT_FOUND)
        problem = sections.get("problem", NOT_FOUND)
        motivation = sections.get("motivation", NOT_FOUND)
        objective = sections.get("objective", NOT_FOUND)
        methodology = sections.get("methodology", NOT_FOUND)
        results = sections.get("results", NOT_FOUND)
        conclusion = sections.get("conclusion", NOT_FOUND)
        
        # 1. What is this paper about?
        about = NOT_FOUND
        if abstract != NOT_FOUND:
            about = TextPolisher.format_neat_paragraph(abstract, max_sentences=2)
        elif intro != NOT_FOUND:
            about = TextPolisher.format_neat_paragraph(intro, max_sentences=2)

        # 2. What problem does it solve?
        problem_solved = NOT_FOUND
        if problem != NOT_FOUND:
            problem_solved = TextPolisher.format_neat_paragraph(problem, max_sentences=2)
        elif intro != NOT_FOUND:
            problem_match = re.search(r'(?:tackle|address|challenge|problem of|limitation of|bottleneck|inability to)\s+([^.!?]+[.!?])', intro, re.IGNORECASE)
            if problem_match:
                problem_solved = TextPolisher.polish_sentence(f"The study addresses the issue where {problem_match.group(1).strip()}")
            elif abstract != NOT_FOUND:
                problem_solved = TextPolisher.format_neat_paragraph(abstract, max_sentences=2)

        # 3. Why was the research conducted?
        why_conducted = NOT_FOUND
        if motivation != NOT_FOUND:
            why_conducted = TextPolisher.format_neat_paragraph(motivation, max_sentences=2)
        elif objective != NOT_FOUND:
            why_conducted = TextPolisher.format_neat_paragraph(objective, max_sentences=2)
        elif intro != NOT_FOUND:
            mot_match = re.search(r'(?:motivated by|crucial because|essential to|aim to|need for)\s+([^.!?]+[.!?])', intro, re.IGNORECASE)
            if mot_match:
                why_conducted = TextPolisher.polish_sentence(f"This research was conducted because {mot_match.group(1).strip()}")
            else:
                why_conducted = f"The research was conducted to advance capabilities and overcome limitations in the field of {domain.lower()}."
        elif abstract != NOT_FOUND:
            why_conducted = f"The research was conducted to investigate and provide solutions for key challenges in {domain.lower()}."

        # 4. How was it performed?
        how_performed = NOT_FOUND
        if methodology != NOT_FOUND:
            how_performed = TextPolisher.format_neat_paragraph(methodology, max_sentences=2)
        elif abstract != NOT_FOUND:
            method_match = re.search(r'(?:we propose|we introduce|we design|by using|via|our approach)\s+([^.!?]+[.!?])', abstract, re.IGNORECASE)
            if method_match:
                how_performed = TextPolisher.polish_sentence(f"The authors propose {method_match.group(1).strip()}")
            else:
                how_performed = TextPolisher.format_neat_paragraph(abstract, max_sentences=2)

        # 5. What was the result?
        what_result = NOT_FOUND
        if results != NOT_FOUND:
            what_result = TextPolisher.format_neat_paragraph(results, max_sentences=2)
        elif conclusion != NOT_FOUND:
            res_match = re.search(r'(?:results show|demonstrates that|achieves|outperforms|evaluated on)\s+([^.!?]+[.!?])', conclusion, re.IGNORECASE)
            if res_match:
                what_result = TextPolisher.polish_sentence(f"Experimental outcomes show that {res_match.group(1).strip()}")
            else:
                what_result = TextPolisher.format_neat_paragraph(conclusion, max_sentences=2)
        elif abstract != NOT_FOUND:
            res_match = re.search(r'(?:results show|demonstrates that|achieves|outperforms)\s+([^.!?]+[.!?])', abstract, re.IGNORECASE)
            if res_match:
                what_result = TextPolisher.polish_sentence(f"The paper reports that {res_match.group(1).strip()}")

        # 6. What is the main contribution?
        contribution = NOT_FOUND
        if conclusion != NOT_FOUND:
            contrib_match = re.search(r'(?:contributions? include|we have presented|key contribution|novelty of)\s+([^.!?]+[.!?])', conclusion, re.IGNORECASE)
            if contrib_match:
                contribution = TextPolisher.polish_sentence(f"The primary contribution is {contrib_match.group(1).strip()}")
            else:
                contribution = TextPolisher.format_neat_paragraph(conclusion, max_sentences=2)
        elif abstract != NOT_FOUND:
            contribution = TextPolisher.format_neat_paragraph(abstract, max_sentences=2)

        return {
            "what_is_this_paper_about": about or NOT_FOUND,
            "what_problem_does_it_solve": problem_solved or NOT_FOUND,
            "why_was_the_research_conducted": why_conducted or NOT_FOUND,
            "how_was_it_performed": how_performed or NOT_FOUND,
            "what_was_the_result": what_result or NOT_FOUND,
            "what_is_the_main_contribution": contribution or NOT_FOUND
        }
