import { useEffect, useState } from "react";

function App() {
  const [data, setData] = useState(null);
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/coverage")
      .then(res => res.json())
      .then(setData)
      .catch(err => console.error(err));
  }, []);

  if (!data) return <h2 style={{ padding: 20 }}>Loading coverage data...</h2>;

  const filteredBins = data.uncovered_bins.filter(b =>
    `${b.covergroup} ${b.coverpoint} ${b.bin}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  return (
    <div style={{ padding: 20, fontFamily: "Arial", maxWidth: 1100, margin: "auto" }}>
      <h1>📊 Coverage Analyzer Dashboard</h1>

      {/* SUMMARY CARDS */}
      <div style={{ display: "flex", gap: 20, marginBottom: 20 }}>
        <SummaryCard title="Design" value={data.design} />
        <SummaryCard title="Overall Coverage" value={`${data.overall_coverage}%`} />
        <SummaryCard title="Uncovered Bins" value={data.uncovered_bins.length} />
      </div>

      {/* SEARCH */}
      <input
        placeholder="Search uncovered bins..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        style={{ padding: 8, width: "100%", marginBottom: 20 }}
      />

      {/* UNCOVERED BINS TABLE */}
      <h2>🧪 Uncovered Bins</h2>
      <table width="100%" border="1" cellPadding="8" style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#f2f2f2" }}>
            <th>Covergroup</th>
            <th>Coverpoint</th>
            <th>Bin</th>
          </tr>
        </thead>
        <tbody>
          {filteredBins.map((b, i) => (
            <tr key={i}>
              <td>{b.covergroup}</td>
              <td>{b.coverpoint}</td>
              <td>{b.bin}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* SUGGESTIONS */}
      <h2 style={{ marginTop: 30 }}>🚀 Prioritized Suggestions</h2>

      {data.prioritized_suggestions.map((s, i) => (
        <div
          key={i}
          style={{
            border: "1px solid #ccc",
            padding: 12,
            marginBottom: 10,
            borderLeft: `6px solid ${priorityColor(s.suggestion.priority)}`
          }}
        >
          <p><b>Target:</b> {s.target}</p>
          <p><b>Score:</b> {s.score}</p>
          <p><b>Priority:</b> {s.suggestion.priority}</p>

          <button onClick={() => setExpanded(expanded === i ? null : i)}>
            {expanded === i ? "Hide Details" : "Show Details"}
          </button>

          {expanded === i && (
            <div style={{ marginTop: 10 }}>
              <p><b>Suggestion:</b> {s.suggestion.suggestion}</p>
              <p><b>Reasoning:</b> {s.suggestion.reasoning}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/* SMALL COMPONENTS */

function SummaryCard({ title, value }) {
  return (
    <div style={{
      flex: 1,
      padding: 15,
      border: "1px solid #ddd",
      borderRadius: 4,
      background: "#fafafa"
    }}>
      <h3>{title}</h3>
      <p style={{ fontSize: 20 }}>{value}</p>
    </div>
  );
}

function priorityColor(priority) {
  if (priority === "high") return "red";
  if (priority === "medium") return "orange";
  return "green";
}

export default App;
