import dash
from dash import html, dcc
import plotly.graph_objects as go

labels = [
    'Online Learning', 'Volunteer Scheduling', 'Volunteer Portal / App',
    'Communication', 'Volunteer Matching', 'Event Management',
    'Reporting & Analytics', 'User Management', 'Recruitment & Onboarding',
    'Gamification / Motivation', 'Multi-language / Accessibility',
    'Verification & Safety', 'Platform Integration', 'Support & Documentation',
    'Administration Tools', 'Community Engagement',

    # Platform names – these are linked to keywords above
    'VolunteerMatters', 'Volgistics', 'Better Impact', 'YourVolunteers'
]

parents = [
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
    'Volunteer Portal / App', 'Volunteer Portal / App', 'Volunteer Scheduling', 'Communication'
]

values = [
    0, 1, 2, 2, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1
]

fig = go.Figure(go.Sunburst(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",
    maxdepth=2
))

fig.update_layout(
    margin=dict(t=40, l=0, r=0, b=0),
    width=700,
    height=700,
    title="Keyword → Platform Mapping (Comparison Sunburst)"
)

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1("Compare Volunteer Platforms by Feature Keywords"),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run(debug=True)
