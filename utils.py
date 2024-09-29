import base64
import io
import pandas as pd
import plotly.graph_objs as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Function to parse file contents (CSV, Excel)
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        return df
    except Exception as e:
        return html.Div(['There was an error processing this file.'])

# Function to create a line plot
def create_line_plot(df, x_column, y_column):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x_column], y=df[y_column], mode='lines'))
    fig.update_layout(title=f'Line Plot: {y_column} vs {x_column}', xaxis_title=x_column, yaxis_title=y_column)
    return fig

# Function to create a correlation matrix
def create_correlation_matrix(df):
    corr = df.corr()
    fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, colorscale='Viridis'))
    fig.update_layout(title='Correlation Matrix')
    return fig
