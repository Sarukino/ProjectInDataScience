import dash
from dash import html, dcc
import pandas as pd
import plotly.express as px

# Dummy data
data = pd.DataFrame({
    'Category': ['Volunteer Profile', 'Volunteer Profile', 'Volunteer Profile', 
                 'Task', 'Task', 'Platform'],
    'Subcategory': ['Skills', 'Interests', 'Availability', 
                    'Gamification', 'Workflow', 'Multilingual Support'],
    'Value': [15, 25, 10, 30, 20, 18]
})

# Sunburst diagram 
fig = px.sunburst(
    data,
    path=['Category', 'Subcategory'],
    values='Value',
    title='Volunteer Platform Feature Breakdown'
)

# Dash app 
app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1('Volunteer Platform Visualization'),
    dcc.Graph(figure=fig)
])

if __name__ == '__main__':
    app.run(debug=True)

