import React, { useEffect, useState } from "react";

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/coverage") // Make sure this matches your FastAPI endpoint
      .then((res) => res.json())
      .then((result) => {
        // Sort suggestions by score descending
        if (result.suggestions) {
          result.suggestions.sort((a, b) => b.score - a.score);
        }
        setData(result);
        setLoading(false);
      })
      .catch((err) => {
        console.error("API error:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div style={{ padding: 20 }}>Loading coverage data...</div>;
  }

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h2>Coverage Analyzer Dashboard</h2>

      <p>
        <strong>Design:</strong> {data.design}
      </p>
      <p>
        <strong>Overall Coverage:</strong> {data.overall_coverage}%
      </p>

      <h3>Uncovered Bins</h3>
      <table border="1" cellPadding="8" cellSpacing="0" width="100%">
        <thead>
          <tr>
            <th>Covergroup</th>
            <th>Coverpoint</th>
            <th>Bin</th>
          </tr>
        </thead>
        <tbody>
          {data.uncovered_bins.map((bin, idx) => (
            <tr key={idx}>
              <td>{bin.covergroup}</td>
              <td>{bin.coverpoint}</td>
              <td>{bin.bin}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3 style={{ marginTop: 30 }}>Prioritized Suggestions</h3>
{(data.suggestions || []).map((item, idx) => (
  <div
    key={idx}
    style={{
      border: "1px solid #ccc",
      padding: "12px",
      marginBottom: "12px",
      borderRadius: "4px",
    }}
  >
    <p>
      <strong>Target Bin:</strong> {item.target_bin}
    </p>
    <p>
      <strong>Score:</strong> {item.score}
    </p>
    <p>
      <strong>Priority:</strong> {item.priority} |{" "}
      <strong>Difficulty:</strong> {item.difficulty}
    </p>
    <p>
      <strong>Suggestion:</strong> {item.suggestion}
    </p>
    <p>
      <strong>Dependencies:</strong>{" "}
      {(item.dependencies || []).join(", ")}
    </p>
    <p>
      <strong>Test Outline:</strong>
      <ol>
        {(item.test_outline || []).map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ol>
    </p>
    <p>
      <strong>Reasoning:</strong> {item.reasoning}
    </p>
  </div>
))}

    <h3 style={{ marginTop: 30 }}>Coverage Closure Prediction</h3>
    {data.coverage_closure_prediction && (
      <div
        style={{
          border: "1px solid #007bff",
          padding: "12px",
          borderRadius: "4px",
          backgroundColor: "#f0f8ff",
        }}
      >
        <p>
          <strong>Estimated Time to Closure:</strong>{" "}
          {data.coverage_closure_prediction.estimated_time_to_closure_hours ?? "N/A"} hours
        </p>
        <p>
          <strong>Closure Probability:</strong>{" "}
          {(data.coverage_closure_prediction.closure_probability ?? 0) * 100}%
        </p>
        <p>
          <strong>Blocking Bins:</strong>{" "}
          {(data.coverage_closure_prediction.blocking_bins || [])
            .map((b) => b.bin)
            .join(", ") || "None"}
        </p>
      </div>
    )}
    </div>
  );
}

export default App;
