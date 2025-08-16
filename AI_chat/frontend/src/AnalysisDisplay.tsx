import React from 'react';
import ReactMarkdown from 'react-markdown';
import './AnalysisDisplay.css';

interface AnalysisDisplayProps {
  content: string;
}

const AnalysisDisplay: React.FC<AnalysisDisplayProps> = ({ content }) => {
  // Extract only the analysis field from JSON
  let analysisContent = content; // fallback to original content
  
  try {
    const jsonStart = content.indexOf('{');
    if (jsonStart !== -1) {
      const jsonStr = content.substring(jsonStart);
      const data = JSON.parse(jsonStr);
      
      // Extract only the analysis field
      if (data.analysis?.analysis) {
        analysisContent = data.analysis.analysis;
      }
    }
  } catch (error) {
    // If parsing fails, use original content
  }

  return (
    <div className="analysis-display">
      <div className="analysis-section">
        <div className="analysis-content markdown-content">
          <ReactMarkdown>{analysisContent}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default AnalysisDisplay;
