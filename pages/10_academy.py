"""Academy — coming soon."""

from components.placeholder import render_placeholder

render_placeholder(
    title="Academy",
    icon="🎓",
    description="Learn finance by doing — from basics to advanced, all inside the app",
    features=[
        ("Learning paths", "Structured courses: Fundamentals, Valuation, Technicals, Risk, Economics"),
        ("Concept explainers", "Tap any number or assumption for a 3-level explanation"),
        ("Interactive exercises", "Change an assumption and see what happens to the valuation"),
        ("AI tutor", "Personalized teaching adapted to your knowledge level"),
        ("Progress tracking", "See where you are and what comes next in each path"),
    ],
)
