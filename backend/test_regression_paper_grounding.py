import sys
from app.services.pdf_service import PDFService
from app.services.llm_service import LLMService
from app.services.summary_service import SummaryService
from app.services.visualization_service import VisualizationService
from app.services.analysis_service import AnalysisService

TEST_PAPER_TEXT = """A look at advanced learners’ use of mobile devices for English language study: Insights from interview data
Mariusz Kruk
University of Zielona Góra
mkruk@uz.zgora.pl

Abstract
The aim of this paper is to investigate how advanced English language learners use mobile devices for English language study. The study involved 20 advanced EFL students and employed semi-structured interviews. Both qualitative and quantitative analysis of the interview data revealed various patterns of mobile device usage, resources and tools used, language skills practiced, and perceived benefits for English language learning.

1. Introduction
With the proliferation of mobile technology, mobile-assisted language learning (MALL) has gained significant prominence. The primary problem investigated is the lack of in-depth qualitative and quantitative understanding regarding how advanced learners self-direct their English language study using mobile devices outside the classroom. The motivation behind this research is the need to explore learner autonomy and the actual practices of advanced students.

2. The Study
2.1. Participants
The study was conducted with 20 advanced English language students (9 males and 11 females) enrolled in an English philology program.

2.2. Data Collection and Analysis
Data collection was carried out by means of semi-structured interviews. The collected interview data were subjected to both qualitative and quantitative analysis, including coding recurring themes and computing frequencies and percentages.

3. Findings and Discussion
The findings demonstrate that 20 participants (100%) regularly use mobile devices for their English language learning. Specifically, 9 participants (45%) reported using mobile devices on a daily basis for more than two hours, whereas 11 participants (55%) reported using mobile devices between one and two hours per day. Furthermore, 16 participants (80%) utilized online dictionaries and translation applications, 14 participants (70%) watched English-language videos and listened to podcasts, and 12 participants (60%) engaged in social media and messaging in English.

4. Limitations and Future Research
A major limitation of the study is the relatively small sample size of 20 students from a single university. Future research should include larger and more diverse participant samples across different proficiency levels.

5. Conclusion and Pedagogical Implications
The findings highlight that advanced learners actively utilize mobile devices as powerful learning tools. The study contributes valuable insights into autonomous mobile-assisted language learning practices.
"""

PAPER_B_CV_TEXT = """Deep Residual Learning for Image Recognition
Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun
Microsoft Research

Abstract
Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously. We explicitly reformulate the layers as learning residual functions with reference to the layer inputs. On the ImageNet dataset, our ResNet-152 achieves 95.4% top-5 accuracy.

1. Introduction
The problem addressed is the degradation problem: with the network depth increasing, accuracy gets saturated. The motivation is to train ultra-deep networks easily.

2. Proposed Method
We introduce Deep Residual Networks with shortcut connections.

3. Results
On the ImageNet classification dataset, ResNet-50 achieves 93.3% accuracy, ResNet-101 achieves 94.6% accuracy, and ResNet-152 reaches 95.4% top-5 accuracy.

4. Conclusion
Residual networks provide comprehensive optimization benefits for visual recognition.
"""

PAPER_C_THEORETICAL_TEXT = """Philosophical Foundations of Machine Consciousness
Arthur Pendelton
Department of Philosophy, Oxford University

Abstract
This paper presents a conceptual critique of contemporary definitions of machine consciousness. We evaluate functionalist and phenomenological paradigms.

1. Introduction
The fundamental problem investigated is the ontological status of subjective experience in computational architectures.

2. Discussion
We argue that functional equivalence does not entail phenomenal awareness without biological grounding.

3. Conclusion
Philosophical rigor is essential for future AI consciousness frameworks.
"""

def test_regression_paper_author_extraction():
    lines = [line.strip() for line in TEST_PAPER_TEXT.split('\n') if line.strip()]
    author = PDFService.extract_clean_authors(TEST_PAPER_TEXT, lines)
    assert author == "Mariusz Kruk", f"Expected 'Mariusz Kruk', got '{author}'"
    assert "Zielona" not in author
    assert "mkruk" not in author

def test_regression_paper_sections_and_dataset():
    sections = PDFService.segment_sections(TEST_PAPER_TEXT)
    assert "20 advanced English language students" in sections["participants"]
    assert "semi-structured interviews" in sections["data_collection"]
    assert sections["dataset"] == "Dataset information is not explicitly mentioned in the paper."

