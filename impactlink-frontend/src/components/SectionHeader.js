export default function SectionHeader({ label, title, subtitle }) {
  return (
    <div style={{ marginBottom: 32 }}>
      {label && (
        <p style={{ color: "var(--accent)", fontSize: 13, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6 }}>
          {label}
        </p>
      )}
      <h1 style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.03em", color: "#fff", margin: "0 0 8px" }}>
        {title}
      </h1>
      {subtitle && (
        <p style={{ color: "var(--text-muted)", fontSize: 15, margin: 0 }}>{subtitle}</p>
      )}
    </div>
  );
}