import plotly.express as px

def plot_stats(df):
    fig = px.histogram(df, x='Valeur', nbins=50, title="Distribution statistique des consommations")
    return fig
