import React, { useEffect, useState } from "react";

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("https://coverage-analyzer-1.onrender.com/coverage")
      .then((res) => res.json())
      .then((result) => {
        setData(result);
        setLoading(false);
      })
      .catch((err) => {
        console.error("API error:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ padding: 40, fontSize: 18, textAlign: "center" }}>
        Loading coverage data...
      </div>
    );
  }

  const containerStyle = {
    maxWidth: 1200,
    margin: "20px auto",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    color: "#333",
  };

  const sectionTitle = {
    color: "#007bff",
    borderBottom: "2px solid #007bff",
    paddingBottom: "4px",
    marginTop: "30px",
  };

  const cardStyle = {
    border: "1px solid #ddd",
    borderRadius: "8px",
    padding: "16px",
    marginBottom: "16px",
    boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
    backgroundColor: "#fefefe",
    transition: "transform 0.2s, box-shadow 0.2s",
  };

  const cardHover = {
    transform: "translateY(-3px)",
    boxShadow: "0 6px 12px rgba(0,0,0,0.15)",
  };

  const tableStyle = {
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "12px",
  };

  const thTdStyle = {
    border: "1px solid #ccc",
    padding: "10px",
    textAlign: "left",
  };

  return (
    <div style={containerStyle}>
      <h2>🚀 Coverage Analyzer Dashboard</h2>

      <p>
        <strong>Design:</strong> {data.design}
      </p>
      <p>
        <strong>Overall Coverage:</strong> {data.overall_coverage}%
      </p>

      <h3 style={sectionTitle}>Uncovered Bins</h3>
      <table style={tableStyle}>
        <thead style={{ backgroundColor: "#007bff", color: "#fff" }}>
          <tr>
            <th style={thTdStyle}>Covergroup</th>
            <th style={thTdStyle}>Coverpoint</th>
            <th style={thTdStyle}>Bin</th>
          </tr>
        </thead>
        <tbody>
          {(data.uncovered_bins || []).map((bin, idx) => (
            <tr key={idx}>
              <td style={thTdStyle}>{bin.covergroup}</td>
              <td style={thTdStyle}>{bin.coverpoint}</td>
              <td style={thTdStyle}>{bin.bin}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3 style={sectionTitle}>💡 Prioritized Suggestions</h3>
      {(data.suggestions || []).map((item, idx) => (
        <div
          key={idx}
          style={{ ...cardStyle }}
          onMouseEnter={(e) =>
            (e.currentTarget.style.transform = "translateY(-3px)")
          }
          onMouseLeave={(e) =>
            (e.currentTarget.style.transform = "translateY(0px)")
          }
        >
          <p>
            <strong>Target Bin:</strong> {item.target_bin}
          </p>
          <p>
            <strong>Score:</strong> {item.score}
          </p>
          <p>
            <strong>Priority:</strong> {item.priority} | <strong>Difficulty:</strong>{" "}
            {item.difficulty}
          </p>
          <p>
            <strong>Suggestion:</strong> {item.suggestion}
          </p>
          <p>
            <strong>Dependencies:</strong>{" "}
            {(item.dependencies || []).join(", ") || "None"}
          </p>
          <p>
            <strong>Test Outline:</strong>
          </p>
          <ol>
            {(item.test_outline || []).map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
          <p>
            <strong>Reasoning:</strong> {item.reasoning}
          </p>
        </div>
      ))}

      <h3 style={sectionTitle}>⏱️ Coverage Closure Prediction</h3>
      {data.coverage_closure_prediction && (
        <div style={{ ...cardStyle, backgroundColor: "#f0f8ff" }}>
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
