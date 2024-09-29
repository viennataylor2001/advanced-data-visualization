import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go
import io
import base64
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# App Layout
app.layout = html.Div([
    html.H1("Advanced 3D Data Visualization Platform", style={'textAlign': 'center'}),

    # File upload section
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed',
            'borderRadius': '5px', 'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    
    # Dropdown for plot type selection
    html.Div([
        html.Label("Choose Plot Type:"),
        dcc.Dropdown(id='plot-type', options=[
            {'label': '3D Surface Plot', 'value': '3d-surface'},
            {'label': 'Line Plot', 'value': 'line'},
            {'label': 'Bar Plot', 'value': 'bar'},
            {'label': 'Scatter Plot', 'value': 'scatter'},
        ], value='3d-surface')
    ], style={'width': '50%', 'display': 'inline-block', 'margin': '10px'}),

    # Data filtering options
    html.Div([
        html.Label("Filter Columns:"),
        dcc.Checklist(id='columns-to-display')
    ], style={'width': '100%', 'margin': '10px'}),

    # Placeholder for the table displaying the uploaded data
    html.Div(id='output-data-upload'),
    
    # Graph component to display plots
    dcc.Graph(id='output-plot'),

    # Interval for real-time data updates (optional)
    dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0)
])


# Helper function to parse uploaded file
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        return html.Div(['There was an error processing the file.'])
    
    # Return a table and filter options
    return html.Div([
        dash_table.DataTable(
            id='data-table',
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=10,
        ),
        dcc.Checklist(id='columns-to-display',
                      options=[{'label': col, 'value': col} for col in df.columns],
                      value=df.columns.tolist())
    ]), df


# Callback to update the data table
@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-data', 'contents'),
     Input('upload-data', 'filename')]
)
def update_output(contents, filename):
    if contents is not None:
        children, df = parse_contents(contents, filename)
        return children


# Callback to update the plot based on the selected type
@app.callback(
    Output('output-plot', 'figure'),
    [Input('plot-type', 'value'),
     Input('data-table', 'data'),
     Input('columns-to-display', 'value')],
    prevent_initial_call=True
)
def update_plot(plot_type, rows, selected_columns):
    if rows is None or not selected_columns:
        return {}
    
    # Convert rows back to DataFrame
    df = pd.DataFrame(rows)
    
    if plot_type == '3d-surface' and len(selected_columns) >= 3:
        x = df[selected_columns[0]]
        y = df[selected_columns[1]]
        z = df[selected_columns[2]]
        surface = go.Surface(x=x, y=y, z=z)
        fig = go.Figure(data=[surface])
    elif plot_type == 'line' and len(selected_columns) >= 2:
        fig = go.Figure(data=[go.Scatter(x=df[selected_columns[0]], y=df[selected_columns[1]], mode='lines')])
    elif plot_type == 'bar' and len(selected_columns) >= 2:
        fig = go.Figure(data=[go.Bar(x=df[selected_columns[0]], y=df[selected_columns[1]])])
    elif plot_type == 'scatter' and len(selected_columns) >= 2:
        fig = go.Figure(data=[go.Scatter(x=df[selected_columns[0]], y=df[selected_columns[1]], mode='markers')])
    else:
        fig = {}
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
