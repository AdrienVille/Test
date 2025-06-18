import base64
import io

import pandas as pd
import dash
from dash import html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import scipy


def parse_excel(contents, filename, header=0):
    """Parse uploaded Excel file into a DataFrame."""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded), header=header)
    # Ensure the first column is datetime
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
    df.set_index(df.columns[0], inplace=True)
    return df


def monotone_curve(df):
    """Create a monotone curve figure sorted by consumption."""
    total = df.sum(axis=1)
    sorted_total = total.sort_values(ascending=False)
    fig = px.line(sorted_total.reset_index(), y=0, labels={"index": "Sample", "0": "Consumption"})
    fig.update_layout(title="Monotone Curve")
    return fig


def chronogram(df):
    """Create a chronogram (time series) figure."""
    fig = px.line(df)
    fig.update_layout(title="Chronogram")
    return fig


def heat_map(df):
    """Create a heat map of hourly average consumption."""
    hourly = df.resample("H").mean()
    pivot = hourly.pivot_table(index=hourly.index.date, columns=hourly.index.hour, values=df.columns[0])
    fig = px.imshow(pivot, aspect="auto")
    fig.update_layout(title="Heat Map", xaxis_title="Hour", yaxis_title="Date")
    return fig


def distribution(df):
    """Create a histogram of consumption values."""
    total = df.sum(axis=1)
    fig = px.histogram(total, nbins=50, labels={"value": "Consumption"})
    fig.update_layout(title="Distribution")
    return fig


def fit_statistical_model(df, variables):
    """Fit a linear regression model using given variables."""
    y = df.sum(axis=1)
    X = df[variables]
    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit()
    return model


def generate_pdf(figures, filename="report.pdf"):
    """Generate a PDF file from Plotly figures."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y_pos = height - 100
    for title, fig in figures:
        img_bytes = fig.to_image(format="png")
        img = ImageReader(io.BytesIO(img_bytes))
        c.drawString(50, y_pos + 40, title)
        c.drawImage(img, 50, y_pos - 300, width=500, height=300)
        c.showPage()
        y_pos = height - 100
    c.save()


app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Energy Dashboard"),
    dcc.Upload(
        id="upload-data",
        children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
        style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
        },
        multiple=False,
    ),
    html.Div(id="output-data-upload"),
    html.Div(id="dummy", style={"display": "none"}),
])


def build_layout(df):
    return html.Div([
        html.H2("Analysis"),
        dcc.Graph(id="monotone", figure=monotone_curve(df)),
        dcc.Graph(id="chronogram", figure=chronogram(df)),
        dcc.Graph(id="heatmap", figure=heat_map(df)),
        dcc.Graph(id="distribution", figure=distribution(df)),
        html.Button("Export PDF", id="export-button"),
    ])


@app.callback(Output("output-data-upload", "children"),
              Input("upload-data", "contents"),
              State("upload-data", "filename"))
def update_output(content, name):
    if content is not None:
        df = parse_excel(content, name)
        return build_layout(df)
    return html.Div()


@app.callback(Output("dummy", "children"),
              Input("export-button", "n_clicks"),
              State("monotone", "figure"),
              State("chronogram", "figure"),
              State("heatmap", "figure"),
              State("distribution", "figure"))
def export_pdf(n, mono_fig, chrono_fig, heat_fig, dist_fig):
    if n:
        figures = [
            ("Monotone Curve", go.Figure(mono_fig)),
            ("Chronogram", go.Figure(chrono_fig)),
            ("Heat Map", go.Figure(heat_fig)),
            ("Distribution", go.Figure(dist_fig)),
        ]
        generate_pdf(figures)
    return ""


if __name__ == "__main__":
    app.run_server(debug=True)
