export default function EmptyState({ icon = "◎", title, subtitle }) {
  return (
    <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-muted)" }}>
      <p style={{ fontSize: 40, marginBottom: 12 }}>{icon}</p>
      <p style={{ fontSize: 16, fontWeight: 600, color: "#bbb", marginBottom: 6 }}>{title}</p>
      {subtitle && <p style={{ fontSize: 13 }}>{subtitle}</p>}
    </div>
  );
}