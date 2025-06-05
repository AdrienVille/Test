import plotly.express as px

def plot_monotone(df):
    df_sorted = df.sort_values('Valeur', ascending=False)
    fig = px.line(df_sorted, x=df_sorted.index, y='Valeur', color='Compteur', title="Monotone de consommation")
    return fig
