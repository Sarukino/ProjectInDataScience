import dash
from dash import html, dcc
import plotly.graph_objects as go

labels = [
    "Volunteer Profile",
    "Skills", "Communication", "First Aid",
    "Interests", "Environment", "Education",
    "Availability", "Weekdays", "Weekends"
]

parents = [
    "",  # Volunteer Profile (root)
    "Volunteer Profile", "Skills", "Skills",
    "Volunteer Profile", "Interests", "Interests",
    "Volunteer Profile", "Availability", "Availability"
]

values = [10, 4, 2, 2, 3, 2, 1, 3, 2, 1]  # használható nem-nulla értékek

fig = go.Figure(go.Sunburst(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",
    maxdepth=2
))

fig.update_layout(
    margin=dict(t=40, l=0, r=0, b=0),
    width=600,  # vagy 800
    height=600,
    title="Volunteer Profile Hierarchy (Interactive Sunburst)"
)

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1("Volunteer Platform Visualization"),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run(debug=True)
