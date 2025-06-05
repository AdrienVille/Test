import plotly.express as px

def plot_chronogram(df):
    fig = px.line(df, x='Date', y='Valeur', color='Compteur', title="Chronogramme de consommation")
    return fig
