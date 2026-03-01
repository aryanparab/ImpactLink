import { useNavigate } from "react-router-dom";
import Nav from "../components/Nav";

export default function Landing() {
  const navigate = useNavigate();
  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <Nav />
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "100px 40px 60px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 60, alignItems: "center" }}>
        <div>
          <span style={{
            display: "inline-flex", alignItems: "center", gap: 6,
            background: "#1a1a2e", border: "1px solid #2e2e4e",
            color: "var(--accent)", padding: "6px 14px", borderRadius: 20,
            fontSize: 12, fontWeight: 600, marginBottom: 24,
          }}>
            ✦ AI-Powered NGO Intelligence
          </span>
          <h1 style={{ fontSize: 52, fontWeight: 800, letterSpacing: "-0.04em", color: "#fff", lineHeight: 1.1, marginBottom: 20 }}>
            Scale Your NGO's Impact with{" "}
            <span style={{ color: "var(--accent)" }}>Intelligent Grant Strategy</span>
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: 17, lineHeight: 1.7, marginBottom: 36 }}>
            ImpactLink AI helps NGOs find funding, match with funders, and draft winning proposals — all from a single upload.
          </p>
          <div style={{ display: "flex", gap: 12 }}>
            <button
              onClick={() => navigate("/upload")}
              style={{
                background: "var(--accent)", border: "none", color: "#fff",
                padding: "14px 28px", borderRadius: 10,
                fontSize: 15, fontWeight: 700, cursor: "pointer",
                display: "flex", alignItems: "center", gap: 8,
              }}
            >
              📄 Upload Your Proposal
            </button>
            <button
              onClick={() => navigate("/dashboard")}
              style={{
                background: "transparent", border: "1px solid var(--border)", color: "#fff",
                padding: "14px 28px", borderRadius: 10,
                fontSize: 15, fontWeight: 600, cursor: "pointer",
              }}
            >
              View Dashboard
            </button>
          </div>
        </div>

        {/* Feature Cards */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {[
            { icon: "✦", title: "AI Grant Matching", desc: "Upload your proposal, get ranked matches with fit scores and explanations." },
            { icon: "✍", title: "Smart Proposal Drafting", desc: "Specialized agents rewrite your proposal for each funder's language and priorities." },
            { icon: "◈", title: "Application Tracker", desc: "Track deadlines, stages, and progress across all active applications." },
          ].map(f => (
            <div key={f.title} style={{
              background: "var(--bg-card)", border: "1px solid var(--border)",
              borderRadius: 14, padding: "20px 22px",
              display: "flex", gap: 16, alignItems: "flex-start",
            }}>
              <div style={{
                width: 40, height: 40, borderRadius: 10, flexShrink: 0,
                background: "#1a1a2e", display: "flex", alignItems: "center",
                justifyContent: "center", fontSize: 18, color: "var(--accent)",
              }}>{f.icon}</div>
              <div>
                <p style={{ fontWeight: 700, color: "#fff", fontSize: 15, margin: "0 0 4px" }}>{f.title}</p>
                <p style={{ color: "var(--text-muted)", fontSize: 13, margin: 0, lineHeight: 1.5 }}>{f.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}