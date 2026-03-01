import { useState } from "react";
import { Nav, GrantCard, SectionHeader, EmptyState } from "../components";
import useGrants from "../hooks/useGrants";

export default function GrantsList() {
  const { grants, hasRealData } = useGrants();
  const [search,    setSearch]    = useState("");
  const [fitFilter, setFitFilter] = useState("all");
  const [sortBy,    setSortBy]    = useState("score");

  const filtered = grants
    .filter(g => fitFilter === "all" || g.fit_level === fitFilter)
    .filter(g =>
      g.title.toLowerCase().includes(search.toLowerCase()) ||
      g.agency.toLowerCase().includes(search.toLowerCase()) ||
      (Array.isArray(g.focus_areas) ? g.focus_areas.join(" ") : g.focus_areas || "")
        .toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) =>
      sortBy === "score"
        ? b.similarity_score - a.similarity_score
        : a.title.localeCompare(b.title)
    );

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <Nav />
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "40px" }}>

        <SectionHeader
          label="Grant Intelligence"
          title="Matched Grants"
          subtitle={`${filtered.length} grants ranked by AI match score${hasRealData ? " for your proposal" : " (demo data)"}`}
        />

        {/* Filters */}
        <div style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap", alignItems: "center" }}>
          <div style={{ position: "relative", flex: 1, minWidth: 240 }}>
            <span style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "#444", fontSize: 16 }}>⌕</span>
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search grants, agencies, focus areas..."
              style={{
                width: "100%", background: "var(--bg-card)", border: "1px solid var(--border)",
                borderRadius: 10, padding: "10px 14px 10px 40px",
                color: "#fff", fontSize: 14, outline: "none", boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ display: "flex", gap: 6 }}>
            {["all", "strong", "moderate", "weak"].map(f => (
              <button
                key={f}
                onClick={() => setFitFilter(f)}
                style={{
                  background: fitFilter === f ? "var(--accent)" : "var(--bg-card)",
                  border: `1px solid ${fitFilter === f ? "var(--accent)" : "var(--border)"}`,
                  color: fitFilter === f ? "#fff" : "var(--text-dim)",
                  padding: "8px 16px", borderRadius: 8,
                  fontSize: 13, fontWeight: 600, cursor: "pointer",
                  textTransform: "capitalize",
                }}
              >
                {f === "all" ? "All" : f}
              </button>
            ))}
          </div>

          <select
            value={sortBy}
            onChange={e => setSortBy(e.target.value)}
            style={{
              background: "var(--bg-card)", border: "1px solid var(--border)",
              color: "var(--text-dim)", padding: "8px 14px",
              borderRadius: 8, fontSize: 13, cursor: "pointer", outline: "none",
            }}
          >
            <option value="score">Best Match</option>
            <option value="title">A–Z</option>
          </select>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {filtered.length > 0
            ? filtered.map(grant => <GrantCard key={grant.grant_id} grant={grant} />)
            : <EmptyState icon="◎" title="No grants match your filters" subtitle="Try adjusting your search or fit level filter" />
          }
        </div>
      </div>
    </div>
  );
}