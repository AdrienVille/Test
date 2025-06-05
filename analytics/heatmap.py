import plotly.express as px

def plot_heatmap(df):
    df['Hour'] = df['Date'].dt.hour
    df['Day'] = df['Date'].dt.date
    pivot = df.pivot_table(index='Day', columns='Hour', values='Valeur', aggfunc='mean')
    fig = px.imshow(pivot, labels=dict(x="Heure", y="Jour", color="Consommation"), title="Heatmap consommation")
    return fig
