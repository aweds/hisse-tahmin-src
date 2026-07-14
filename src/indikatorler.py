import pandas as pd
import numpy as np

def hesapla(df):
    """8 indikatörü hesaplar ve DataFrame döndürür."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    kapanis = df['Close'].squeeze().ffill().dropna()
    yuksek = df['High'].squeeze().ffill().dropna()
    dusuk = df['Low'].squeeze().ffill().dropna()
    hacim = df['Volume'].squeeze().fillna(0)

    sma_50 = kapanis.rolling(50).mean()
    sma_200 = kapanis.rolling(200).mean()

    ema_12 = kapanis.ewm(span=12, adjust=False).mean()
    ema_26 = kapanis.ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    sinyal = macd.ewm(span=9, adjust=False).mean()

    delta = kapanis.diff()
    kazanc = delta.clip(lower=0)
    kayip = -delta.clip(upper=0)
    ortalama_kazanc = kazanc.rolling(14).mean()
    ortalama_kayip = kayip.rolling(14).mean()
    rs = ortalama_kazanc / ortalama_kayip
    rsi = 100 - (100 / (1 + rs))

    sma_20 = kapanis.rolling(20).mean()
    std_20 = kapanis.rolling(20).std()
    bollinger_ust = sma_20 + 2 * std_20
    bollinger_alt = sma_20 - 2 * std_20

    high_low = yuksek - dusuk
    high_close = np.abs(yuksek - kapanis.shift())
    low_close = np.abs(dusuk - kapanis.shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()

    yon = np.sign(kapanis.diff()).fillna(0)
    obv = (yon * hacim).cumsum()

    dusuk_14 = dusuk.rolling(14).min()
    yuksek_14 = yuksek.rolling(14).max()
    stok_k = (kapanis - dusuk_14) / (yuksek_14 - dusuk_14) * 100
    stok_d = stok_k.rolling(3).mean()

    artis = yuksek.diff()
    dusus = -dusuk.diff()
    pdm = pd.Series(np.where((artis > dusus) & (artis > 0), artis, 0), index=kapanis.index)
    ndm = pd.Series(np.where((dusus > artis) & (dusus > 0), dusus, 0), index=kapanis.index)
    tr14 = tr.rolling(14).mean()
    pdm14 = pdm.rolling(14).mean()
    ndm14 = ndm.rolling(14).mean()
    pdi = 100 * pdm14 / tr14
    ndi = 100 * ndm14 / tr14
    dx = 100 * np.abs(pdi - ndi) / (pdi + ndi)
    adx = dx.rolling(14).mean()

    indikatorler = pd.DataFrame({
        'Close': kapanis,
        'SMA_50': sma_50, 'SMA_200': sma_200,
        'MACD': macd, 'MACD_Sinyal': sinyal,
        'RSI': rsi,
        'Bollinger_Ust': bollinger_ust, 'Bollinger_Alt': bollinger_alt,
        'ATR': atr, 'OBV': obv,
        'Stokastik_K': stok_k, 'Stokastik_D': stok_d,
        'ADX': adx,
        'Volume': hacim,
        'High': yuksek,
        'Low': dusuk
    }, index=kapanis.index)
    return indikatorler 
