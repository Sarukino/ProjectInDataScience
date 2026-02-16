import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

# Adatok létrehozása
data = {
    'Category': ['Volunteer Profile', 'Volunteer Profile', 'Volunteer Profile', 'Skills', 'Skills', 'Availability', 'Availability'],
    'Label': ['Skills', 'Interests', 'Availability', 'Communication', 'First Aid', 'Weekdays', 'Weekends'],
    'Value': [0, 0, 0, 4, 2, 3, 1]
}

df = pd.DataFrame(data)

# Treemap létrehozása
fig = px.treemap(
    df,
    path=['Category', 'Label'],
    values='Value',
    title='Volunteer Platform Hierarchy (Treemap)'
)

# Dash app beállítása
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Volunteer Platform Visualization"),
    html.P("Volunteer Profile Hierarchy (Treemap)"),
    dcc.Graph(id='treemap', figure=fig)
])

if __name__ == '__main__':
    app.run(debug=True)
