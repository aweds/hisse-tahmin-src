import numpy as np
import pandas as pd

def hedef_olasilik(df, gun=50, hedef_yuzde=5):
    kapanis = df['Close']
    sma = kapanis.rolling(gun).mean()
    sinyal = kapanis > sma
    getiri = kapanis.pct_change(5).shift(-5) * 100
    kosul = sinyal & sinyal.shift(1)
    hedef = getiri >= hedef_yuzde
    ortak = kosul & hedef.notna()
    olasilik = hedef[ortak].mean() * 100 if ortak.any() else 0
    return olasilik

def kesişim_dedektoru(ind_df):
    df = ind_df.dropna(subset=['SMA_50', 'SMA_200']).copy()
    if len(df) < 20:
        return None
    son_fark = df['SMA_50'].iloc[-1] - df['SMA_200'].iloc[-1]
    fark_serisi = df['SMA_50'] - df['SMA_200']
    y = fark_serisi.iloc[-20:].values
    x = np.arange(len(y))
    if np.std(y) < 1e-9:
        return None
    egim, intercept = np.polyfit(x, y, 1)
    if abs(egim) < 1e-9:
        return None
    x_kesişim = -intercept / egim
    kalan_gun = x_kesişim - (len(y) - 1)
    if kalan_gun < 0:
        return {'tip': 'none', 'gun': 0, 'son_fark': son_fark}
    if son_fark < 0 and egim > 0:
        tip = 'Golden Cross'
    elif son_fark > 0 and egim < 0:
        tip = 'Death Cross'
    else:
        tip = 'Belirsiz'
    return {'tip': tip, 'gun': round(kalan_gun), 'son_fark': son_fark}

def teknik_puanlama(ind_df):
    son = ind_df.iloc[-1]
    trend = 0
    if son['SMA_50'] > son['SMA_200']: trend += 4
    if son['Close'] > son['SMA_50']: trend += 3
    if son['Close'] > son['SMA_200']: trend += 3
    trend = min(trend, 10)

    momentum = 0
    rsi = son['RSI']
    if rsi > 60: momentum += 4
    elif rsi > 50: momentum += 3
    elif rsi > 30: momentum += 1
    else: momentum += 2
    if son['MACD'] > son['MACD_Sinyal']: momentum += 4
    if son['Stokastik_K'] > son['Stokastik_D']: momentum += 2
    momentum = min(momentum, 10)

    volatilite = 5
    fiyat = son['Close']
    sma20 = (son['Bollinger_Ust'] + son['Bollinger_Alt']) / 2
    bant_genisligi = (son['Bollinger_Ust'] - son['Bollinger_Alt']) / sma20 * 100
    fark_yuzde = abs(fiyat - sma20) / sma20 * 100
    if fark_yuzde < 1: volatilite += 3
    elif fark_yuzde < 2: volatilite += 1
    if bant_genisligi < 5: volatilite += 2
    ortalama_atr = ind_df['ATR'].rolling(20).mean().iloc[-1]
    if son['ATR'] < ortalama_atr: volatilite += 2
    else: volatilite -= 1
    volatilite = max(0, min(volatilite, 10))

    hacim_p = 0
    obv_ortalama = ind_df['OBV'].rolling(5).mean().iloc[-1]
    if son['OBV'] > obv_ortalama: hacim_p += 5
    ortalama_hacim = ind_df['Volume'].rolling(20).mean().iloc[-1]
    if son['Volume'] > ortalama_hacim: hacim_p += 5
    hacim_p = min(hacim_p, 10)

    genel = round((trend + momentum + volatilite + hacim_p) / 4, 1)
    return {
        'trend': trend,
        'momentum': momentum,
        'volatilite': volatilite,
        'hacim': hacim_p,
        'genel': genel
    }

def destek_direnc_bul(veri, pencere=5):
    yuksek = veri['High']
    dusuk = veri['Low']
    kapanis = veri['Close']
    pivot_tepeler = []
    pivot_dipler = []
    for i in range(pencere, len(veri)-pencere):
        if yuksek.iloc[i] == yuksek.iloc[i-pencere:i+pencere+1].max():
            pivot_tepeler.append({'tarih': yuksek.index[i], 'fiyat': yuksek.iloc[i]})
        if dusuk.iloc[i] == dusuk.iloc[i-pencere:i+pencere+1].min():
            pivot_dipler.append({'tarih': dusuk.index[i], 'fiyat': dusuk.iloc[i]})

    tolerans = kapanis.iloc[-1] * 0.01
    destek_seviyeleri = []
    for dip in pivot_dipler:
        eklendi = False
        for seviye in destek_seviyeleri:
            if abs(dip['fiyat'] - seviye['fiyat']) < tolerans:
                seviye['sayi'] += 1
                seviye['tarihler'].append(dip['tarih'])
                eklendi = True
                break
        if not eklendi:
            destek_seviyeleri.append({'fiyat': dip['fiyat'], 'sayi': 1, 'tarihler': [dip['tarih']]})

    direnc_seviyeleri = []
    for tepe in pivot_tepeler:
        eklendi = False
        for seviye in direnc_seviyeleri:
            if abs(tepe['fiyat'] - seviye['fiyat']) < tolerans:
                seviye['sayi'] += 1
                seviye['tarihler'].append(tepe['tarih'])
                eklendi = True
                break
        if not eklendi:
            direnc_seviyeleri.append({'fiyat': tepe['fiyat'], 'sayi': 1, 'tarihler': [tepe['tarih']]})

    guclu_destek = [s for s in destek_seviyeleri if s['sayi'] >= 2]
    guclu_direnc = [s for s in direnc_seviyeleri if s['sayi'] >= 2]
    return guclu_destek, guclu_direnc 
