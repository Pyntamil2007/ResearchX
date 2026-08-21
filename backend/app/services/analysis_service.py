import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.paper import ResearchPaper
from app.models.analysis import Analysis
from app.models.result import ExtractedResult
from app.models.history import AnalysisHistory
from app.services.pdf_service import PDFService
from app.services.ocr_service import OCRService
from app.services.llm_service import LLMService
from app.services.summary_service import SummaryService
from app.services.visualization_service import VisualizationService
from app.services.notification_service import NotificationService

# 28 Standard Research Domains with Definitions & Keywords
RESEARCH_DOMAINS_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "Artificial Intelligence": {
        "description": "Artificial Intelligence focuses on creating systems that can perform tasks that normally require human intelligence, such as reasoning, learning, prediction, and decision making.",
        "keywords": ["artificial intelligence", "ai", "intelligent agent", "expert system", "heuristic", "cognitive", "autonomous", "reasoning", "knowledge graph"]
    },
    "Machine Learning": {
        "description": "Machine Learning investigates algorithms and statistical models that computer systems use to perform specific tasks relying on patterns and inference rather than explicit instructions.",
        "keywords": ["machine learning", "supervised learning", "unsupervised", "classification", "regression", "clustering", "gradient descent", "random forest", "svm", "cross-validation"]
    },
    "Deep Learning": {
        "description": "Deep Learning utilizes artificial neural networks with multiple layers (deep architectures) to progressively extract higher-level features from raw input data.",
        "keywords": ["deep learning", "neural network", "backpropagation", "layer", "activation function", "sgd", "adam", "epoch", "dropout", "batchnorm"]
    },
    "Computer Vision": {
        "description": "Computer Vision enables computers and machines to derive meaningful information from digital images, videos, and other visual inputs.",
        "keywords": ["computer vision", "convolutional", "cnn", "resnet", "image classification", "object detection", "segmentation", "pixels", "bounding box", "vgg", "yolo", "optical"]
    },
    "Natural Language Processing": {
        "description": "Natural Language Processing (NLP) gives machines the ability to understand, interpret, and manipulate human spoken and written languages.",
        "keywords": ["natural language processing", "nlp", "transformer", "attention", "bleu", "bert", "gpt", "language model", "tokenization", "sentiment", "translation", "syntax", "semantics"]
    },
    "Cybersecurity": {
        "description": "Cybersecurity focuses on protecting computer systems, networks, devices, and programs from digital attacks, unauthorized access, and data destruction.",
        "keywords": ["cybersecurity", "intrusion detection", "malware", "vulnerability", "encryption", "cryptography", "adversarial", "attack", "defense", "phishing", "firewall", "zero-day"]
    },
    "Data Science": {
        "description": "Data Science combines domain expertise, programming skills, and mathematics to extract actionable insights and structured knowledge from noisy data.",
        "keywords": ["data science", "big data", "data mining", "analytics", "visualization", "feature engineering", "predictive modeling", "statistical analysis", "data preprocessing"]
    },
    "Software Engineering": {
        "description": "Software Engineering applies systematic engineering principles to the design, development, maintenance, testing, and evaluation of software systems.",
        "keywords": ["software engineering", "refactoring", "code smell", "testing", "ci/cd", "agile", "design pattern", "microservices", "code review", "debugging", "version control"]
    },
    "Cloud Computing": {
        "description": "Cloud Computing delivers computing services including servers, storage, databases, networking, and software over the Internet.",
        "keywords": ["cloud computing", "virtualization", "serverless", "kubernetes", "docker", "aws", "azure", "distributed cloud", "iaas", "paas", "saas"]
    },
    "Internet of Things": {
        "description": "The Internet of Things (IoT) describes the network of physical objects embedded with sensors, software, and connectivity technologies to exchange data.",
        "keywords": ["internet of things", "iot", "sensor", "actuator", "smart device", "mqtt", "zigbee", "edge computing", "embedded system", "rfid", "smart home"]
    },
    "Blockchain": {
        "description": "Blockchain is a decentralized, distributed, and public digital ledger that is used to record transactions across many computers securely.",
        "keywords": ["blockchain", "smart contract", "ethereum", "bitcoin", "cryptocurrency", "consensus mechanism", "proof of work", "proof of stake", "distributed ledger", "decentralized"]
    },
    "Robotics": {
        "description": "Robotics deals with the design, construction, operation, and application of robots, as well as computer systems for their control and sensor feedback.",
        "keywords": ["robotics", "robot", "kinematics", "actuator", "manipulator", "slam", "path planning", "motion control", "autonomous vehicle", "reinforcement learning"]
    },
    "Healthcare": {
        "description": "Healthcare AI and Medical Informatics investigate computational methods applied to biomedical data, clinical diagnosis, electronic health records, and therapeutics.",
        "keywords": ["healthcare", "medical", "clinical", "patient", "biomedical", "disease", "diagnosis", "mri", "ct scan", "ehr", "pathology", "hospital", "treatment"]
    },
    "Agriculture": {
        "description": "Agriculture Technology (AgTech) leverages computational models, sensors, and remote sensing to optimize farming, crop health, pest management, and yield prediction.",
        "keywords": ["agriculture", "crop", "plant disease", "farming", "soil", "harvest", "leaf", "pest", "irrigation", "yield", "agtech", "botanical"]
    },
    "Education": {
        "description": "Educational Technology and Learning Analytics study digital pedagogical methodologies, automated grading, intelligent tutoring systems, and student learning patterns.",
        "keywords": ["education", "learning analytics", "student", "pedagogy", "curriculum", "tutoring", "classroom", "academic performance", "e-learning", "mooc"]
    },
    "Finance": {
        "description": "Financial Computing and FinTech apply quantitative models and algorithmic intelligence to trading, risk management, fraud detection, and credit scoring.",
        "keywords": ["finance", "fintech", "stock market", "trading", "fraud detection", "portfolio", "credit risk", "banking", "asset pricing", "algorithmic trading"]
    },
    "Computer Networks": {
        "description": "Computer Networks analyze data transmission protocols, network topologies, routing algorithms, wireless communications, and traffic optimization.",
        "keywords": ["computer networks", "protocol", "routing", "tcp/ip", "packet", "bandwidth", "latency", "sdn", "5g", "wireless", "throughput", "topology"]
    },
    "Information Technology": {
        "description": "Information Technology encompasses the infrastructure, governance, and operation of computing hardware, systems, and enterprise data architectures.",
        "keywords": ["information technology", "it infrastructure", "system administration", "enterprise architecture", "it governance", "database administration", "telecommunications"]
    },
    "Database Systems": {
        "description": "Database Systems study data modeling, query optimization, concurrency control, transaction processing, and scalable storage architectures (SQL and NoSQL).",
        "keywords": ["database", "sql", "nosql", "query optimization", "indexing", "acid", "relational", "mongodb", "transaction", "storage engine", "olap", "oltp"]
    },
    "Human-Computer Interaction": {
        "description": "Human-Computer Interaction (HCI) researches the design and use of computer technology, focusing on the interfaces between humans and computer systems.",
        "keywords": ["human-computer interaction", "hci", "user experience", "ux", "ui", "usability", "interface design", "accessibility", "user study", "interaction design"]
    },
    "Renewable Energy": {
        "description": "Renewable Energy and Smart Grid research focuses on computational modeling of solar, wind, and storage energy systems and power distribution optimization.",
        "keywords": ["renewable energy", "solar", "wind energy", "smart grid", "power system", "photovoltaic", "energy storage", "battery", "sustainability", "carbon"]
    },
    "Environmental Science": {
        "description": "Environmental Science uses modeling and data analysis to study climate change, ecosystem dynamics, pollution monitoring, and natural resource conservation.",
        "keywords": ["environmental science", "climate", "pollution", "ecology", "biodiversity", "emissions", "air quality", "ecosystem", "carbon footprint", "conservation"]
    },
    "Biotechnology": {
        "description": "Biotechnology applies biological systems, organisms, or derivatives to develop products, including genomics, protein engineering, and molecular biology.",
        "keywords": ["biotechnology", "genomics", "dna", "rna", "protein folding", "crispr", "molecular biology", "bioinformatics", "gene expression", "sequencing"]
    },
    "Physics": {
        "description": "Computational Physics applies algorithmic techniques, numerical analysis, and simulation to solve complex physical models and phenomena.",
        "keywords": ["physics", "quantum", "thermodynamics", "optics", "electromagnetism", "mechanics", "simulation", "particle", "gravity", "wave"]
    },
    "Mathematics": {
        "description": "Mathematics investigates numerical theory, optimization algorithms, linear algebra, graph theory, differential equations, and formal proofs.",
        "keywords": ["mathematics", "linear algebra", "calculus", "differential equations", "graph theory", "topology", "combinatorics", "theorem", "proof", "convex optimization"]
    },
    "Business & Management": {
        "description": "Business & Management investigates strategic planning, organizational operations, supply chain logistics, marketing analytics, and corporate decision-making.",
        "keywords": ["business", "management", "supply chain", "marketing", "operations", "strategy", "enterprise", "consumer", "organizational", "leadership"]
    },
    "Social Science": {
        "description": "Social Science explores human society, social relationships, ethics, policy, anthropology, and socio-economic dynamics.",
        "keywords": ["social science", "sociology", "society", "ethics", "policy", "governance", "public policy", "behavioral", "demographics", "fairness"]
    },
    "Other": {
        "description": "Interdisciplinary and specialized research studies spanning multiple emerging or domain-specific fields.",
        "keywords": ["interdisciplinary", "multidisciplinary", "general science", "exploratory study"]
    }
}

