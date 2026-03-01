import { useNavigate } from "react-router-dom";
import { Nav, StatCard, GrantCard, SectionHeader } from "../components";
import { mockProfile as p, mockGrants, mockActivity } from "../services/mockData";

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <Nav />
      <div style={{ maxWidth: 1280, margin: "0 auto", padding: "40px" }}>

        <SectionHeader
          label="NGO Dashboard"
          title={`Welcome back, ${p.name.split(" ")[0]} 👋`}
          subtitle={p.mission}
        />

        {/* Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 36 }}>
          <StatCard label="Funding Secured"    value={`$${(p.funding_secured/1000).toFixed(0)}K`} sub="lifetime"                      accent="var(--accent)" />
          <StatCard label="Grants Won"          value={p.total_won}                                sub={`of ${p.total_applied} applied`}  accent="var(--green)" />
          <StatCard label="Active Applications" value={p.active_applications}                      sub="in progress"                      accent="var(--yellow)" />
          <StatCard label="Avg Match Score"     value="61%"                                        sub="across matched grants"             accent="var(--pink)" />
        </div>

        {/* Main Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: 24 }}>

          {/* Left */}
          <div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
              <h2 style={{ fontSize: 18, fontWeight: 700, color: "#fff", margin: 0 }}>Top Matched Grants</h2>
              <button
                onClick={() => navigate("/grants")}
                style={{
                  background: "transparent", border: "1px solid var(--border)",
                  color: "var(--accent)", padding: "8px 18px", borderRadius: 8,
                  fontSize: 13, fontWeight: 600, cursor: "pointer",
                }}
              >
                View All Grants →
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {mockGrants.slice(0, 3).map(grant => (
                <GrantCard key={grant.grant_id} grant={grant} compact />
              ))}
            </div>

            {/* Quick Actions */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 20 }}>
              {[
                { icon: "⬆", label: "Upload New Proposal", sub: "Re-run AI matching with new docs", path: "/upload" },
                { icon: "✍", label: "Draft Assistant",      sub: "AI agents write your proposal",   path: "/draft" },
              ].map(a => (
                <div
                  key={a.label}
                  onClick={() => navigate(a.path)}
                  style={{
                    background: "var(--bg-card)", border: "1px solid var(--border)",
                    borderRadius: 14, padding: "20px", cursor: "pointer",
                    transition: "border-color 0.2s",
                  }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = "var(--accent)"}
                  onMouseLeave={e => e.currentTarget.style.borderColor = "var(--border)"}
                >
                  <div style={{ fontSize: 22, marginBottom: 8 }}>{a.icon}</div>
                  <p style={{ fontWeight: 700, color: "#fff", fontSize: 14, margin: "0 0 4px" }}>{a.label}</p>
                  <p style={{ color: "#444", fontSize: 12, margin: 0 }}>{a.sub}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Right */}
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>

            {/* Org Card */}
            <div style={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 16, padding: 24 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 16 }}>
                <div style={{
                  width: 48, height: 48, borderRadius: 12,
                  background: "linear-gradient(135deg, var(--accent), var(--accent-dim))",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontWeight: 800, fontSize: 20, color: "#fff",
                }}>
                  {p.name[0]}
                </div>
                <div>
                  <p style={{ fontWeight: 700, color: "#fff", margin: 0, fontSize: 15 }}>{p.name}</p>
                  <p style={{ color: "var(--text-muted)", fontSize: 12, margin: 0 }}>📍 {p.location}</p>
                </div>
              </div>
              <div style={{ borderTop: "1px solid #1a1a2e", paddingTop: 14 }}>
                <p style={{ color: "#444", fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", margin: "0 0 4px" }}>Cause Area</p>
                <p style={{ color: "#bbb", fontSize: 13, margin: "0 0 14px" }}>{p.cause_area}</p>
                <p style={{ color: "#444", fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", margin: "0 0 8px" }}>SDG Alignment</p>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {p.sdgs.map(sdg => (
                    <span key={sdg} style={{
                      background: "#1a1a2e", color: "var(--accent)",
                      border: "1px solid #2e2e4e", borderRadius: 6,
                      padding: "3px 10px", fontSize: 11, fontWeight: 600,
                    }}>{sdg}</span>
                  ))}
                </div>
              </div>
              <button style={{
                width: "100%", marginTop: 16, background: "transparent",
                border: "1px solid var(--border)", color: "var(--accent)",
                padding: 10, borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: "pointer",
              }}>
                Edit Profile
              </button>
            </div>

            {/* Activity Feed */}
            <div style={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 16, padding: 24, flex: 1 }}>
              <h3 style={{ fontWeight: 700, color: "#fff", fontSize: 15, margin: "0 0 16px" }}>Recent Activity</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                {mockActivity.map((item, i) => (
                  <div key={i} style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: 8, flexShrink: 0,
                      background: "#1a1a2e",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      fontSize: 14, color: "var(--accent)",
                    }}>
                      {item.icon}
                    </div>
                    <div>
                      <p style={{ color: "#ccc", fontSize: 13, margin: "0 0 2px", lineHeight: 1.4 }}>{item.text}</p>
                      <p style={{ color: "#444", fontSize: 11, margin: 0 }}>{item.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}