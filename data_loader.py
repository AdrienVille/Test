import pandas as pd

def load_energy_data(filepath):
    df = pd.read_excel(filepath)
    date_col = [col for col in df.columns if 'date' in col.lower()][0]
    meter_col = [col for col in df.columns if 'compteur' in col.lower() or 'meter' in col.lower()][0]
    value_col = [col for col in df.columns if 'conso' in col.lower() or 'valeur' in col.lower()][0]
    df = df.rename(columns={date_col: 'Date', meter_col: 'Compteur', value_col: 'Valeur'})
    df['Date'] = pd.to_datetime(df['Date'])
    return df
