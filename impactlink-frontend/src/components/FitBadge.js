export default function FitBadge({ level }) {
  const map = {
    strong:   { bg: "#0d2e1a", color: "#4ade80", border: "#166534" },
    moderate: { bg: "#1c1a06", color: "#facc15", border: "#713f12" },
    weak:     { bg: "#2d0f0f", color: "#f87171", border: "#7f1d1d" },
  };
  const s = map[level] || map.moderate;
  return (
    <span style={{
      background: s.bg, color: s.color, border: `1px solid ${s.border}`,
      padding: "3px 10px", borderRadius: 20,
      fontSize: 11, fontWeight: 700,
      textTransform: "uppercase", letterSpacing: "0.06em",
    }}>
      {level}
    </span>
  );
}