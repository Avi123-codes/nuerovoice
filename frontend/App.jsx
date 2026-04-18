import React, { useState } from "react";
import axios from "axios";
import { Bar } from "react-chartjs-2";
import "chart.js/auto";

function App() {
  const [text, setText] = useState("");
  const [reply, setReply] = useState("");
  const [analysis, setAnalysis] = useState(null);

  const handleChat = async () => {
    const res = await axios.post("http://localhost:8000/chat", { text });
    setReply(res.data.reply);
  };

  const handleAnalyze = async () => {
    const res = await axios.post("http://localhost:8000/analyze", { text });
    setAnalysis(res.data);
  };

  const indicatorData = {
    labels: ["Repetition", "Confusion", "Memory Fail", "ML Score"],
    datasets: [
      {
        label: "Cognitive Indicators",
        data: analysis
          ? [
              analysis.details.repetition,
              analysis.details.confusion,
              analysis.details.memory_fail,
              analysis.details.ml_score * 10
            ]
          : [0, 0, 0, 0],
      },
    ],
  };

  const trendData = {
    labels: analysis?.history.map((_, i) => `Session ${i + 1}`),
    datasets: [
      {
        label: "Cognitive Risk Trend",
        data: analysis?.history,
      },
    ],
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold">NeuroVoice Companion</h1>

      <textarea
        className="border p-2 w-full mt-4"
        placeholder="Enter patient speech..."
        onChange={(e) => setText(e.target.value)}
      />

      <div className="mt-4 space-x-2">
        <button onClick={handleChat} className="bg-blue-500 text-white px-4 py-2">
          Talk
        </button>

        <button onClick={handleAnalyze} className="bg-green-500 text-white px-4 py-2">
          Analyze
        </button>
      </div>

      <div className="mt-4">
        <h2 className="text-lg font-semibold">AI Reply:</h2>
        <p>{reply}</p>
      </div>

      {analysis && (
        <div className="mt-6">
          <h2 className="text-xl font-bold">Risk Result:</h2>
          <p>{analysis.result}</p>

          <h3 className="mt-4">Cognitive Indicators</h3>
          <Bar data={indicatorData} />

          <h3 className="mt-6">Trend Over Time</h3>
          <Bar data={trendData} />
        </div>
      )}
    </div>
  );
}

export default App;
