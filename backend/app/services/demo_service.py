import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.paper import ResearchPaper

class DemoService:
    @staticmethod
    def generate_sample_pdfs():
        """Generate realistic academic research PDF files for testing and demonstration."""
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'AcademicTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        author_style = ParagraphStyle(
            'AcademicAuthor',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            spaceAfter=15
        )
        
        heading_style = ParagraphStyle(
            'AcademicHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            spaceBefore=12,
            spaceAfter=6
        )
        
        body_style = ParagraphStyle(
            'AcademicBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        )

        papers_to_create = [
            {
                "file_name": "ResNet_Deep_Residual_Learning.pdf",
                "title": "Deep Residual Learning for Image Recognition",
                "authors": "Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun (Microsoft Research)",
                "sections": [
                    ("ABSTRACT", "Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously. We explicitly reformulate the layers as learning residual functions with reference to the layer inputs, instead of learning unreferenced functions. We provide comprehensive empirical evidence showing that these residual networks are easier to optimize, and can gain accuracy from considerably increased depth. On the ImageNet dataset, we evaluate residual nets with a depth of up to 152 layers—8× deeper than VGG nets but still having lower complexity. An ensemble of these residual nets achieves 3.57% error on the ImageNet test set."),
                    ("1. INTRODUCTION", "Deep convolutional neural networks have led to a series of breakthroughs for image classification. When deeper networks are able to start converging, a degradation problem has been exposed: with the network depth increasing, accuracy gets saturated and then degrades rapidly. Unexpectedly, such degradation is not caused by overfitting, and adding more layers to a suitably deep model leads to higher training error."),
                    ("2. PROPOSED METHOD", "In this paper, we address the degradation problem by introducing a deep residual learning framework. Instead of hoping each few stacked layers directly fit a desired underlying mapping, we explicitly let these layers fit a residual mapping. Formally, denoting the desired underlying mapping as H(x), we let the stacked nonlinear layers fit another mapping of F(x) := H(x) - x. The original mapping is recast into F(x) + x. We hypothesize that it is easier to optimize the residual mapping than to optimize the original, unreferenced mapping."),
                    ("3. EXPERIMENTAL SETUP", "Our ImageNet 2012 classification dataset consists of 1,000 classes. The models are trained on the 1.28 million training images, and evaluated on the 50,000 validation images. We use standard data augmentation, batch normalization immediately after each convolution, and stochastic gradient descent (SGD) with a mini-batch size of 256."),
                    ("4. EXPERIMENTAL RESULTS", "We evaluate our method on the ImageNet benchmark. The performance across different model architectures shows clear superiority of residual representations. ResNet-152: 96.4% Top-1 Accuracy. ResNet-50: 95.2% Top-1 Accuracy. ResNet-34: 92.8% Top-1 Accuracy. VGG-16: 89.4% Top-1 Accuracy. AlexNet: 82.1% Top-1 Accuracy. The 152-layer ResNet demonstrates significant empirical gains while maintaining competitive computational latency."),
                    ("5. DISCUSSION", "The degradation problem illustrates that deep plain networks have exponentially large convergence difficulties. In contrast, our residual learning framework enables efficient training and backpropagation without vanishing gradients."),
                    ("6. LIMITATIONS", "Extremely deep residual architectures still require considerable GPU memory buffers during forward-backward propagation passes and training epochs."),
                    ("7. FUTURE WORK", "We plan to extend residual learning mechanisms to object detection, semantic segmentation, and temporal sequence modeling frameworks."),
                    ("8. CONCLUSION", "We have introduced a deep residual learning framework for image recognition. Deep residual networks are easy to optimize and substantially improve classification accuracy with greater depth.")
                ]
            },
            {
                "file_name": "Attention_Is_All_You_Need.pdf",
                "title": "Attention Is All You Need: The Transformer Architecture",
                "authors": "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit (Google Brain & Google Research)",
                "sections": [
                    ("ABSTRACT", "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 41.8 BLEU on the WMT 2014 English-to-French translation task."),
                    ("1. INTRODUCTION", "Recurrent neural networks, long short-term memory (LSTM) and gated recurrent neural networks have been firmly established as state of the art approaches in sequence modeling. In this work we propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output."),
                    ("2. PROPOSED METHOD", "The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder. Multi-Head Attention allows the model to jointly attend to information from different representation subspaces at different positions."),
                    ("3. EXPERIMENTAL SETUP", "We trained on the standard WMT 2014 English-German dataset consisting of about 4.5 million sentence pairs. Sentences were encoded using byte-pair encoding, which has a shared source-target vocabulary of about 37000 tokens."),
                    ("4. EXPERIMENTAL RESULTS", "On the translation benchmarks, the Transformer outperforms existing architectures: Transformer-Big: 41.8 BLEU. Transformer-Base: 38.4 BLEU. ConvS2S: 32.8 BLEU. ByteNet: 23.7 BLEU. GNMT: 24.6 BLEU. Training cost was reduced by over 80% compared to recurrent baselines."),
                    ("5. LIMITATIONS", "Self-attention computes pairwise token similarities with O(N^2) complexity with respect to sequence length, creating memory bottlenecks on very long documents."),
                    ("6. FUTURE WORK", "Future research will explore sparse attention patterns, linear attention approximations, and multi-modal audio-visual applications."),
                    ("7. CONCLUSION", "In this work, we presented the Transformer, the first sequence transduction model based entirely on attention.")
                ]
            },
            {
                "file_name": "Qualitative_AI_Ethics_Governance.pdf",
                "title": "A Qualitative Survey on Ethical AI Governance and Algorithmic Accountability",
                "authors": "Dr. Elena Rostova, Marcus Vance (Center for Technology & Society)",
                "sections": [
                    ("ABSTRACT", "The exponential deployment of autonomous algorithmic systems in public and private institutions necessitates robust ethical governance frameworks. This qualitative study examines institutional policies, algorithmic transparency mandates, and stakeholder accountability mechanisms across forty-five international organizations. We analyze governance principles, procedural fairness guidelines, and organizational incentives to synthesize actionable policy recommendations for sustainable and equitable AI development."),
                    ("1. INTRODUCTION", "As algorithmic decision-making expands into criminal justice, credit scoring, and healthcare triage, the societal ramifications of systemic bias become paramount. While technical interventions like mathematical fairness constraints are valuable, comprehensive governance demands procedural oversight, institutional audit trails, and multi-stakeholder participation."),
                    ("2. METHODOLOGY", "We conducted semi-structured qualitative interviews with chief ethics officers, legal scholars, civil rights advocates, and machine learning practitioners across Europe, North America, and the Asia-Pacific region. Grounded theory methodology was utilized to categorize themes and regulatory frameworks."),
                    ("3. DISCUSSION", "Our qualitative evaluation reveals a critical gap between high-level ethical principles and operational engineering workflows. While organizations express commitment to algorithmic transparency, few possess formal auditing infrastructure or independent grievance mechanisms for affected individuals."),
                    ("4. LIMITATIONS", "This survey is restricted to institutional perspectives and policy documents available in English and French during the 2023-2024 review cycle."),
                    ("5. FUTURE WORK", "Subsequent research will investigate participatory governance models involving directly impacted communities in algorithmic co-design."),
                    ("6. CONCLUSION", "Effective AI governance requires moving beyond voluntary self-regulation toward enforceable procedural accountability, independent auditing frameworks, and democratic oversight.")
                ]
            }
        ]

        for paper_info in papers_to_create:
            target_path = settings.DEMO_DIR / paper_info["file_name"]
            if not target_path.exists():
                doc = SimpleDocTemplate(
                    str(target_path),
                    pagesize=letter,
                    rightMargin=54,
                    leftMargin=54,
                    topMargin=54,
                    bottomMargin=54
                )
                
                story = []
                # Title & Authors
                story.append(Paragraph(paper_info["title"], title_style))
                story.append(Paragraph(paper_info["authors"], author_style))
                story.append(Spacer(1, 10))
                
                # Sections
                for sec_heading, sec_body in paper_info["sections"]:
                    story.append(Paragraph(sec_heading, heading_style))
                    story.append(Paragraph(sec_body, body_style))
                    story.append(Spacer(1, 4))
                    
                doc.build(story)

    @staticmethod
    def ensure_demo_files():
        """Ensure sample PDF files exist on disk in DEMO_DIR without creating any database records."""
        DemoService.generate_sample_pdfs()
