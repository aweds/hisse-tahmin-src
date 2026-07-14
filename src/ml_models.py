import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import accuracy_score

def tahmin_araligi(ind_df):
    ozellikler = ['SMA_50', 'SMA_200', 'MACD', 'RSI', 'ATR', 'Stokastik_K', 'ADX']
    X = ind_df[ozellikler].dropna()
    y = ind_df['Close'].pct_change(5).shift(-5) * 100
    ortak = X.index.intersection(y.dropna().index)
    X, y = X.loc[ortak], y.loc[ortak]
    if len(X) < 100:
        return None
    son_x = X.iloc[-1:].values
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X[:-1], y[:-1])
    tahmin = model.predict(son_x)[0]
    son_20_pred = model.predict(X.iloc[-20:])
    hatalar = y.iloc[-20:].values - son_20_pred
    std_hata = np.std(hatalar)
    son_fiyat = ind_df['Close'].iloc[-1]
    return {
        'alt_fiyat': round(son_fiyat * (1 + (tahmin - 1.96*std_hata)/100), 2),
        'ust_fiyat': round(son_fiyat * (1 + (tahmin + 1.96*std_hata)/100), 2),
        'tahmini_fiyat': round(son_fiyat * (1 + tahmin/100), 2)
    }

def yon_tahmini(ind_df):
    ozellikler = ['SMA_50', 'SMA_200', 'MACD', 'RSI', 'ATR', 'Stokastik_K', 'ADX']
    df = ind_df.dropna(subset=ozellikler).copy()
    df['Hedef'] = (df['Close'].shift(-5) > df['Close']).astype(int)
    df = df.dropna(subset=['Hedef'])
    if len(df) < 200:
        return None
    split_idx = int(len(df) * 0.8)
    train = df.iloc[:split_idx]
    test = df.iloc[split_idx:]
    X_train = train[ozellikler]
    y_train = train['Hedef']
    X_test = test[ozellikler]
    y_test = test['Hedef']
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred) * 100
    son_x = df[ozellikler].iloc[-1:].values
    son_tahmin = model.predict(son_x)[0]
    yon = 'YUKARI ↑' if son_tahmin == 1 else 'AŞAĞI ↓' 
    return {'dogruluk': round(acc, 1), 'son_tahmin': yon, 'test_boyutu': len(test)}
