# Icicle Chart
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

# data
data = {
    'Category': ['Volunteer Profile', 'Volunteer Profile', 'Volunteer Profile', 'Skills', 'Skills', 'Availability', 'Availability'],
    'Label': ['Skills', 'Interests', 'Availability', 'Communication', 'First Aid', 'Weekdays', 'Weekends'],
    'Value': [0, 0, 0, 4, 2, 3, 1]
}

df = pd.DataFrame(data)

# Icicle diagram 
fig = px.icicle(
    df,
    path=['Category', 'Label'],
    values='Value',
    title='Volunteer Platform Hierarchy (Icicle Chart)'
)

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Volunteer Platform Visualization"),
    html.P("Volunteer Profile Hierarchy (Icicle Chart)"),
    dcc.Graph(figure=fig)
])

if __name__ == '__main__':
    app.run(debug=True)
