from sklearn.linear_model import LinearRegression
import plotly.express as px

def run_impvp_model(df, target_col='Valeur', feature_cols=['temperature']):
    X = df[feature_cols].fillna(0)
    y = df[target_col].values
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    fig = px.scatter(x=y, y=y_pred, labels={'x':'Mesure réelle','y':'Prédiction'}, title='Prédiction IMPVP')
    fig.add_shape(type='line', x0=min(y), y0=min(y), x1=max(y), y1=max(y), line=dict(color='red', dash='dash'))
    summary = f"R2: {model.score(X, y):.3f}\nCoefficients:\n"
    for v, c in zip(feature_cols, model.coef_):
        summary += f"  {v}: {c:.3f}\n"
    summary += f"Intercept: {model.intercept_:.2f}\n"
    return fig, summary

# Pour intégrer les données météo
import requests
import pandas as pd

def get_meteo_data(dates, latitude, longitude):
    meteo_df = pd.DataFrame({'Date': pd.to_datetime(dates)})
    meteo_df['temperature'] = None
    for idx, row in meteo_df.iterrows():
        date_str = row['Date'].strftime('%Y-%m-%d')
        url = f"https://api.meteo.data.gouv.fr/collections/meteofrance-obs/latest?bbox={longitude},{latitude},{longitude},{latitude}&datetime={date_str}T00:00:00Z"
        r = requests.get(url)
        if r.ok and 'features' in r.json() and len(r.json()['features']) > 0:
            feat = r.json()['features'][0]
            meteo_df.at[idx, 'temperature'] = feat['properties'].get('temperature', None)
    return meteo_df
