# Interview-Coach

A web application for practicing mock interviews with AI-powered evaluation and feedback.

## Features

- 🎤 **Speech-to-Text**: Use your microphone to speak answers or type them
- 📝 **Text Input**: Type your answers if you prefer
- 🤖 **AI Evaluation**: Get instant feedback on your answers based on:
  - **Clarity**: How well-structured and coherent your answer is
  - **Conciseness**: Whether you get to the point without being redundant
  - **Confidence**: How confidently you express yourself
  - **Technical Depth**: The level of technical detail in your answer
- 💾 **Session History**: Review past practice sessions and track improvement
- 📊 **Detailed Feedback**: Get specific suggestions for improvement
- 🎯 **Diverse Questions**: Practice with questions across multiple categories

## Getting Started

### Prerequisites

- Node.js 18.x or later
- npm (comes with Node.js)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/VaibhavxLegend/Interview-Coach.git
cd Interview-Coach
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

```bash
npm run build
npm start
```

## How to Use

1. **Start Practicing**: Click on a question to begin
2. **Answer the Question**: 
   - Type your answer in the text area, or
   - Click the microphone button to use speech-to-text
3. **Submit**: Click "Submit Answer" when ready
4. **Review Feedback**: See your scores and improvement suggestions
5. **Track Progress**: View your history to see how you're improving over time

## Technologies Used

- **Next.js 15**: React framework for production
- **TypeScript**: For type safety
- **Tailwind CSS**: For styling
- **Web Speech API**: For speech recognition
- **Local Storage**: For persisting session data

## Question Categories

- JavaScript
- React
- Data Structures
- Algorithms
- System Design
- General/Behavioral

## Evaluation Criteria

Each answer is evaluated on four key dimensions:

1. **Clarity (0-10)**: Measures how well-structured and easy to understand your answer is
2. **Conciseness (0-10)**: Assesses whether you communicate efficiently without redundancy
3. **Confidence (0-10)**: Evaluates the confidence level in your language and expression
4. **Technical Depth (0-10)**: Measures the technical detail and accuracy of your response

## Future Enhancements

- Integration with OpenAI API for more sophisticated evaluation
- More question categories and difficulty levels
- Video recording for behavioral interview practice
- Analytics dashboard for tracking improvement over time
- Customizable question sets
- Multiplayer mode for peer practice

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Vaibhav Jain

## Acknowledgments

- Built with Next.js and React
- Inspired by the need for accessible interview practice tools
