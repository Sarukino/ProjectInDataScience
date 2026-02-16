import dash
from dash import html
import dash_cytoscape as cyto

app = dash.Dash(__name__)

nodes = [
    {'data': {'id': 'Volunteer Profile', 'label': 'Volunteer Profile'}},
    {'data': {'id': 'Skills', 'label': 'Skills'}},
    {'data': {'id': 'Interests', 'label': 'Interests'}},
    {'data': {'id': 'Availability', 'label': 'Availability'}},
    {'data': {'id': 'Communication', 'label': 'Communication'}},
    {'data': {'id': 'First Aid', 'label': 'First Aid'}}
]

edges = [
    {'data': {'source': 'Volunteer Profile', 'target': 'Skills'}},
    {'data': {'source': 'Volunteer Profile', 'target': 'Interests'}},
    {'data': {'source': 'Volunteer Profile', 'target': 'Availability'}},
    {'data': {'source': 'Skills', 'target': 'Communication'}},
    {'data': {'source': 'Skills', 'target': 'First Aid'}}
]

app.layout = html.Div([
    html.H1("Volunteer Platform Network Visualization"),
    cyto.Cytoscape(
        id='network-graph',
        layout={'name': 'breadthfirst'},
        style={'width': '100%', 'height': '600px'},
        elements=nodes + edges,
        stylesheet=[
            {
                'selector': 'node',
                'style': {
                    'label': 'data(label)',
                    'background-color': '#007bff',
                    'color': 'black',
                    'font-size': '18px',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'width': '50px',
                    'height': '50px'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'width': 3,
                    'line-color': '#ccc',
                    'target-arrow-color': '#ccc',
                    'target-arrow-shape': 'triangle'
                }
            }
        ]
    )
])

if __name__ == '__main__':
    app.run(debug=True)
