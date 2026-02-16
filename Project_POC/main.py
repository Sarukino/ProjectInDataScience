import pandas as pd
import dash
from dash import html, dcc, Output, Input, State
import plotly.graph_objects as go


# EXCEL DATA LOADING


EXCEL_PATH = "volunteer_data.xlsx"

# Read sheets
df_platforms = pd.read_excel(EXCEL_PATH, sheet_name="Platforms")
df_features = pd.read_excel(EXCEL_PATH, sheet_name="Features")
df_pf = pd.read_excel(EXCEL_PATH, sheet_name="PlatformFeatures")

# Keep only columns we need
df_platforms = df_platforms[["platform_id", "name", "url"]]
df_features = df_features[["feature_id", "group", "name"]]
df_pf = df_pf[["platform_id", "feature_id"]]

# Join everything into one big table: platform-feature with full info
df_pf_full = (
    df_pf
    .merge(df_platforms, on="platform_id", how="left")       # name_platform, url
    .merge(df_features, on="feature_id", how="left",
           suffixes=("_platform", "_feature"))               # group, name_feature
)


#   Dictionaries for domain features (everything except Language)


df_domain = df_pf_full[df_pf_full["group"] != "Language"].copy()

# Feature name -> list of platforms
keyword_to_platforms = (
    df_domain
    .groupby("name_feature")["name_platform"]
    .apply(lambda s: sorted(s.dropna().unique()))
    .to_dict()
)

# Platform name -> list of feature names
platform_to_keywords = (
    df_domain
    .groupby("name_platform")["name_feature"]
    .apply(lambda s: sorted(s.dropna().unique()))
    .to_dict()
)

# Platform name -> URL
platform_links = (
    df_platforms
    .set_index("name")["url"]
    .dropna()
    .to_dict()
)

# Language info


df_lang = df_pf_full[df_pf_full["group"] == "Language"].copy()

if not df_lang.empty:
    # Extract clean language name from e.g. "Language: English"
    df_lang["language"] = (
        df_lang["name_feature"]
        .str.replace("Language:", "", regex=False)
        .str.strip()
    )

    # Platform -> list of languages
    platform_languages_multi = (
        df_lang
        .groupby("name_platform")["language"]
        .apply(lambda s: sorted(s.dropna().unique()))
        .to_dict()
    )

    # Main language (first) – used for filtering & labels
    platform_main_language = {
        p: langs[0] for p, langs in platform_languages_multi.items() if len(langs) > 0
    }
else:
    platform_languages_multi = {}
    platform_main_language = {}

# Language filter options
if platform_main_language:
    language_options = sorted(set(platform_main_language.values()))
else:
    language_options = []

# Feature checklist options
all_keywords = sorted(keyword_to_platforms.keys())


# SMALL HELPERS


def build_platform_card(platform_name, title_suffix=""):
    """Create a nice card for a single platform (all features)."""
    if platform_name is None:
        return html.Div()

    features = platform_to_keywords.get(platform_name, [])
    langs = platform_languages_multi.get(platform_name, [])
    lang_label = ", ".join(langs) if langs else platform_main_language.get(platform_name, "Unknown")
    url = platform_links.get(platform_name, "#")

    title = platform_name
    if title_suffix:
        title = f"{platform_name} ({title_suffix})"

    return html.Div(
        [
            html.H3(title),
            html.P(f"Language(s): {lang_label}"),
            html.P("Features:"),
            html.Ul([html.Li(f) for f in features]) if features else html.P("No features recorded."),
            html.A("Visit Website", href=url, target="_blank", style={"color": "blue"})
        ],
        style={
            "border": "1px solid #aaa",
            "borderRadius": "5px",
            "padding": "15px",
            "backgroundColor": "#f2f2f2",
            "width": "100%",
            "boxSizing": "border-box"
        }
    )


def compute_feature_diff(platform_a, platform_b):
    """Return (only_in_A, only_in_B) feature lists."""
    set_a = set(platform_to_keywords.get(platform_a, []))
    set_b = set(platform_to_keywords.get(platform_b, []))
    only_a = sorted(list(set_a - set_b))
    only_b = sorted(list(set_b - set_a))
    return only_a, only_b


