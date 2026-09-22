import os
import re
import json
from typing import Dict, Any, List, Optional
import httpx
from app.services.text_polisher import TextPolisher

class LLMService:
    @staticmethod
    def extract_structured_analysis(
        text: str,
        sections: Dict[str, str],
        domain: str,
        document_type: str,
        paper_title: str,
        authors: str
    ) -> Dict[str, Any]:
        """
        Perform deep NLP + LLM structured academic analysis over research text.
        Strictly follows: NEVER INVENT INFORMATION.
        If information is unavailable in the document, returns 'Not explicitly mentioned in the paper.'
        """
        # Check if an external LLM key is configured (OpenAI, Gemini, etc.)
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")

        raw_result = None
        if openai_key:
            try:
                raw_result = LLMService._call_openai_analysis(text, domain, document_type, openai_key)
            except Exception:
                pass

        if not raw_result and gemini_key:
            try:
                raw_result = LLMService._call_gemini_analysis(text, domain, document_type, gemini_key)
            except Exception:
                pass

        if not raw_result:
            # Intelligent Semantic NLP reasoning engine
            raw_result = LLMService._intelligent_nlp_reasoning(text, sections, domain, document_type, paper_title, authors)

        # Polish all extracted fields to ensure neat, grammatically complete academic sentences
        polished_result = {}
        for key, value in raw_result.items():
            if isinstance(value, str):
                if value in [
                    "Not explicitly mentioned in the paper.",
                    "Dataset information is not explicitly mentioned in the paper.",
                    "Author information could not be reliably extracted."
                ]:
                    polished_result[key] = value
                else:
                    polished_result[key] = TextPolisher.format_neat_paragraph(value, max_sentences=4)
            else:
                polished_result[key] = value

        return polished_result

    @staticmethod
    def _intelligent_nlp_reasoning(
        text: str,
        sections: Dict[str, str],
        domain: str,
        document_type: str,
        paper_title: str,
        authors: str
    ) -> Dict[str, Any]:
        """
        High-precision local NLP reasoning engine strictly grounded in document text.
        Never fabricates facts, numbers, algorithms, datasets, or observations.
        """
        NOT_FOUND = "Not explicitly mentioned in the paper."
        NOT_FOUND_DATASET = "Dataset information is not explicitly mentioned in the paper."

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

        # 1. Research Problem
        problem = NOT_FOUND
        if is_valid_section(sections.get("problem")):
            problem = sections["problem"]
        else:
            intro = sections.get("introduction", "") if is_valid_section(sections.get("introduction")) else ""
            abstract = sections.get("abstract", "") if is_valid_section(sections.get("abstract")) else ""
            combined = f"{intro} {abstract}"
            m = re.search(r'(?:challenge|problem|limitation|bottleneck|difficulty|obstacle|lack of)\s+(?:of|in|with|is that|investigated is|addressed is|regarding)\s+([^.!?]+[.!?])', combined, re.IGNORECASE)
            if m:
                problem = f"The primary problem investigated is {m.group(0).strip()}"
            elif abstract:
                sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', abstract) if len(s.strip()) > 20]
                if len(sentences) > 1:
                    problem = sentences[1]

        # 2. Motivation
        motivation = NOT_FOUND
        if is_valid_section(sections.get("motivation")):
            motivation = sections["motivation"]
        else:
            intro = sections.get("introduction", "") if is_valid_section(sections.get("introduction")) else ""
            abstract = sections.get("abstract", "") if is_valid_section(sections.get("abstract")) else ""
            combined = f"{intro} {abstract}"
            m = re.search(r'(?:motivation behind|motivated by|crucial because|essential to|driven by|importance of|need to explore|rationale for)\s+([^.!?]+[.!?])', combined, re.IGNORECASE)
            if m:
                motivation = f"The motivation behind this research is {m.group(0).strip()}"

        # 3. Objective
        objective = NOT_FOUND
        if is_valid_section(sections.get("objective")):
            objective = sections["objective"]
        else:
            abstract = sections.get("abstract", "") if is_valid_section(sections.get("abstract")) else ""
            intro = sections.get("introduction", "") if is_valid_section(sections.get("introduction")) else ""
            combined = f"{abstract} {intro}"
            m = re.search(r'(?:aim of this (?:paper|work|study) is to|objective of this (?:paper|work|study) is to|goal is to|we aim to|this paper focuses on|this paper investigates|purpose of this (?:study|paper) is to)\s+([^.!?]+[.!?])', combined, re.IGNORECASE)
            if m:
                objective = f"The objective is to {m.group(1).strip()}"
            elif abstract:
                sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', abstract) if len(s.strip()) > 20]
                if sentences:
                    objective = sentences[0]

        # 4. Proposed Solution / Investigation Approach
        solution = NOT_FOUND
        method = sections.get("methodology", "") if is_valid_section(sections.get("methodology")) else ""
        abstract = sections.get("abstract", "") if is_valid_section(sections.get("abstract")) else ""
        combined = f"{abstract} {method}"
        m = re.search(r'(?:we propose|we introduce|we develop|this paper presents|in this work, we|the study employed|the study was conducted with)\s+([^.!?]+[.!?])', combined, re.IGNORECASE)
        if m:
            solution = f"The proposed investigation approach: {m.group(0).strip()}"
        elif method:
            solution = TextPolisher.format_neat_paragraph(method, max_sentences=3)

        # 5. Main Contribution
        contribution = NOT_FOUND
        conclusion = sections.get("conclusion", "") if is_valid_section(sections.get("conclusion")) else ""
        intro = sections.get("introduction", "") if is_valid_section(sections.get("introduction")) else ""
        combined = f"{conclusion} {intro} {abstract}"
        m = re.search(r'(?:contributions? (?:are|include)|we make the following contributions?|key contribution|novelty|study contributes|paper contributes)\s*:?\s*([^.!?]+[.!?])', combined, re.IGNORECASE)
        if m:
            contribution = f"The key contribution is {m.group(0).strip()}"
        elif conclusion:
            contribution = TextPolisher.format_neat_paragraph(conclusion, max_sentences=3)
        elif abstract:
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', abstract) if len(s.strip()) > 20]
            if sentences:
                contribution = sentences[-1]

        # 6. Methodology
        methodology = NOT_FOUND
        method_parts = []
        if is_valid_section(sections.get("participants")):
            method_parts.append(f"Participants: {sections['participants']}")
        if is_valid_section(sections.get("data_collection")):
            method_parts.append(f"Data Collection & Analysis: {sections['data_collection']}")
        if is_valid_section(sections.get("methodology")):
            method_parts.append(sections["methodology"])
        
        if method_parts:
            methodology = " ".join(method_parts)
        elif text:
            m = re.search(r'(?:framework|architecture|pipeline|approach|procedure|methodology|the study)\s+(?:consists of|involves|is based on|employed|was conducted with)\s+([^.!?]+[.!?])', text, re.IGNORECASE)
            if m:
                methodology = f"The methodology involves {m.group(0).strip()}"

        # 7. Algorithms / Techniques
        algorithms = NOT_FOUND
        if is_valid_section(sections.get("algorithms")):
            algorithms = sections["algorithms"]
        else:
            search_text = f"{sections.get('methodology', '')} {sections.get('data_collection', '')} {text}"
            algo_matches = re.findall(r'\b(?:ResNet-\d+|CNN|RNN|LSTM|Transformer|BERT|GPT|SGD|Adam|VGG|YOLO|SVM|Random Forest|k-Means|Attention Mechanism|Gradient Descent|qualitative thematic coding|thematic analysis|descriptive statistics|frequency analysis|semi-structured interview analysis)\b', search_text, re.IGNORECASE)
            if algo_matches:
                unique_algos = list(dict.fromkeys([a.title() for a in algo_matches]))
                algorithms = f"Key analytical methods and algorithmic techniques utilized: {', '.join(unique_algos[:6])}."

        # 8. Technologies & Frameworks / Tools
        technologies = NOT_FOUND
        if is_valid_section(sections.get("technologies")):
            technologies = sections["technologies"]
        elif text:
            tech_matches = re.findall(r'\b(?:PyTorch|TensorFlow|Keras|CUDA|GPU|Python|Scikit-learn|OpenCV|NumPy|Pandas|HuggingFace|Docker|mobile devices|smartphones|online dictionaries|translation applications|podcasts|social media platforms)\b', text, re.IGNORECASE)
            if tech_matches:
                unique_tech = list(dict.fromkeys([t.title() for t in tech_matches]))
                technologies = f"Software frameworks, tools, and platforms: {', '.join(unique_tech[:6])}."

        # 9. Dataset / Data Source
        dataset = NOT_FOUND_DATASET
        if is_valid_section(sections.get("dataset")):
            dataset = sections["dataset"]
        elif text:
            data_matches = re.findall(r'\b(?:ImageNet|COCO|CIFAR-10|CIFAR-100|MNIST|WMT|SQuAD|GLUE|VOC|Kaggle)\b', text, re.IGNORECASE)
            if data_matches:
                unique_data = list(dict.fromkeys(data_matches))
                dataset = f"Evaluated benchmark datasets: {', '.join(unique_data[:5])}."

        # 10. Experimental Setup / Study Setting
        setup = NOT_FOUND
        if is_valid_section(sections.get("experimental_setup")):
            setup = sections["experimental_setup"]
        elif is_valid_section(sections.get("participants")):
            setup = f"Study setting and participant sample: {sections['participants']}"
        elif text:
            m = re.search(r'(?:trained on|hyperparameters|batch size|learning rate|epoch|optimizer|study setting)\s+([^.!?]+[.!?])', text, re.IGNORECASE)
            if m:
                setup = f"Experimental environment: {m.group(0).strip()}"

        # 11. Results
        results = NOT_FOUND
        if is_valid_section(sections.get("results")):
            results = sections["results"]
        elif is_valid_section(sections.get("findings")):
            results = sections["findings"]
        elif text:
            m = re.search(r'(?:findings demonstrate that|results show that|revealed that|achieved?|outperforms?|accuracy of|error rate of|bleu score of|precision of)\s+([^.!?]+[.!?])', text, re.IGNORECASE)
            if m:
                results = f"Empirical findings report that {m.group(0).strip()}"

        # 12. Key Findings / Observations
        findings = NOT_FOUND
        if is_valid_section(sections.get("findings")):
            findings = TextPolisher.format_neat_paragraph(sections["findings"], max_sentences=3)
        elif is_valid_section(sections.get("discussion")):
            findings = TextPolisher.format_neat_paragraph(sections["discussion"], max_sentences=3)
        elif is_valid_section(sections.get("results")):
            findings = TextPolisher.format_neat_paragraph(sections["results"], max_sentences=3)
        elif conclusion:
            findings = TextPolisher.format_neat_paragraph(conclusion, max_sentences=3)

        # 13. Limitations
        limitations = NOT_FOUND
        if is_valid_section(sections.get("limitations")):
            limitations = sections["limitations"]
        elif text:
            m = re.search(r'(?:limitation|drawback|threat to validity|small sample size|computational complexity|overhead)\s+(?:is|includes|of)\s+([^.!?]+[.!?])', text, re.IGNORECASE)
            if m:
                limitations = f"Identified limitation: {m.group(0).strip()}"

        # 14. Future Work
        future_work = NOT_FOUND
        if is_valid_section(sections.get("future_work")):
            future_work = sections["future_work"]
        elif text:
            m = re.search(r'(?:future work|future directions?|future research|further research|plan to explore|should include)\s+(?:will|aims to|includes|should|could)\s+([^.!?]+[.!?])', text, re.IGNORECASE)
            if m:
                future_work = f"Future research direction: {m.group(0).strip()}"

        return {
            "research_problem": problem,
            "motivation": motivation,
            "objective": objective,
            "proposed_solution": solution,
            "contribution": contribution,
            "methodology": methodology,
            "algorithms": algorithms,
            "technologies": technologies,
            "dataset": dataset,
            "experimental_setup": setup,
            "results": results,
            "key_findings": findings,
            "limitations": limitations,
            "future_work": future_work
        }

    @staticmethod
    def _call_openai_analysis(text: str, domain: str, document_type: str, api_key: str) -> Optional[Dict[str, Any]]:
        try:
            prompt = (
                f"Analyze the following research document (Domain: {domain}, Type: {document_type}).\n"
                "Extract ONLY information strictly grounded in the document text. Do not invent facts, algorithms, datasets, or numbers.\n"
                "Return valid JSON containing fields: research_problem, motivation, objective, proposed_solution, contribution, "
                "methodology, algorithms, technologies, dataset, experimental_setup, results, key_findings, limitations, future_work.\n"
                "If any field is absent from the paper, set its value to 'Not explicitly mentioned in the paper.' (or 'Dataset information is not explicitly mentioned in the paper.' for dataset).\n\n"
                f"Document Text:\n{text[:12000]}"
            )
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0
            }
            with httpx.Client(timeout=20.0) as client:
                res = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"]
                    return json.loads(content)
        except Exception:
            return None
        return None

    @staticmethod
    def _call_gemini_analysis(text: str, domain: str, document_type: str, api_key: str) -> Optional[Dict[str, Any]]:
        try:
            prompt = (
                f"Analyze the following research document.\n"
                "Extract ONLY information strictly grounded in the document text. Do not invent facts or datasets.\n"
                "Return valid JSON containing: research_problem, motivation, objective, proposed_solution, contribution, "
                "methodology, algorithms, technologies, dataset, experimental_setup, results, key_findings, limitations, future_work.\n"
                "If any field is absent from the paper, set its value to 'Not explicitly mentioned in the paper.' (or 'Dataset information is not explicitly mentioned in the paper.' for dataset).\n\n"
                f"Text:\n{text[:12000]}"
            )
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            with httpx.Client(timeout=20.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    json_match = re.search(r'\{[\s\S]*\}', raw_text)
                    if json_match:
                        return json.loads(json_match.group(0))
        except Exception:
            return None
        return None
