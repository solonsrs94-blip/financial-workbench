"""Investment Journal — coming soon."""

from components.placeholder import render_placeholder

render_placeholder(
    title="Investment Journal",
    icon="📝",
    description="Notes, theses, and research library for your investment decisions",
    phase="Fasi 3f — Tools & learning",
    target_quarter="Q1 2027",
    progress_pct=0,
    tier="personal",
    features=[
        ("Per-stock notes", "Markdown notes linked to tickers, searchable across your history"),
        ("Investment theses", "Structured thesis templates — what you believe, why, and what would invalidate it"),
        ("Thesis tracking", "Track whether your thesis is playing out over time"),
        ("Ideas queue", "Save research ideas with status (to-research, active, rejected)"),
        ("Research library", "Save articles and reports with highlights and annotations"),
        ("AI summary integration", "Ask the AI assistant to summarize your own notes on a company"),
    ],
)
