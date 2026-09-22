import re
from typing import List, Dict, Any, Tuple

class VisualizationService:
    @staticmethod
    def extract_metrics_and_comparisons(
        full_text: str,
        sections: Dict[str, str],
        domain: str = "Computer Science"
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Extract genuine numerical metrics and model comparisons from the uploaded research paper.
        STRICT RULE: Never inject fake or domain-default synthetic data.
        If no suitable numerical data exists, returns has_visualizations = False with a clear message.
        """
        target_text = "\n".join([
            sections.get("findings", ""),
            sections.get("results", ""),
            sections.get("discussion", ""),
            sections.get("experimental_setup", ""),
            sections.get("abstract", "")
        ]).strip()

        if not target_text or "not explicitly mentioned in the paper" in target_text.lower() or "information not available" in target_text.lower():
            target_text = full_text

        extracted_results = []
        seen_keys = set()
        
        # 1. Regex pattern matching for in-text metrics, markdown tables, and comparative models
        comparison_patterns = [
            # Markdown or ASCII table rows: | Model | 95.4 | or Model | 95.4 | Accuracy
            r'(?:^|\n)\s*\|?\s*(?P<model>[A-Za-z0-9\-\_\(\)\s]{2,35})\s*\|\s*(?P<val>\d{1,3}(?:\.\d{1,2})?)\s*(?:%|\s*\|\s*(?P<metric>BLEU|mAP|Accuracy|Precision|Recall|F1|F1-Score|Top-1|Top-5|AUC|ROUGE|WER|Latency|Fidelity|Loss|Error Rate)?)?',
            # Model : 95.4% or Model - 95.4
            r'(?P<model>[A-Z0-9][A-Za-z0-9\-\_\(\)\s]{2,30})\s*[:–—\-]\s*(?P<val>\d{1,3}(?:\.\d{1,2})?)\s*(?:%|\s*(?P<metric>BLEU|mAP|Accuracy|Precision|Recall|F1|F1-Score|Top-1|Top-5|AUC|ROUGE|WER))?',
            # Model achieves 95.4% Accuracy
            r'(?P<model>[A-Z0-9][A-Za-z0-9\-\_\(\)\s]{2,30})\s+(?:achieves?|obtained?|reaches?|demonstrates?|scored?|yields?|reports?)\s+(?:a\s+)?(?P<val>\d{1,3}(?:\.\d{1,2})?)\s*(?:%|\s*(?P<metric>accuracy|precision|recall|f1|f1-score|top-1|top-5|bleu|map|auc|rouge|fidelity|error rate))?',
            # Accuracy of 95.4% for Model
            r'(?P<metric>accuracy|precision|recall|f1-score|f1|top-1|top-5|bleu|map|auc|rouge|fidelity|error rate)\s+(?:of|is|was|reached)\s+(?P<val>\d{1,3}(?:\.\d{1,2})?)\s*(?:%|\s+points?)?\s*(?:for|with|by|on)?\s*(?P<model>[A-Z0-9][A-Za-z0-9\-\_\(\)\s]{2,30})?'
        ]

        for pat in comparison_patterns:
            for m in re.finditer(pat, target_text, re.IGNORECASE):
                groups = m.groupdict()
                val_str = groups.get("val")
                if not val_str:
                    continue
                try:
                    val_float = float(val_str)
                except (ValueError, TypeError):
                    continue

                if val_float <= 0 or val_float > 1000:
                    continue

                raw_model = groups.get("model") or "Proposed Framework"
                raw_model = raw_model.strip(" :–—-\n\t|()").strip()
                raw_model = re.sub(r'^(?:The|Our|A|In|With|For|Table \d+:?|Figure \d+:?)\s+', '', raw_model, flags=re.IGNORECASE)
                
                # Exclude invalid header or stop words
                invalid_model_names = [
                    "we", "this", "model", "method", "paper", "result", "results", "table", "figure",
                    "evaluation", "score", "value", "metric", "comparison", "baseline", "total", "average", "mean"
                ]
                if len(raw_model) < 2 or len(raw_model) > 35 or raw_model.lower() in invalid_model_names:
                    continue

                raw_metric = groups.get("metric") or "Accuracy"
                raw_metric = raw_metric.strip().upper()
                if raw_metric in ["ACCURACY", "ACC"]:
                    raw_metric = "Accuracy"
                elif raw_metric in ["F1", "F1-SCORE"]:
                    raw_metric = "F1 Score"
                elif raw_metric in ["TOP-1", "TOP1"]:
                    raw_metric = "Top-1 Accuracy"
                elif raw_metric in ["TOP-5", "TOP5"]:
                    raw_metric = "Top-5 Accuracy"
                elif raw_metric == "BLEU":
                    raw_metric = "BLEU Score"
                elif raw_metric == "MAP":
                    raw_metric = "mAP Score"
                elif raw_metric == "AUC":
                    raw_metric = "AUC Score"
                elif raw_metric == "FIDELITY":
                    raw_metric = "Fidelity"
                elif raw_metric == "LATENCY":
                    raw_metric = "Latency (ms)"
                elif raw_metric in ["ERROR RATE", "ERROR"]:
                    raw_metric = "Error Rate"
                else:
                    raw_metric = raw_metric.capitalize()

                key = (raw_model.lower(), raw_metric.lower())
                if key not in seen_keys:
                    seen_keys.add(key)
                    extracted_results.append({
                        "model_name": raw_model,
                        "metric_name": raw_metric,
                        "metric_value": val_float,
                        "comparison_group": f"{raw_metric} Benchmark"
                    })

        # 2. Survey, empirical findings, and percentage distributions
        empirical_patterns = [
            # 9 participants (45%) reported using ... or 9 participants / 45% ...
            r'(?P<count>\d+)\s*(?:participants?|students?|respondents?|subjects?|users?|informants?)\s*[\(\/\-]\s*(?P<val>\d{1,3}(?:\.\d{1,2})?)\s*%\s*[\)]?\s*(?:reported|stated|used|utilized|watched|engaged in|preferred|chose|indicated|for)?\s*(?P<label>[A-Za-z0-9\s\-\_\(\)\'\’\/]{3,65})',
            # 45% (9 participants) ...
            r'(?P<val>\d{1,3}(?:\.\d{1,2})?)\s*%\s*\(\s*(?P<count>\d+)\s*(?:participants?|students?|respondents?|subjects?|users?)\s*\)\s*(?:reported|stated|used|utilized|watched|engaged in|preferred|chose|indicated|for)?\s*(?P<label>[A-Za-z0-9\s\-\_\(\)\'\’\/]{3,65})',
            # 45% of participants reported ...
            r'(?P<val>\d{1,3}(?:\.\d{1,2})?)\s*%\s*(?:of\s+(?:the\s+)?(?:participants?|students?|respondents?|sample|users?|subjects?))?\s*(?:reported|stated|used|utilized|watched|engaged in|preferred|chose|indicated)\s+(?P<label>[A-Za-z0-9\s\-\_\(\)\'\’\/]{3,65})',
            # Item : 45% or Item - 45%
            r'(?:^|\n)\s*[\-\*\•]?\s*(?P<label>[A-Z][A-Za-z0-9\s\-\_\(\)\'\’\/]{2,40})\s*[:–—\-]\s*(?P<val>\d{1,3}(?:\.\d{1,2})?)\s*%'
        ]

        for pat in empirical_patterns:
            for m in re.finditer(pat, target_text, re.IGNORECASE):
                groups = m.groupdict()
                val_str = groups.get("val")
                if not val_str:
                    continue
                try:
                    val_float = float(val_str)
                except (ValueError, TypeError):
                    continue

                if val_float <= 0 or val_float > 100:
                    continue

                raw_label = groups.get("label") or "Empirical Observation"
                # Clean up raw label at clause splitters
                raw_label = re.split(r'[,;\.\n]|\bwhereas\b|\bwhile\b', raw_label, flags=re.IGNORECASE)[0].strip(" :–—-\n\t|()").strip()
                raw_label = re.sub(r'^(?:reported|stated|used|utilized|watched|engaged in|preferred|chose|indicated|that|to)\s+', '', raw_label, flags=re.IGNORECASE).strip()
                
                # Truncate clean label if too long
                if len(raw_label) > 55:
                    raw_label = raw_label[:52].rstrip() + "..."

                if len(raw_label) < 3 or raw_label.lower() in ["we", "this", "study", "paper", "data", "results"]:
                    continue

                label_formatted = raw_label[0].upper() + raw_label[1:] if len(raw_label) > 0 else raw_label
                count_info = f" ({groups['count']} participants)" if groups.get("count") else ""
                metric_name = "Percentage (%)"
                
                key = (label_formatted.lower(), metric_name.lower())
                if key not in seen_keys:
                    seen_keys.add(key)
                    extracted_results.append({
                        "model_name": f"{label_formatted}{count_info}",
                        "metric_name": metric_name,
                        "metric_value": val_float,
                        "comparison_group": "Survey & Empirical Findings"
                    })

        # 3. Check for explicit landmark model evaluations in paper text
        landmarks = [
            (r'Transformer\s*\(big\)[^\d]*(\d{1,2}(?:\.\d{1,2})?)', "Transformer (Big)", "BLEU Score"),
            (r'Transformer\s*\(base\)[^\d]*(\d{1,2}(?:\.\d{1,2})?)', "Transformer (Base)", "BLEU Score"),
            (r'ByteNet[^\d]*(\d{1,2}(?:\.\d{1,2})?)', "ByteNet", "BLEU Score"),
            (r'ConvS2S[^\d]*(\d{1,2}(?:\.\d{1,2})?)', "ConvS2S", "BLEU Score"),
            (r'MoE[^\d]*(\d{1,2}(?:\.\d{1,2})?)', "MoE Ensemble", "BLEU Score"),
            (r'ResNet-152[^\d]*(\d{1,3}(?:\.\d{1,2})?)', "ResNet-152", "Accuracy"),
            (r'ResNet-101[^\d]*(\d{1,3}(?:\.\d{1,2})?)', "ResNet-101", "Accuracy"),
            (r'ResNet-50[^\d]*(\d{1,3}(?:\.\d{1,2})?)', "ResNet-50", "Accuracy"),
            (r'ResNet-34[^\d]*(\d{1,3}(?:\.\d{1,2})?)', "ResNet-34", "Accuracy"),
            (r'ResNet-18[^\d]*(\d{1,3}(?:\.\d{1,2})?)', "ResNet-18", "Accuracy"),
            (r'VGG-16[^\d]*(\d{1,3}(?:\.\d{1,2})?)', "VGG-16", "Accuracy"),
            (r'GoogLeNet[^\d]*(\d{1,3}(?:\.\d{1,2})?)', "GoogLeNet", "Accuracy"),
            (r'AlexNet[^\d]*(\d{1,3}(?:\.\d{1,2})?)', "AlexNet", "Accuracy"),
        ]
        for pat, model_name, metric_name in landmarks:
            m = re.search(pat, target_text, re.IGNORECASE)
            if m:
                try:
                    v = float(m.group(1))
                    k = (model_name.lower(), metric_name.lower())
                    if k not in seen_keys:
                        seen_keys.add(k)
                        extracted_results.append({
                            "model_name": model_name,
                            "metric_name": metric_name,
                            "metric_value": v,
                            "comparison_group": f"{metric_name} Benchmark"
                        })
                except Exception:
                    pass

        # 4. If paper contains no suitable numerical comparison data, do NOT generate fake data.
        if len(extracted_results) < 2:
            return [], {
                "has_visualizations": False,
                "message": "No suitable numerical data was found in the paper for this visualization.",
                "chart_type": "none",
                "metrics_summary": [],
                "series": [],
                "table_rows": []
            }

        # Build chart data structures from pure extracted metrics
        metrics_set = list({r["metric_name"] for r in extracted_results})
        
        series = [
            {
                "name": item["model_name"],
                "value": item["metric_value"],
                "metric": item["metric_name"],
                "group": item["comparison_group"]
            }
            for item in extracted_results
        ]

        table_rows = [
            {
                "model": item["model_name"],
                "metric": item["metric_name"],
                "value": f"{item['metric_value']}%" if item["metric_value"] <= 100 and "accuracy" in item["metric_name"].lower() else str(item["metric_value"]),
                "benchmark": item["comparison_group"]
            }
            for item in extracted_results
        ]

        visualization_data = {
            "has_visualizations": True,
            "message": "Empirical metrics and comparative model benchmarks extracted directly from the research document.",
            "chart_type": "bar" if len(extracted_results) <= 8 else "comparison",
            "metrics_summary": metrics_set,
            "series": series,
            "table_rows": table_rows
        }

        return extracted_results, visualization_data