class AnalysisService:
    @staticmethod
    def analyze_paper(paper_id: int, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Execute end-to-end NLP / AI analysis on an uploaded research paper.
        Extracts content, detects sections, calculates keywords & domain,
        generates 6-question easy summary, extracts metrics & comparisons,
        and saves results to SQLite database.
        """
        paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
        if not paper:
            raise ValueError(f"Research paper with id {paper_id} not found.")

        # Update paper status to Processing
        paper.status = "Processing"
        db.commit()

        # User In-App Notification: Analysis started
        NotificationService.create_user_notification(
            db=db,
            user_id=user_id,
            title="Analysis started",
            message=f"AI/NLP analysis started for \"{paper.title}\".",
            notification_type="analysis_started"
        )

        try:
            # 1. Read document and extract text (PDF or Image via OCR)
            file_path = Path(paper.file_path)
            file_ext = file_path.suffix.lower()
            
            if file_ext in (".jpg", ".jpeg", ".png", ".webp"):
                raw_text = OCRService.extract_text_from_image(file_path)
            else:
                raw_text = PDFService.extract_text_from_pdf(file_path)
                
            paper.raw_text = raw_text

            # 2. Segment into sections
            sections = PDFService.segment_sections(raw_text)

            # 3. Detect Document Type
            doc_type = PDFService.detect_document_type(raw_text)
            paper.document_type = doc_type

            # 4. Detect Research Domain, Recommendations & Explanation
            primary_domain, recommended_domains, domain_explanation = AnalysisService._detect_domain_and_recommendations(raw_text, sections)
            paper.domain = primary_domain

            # 5. Extract Keywords
            keywords = AnalysisService._extract_keywords(raw_text, sections)

            # 6. Extract Paper Overview metadata
            title = sections.get("title") or paper.title
            if title and title not in ("Information not available in the paper.", "Information not available in the document."):
                paper.title = title
            
            authors = sections.get("authors") or paper.authors
            if authors and authors not in ("Information not available in the paper.", "Information not available in the document."):
                paper.authors = authors

            publication_info = AnalysisService._detect_publication_info(raw_text)

            # 7. Extract Structured Sections via NLP + LLM Reasoning Pipeline
            llm_analysis = LLMService.extract_structured_analysis(
                raw_text, sections, primary_domain, doc_type, paper.title, paper.authors
            )

            problem = llm_analysis.get("research_problem") or "Information not available in the document."
            motivation = llm_analysis.get("motivation") or "Information not available in the document."
            objective = llm_analysis.get("objective") or "Information not available in the document."
            proposed_sol = llm_analysis.get("proposed_solution") or "Information not available in the document."
            contribution = llm_analysis.get("contribution") or "Information not available in the document."
            methodology = llm_analysis.get("methodology") or sections.get("methodology") or "Methodology could not be reliably identified."
            algorithms = llm_analysis.get("algorithms") or "Information not available in the document."
            technologies = llm_analysis.get("technologies") or "Information not available in the document."
            dataset = llm_analysis.get("dataset") or "Information not available in the document."
            experimental_setup = llm_analysis.get("experimental_setup") or "Information not available in the document."
            results_text = llm_analysis.get("results") or sections.get("results") or "Information not available in the document."
            key_findings = llm_analysis.get("key_findings") or "Information not available in the document."
            limitations = llm_analysis.get("limitations") or "Information not available in the document."
            future_work = llm_analysis.get("future_work") or "Information not available in the document."

            # 8. Generate Easy Summary (6 beginner questions)
            easy_summary = SummaryService.generate_easy_summary(sections, primary_domain)

            # 9. Extract Numerical Metrics & Model Comparisons (Guaranteed for every paper)
            extracted_metrics, viz_data = VisualizationService.extract_metrics_and_comparisons(raw_text, sections, primary_domain)

            # 10. Create or Update Analysis record
            analysis = Analysis(
                paper_id=paper.id,
                paper_title=paper.title,
                authors=paper.authors,
                publication_info=publication_info,
                research_domain=primary_domain,
                document_type=doc_type,
                recommended_domains=json.dumps(recommended_domains),
                domain_explanation=json.dumps(domain_explanation),
                keywords=json.dumps(keywords),
                research_problem=problem,
                motivation=motivation,
                objective=objective,
                proposed_solution=proposed_sol,
                contribution=contribution,
                methodology=methodology,
                algorithms=algorithms,
                technologies=technologies,
                dataset=dataset,
                experimental_setup=experimental_setup,
                results=results_text,
                key_findings=key_findings,
                limitations=limitations,
                future_work=future_work,
                easy_summary=json.dumps(easy_summary),
                has_visualizations=1 if viz_data.get("has_visualizations") else 0
            )

            db.add(analysis)
            db.flush()

            # 13. Save Extracted Results
            if extracted_metrics:
                for metric in extracted_metrics:
                    res_entry = ExtractedResult(
                        analysis_id=analysis.id,
                        metric_name=metric["metric_name"],
                        metric_value=metric["metric_value"],
                        model_name=metric["model_name"],
                        comparison_group=metric.get("comparison_group", "Default Evaluation")
                    )
                    db.add(res_entry)

            # 14. Create Analysis History entry
            history_entry = AnalysisHistory(
                user_id=user_id,
                paper_id=paper.id,
                analysis_id=analysis.id
            )
            db.add(history_entry)

            # 15. Update Paper status to Analyzed
            paper.status = "Analyzed"

            # 16. In-App Notifications on Completion
            # User Notification: Analysis completed
            NotificationService.create_user_notification(
                db=db,
                user_id=user_id,
                title="Analysis completed",
                message=f"Analysis completed successfully for \"{paper.title}\". Domain: {primary_domain}.",
                notification_type="analysis_completed"
            )

            # User Notification: Report generated
            NotificationService.create_user_notification(
                db=db,
                user_id=user_id,
                title="Report generated",
                message=f"Comprehensive 14-section research report & visualizations generated for \"{paper.title}\".",
                notification_type="report_generated"
            )

            # Admin Notification: Paper Analysis Completed
            NotificationService.notify_admins(
                db=db,
                title="Analysis completed",
                message=f"Analysis completed for paper \"{paper.title}\" (ID: {paper.id}) in domain '{primary_domain}'.",
                notification_type="admin_analysis_completed"
            )

            db.commit()
            db.refresh(analysis)

            return {
                "analysis_id": analysis.id,
                "paper_id": paper.id,
                "paper_title": paper.title,
                "domain": primary_domain,
                "document_type": doc_type,
                "status": "Analyzed",
                "has_visualizations": bool(analysis.has_visualizations)
            }

        except Exception as e:
            db.rollback()
            paper.status = "Failed"
            
            # User Notification: Analysis failed
            NotificationService.create_user_notification(
                db=db,
                user_id=user_id,
                title="Analysis failed",
                message=f"Analysis could not be completed for \"{paper.title}\". Reason: {str(e)}",
                notification_type="analysis_failed"
            )

            # Admin Notification: Analysis failed
            NotificationService.notify_admins(
                db=db,
                title="Analysis failed",
                message=f"Analysis failed for paper \"{paper.title}\" (ID: {paper.id}). Error: {str(e)}",
                notification_type="admin_analysis_failed"
            )

            db.commit()
            raise RuntimeError(f"Analysis failed: {str(e)}")

    @staticmethod
    def _detect_domain_and_recommendations(text: str, sections: Dict[str, str]) -> Tuple[str, List[str], Dict[str, str]]:
        """
        Intelligently analyze document content against 28 research domains.
        Returns:
            - Primary detected domain
            - List of 4-5 recommended domain alternatives
            - Domain explanation dictionary (description + contextual why_this_domain rationale)
        """
        search_corpus = (
            sections.get("title", "") + " " +
            sections.get("abstract", "") + " " +
            sections.get("introduction", "") + " " +
            text[:5000]
        ).lower()

        # Score each domain
        scores: Dict[str, int] = {}
        matched_terms: Dict[str, List[str]] = {}

        for domain, info in RESEARCH_DOMAINS_TAXONOMY.items():
            if domain == "Other":
                scores[domain] = 0
                continue
                
            score = 0
            hits = []
            for kw in info["keywords"]:
                # Count occurrences
                count = search_corpus.count(kw)
                if count > 0:
                    score += count * (3 if len(kw.split()) > 1 else 1)
                    hits.append(kw)
            
            scores[domain] = score
            matched_terms[domain] = hits

        # Rank domains by score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_candidates = [d for d, score in ranked if score > 0]

        if top_candidates:
            primary_domain = top_candidates[0]
            # Recommend next top 4 domains
            recommended = top_candidates[1:5]
            if len(recommended) < 3:
                # Add default relevant domains
                defaults = ["Artificial Intelligence", "Machine Learning", "Data Science", "Computer Vision", "Cybersecurity"]
                for def_dom in defaults:
                    if def_dom != primary_domain and def_dom not in recommended:
                        recommended.append(def_dom)
                    if len(recommended) >= 4:
                        break
        else:
            primary_domain = "Computer Science"
            recommended = ["Artificial Intelligence", "Machine Learning", "Data Science", "Information Technology"]

        # Build contextual "Why this domain?" explanation
        top_hits = matched_terms.get(primary_domain, [])
        if top_hits:
            terms_str = ", ".join(f"'{t}'" for t in top_hits[:3])
            why_this_domain = f"This document frequently addresses key concepts including {terms_str}, indicating significant alignment with research in {primary_domain}."
        else:
            why_this_domain = f"This document's computational methodologies and academic framing align with foundational principles in {primary_domain}."

        domain_info = RESEARCH_DOMAINS_TAXONOMY.get(primary_domain, RESEARCH_DOMAINS_TAXONOMY["Other"])
        explanation = {
            "description": domain_info["description"],
            "why_this_domain": why_this_domain
        }

        return primary_domain, recommended, explanation

    @staticmethod
    def get_domain_info(domain_name: str, paper_content: str = "") -> Dict[str, str]:
        """Get standard description and contextual rationale for any domain."""
        info = RESEARCH_DOMAINS_TAXONOMY.get(domain_name, {
            "description": f"{domain_name} investigates domain-specific theories, methodologies, and technological applications.",
            "keywords": []
        })

        why_this_domain = f"Selected research domain '{domain_name}' focuses on: {info['description']}"
        return {
            "description": info["description"],
            "why_this_domain": why_this_domain
        }

    @staticmethod
    def _extract_keywords(text: str, sections: Dict[str, str]) -> List[str]:
        """Extract top 5-8 relevant academic keyword tags."""
        kw_match = re.search(r'(?:Keywords?|Index Terms?)[:\s]+([^\n\r]+)', text, re.IGNORECASE)
        if kw_match:
            raw_kws = [k.strip() for k in re.split(r'[,;–—]', kw_match.group(1)) if len(k.strip()) > 1]
            if len(raw_kws) >= 3:
                return raw_kws[:8]

        candidates = [
            "Deep Learning", "Neural Networks", "Computer Vision", "Machine Learning",
            "Natural Language Processing", "Transformers", "Self-Attention", "Classification",
            "Supervised Learning", "Optimization", "Model Comparison", "Benchmark Evaluation",
            "Feature Extraction", "Empirical Study", "Residual Learning", "Representation Learning",
            "Cybersecurity", "Data Analytics", "Robotics", "IoT", "Healthcare AI"
        ]
        
        found = []
        lower_text = text.lower()
        for cand in candidates:
            if cand.lower() in lower_text:
                found.append(cand)
                if len(found) >= 7:
                    break

        if not found:
            found = ["Artificial Intelligence", "Empirical Evaluation", "Research Methodology"]

        return found

    @staticmethod
    def _detect_publication_info(text: str) -> str:
        """Extract publication venue, conference, year if present."""
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text[:500])
        year = year_match.group(1) if year_match else "2024"

        venue_match = re.search(r'(?:Published in|Conference|Proceedings of|Journal of|arXiv:\d+\.\d+|IEEE|ACM|CVPR|NeurIPS|ICML|ICLR|ACL)\s*([^\n,]{3,40})', text[:1000], re.IGNORECASE)
        if venue_match:
            return f"{venue_match.group(0).strip()} ({year})"
        return f"Academic Research Publication ({year})"

    @staticmethod
    def _extract_targeted_snippet(source_text: str, regex_keywords: List[str]) -> str:
        """Find matching sentence or return not available."""
        if not source_text or source_text == "Information not available in the paper.":
            return "Information not available in the paper."

        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', source_text) if len(s.strip()) > 15]
        for sentence in sentences:
            for kw in regex_keywords:
                if re.search(r'\b' + kw, sentence, re.IGNORECASE):
                    return sentence

        return sentences[0] if sentences else "Information not available in the paper."

    @staticmethod
    def _detect_algorithms(text: str) -> str:
        """Identify mention of algorithms or mathematical models."""
        algos = ["Stochastic Gradient Descent (SGD)", "Adam Optimizer", "Backpropagation", "Convolutional Neural Network", "Residual Network", "Transformer Self-Attention", "Support Vector Machine", "Random Forest", "Cross-Entropy Loss"]
        found = [a for a in algos if a.lower() in text.lower()]
        return ", ".join(found) if found else "Information not available in the paper."

    @staticmethod
    def _detect_technologies(text: str) -> str:
        """Identify frameworks & tools."""
        techs = ["PyTorch", "TensorFlow", "CUDA", "Python", "NumPy", "Scikit-Learn", "Hugging Face", "Keras", "OpenCV", "Docker"]
        found = [t for t in techs if t.lower() in text.lower()]
        return ", ".join(found) if found else "Information not available in the paper."

    @staticmethod
    def _detect_dataset(text: str) -> str:
        """Identify benchmark datasets."""
        datasets = ["ImageNet (ILSVRC)", "CIFAR-10 / CIFAR-100", "COCO Dataset", "MNIST", "GLUE Benchmark", "SQuAD", "WMT Translation Dataset", "MIMIC-III", "Custom Experimental Dataset"]
        found = [d for d in datasets if d.lower() in text.lower() or d.split()[0].lower() in text.lower()]
        return ", ".join(found) if found else "Information not available in the paper."
