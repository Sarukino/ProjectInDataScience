import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go

# Kulcsszavak → Platformok
keyword_to_platforms = {
    "Online Learning": ["Better Impact", "Volunteer Impact", "freiwillig-engagiert", "Treffpunkt Ehrenamt (OÖ)", "Freiwilligencenter Niederösterreich", "füruns"],
    "Volunteer Portal / App": ["Better Impact", "Track It Forward", "Volgistics", "VolunteerMatters", "GiveGab", "Freiwilligenbörse Caritas Österreich"],
    "Recruitment & Onboarding": ["Better Impact", "Freiwilligencenter Niederösterreich", "Treffpunkt Ehrenamt (OÖ)", "VolunteerMatters", "freiwillig-engagiert"],
    "Volunteer Scheduling": ["YourVolunteers", "freiwillig für wien", "freiwillig-engagiert"],
    "Communication": ["GiveGab", "Track It Forward", "YourVolunteers"]
}

# Platform nyelvek
platform_languages = {
    "Better Impact": "English",
    "Volunteer Impact": "English",
    "VolunteerMatters": "English",
    "Volgistics": "English",
    "freiwillig für wien": "German",
    "GiveGab": "English",
    "Track It Forward": "English",
    "freiwillig-engagiert": "German",
    "Treffpunkt Ehrenamt (OÖ)": "German",
    "Freiwilligencenter Niederösterreich": "German",
    "füruns": "German",
    "Freiwilligenbörse Caritas Österreich": "German",
    "YourVolunteers": "English"
}

# Platform linkek
platform_links = {
    "Better Impact": "https://www.betterimpact.com/",
    "Volunteer Impact": "https://volunteeringimpact.epic.com/",
    "VolunteerMatters": "https://www.volunteermatters.com/",
    "Volgistics": "https://www.volgistics.com/",
    "freiwillig für wien": "https://diehelferwiens.wien.gv.at/",
    "GiveGab": "https://www.bonterratech.com/",
    "Track It Forward": "https://www.trackitforward.com/",
    "freiwillig-engagiert": "https://www.freiwillig-engagiert.at/",
    "Treffpunkt Ehrenamt (OÖ)": "https://www.treffpunkt-ehrenamt.at/",
    "Freiwilligencenter Niederösterreich": "https://freiwilligencenter.at/",
    "füruns": "https://www.fuer-uns.at/",
    "Freiwilligenbörse Caritas Österreich": "https://www.caritas.at/spenden-helfen/freiwilligenboerse",
    "YourVolunteers": "https://www.yourvolunteers.com/"
}

# Platform → kulcsszavak
platform_to_keywords = {}
for keyword, platforms in keyword_to_platforms.items():
    for platform in platforms:
        platform_to_keywords.setdefault(platform, []).append(keyword)

# Sunburst adat
labels, parents, values = [], [], []
added_keywords = set()
for keyword, platforms in keyword_to_platforms.items():
    if keyword not in added_keywords:
        labels.append(keyword)
        parents.append("")
        values.append(len(platforms))
        added_keywords.add(keyword)
    for platform in platforms:
        labels.append(platform)
        parents.append(keyword)
        values.append(1)

fig = go.Figure(go.Sunburst(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",
    maxdepth=2
))

fig.update_layout(
    margin=dict(t=40, l=0, r=0, b=0),
    width=800,
    height=700,
    title="Compare Volunteer Platforms by Supported Features"
)

# Dash app
app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1("Volunteer Platform Comparison"),
    html.P("Volunteer Platforms by Feature and Language"),
    dcc.Graph(id="sunburst-graph", figure=fig),
    html.Div(id="platform-card", style={"marginTop": "20px"})
])

# Interaktív infókártya kattintásra
@app.callback(
    Output("platform-card", "children"),
    Input("sunburst-graph", "clickData")
)
def show_platform_card(clickData):
    if not clickData or "label" not in clickData["points"][0]:
        return ""

    platform = clickData["points"][0]["label"]
    if platform not in platform_to_keywords:
        return ""

    features = platform_to_keywords[platform]
    lang = platform_languages.get(platform, "Unknown")
    url = platform_links.get(platform, "#")

    return html.Div([
        html.H3(platform),
        html.P(f"Language: {lang}"),
        html.P("Features:"),
        html.Ul([html.Li(feat) for feat in features]),
        html.A("Visit Website", href=url, target="_blank", style={"color": "blue"})
    ], style={
        "border": "1px solid #aaa",
        "borderRadius": "5px",
        "padding": "15px",
        "backgroundColor": "#f2f2f2",
        "width": "400px"
    })


if __name__ == "__main__":
    app.run(debug=True)
