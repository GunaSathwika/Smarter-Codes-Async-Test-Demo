import { useState } from "react";

function App() {
  const [url, setUrl] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setResults([]);
    try {
      const res = await fetch("http://localhost:8000/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, query }),
      });
      const data = await res.json();
      setResults(data.results || []);
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 24, fontFamily: "Arial, sans-serif" }}>
      <h2>Smarter.Codes — Async Test Demo</h2>
      <form onSubmit={onSubmit}>
        <div>
          <label>Website URL</label><br/>
          <input value={url} onChange={(e)=>setUrl(e.target.value)} style={{width: "60%"}} required />
        </div>
        <div style={{marginTop:8}}>
          <label>Search Query</label><br/>
          <input value={query} onChange={(e)=>setQuery(e.target.value)} style={{width: "60%"}} required />
        </div>
        <div style={{marginTop:12}}>
          <button type="submit" disabled={loading}>{loading? "Searching..." : "Search"}</button>
        </div>
      </form>

      <div style={{marginTop:20}}>
        <h3>Top results</h3>
        {results.map((r, idx) => (
          <div key={idx} style={{border:"1px solid #ddd", padding:12, marginBottom:8}}>
            <div style={{fontSize:12, color:"#555"}}>Score: {r.score.toFixed(4)}</div>
            <div style={{whiteSpace:"pre-wrap"}}>{r.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;