def test_regression_paper_domain_detection():
    sections = PDFService.segment_sections(TEST_PAPER_TEXT)
    domain, recs, explanation = AnalysisService._detect_domain_and_recommendations(TEST_PAPER_TEXT, sections)
    assert domain in ["Education", "Social Science"], f"Expected Education or Social Science, got '{domain}'"

def test_regression_paper_structured_analysis():
    sections = PDFService.segment_sections(TEST_PAPER_TEXT)
    analysis = LLMService.extract_structured_analysis(
        TEST_PAPER_TEXT, sections, "Education", "Research Paper", sections["title"], sections["authors"]
    )
    
    assert analysis["dataset"] == "Dataset information is not explicitly mentioned in the paper."
    assert "20" in analysis["methodology"]
    assert "interview" in analysis["methodology"].lower()
    assert "20" in analysis["key_findings"] or "45%" in analysis["results"] or "55%" in analysis["results"]
    assert "sample size" in analysis["limitations"].lower() or "limitation" in analysis["limitations"].lower()

def test_regression_paper_easy_summary():
    sections = PDFService.segment_sections(TEST_PAPER_TEXT)
    easy_summary = SummaryService.generate_easy_summary(sections, "Education")
    
    assert easy_summary["what_is_this_paper_about"] != "Not explicitly mentioned in the paper."
    assert "mobile" in easy_summary["what_is_this_paper_about"].lower()
    assert "20" in easy_summary["how_was_it_performed"] or "interview" in easy_summary["how_was_it_performed"].lower()
    assert easy_summary["what_was_the_result"] != "Not explicitly mentioned in the paper."

def test_regression_paper_dynamic_visualizations():
    sections = PDFService.segment_sections(TEST_PAPER_TEXT)
    extracted_metrics, viz_data = VisualizationService.extract_metrics_and_comparisons(TEST_PAPER_TEXT, sections, "Education")
    
    assert viz_data["has_visualizations"] is True
    assert len(viz_data["series"]) >= 2
    
    values = [item["value"] for item in viz_data["series"]]
    assert 45.0 in values or 55.0 in values or 80.0 in values, f"Expected 45.0, 55.0, or 80.0 in {values}"
    
    # Assert NO domain default benchmarks were injected
    names = [item["name"] for item in viz_data["series"]]
    for name in names:
        assert "transformer" not in name.lower()
        assert "resnet" not in name.lower()

def test_cross_paper_isolation():
    # Test Paper A (Mariusz Kruk / Education)
    sections_a = PDFService.segment_sections(TEST_PAPER_TEXT)
    author_a = PDFService.extract_clean_authors(TEST_PAPER_TEXT, [l.strip() for l in TEST_PAPER_TEXT.split('\n') if l.strip()])
    _, viz_a = VisualizationService.extract_metrics_and_comparisons(TEST_PAPER_TEXT, sections_a, "Education")
    
    # Test Paper B (Kaiming He / ResNet / Computer Vision)
    sections_b = PDFService.segment_sections(PAPER_B_CV_TEXT)
    author_b = PDFService.extract_clean_authors(PAPER_B_CV_TEXT, [l.strip() for l in PAPER_B_CV_TEXT.split('\n') if l.strip()])
    _, viz_b = VisualizationService.extract_metrics_and_comparisons(PAPER_B_CV_TEXT, sections_b, "Computer Vision")
    
    assert author_a == "Mariusz Kruk"
    assert "Kaiming He" in author_b
    assert author_a != author_b
    
    # Verify Visualizations differ completely and are isolated
    values_a = [s["value"] for s in viz_a["series"]]
    values_b = [s["value"] for s in viz_b["series"]]
    assert values_a != values_b

def test_no_numerical_data_handling():
    sections_c = PDFService.segment_sections(PAPER_C_THEORETICAL_TEXT)
    extracted_metrics, viz_data = VisualizationService.extract_metrics_and_comparisons(PAPER_C_THEORETICAL_TEXT, sections_c, "Other")
    
    assert viz_data["has_visualizations"] is False
    assert viz_data["message"] == "No suitable numerical data was found in the paper for this visualization."
    assert len(viz_data["series"]) == 0
    assert len(viz_data["table_rows"]) == 0

if __name__ == "__main__":
    tests = [
        test_regression_paper_author_extraction,
        test_regression_paper_sections_and_dataset,
        test_regression_paper_domain_detection,
        test_regression_paper_structured_analysis,
        test_regression_paper_easy_summary,
        test_regression_paper_dynamic_visualizations,
        test_cross_paper_isolation,
        test_no_numerical_data_handling
    ]
    for t in tests:
        t()
        print(f"PASS: {t.__name__}")
    print("\nALL REGRESSION TESTS PASSED SUCCESSFULLY!")
