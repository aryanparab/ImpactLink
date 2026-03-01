export default function ScoreRing({ score, size = 56 }) {
  const color = score >= 60 ? "var(--accent)" : score >= 45 ? "var(--yellow)" : "var(--red)";
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{
        width: size, height: size, borderRadius: "50%",
        border: `3px solid ${color}`,
        display: "flex", alignItems: "center", justifyContent: "center",
        background: "var(--bg)",
      }}>
        <span style={{ fontSize: size * 0.25, fontWeight: 800, color, lineHeight: 1 }}>
          {score}%
        </span>
      </div>
      <span style={{ fontSize: 10, color: "#444", display: "block", marginTop: 4 }}>match</span>
    </div>
  );
}