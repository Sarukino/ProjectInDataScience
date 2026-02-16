import pandas as pd
import dash
from dash import html, dcc, Output, Input
import plotly.graph_objects as go

# ============================================================
#  EXCEL ADATOK BEOLVASÁSA
# ============================================================

EXCEL_PATH = "volunteer_data.xlsx"  

# Sheet-ek beolvasása
df_platforms = pd.read_excel(EXCEL_PATH, sheet_name="Platforms")
df_features = pd.read_excel(EXCEL_PATH, sheet_name="Features")
df_pf = pd.read_excel(EXCEL_PATH, sheet_name="PlatformFeatures")

# Csak a szükséges oszlopokkal dolgozunk
df_platforms = df_platforms[["platform_id", "name", "url"]]
df_features = df_features[["feature_id", "group", "name"]]
df_pf = df_pf[["platform_id", "feature_id"]]

# Összefésülés: platform-feature-k teljes infóval
df_pf_full = (
    df_pf
    .merge(df_platforms, on="platform_id", how="left")      # name_platform, url
    .merge(df_features, on="feature_id", how="left",
           suffixes=("_platform", "_feature"))              # group, name_feature
)

# ============================================================
#  SZÓTÁRAK ELŐÁLLÍTÁSA
# ============================================================

# 1) Csak domain feature-ök (nem Language)
df_domain = df_pf_full[df_pf_full["group"] != "Language"].copy()

# Feature név -> platform nevek listája
keyword_to_platforms = (
    df_domain
    .groupby("name_feature")["name_platform"]
    .apply(lambda s: sorted(s.dropna().unique()))
    .to_dict()
)

# Platform név -> feature nevek listája
platform_to_keywords = (
    df_domain
    .groupby("name_platform")["name_feature"]
    .apply(lambda s: sorted(s.dropna().unique()))
    .to_dict()
)

# Platform név -> URL
platform_links = (
    df_platforms
    .set_index("name")["url"]
    .dropna()
    .to_dict()
)

# 2) Nyelvi feature-ökből platform -> language(ek)

df_lang = df_pf_full[df_pf_full["group"] == "Language"].copy()

if not df_lang.empty:
    # "Language: English" -> "English"
    df_lang["language"] = (
        df_lang["name_feature"]
        .str.replace("Language:", "", regex=False)
        .str.strip()
    )

    platform_languages_multi = (
        df_lang
        .groupby("name_platform")["language"]
        .apply(lambda s: sorted(s.dropna().unique()))
        .to_dict()
    )

    # Egyszerűsítés: főnyelv = lista első eleme
    platform_main_language = {
        p: langs[0] for p, langs in platform_languages_multi.items() if len(langs) > 0
    }
else:
    platform_languages_multi = {}
    platform_main_language = {}

# Language filter opciók
if platform_main_language:
    language_options = sorted(set(platform_main_language.values()))
else:
    # Ha még nincs nyelvi adat az Excelben
    language_options = []

# Feature checklist opciók
all_keywords = sorted(keyword_to_platforms.keys())

# ============================================================
#  DASH APP LAYOUT
# ============================================================

app = dash.Dash(__name__)

app.layout = html.Div(style={"display": "flex"}, children=[
    # BAL OLDAL: szűrők
    html.Div(style={"width": "25%", "padding": "20px"}, children=[
        html.H3("Filter by Feature"),
        dcc.Checklist(
            id="keyword-filter",
            options=[{"label": k, "value": k} for k in all_keywords],
            value=all_keywords,  # alapból minden feature bejelölve
            inputStyle={"margin-right": "10px", "margin-left": "5px"}
        ),
        html.H3("Filter by Language"),
        dcc.Checklist(
            id="language-filter",
            options=[{"label": lang, "value": lang} for lang in language_options],
            value=language_options,  # alapból minden nyelv bejelölve
            inputStyle={"margin-right": "10px", "margin-left": "5px"}
        )
    ]),

    # JOBB OLDAL: cím + (sunburst + kártya egymás mellett)
    html.Div(style={"width": "75%", "padding": "20px"}, children=[
        html.H1("Volunteer Platform Comparison"),

        html.Div(style={"display": "flex"}, children=[
            dcc.Graph(
                id="sunburst-graph",
                style={"width": "70%", "height": "800px"}
            ),
            html.Div(
                id="platform-card",
                style={
                    "width": "30%",
                    "marginLeft": "20px",
                    "alignSelf": "flex-start"
                }
            )
        ])
    ])
])

# ============================================================
#  CALLBACK 1 – SUNBURST FRISSÍTÉS
# ============================================================

@app.callback(
    Output("sunburst-graph", "figure"),
    [Input("keyword-filter", "value"),
     Input("language-filter", "value")]
)
def update_sunburst(selected_keywords, selected_languages):
    # Ha semmi nincs kijelölve → üres ábra
    if not selected_keywords or (language_options and not selected_languages):
        return go.Figure()

    labels = []
    parents = []
    values = []

    for keyword in selected_keywords:
        platforms = keyword_to_platforms.get(keyword, [])

        # Nyelvi szűrés (csak ha van nyelv infó)
        if selected_languages and platform_main_language:
            platforms = [
                p for p in platforms
                if platform_main_language.get(p) in selected_languages
            ]

        if not platforms:
            continue

        labels.append(keyword)
        parents.append("")
        values.append(len(platforms))

        for p in platforms:
            labels.append(p)
            parents.append(keyword)
            values.append(1)

    if not labels:
        return go.Figure()

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
        height=800,
        title="Volunteer Platforms by Feature and Language"
    )

    return fig

# ============================================================
#  CALLBACK 2 – INFÓKÁRTYA KATTINTÁSRA
# ============================================================

@app.callback(
    Output("platform-card", "children"),
    [Input("sunburst-graph", "clickData"),
     Input("keyword-filter", "value"),
     Input("language-filter", "value")]
)
def show_platform_card(clickData, selected_keywords, selected_languages):
    if not clickData or "label" not in clickData["points"][0]:
        return ""

    platform = clickData["points"][0]["label"]

    # Ha nem platform (hanem feature), vagy nincs róla adat
    if platform not in platform_to_keywords:
        return ""

    # Nyelv-szűrés, ha van language filter
    if selected_languages and platform_main_language:
        if platform_main_language.get(platform) not in selected_languages:
            return ""

    # Csak azokat a feature-öket mutatjuk, amik a jelenlegi feature-szűrésben is benne vannak
    features = [f for f in platform_to_keywords.get(platform, []) if f in selected_keywords]
    if not features:
        return ""

    lang = platform_main_language.get(platform, "Unknown")
    url = platform_links.get(platform, "#")

    return html.Div([
        html.H3(platform),
        html.P(f"Language: {lang}"),
        html.P("Features:"),
        html.Ul([html.Li(f) for f in features]),
        html.A("Visit Website", href=url, target="_blank", style={"color": "blue"})
    ], style={
        "border": "1px solid #aaa",
        "borderRadius": "5px",
        "padding": "15px",
        "backgroundColor": "#f2f2f2",
        "width": "400px"
    })


# ============================================================
#  FŐPROGRAM
# ============================================================
if __name__ == "__main__":
    app.run(debug=True)