# Base styles for showing/hiding browse vs comparison
BROWSE_STYLE = {"display": "flex"}
COMPARE_HIDDEN_STYLE = {
    "display": "none",
    "marginTop": "40px",
    "width": "100%",
    "flexDirection": "column",
    "alignItems": "center",
}
COMPARE_VISIBLE_STYLE = {
    "display": "flex",
    "marginTop": "40px",
    "width": "100%",
    "flexDirection": "column",
    "alignItems": "center",
}


# DASH APP LAYOUT


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        # Stores for comparison logic
        dcc.Store(id="platform-a-store"),
        dcc.Store(id="platform-b-store"),
        dcc.Store(id="current-platform-store"),

        html.Div(
            style={"display": "flex"},
            children=[
                #  LEFT: FILTERS
                html.Div(
                    style={"width": "25%", "padding": "20px"},
                    children=[
                        html.H3("Filter by Feature"),
                        dcc.Checklist(
                            id="keyword-filter",
                            options=[{"label": k, "value": k} for k in all_keywords],
                            value=all_keywords,  # all selected by default
                            inputStyle={"margin-right": "10px", "margin-left": "5px"}
                        ),
                        html.H3("Filter by Language"),
                        dcc.Checklist(
                            id="language-filter",
                            options=[{"label": lang, "value": lang} for lang in language_options],
                            value=language_options,  # all languages selected by default
                            inputStyle={"margin-right": "10px", "margin-left": "5px"}
                        )
                    ]
                ),

                # RIGHT: MAIN AREA
                html.Div(
                    style={"width": "75%", "padding": "20px"},
                    children=[
                        html.H1("Volunteer Platform Comparison"),

                        #BROWSE SECTION: Sunburst + single card + Set A/B
                        html.Div(
                            id="browse-section",
                            style=BROWSE_STYLE.copy(),
                            children=[
                                dcc.Graph(
                                    id="sunburst-graph",
                                    style={"width": "70%", "height": "800px"}
                                ),
                                html.Div(
                                    style={
                                        "width": "30%",
                                        "marginLeft": "20px",
                                        "alignSelf": "flex-start"
                                    },
                                    children=[
                                        html.Div(id="platform-card"),
                                        html.Div(
                                            style={"marginTop": "10px"},
                                            children=[
                                                html.Button("Set as A", id="set-a-button", n_clicks=0),
                                                html.Button("Set as B", id="set-b-button", n_clicks=0,
                                                            style={"marginLeft": "10px"})
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),

                        #  COMPARISON SECTION: initially hidden
                        html.Div(
                            id="comparison-section",
                            style=COMPARE_HIDDEN_STYLE.copy(),
                            children=[
                                html.Div(id="comparison-content", style={"width": "100%"}),
                                html.Button(
                                    "Clear comparison (back to browsing)",
                                    id="clear-compare-button",
                                    n_clicks=0,
                                    style={"marginTop": "20px"}
                                )
                            ]
                        ),
                    ]
                )
            ]
        )
    ]
)

#               CALLBACK 1 – SUNBURST FIGURE


@app.callback(
    Output("sunburst-graph", "figure"),
    [Input("keyword-filter", "value"),
     Input("language-filter", "value")]
)
def update_sunburst(selected_keywords, selected_languages):
    # If no feature selected OR (we have language info and none selected) -> empty
    if not selected_keywords or (language_options and not selected_languages):
        return go.Figure()

    labels = []
    parents = []
    values = []

    for keyword in selected_keywords:
        platforms = keyword_to_platforms.get(keyword, [])

        # Apply language filter if available
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

    fig = go.Figure(
        go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            maxdepth=2
        )
    )

    fig.update_layout(
        margin=dict(t=40, l=0, r=0, b=0),
        width=800,
        height=800,
        title="Volunteer Platforms by Feature and Language"
    )

    return fig


#   CALLBACK 2 – SINGLE PLATFORM CARD + CURRENT PLATFORM STORE


@app.callback(
    [Output("platform-card", "children"),
     Output("current-platform-store", "data")],
    Input("sunburst-graph", "clickData")
)
def show_platform_card(clickData):
    """
    When user clicks on a platform in the sunburst, show its card
    and remember it as 'current platform' for Set A / Set B buttons.
    """
    if not clickData or "label" not in clickData["points"][0]:
        return "", None

    label = clickData["points"][0]["label"]

    # If user clicked on a feature segment (keyword), not a platform:
    if label not in platform_to_keywords:
        return "", None

    card = build_platform_card(label)
    return card, label


#   CALLBACK 3 – SET A / B / CLEAR COMPARISON


@app.callback(
    [Output("platform-a-store", "data"),
     Output("platform-b-store", "data")],
    [Input("set-a-button", "n_clicks"),
     Input("set-b-button", "n_clicks"),
     Input("clear-compare-button", "n_clicks")],
    [State("current-platform-store", "data"),
     State("platform-a-store", "data"),
     State("platform-b-store", "data")],
    prevent_initial_call=True
)
def manage_comparison(n_clicks_a, n_clicks_b, n_clicks_clear,
                      current_platform, platform_a, platform_b):
    """
    - 'Set as A' -> current platform becomes A
    - 'Set as B' -> current platform becomes B
    - 'Clear comparison' -> both becomes None
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Clear comparison: back to browsing
    if trigger_id == "clear-compare-button":
        return None, None

    # Need a selected platform to set A or B
    if not current_platform:
        raise dash.exceptions.PreventUpdate

    if trigger_id == "set-a-button":
        return current_platform, platform_b
    elif trigger_id == "set-b-button":
        return platform_a, current_platform

    raise dash.exceptions.PreventUpdate


#   CALLBACK 4 – TOGGLE BROWSE vs COMPARISON + FILL COMPARISON

@app.callback(
    [Output("browse-section", "style"),
     Output("comparison-section", "style"),
     Output("comparison-content", "children")],
    [Input("platform-a-store", "data"),
     Input("platform-b-store", "data")]
)
def toggle_view_and_build_comparison(platform_a, platform_b):
    """
    If both A and B are set -> hide browse-section, show comparison-section
    and render the two cards + DIF list.
    Otherwise show browse-section and hide comparison-section.
    """
    # Are we in comparison mode?
    in_compare = bool(platform_a) and bool(platform_b)

    if not in_compare:
        # Browsing mode
        return (
            BROWSE_STYLE.copy(),
            COMPARE_HIDDEN_STYLE.copy(),
            ""
        )

    # Comparison mode: build A/B cards and differences
    card_a = build_platform_card(platform_a, "A")
    card_b = build_platform_card(platform_b, "B")

    only_a, only_b = compute_feature_diff(platform_a, platform_b)

    diff_block = html.Div(
        [
            html.H3("DIF – Feature differences"),
            html.Div(
                style={"display": "flex", "width": "100%"},
                children=[
                    html.Div(
                        style={"width": "50%", "paddingRight": "20px"},
                        children=[
                            html.H4(f"Only in {platform_a} (A)"),
                            html.Ul([html.Li(f) for f in only_a]) if only_a else html.P("—")
                        ]
                    ),
                    html.Div(
                        style={"width": "50%", "paddingLeft": "20px"},
                        children=[
                            html.H4(f"Only in {platform_b} (B)"),
                            html.Ul([html.Li(f) for f in only_b]) if only_b else html.P("—")
                        ]
                    )
                ]
            )
        ],
        style={"marginTop": "30px", "width": "100%"}
    )

    comparison_layout = html.Div(
        style={"width": "100%"},
        children=[
            html.H2("Platform Comparison"),
            html.Div(
                style={"display": "flex", "gap": "20px", "marginTop": "20px"},
                children=[
                    html.Div(style={"width": "50%"}, children=[card_a]),
                    html.Div(style={"width": "50%"}, children=[card_b]),
                ]
            ),
            diff_block
        ]
    )

    return (
        BROWSE_STYLE.copy() | {"display": "none"},
        COMPARE_VISIBLE_STYLE.copy(),
        comparison_layout
    )

#   MAIN


if __name__ == "__main__":
    app.run(debug=True)
