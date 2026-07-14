import numpy as np

def fiyat_aralik_tahmini(ind_df, son_kapanis, gun_sayisi=1):
    son = ind_df.iloc[-1]
    trend_puani = 0
    if son['Close'] > son['SMA_50']: trend_puani += 1
    if son['SMA_50'] > son['SMA_200']: trend_puani += 1
    if son['MACD'] > son['MACD_Sinyal']: trend_puani += 1
    if 50 < son['RSI'] < 70: trend_puani += 1
    if son['OBV'] > ind_df['OBV'].rolling(5).mean().iloc[-1]: trend_puani += 1
    if son['Stokastik_K'] > son['Stokastik_D']: trend_puani += 1
    if son['ADX'] > 25: trend_puani += 1

    yon = 1 if trend_puani >= 4 else (-1 if trend_puani <= 2 else 0)
    gunluk_getiri = ind_df['Close'].pct_change().dropna()
    son_20_gun = gunluk_getiri.tail(20)
    ortalama_getiri = son_20_gun.mean()

    if gun_sayisi == 1:
        atr_deger = son['ATR']
        tahmini_kapanis = son_kapanis * (1 + ortalama_getiri * yon * 0.5)
        aralik = atr_deger * 0.8
    else:
        atr_haftalik = son['ATR'] * np.sqrt(5)
        haftalik_getiri = son_20_gun.rolling(5).sum().dropna().mean()
        tahmini_kapanis = son_kapanis * (1 + haftalik_getiri * yon * 0.5)
        aralik = atr_haftalik * 0.8

    yuksek = tahmini_kapanis + aralik/2
    dusuk = tahmini_kapanis - aralik/2
    min_aralik = son_kapanis * 0.005
    if (yuksek - dusuk) < min_aralik:
        yuksek = tahmini_kapanis + min_aralik/2
        dusuk = tahmini_kapanis - min_aralik/2 

    return {
        'yon': 'YÜKSELİŞ' if yon==1 else ('DÜŞÜŞ' if yon==-1 else 'YATAY'),
        'tahmini_kapanis': round(tahmini_kapanis, 2),
        'yuksek': round(yuksek, 2),
        'dusuk': round(dusuk, 2),
        'guven_skoru': trend_puani / 7 * 100
    }
