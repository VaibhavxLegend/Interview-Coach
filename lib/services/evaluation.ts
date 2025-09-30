import { Evaluation } from '../types';

/**
 * Evaluates an interview answer based on multiple criteria
 * This is a rule-based evaluation system that can be enhanced with AI APIs
 */
export function evaluateAnswer(answer: string): Evaluation {
  // Basic evaluation metrics
  const wordCount = answer.trim().split(/\s+/).length;
  const sentenceCount = answer.split(/[.!?]+/).filter(s => s.trim().length > 0).length;
  const avgWordsPerSentence = sentenceCount > 0 ? wordCount / sentenceCount : 0;
  
  // Clarity (0-10): Based on sentence structure and coherence
  let clarity = 5;
  if (avgWordsPerSentence >= 10 && avgWordsPerSentence <= 25) clarity += 3;
  else if (avgWordsPerSentence >= 8 && avgWordsPerSentence <= 30) clarity += 2;
  else if (avgWordsPerSentence < 5 || avgWordsPerSentence > 40) clarity -= 1;
  
  if (wordCount >= 50) clarity += 2;
  else if (wordCount < 20) clarity -= 2;
  
  clarity = Math.max(0, Math.min(10, clarity));
  
  // Conciseness (0-10): Based on word count and redundancy
  let conciseness = 7;
  if (wordCount >= 50 && wordCount <= 150) conciseness += 2;
  else if (wordCount > 200) conciseness -= 2;
  else if (wordCount < 30) conciseness -= 1;
  
  const repetitiveWords = detectRepetition(answer);
  if (repetitiveWords > 3) conciseness -= 2;
  
  conciseness = Math.max(0, Math.min(10, conciseness));
  
  // Confidence (0-10): Based on language patterns
  let confidence = 6;
  const uncertainPhrases = ['i think', 'maybe', 'probably', 'i guess', 'not sure', 'kind of', 'sort of'];
  const confidencePhrases = ['i believe', 'certainly', 'definitely', 'clearly', 'in my experience'];
  
  const lowerAnswer = answer.toLowerCase();
  uncertainPhrases.forEach(phrase => {
    if (lowerAnswer.includes(phrase)) confidence -= 0.5;
  });
  confidencePhrases.forEach(phrase => {
    if (lowerAnswer.includes(phrase)) confidence += 0.5;
  });
  
  confidence = Math.max(0, Math.min(10, confidence));
  
  // Technical Depth (0-10): Based on technical keywords and detail
  let technicalDepth = 5;
  const technicalKeywords = [
    'algorithm', 'complexity', 'data structure', 'optimization', 'performance',
    'scalability', 'architecture', 'implementation', 'api', 'framework',
    'function', 'method', 'class', 'object', 'interface', 'component',
    'state', 'props', 'hook', 'callback', 'promise', 'async', 'await',
    'variable', 'scope', 'closure', 'prototype', 'inheritance', 'encapsulation',
    'database', 'query', 'index', 'cache', 'server', 'client'
  ];
  
  let techKeywordCount = 0;
  technicalKeywords.forEach(keyword => {
    if (lowerAnswer.includes(keyword)) {
      techKeywordCount++;
    }
  });
  
  if (techKeywordCount >= 5) technicalDepth += 3;
  else if (techKeywordCount >= 3) technicalDepth += 2;
  else if (techKeywordCount >= 1) technicalDepth += 1;
  
  if (wordCount > 100) technicalDepth += 1;
  
  technicalDepth = Math.max(0, Math.min(10, technicalDepth));
  
  // Calculate overall score
  const overallScore = Math.round(
    (clarity + conciseness + confidence + technicalDepth) / 4
  );
  
  // Generate feedback
  const feedback = generateFeedback({
    clarity,
    conciseness,
    confidence,
    technicalDepth,
    overallScore,
    feedback: '',
    improvements: []
  }, wordCount);
  
  // Generate improvements
  const improvements = generateImprovements({
    clarity,
    conciseness,
    confidence,
    technicalDepth,
    overallScore,
    feedback: '',
    improvements: []
  });
  
  return {
    clarity,
    conciseness,
    confidence,
    technicalDepth,
    overallScore,
    feedback,
    improvements
  };
}

function detectRepetition(text: string): number {
  const words = text.toLowerCase().split(/\s+/);
  const wordFrequency: { [key: string]: number } = {};
  
  words.forEach(word => {
    if (word.length > 4) { // Only count meaningful words
      wordFrequency[word] = (wordFrequency[word] || 0) + 1;
    }
  });
  
  return Object.values(wordFrequency).filter(count => count > 2).length;
}

function generateFeedback(evaluation: Evaluation, wordCount: number): string {
  const { overallScore, clarity, conciseness, confidence, technicalDepth } = evaluation;
  
  let feedback = '';
  
  if (overallScore >= 8) {
    feedback = 'Excellent answer! You demonstrated strong understanding and communication skills.';
  } else if (overallScore >= 6) {
    feedback = 'Good answer overall. There are a few areas where you can improve.';
  } else if (overallScore >= 4) {
    feedback = 'Your answer shows basic understanding, but needs significant improvement.';
  } else {
    feedback = 'Your answer needs substantial work. Consider reviewing the topic and practicing more.';
  }
  
  const details = [];
  
  if (clarity < 5) details.push('Try to structure your thoughts more clearly.');
  else if (clarity >= 8) details.push('Your answer was very clear and well-structured.');
  
  if (conciseness < 5) details.push('Work on being more concise and avoiding redundancy.');
  else if (conciseness >= 8) details.push('Your answer was appropriately concise.');
  
  if (confidence < 5) details.push('Try to sound more confident and avoid uncertain language.');
  else if (confidence >= 8) details.push('You demonstrated good confidence in your answer.');
  
  if (technicalDepth < 5) details.push('Add more technical details and specific examples.');
  else if (technicalDepth >= 8) details.push('You showed excellent technical depth.');
  
  if (details.length > 0) {
    feedback += ' ' + details.join(' ');
  }
  
  return feedback;
}

function generateImprovements(evaluation: Evaluation): string[] {
  const improvements: string[] = [];
  const { clarity, conciseness, confidence, technicalDepth } = evaluation;
  
  if (clarity < 7) {
    improvements.push('Structure your answer with a clear beginning, middle, and end. Use transitional phrases.');
  }
  
  if (conciseness < 7) {
    improvements.push('Eliminate redundant phrases and get to the point more quickly. Aim for 50-150 words.');
  }
  
  if (confidence < 7) {
    improvements.push('Avoid uncertain phrases like "I think" or "maybe". Use definitive language like "This is" or "In my experience".');
  }
  
  if (technicalDepth < 7) {
    improvements.push('Include more technical terminology and specific examples. Mention relevant algorithms, data structures, or design patterns.');
  }
  
  if (improvements.length === 0) {
    improvements.push('Great job! Continue practicing to maintain this level of performance.');
    improvements.push('Try answering more challenging questions to further develop your skills.');
  }
  
  return improvements;
}
