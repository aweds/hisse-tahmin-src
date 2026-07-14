import numpy as np

def max_drawdown(seri):
    tepe = seri.expanding(min_periods=1).max()
    drawdown = (seri - tepe) / tepe * 100
    return drawdown.min()

def al_sat_sinyalleri_uret(ind_df):
    df = ind_df.copy()
    df['MACD_kesisme'] = (df['MACD'] > df['MACD_Sinyal']) & (df['MACD'].shift(1) <= df['MACD_Sinyal'].shift(1))
    df['MACD_asagi_kesisme'] = (df['MACD'] < df['MACD_Sinyal']) & (df['MACD'].shift(1) >= df['MACD_Sinyal'].shift(1))
    al_sinyali = df['MACD_kesisme'] & (df['RSI'] < 70)
    sat_sinyali = df['MACD_asagi_kesisme'] | (df['RSI'] >= 70)
    df['Sinyal'] = 0
    df.loc[al_sinyali, 'Sinyal'] = 1
    df.loc[sat_sinyali, 'Sinyal'] = -1
    return df

def strateji_simulasyonu(df):
    sinyal_df = al_sat_sinyalleri_uret(df)
    pozisyon = 0
    alis_fiyat = 0
    islemler = []
    for i in range(len(sinyal_df)):
        if sinyal_df['Sinyal'].iloc[i] == 1 and pozisyon == 0:
            pozisyon = 1
            alis_fiyat = sinyal_df['Close'].iloc[i]
            islemler.append({'Tarih': sinyal_df.index[i], 'Tip': 'AL', 'Fiyat': alis_fiyat})
        elif sinyal_df['Sinyal'].iloc[i] == -1 and pozisyon == 1:
            pozisyon = 0
            satis_fiyat = sinyal_df['Close'].iloc[i]
            islemler.append({'Tarih': sinyal_df.index[i], 'Tip': 'SAT', 'Fiyat': satis_fiyat})
            getiri = (satis_fiyat - alis_fiyat) / alis_fiyat * 100
            islemler[-1]['Getiri (%)'] = round(getiri, 2)
    if len(islemler) < 2:
        return None, None
    kazananlar = [i for i in islemler if i.get('Getiri (%)', 0) > 0]
    toplam_getiri = sum(i.get('Getiri (%)', 0) for i in islemler)
    kazanc_orani = len(kazananlar) / (len(islemler) // 2) * 100 if len(islemler) // 2 > 0 else 0
    return islemler, {
        'Toplam Getiri (%)': round(toplam_getiri, 2),
        'İşlem Sayısı': len(islemler) // 2,
        'Kazanma Oranı (%)': round(kazanc_orani, 1), 
        'Maksimum Drawdown (%)': round(max_drawdown(sinyal_df['Close']), 2)
    }
