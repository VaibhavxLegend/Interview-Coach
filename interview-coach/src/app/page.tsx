"use client";
import { useEffect, useRef, useState } from "react";
import { startSession as apiStart, submitAnswer as apiSubmit, completeSession as apiComplete } from "../lib/api";

type Message = { role: "system" | "assistant" | "user"; content: string };

export default function Home() {
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [input, setInput] = useState("");
  const [question, setQuestion] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [listening, setListening] = useState(false);
  const [email, setEmail] = useState("");
  const [summary, setSummary] = useState<string | null>(null);
  // Minimal typing for Web Speech API
  type SRType = {
    start: () => void;
    stop: () => void;
    lang: string;
    interimResults: boolean;
    maxAlternatives: number;
    onresult: ((event: { results: { [key: number]: { [key: number]: { transcript: string } } } }) => void) | null;
    onend: (() => void) | null;
  };
  const recognitionRef = useRef<SRType | null>(null);

  useEffect(() => {
    // Start session on load
    const start = async () => {
      try {
        const data = await apiStart();
        setSessionId(data.session_id);
        setQuestion(data.question);
        setMessages([{ role: "assistant", content: data.question }]);
      } catch (e) {
        console.error(e);
      }
    };
    start();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const submitAnswer = async (answer: string) => {
    if (!sessionId || !question) return;
    setMessages((m) => [...m, { role: "user", content: answer }]);
    setInput("");
    try {
      const data = await apiSubmit(sessionId, question, answer);
      const evalText = `Score: ${data.evaluation.overall}/10\n` +
        `- Clarity: ${data.evaluation.clarity}\n` +
        `- Conciseness: ${data.evaluation.conciseness}\n` +
        `- Confidence: ${data.evaluation.confidence}\n` +
        `- Technical Depth: ${data.evaluation.technical_depth}\n` +
        `Feedback: ${data.evaluation.friendly}`;
      setMessages((m) => [
        ...m,
        { role: "assistant", content: evalText },
        { role: "assistant", content: data.next_question },
      ]);
      setQuestion(data.next_question);
    } catch (e) {
      console.error(e);
    }
  };

  const onMicToggle = () => {
  const w = window as unknown as { webkitSpeechRecognition?: new () => SRType; SpeechRecognition?: new () => SRType };
  const SpeechRecognition = w.webkitSpeechRecognition || w.SpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech Recognition not supported in this browser.");
      return;
    }
    if (!recognitionRef.current) {
      const rec = new SpeechRecognition();
      rec.lang = "en-US";
      rec.interimResults = false;
      rec.maxAlternatives = 1;
      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        submitAnswer(transcript);
      };
      rec.onend = () => setListening(false);
      recognitionRef.current = rec;
    }
    if (!listening) {
      setListening(true);
      recognitionRef.current.start();
    } else {
      recognitionRef.current.stop();
    }
  };

  return (
    <div className="min-h-screen p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">Interview Coach</h1>
      <div className="border rounded-md p-4 space-y-3 bg-white/50">
        <div className="h-[420px] overflow-y-auto border rounded p-3 bg-white">
          {messages.map((m, i) => (
            <div key={i} className={m.role === "user" ? "text-right" : "text-left"}>
              <span className={`inline-block px-3 py-2 my-1 rounded-md ${m.role === "user" ? "bg-green-100" : "bg-blue-50"}`}>
                <strong>{m.role === "user" ? "You" : "Coach"}:</strong> {m.content}
              </span>
            </div>
          ))}
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (input.trim()) submitAnswer(input.trim());
          }}
          className="flex gap-2"
        >
          <input
            className="flex-1 border rounded px-3 py-2"
            placeholder="Type your answer..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button className="px-4 py-2 rounded bg-black text-white" type="submit">Send</button>
          <button className="px-3 py-2 rounded border" type="button" onClick={onMicToggle}>
            {listening ? "Stop" : "🎤 Speak"}
          </button>
        </form>
        <div className="flex items-center gap-2">
          <input
            className="flex-1 border rounded px-3 py-2"
            placeholder="Email to receive summary (optional)"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <button
            className="px-4 py-2 rounded border"
            type="button"
            onClick={async () => {
              if (!sessionId) return;
              try {
                const data = await apiComplete(sessionId, email || undefined);
                setSummary(data.summary);
              } catch (e) {
                console.error(e);
              }
            }}
          >
            End Session
          </button>
        </div>
        {summary && (
          <div className="mt-2 text-sm text-gray-700 bg-gray-50 border rounded p-2 whitespace-pre-line">{summary}</div>
        )}
      </div>
      <p className="text-xs text-gray-500 mt-3">Tip: Use the mic or type. The coach evaluates clarity, conciseness, confidence, and technical depth.</p>
    </div>
  );
}
