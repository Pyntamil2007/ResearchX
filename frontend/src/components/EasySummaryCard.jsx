import React from 'react';
import { HelpCircle, Target, Lightbulb, Cog, Award, CheckCircle2, Sparkles } from 'lucide-react';

export const EasySummaryCard = ({ easySummary }) => {
  if (!easySummary) return null;

  const items = [
    {
      qNum: "1",
      question: "What is this paper about?",
      answer: easySummary.what_is_this_paper_about,
      icon: <HelpCircle size={16} />
    },
    {
      qNum: "2",
      question: "What problem does it solve?",
      answer: easySummary.what_problem_does_it_solve,
      icon: <Target size={16} />
    },
    {
      qNum: "3",
      question: "Why was the research conducted?",
      answer: easySummary.why_was_the_research_conducted,
      icon: <Lightbulb size={16} />
    },
    {
      qNum: "4",
      question: "How was it performed?",
      answer: easySummary.how_was_it_performed,
      icon: <Cog size={16} />
    },
    {
      qNum: "5",
      question: "What was the result?",
      answer: easySummary.what_was_the_result,
      icon: <CheckCircle2 size={16} />
    },
    {
      qNum: "6",
      question: "What is the main contribution?",
      answer: easySummary.what_is_the_main_contribution,
      icon: <Award size={16} />
    }
  ];

  return (
    <div style={{ marginBottom: '2.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.25rem' }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff'
        }}>
          <Sparkles size={18} />
        </div>
        <div>
          <h2 style={{ fontSize: '1.35rem', margin: 0 }}>
            Easy Summary <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500 }}>(Beginner-Friendly Explanation)</span>
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-dim)', margin: 0 }}>
            Plain-language breakdown answering the six fundamental questions of this study.
          </p>
        </div>
      </div>

      <div className="easy-summary-grid">
        {items.map((item, idx) => (
          <div key={idx} className="easy-summary-card">
            <div className="easy-summary-question">
              <div className="easy-summary-q-icon">
                {item.qNum}
              </div>
              <span>{item.question}</span>
            </div>
            <p className="easy-summary-answer">
              {item.answer || 'Information not available in the paper.'}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
