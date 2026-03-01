export default function StatCard({ label, value, sub, accent }) {
  return (
    <div style={{
      background: "var(--bg-card)", border: "1px solid var(--border)",
      borderRadius: 16, padding: "24px",
      position: "relative", overflow: "hidden",
    }}>
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0,
        height: 3, background: accent,
      }} />
      <p style={{ color: "var(--text-muted)", fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", margin: "0 0 10px" }}>
        {label}
      </p>
      <p style={{ fontSize: 32, fontWeight: 800, color: "#fff", margin: 0, letterSpacing: "-0.03em" }}>
        {value}
      </p>
      <p style={{ color: "#444", fontSize: 12, margin: "4px 0 0" }}>{sub}</p>
    </div>
  );
}