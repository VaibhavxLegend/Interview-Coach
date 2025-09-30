import { Question } from '../types';

export const sampleQuestions: Question[] = [
  {
    id: '1',
    category: 'JavaScript',
    difficulty: 'Easy',
    question: 'What is the difference between let, const, and var in JavaScript?',
    topic: 'Variables'
  },
  {
    id: '2',
    category: 'JavaScript',
    difficulty: 'Medium',
    question: 'Explain closures in JavaScript with an example.',
    topic: 'Functions'
  },
  {
    id: '3',
    category: 'React',
    difficulty: 'Easy',
    question: 'What are React hooks and why were they introduced?',
    topic: 'Hooks'
  },
  {
    id: '4',
    category: 'React',
    difficulty: 'Medium',
    question: 'How does the Virtual DOM work in React?',
    topic: 'Virtual DOM'
  },
  {
    id: '5',
    category: 'Data Structures',
    difficulty: 'Easy',
    question: 'What is the difference between an array and a linked list?',
    topic: 'Arrays and Linked Lists'
  },
  {
    id: '6',
    category: 'Data Structures',
    difficulty: 'Medium',
    question: 'Explain how a hash table works and its time complexity.',
    topic: 'Hash Tables'
  },
  {
    id: '7',
    category: 'System Design',
    difficulty: 'Hard',
    question: 'How would you design a URL shortening service like bit.ly?',
    topic: 'System Design'
  },
  {
    id: '8',
    category: 'Algorithms',
    difficulty: 'Medium',
    question: 'Explain the difference between BFS and DFS. When would you use each?',
    topic: 'Graph Algorithms'
  },
  {
    id: '9',
    category: 'JavaScript',
    difficulty: 'Hard',
    question: 'What is the event loop in JavaScript and how does it work?',
    topic: 'Asynchronous Programming'
  },
  {
    id: '10',
    category: 'General',
    difficulty: 'Easy',
    question: 'Tell me about yourself and your technical background.',
    topic: 'Behavioral'
  }
];

export function getRandomQuestion(): Question {
  return sampleQuestions[Math.floor(Math.random() * sampleQuestions.length)];
}

export function getQuestionById(id: string): Question | undefined {
  return sampleQuestions.find(q => q.id === id);
}
