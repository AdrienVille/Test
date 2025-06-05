import dash
from dash import html, dcc, Input, Output, State, dash_table
import pandas as pd
from data_loader import load_energy_data
from analytics.monotone import plot_monotone
from analytics.chronogram import plot_chronogram
from analytics.heatmap import plot_heatmap
from analytics.stats import plot_stats
from analytics.model_impvp import run_impvp_model, get_meteo_data
from report import generate_pdf_report

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Audit énergétique - Interface d'analyse"),
    dcc.Upload(
        id='upload-data',
        children=html.Button('Importer un fichier Excel'),
        multiple=False
    ),
    html.Div(id='output-data-upload'),
    dcc.Dropdown(id='feature-cols', multi=True, placeholder='Choisissez les variables explicatives'),
    dcc.Tabs(id="tabs", value='tab-monotone', children=[
        dcc.Tab(label='Monotones', value='tab-monotone'),
        dcc.Tab(label='Chronogrammes', value='tab-chronogram'),
        dcc.Tab(label='Heat Map', value='tab-heatmap'),
        dcc.Tab(label='Statistiques', value='tab-stats'),
        dcc.Tab(label='Modèle IMPVP', value='tab-model')
    ]),
    html.Div(id='tab-content'),
    html.Button('Générer le rapport PDF', id='generate-report'),
    html.Div(id='report-status')
])

@app.callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(content, filename):
    if content:
        content_type, content_string = content.split(',')
        import base64, io
        decoded = base64.b64decode(content_string)
        df = load_energy_data(io.BytesIO(decoded))
        return dash_table.DataTable(data=df.head(10).to_dict('records'), page_size=10)
    return "Importer un fichier Excel pour démarrer"

@app.callback(
    Output('feature-cols', 'options'),
    Input('upload-data', 'contents')
)
def set_feature_options(content):
    if content:
        content_type, content_string = content.split(',')
        import base64, io
        decoded = base64.b64decode(content_string)
        df = load_energy_data(io.BytesIO(decoded))
        options = [{'label': col, 'value': col} for col in df.columns if col not in ['Date', 'Valeur']]
        return options
    return []

@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value'),
    State('upload-data', 'contents'),
    Input('feature-cols', 'value')
)
def render_tab(tab, content, feature_cols):
    if not content:
        return "Aucune donnée chargée."
    import base64, io
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    df = load_energy_data(io.BytesIO(decoded))

    if tab == 'tab-monotone':
        fig = plot_monotone(df)
        return dcc.Graph(figure=fig)
    elif tab == 'tab-chronogram':
        fig = plot_chronogram(df)
        return dcc.Graph(figure=fig)
    elif tab == 'tab-heatmap':
        fig = plot_heatmap(df)
        return dcc.Graph(figure=fig)
    elif tab == 'tab-stats':
        fig = plot_stats(df)
        return dcc.Graph(figure=fig)
    elif tab == 'tab-model':
        if feature_cols:
            # Gérer la récupération de température météo si nécessaire
            if 'temperature' in feature_cols and 'temperature' not in df.columns:
                # À adapter : renseigner latitude/longitude du site
                meteo = get_meteo_data(df['Date'], 48.8566, 2.3522) # Paris par défaut
                df = pd.merge(df, meteo, on='Date', how='left')
            fig, summary = run_impvp_model(df, feature_cols=feature_cols)
            return html.Div([dcc.Graph(figure=fig), html.Pre(summary)])
        else:
            return "Sélectionnez au moins une variable explicative."
    else:
        return "Sélectionnez un onglet."

@app.callback(
    Output('report-status', 'children'),
    Input('generate-report', 'n_clicks'),
    State('upload-data', 'contents')
)
def generate_report(n_clicks, content):
    if n_clicks and content:
        content_type, content_string = content.split(',')
        import base64, io
        decoded = base64.b64decode(content_string)
        df = load_energy_data(io.BytesIO(decoded))
        generate_pdf_report(df)
        return "Rapport PDF généré !"
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)
