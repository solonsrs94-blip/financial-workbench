"""Portfolio & Risk — coming soon."""

from components.placeholder import render_placeholder

render_placeholder(
    title="Portfolio & Risk",
    icon="💼",
    description="Track your holdings and understand your risk exposure",
    features=[
        ("Portfolio tracker", "Log positions, see returns vs benchmarks, allocation breakdown"),
        ("Risk analysis", "Value at Risk (VaR), Monte Carlo simulation, stress testing"),
        ("Backtesting", "Test strategies on historical data before committing capital"),
        ("Options analysis", "Greeks, payoff diagrams, implied volatility surface"),
        ("Performance attribution", "Understand what drove your returns by sector and position"),
    ],
)
