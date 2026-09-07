import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Modüllerden importlar
from src.indikatorler import hesapla as ind_hesapla
from src.tahmin import fiyat_aralik_tahmini
from src.ml_models import tahmin_araligi, yon_tahmini
from src.analiz import (hedef_olasilik, kesişim_dedektoru,
                        teknik_puanlama, destek_direnc_bul)
from src.simulasyon import strateji_simulasyonu

# ---------------------------
# BIST 100 HİSSE LİSTESİ
# ---------------------------
HISSE_LISTESI = [
    {"sembol": "AEFES.IS", "isim": "Anadolu Efes"},
    {"sembol": "AGHOL.IS", "isim": "AG Anadolu Grubu Holding"},
    {"sembol": "AKBNK.IS", "isim": "Akbank"},
    {"sembol": "AKFGY.IS", "isim": "Akfen GMYO"},
    {"sembol": "AKSA.IS", "isim": "Aksa"},
    {"sembol": "AKSEN.IS", "isim": "Aksa Enerji"},
    {"sembol": "ALARK.IS", "isim": "Alarko Holding"},
    {"sembol": "ALBRK.IS", "isim": "Albaraka Türk"},
    {"sembol": "ARCLK.IS", "isim": "Arçelik"},
    {"sembol": "ASELS.IS", "isim": "Aselsan"},
    {"sembol": "ASTOR.IS", "isim": "Astor Enerji"},
    {"sembol": "BIMAS.IS", "isim": "BİM Mağazalar"},
    {"sembol": "BRSAN.IS", "isim": "Borusan Mannesmann"},
    {"sembol": "BRYAT.IS", "isim": "Borusan Yatırım"},
    {"sembol": "CCOLA.IS", "isim": "Coca-Cola İçecek"},
    {"sembol": "CIMSA.IS", "isim": "Çimsa"},
    {"sembol": "CLEBI.IS", "isim": "Çelebi Hava Servisi"},
    {"sembol": "DEVA.IS", "isim": "Deva Holding"},
    {"sembol": "DOAS.IS", "isim": "Doğuş Otomotiv"},
    {"sembol": "DOHOL.IS", "isim": "Doğan Holding"},
    {"sembol": "ECILC.IS", "isim": "Eczacıbaşı İlaç"},
    {"sembol": "ECZYT.IS", "isim": "Eczacıbaşı Yatırım"},
    {"sembol": "EGEEN.IS", "isim": "Ege Endüstri"},
    {"sembol": "EKGYO.IS", "isim": "Emlak Konut GMYO"},
    {"sembol": "ENJSA.IS", "isim": "Enerjisa"},
    {"sembol": "ENKAI.IS", "isim": "Enka İnşaat"},
    {"sembol": "EREGL.IS", "isim": "Ereğli Demir Çelik"},
    {"sembol": "FENER.IS", "isim": "Fenerbahçe Sportif"},
    {"sembol": "FROTO.IS", "isim": "Ford Otosan"},
    {"sembol": "GARAN.IS", "isim": "Garanti Bankası"},
    {"sembol": "GUBRF.IS", "isim": "Gübre Fabrikaları"},
    {"sembol": "HALKB.IS", "isim": "Halk Bankası"},
    {"sembol": "HEKTS.IS", "isim": "Hektaş"},
    {"sembol": "ISCTR.IS", "isim": "İş Bankası (C)"},
    {"sembol": "ISGYO.IS", "isim": "İş GMYO"},
    {"sembol": "KCHOL.IS", "isim": "Koç Holding"},
    {"sembol": "KLSER.IS", "isim": "Kaleseramik"},
    {"sembol": "KONTR.IS", "isim": "Kontron"},
    {"sembol": "KONYA.IS", "isim": "Konya Çimento"},
    {"sembol": "KORDSA.IS", "isim": "Kordsa"},
    {"sembol": "KOZAA.IS", "isim": "Koza Anadolu Metal"},
    {"sembol": "KOZAL.IS", "isim": "Koza Altın"},
    {"sembol": "KRDMD.IS", "isim": "Kardemir (D)"},
    {"sembol": "MAVI.IS", "isim": "Mavi Giyim"},
    {"sembol": "MGROS.IS", "isim": "Migros"},
    {"sembol": "ODAS.IS", "isim": "Odaş Elektrik"},
    {"sembol": "OYAKC.IS", "isim": "Oyak Çimento"},
    {"sembol": "PENTA.IS", "isim": "Penta Teknoloji"},
    {"sembol": "PETKM.IS", "isim": "Petkim"},
    {"sembol": "PGSUS.IS", "isim": "Pegasus"},
    {"sembol": "QUAGR.IS", "isim": "Qua Granite"},
    {"sembol": "SAHOL.IS", "isim": "Sabancı Holding"},
    {"sembol": "SASA.IS", "isim": "Sasa Polyester"},
    {"sembol": "SELEC.IS", "isim": "Selçuk Ecza Deposu"},
    {"sembol": "SISE.IS", "isim": "Şişe Cam"},
    {"sembol": "SKBNK.IS", "isim": "Şekerbank"},
    {"sembol": "SMRTG.IS", "isim": "Smart Güneş Enerjisi"},
    {"sembol": "SOKM.IS", "isim": "Şok Marketler"},
    {"sembol": "TAVHL.IS", "isim": "TAV Havalimanları"},
    {"sembol": "TCELL.IS", "isim": "Turkcell"},
    {"sembol": "THYAO.IS", "isim": "Türk Hava Yolları"},
    {"sembol": "TKFEN.IS", "isim": "Tekfen Holding"},
    {"sembol": "TOASO.IS", "isim": "Tofaş"},
    {"sembol": "TSKB.IS", "isim": "TSKB"},
    {"sembol": "TTKOM.IS", "isim": "Türk Telekom"},
    {"sembol": "TUPRS.IS", "isim": "TÜPRAŞ"},
    {"sembol": "ULKER.IS", "isim": "Ülker"},
    {"sembol": "VAKBN.IS", "isim": "VakıfBank"},
    {"sembol": "VESBE.IS", "isim": "Vestel Beyaz Eşya"},
    {"sembol": "VESTL.IS", "isim": "Vestel"},
    {"sembol": "YKBNK.IS", "isim": "Yapı Kredi Bankası"},
    {"sembol": "YYLGD.IS", "isim": "Yayla Gıda"},
    {"sembol": "ZOREN.IS", "isim": "Zorlu Enerji"},
]

# ---------------------------
# YENİ HALKA ARZ HİSSELERİ
# ---------------------------
HALKA_ARZ_LISTESI = [
    {"sembol": "AKFYE.IS", "isim": "Akfen Yenilenebilir Enerji"},
    {"sembol": "BINHO.IS", "isim": "Binho Enerji"},
    {"sembol": "BIZIM.IS", "isim": "Bizim Toptan"},
    {"sembol": "BRLSM.IS", "isim": "Birleşim Mühendislik"},
    {"sembol": "CANTE.IS", "isim": "Çan2 Termik"},
    {"sembol": "CVKMD.IS", "isim": "CVK Maden"},
    {"sembol": "DAPGM.IS", "isim": "DAP Gayrimenkul"},
    {"sembol": "DESA.IS", "isim": "Desa Deri"},
    {"sembol": "DOFER.IS", "isim": "Dofer Yapı Malzemeleri"},
    {"sembol": "DURDO.IS", "isim": "Duran Doğan Basım"},
    {"sembol": "EBEBK.IS", "isim": "Ebebek Mağazacılık"},
    {"sembol": "EDATA.IS", "isim": "E-Data Teknoloji"},
    {"sembol": "ELITE.IS", "isim": "Elite Naturel"},
    {"sembol": "EMKEL.IS", "isim": "Emlak Katılım"},
    {"sembol": "ESCOM.IS", "isim": "Escort Teknoloji"},
    {"sembol": "EUREN.IS", "isim": "Europen Endüstri"},
    {"sembol": "FADE.IS", "isim": "Fade Gıda"},
    {"sembol": "FORTE.IS", "isim": "Forte Bilgi İletişim"},
    {"sembol": "FZL.IS", "isim": "Fuzul GYO"},
    {"sembol": "GEDIK.IS", "isim": "Gedik Yatırım"},
    {"sembol": "GIPTA.IS", "isim": "Gıpta Ofis Kırtasiye"},
    {"sembol": "GRTRK.IS", "isim": "Grainturk Tarım"},
    {"sembol": "HUNER.IS", "isim": "Huner Gıda"},
    {"sembol": "IZENR.IS", "isim": "İzmir Enerji"},
    {"sembol": "KAYSE.IS", "isim": "Kayseri Şeker"},
    {"sembol": "KLSYN.IS", "isim": "Koleksiyon Mobilya"},
    {"sembol": "KNFRT.IS", "isim": "Konfrut Gıda"},
    {"sembol": "KOPOL.IS", "isim": "Kopol Plastik"},
    {"sembol": "KRVGD.IS", "isim": "Kervan Gıda"},
    {"sembol": "LIDER.IS", "isim": "Lider Faktoring"},
    {"sembol": "LKMNH.IS", "isim": "Lokman Hekim Sağlık"},
    {"sembol": "MANAS.IS", "isim": "Manas Enerji"},
    {"sembol": "MEGAP.IS", "isim": "Mega Polietilen"},
    {"sembol": "MERKO.IS", "isim": "Merko Gıda"},
    {"sembol": "MIA.IS", "isim": "Mia Teknoloji"},
    {"sembol": "MPARK.IS", "isim": "Medical Park"},
    {"sembol": "NATEN.IS", "isim": "Naturel Enerji"},
    {"sembol": "OBASE.IS", "isim": "Obase Bilgisayar"},
    {"sembol": "ONCSM.IS", "isim": "Oncosem"},
    {"sembol": "ORCAY.IS", "isim": "Orçay Ortaköy Çay"},
    {"sembol": "OSMEN.IS", "isim": "Osmanlı Menkul"},
    {"sembol": "OZSUB.IS", "isim": "Özsu Balık"},
    {"sembol": "PATEK.IS", "isim": "Pasifik Teknoloji"},
    {"sembol": "PCILT.IS", "isim": "PC İletişim"},
    {"sembol": "PEKGY.IS", "isim": "Peker GYO"},
    {"sembol": "PLTUR.IS", "isim": "Platform Turizm"},
    {"sembol": "QNBFL.IS", "isim": "QNB Finans Finansal Kiralama"},
    {"sembol": "RALYH.IS", "isim": "Ral Yatırım Holding"},
    {"sembol": "REEDR.IS", "isim": "Reeder Teknoloji"},
    {"sembol": "SEGMN.IS", "isim": "Segment Yatırım"},
    {"sembol": "SELGD.IS", "isim": "Selçuk Gıda"},
    {"sembol": "SUNTK.IS", "isim": "Sun Tekstil"},
    {"sembol": "TATEN.IS", "isim": "Tatlıpınar Enerji"},
    {"sembol": "TUKAS.IS", "isim": "Tukaş Gıda"},
    {"sembol": "ULUFA.IS", "isim": "Ulusal Faktoring"},
    {"sembol": "VBTYZ.IS", "isim": "VBT Yazılım"},
    {"sembol": "VERUS.IS", "isim": "Verusa Holding"},
    {"sembol": "YAYLA.IS", "isim": "Yayla Enerji"},
    {"sembol": "ZEDUR.IS", "isim": "Zedur Enerji"},
]

SEMBOL_ISIM = {h["sembol"]: h["isim"] for h in HISSE_LISTESI}
HALKA_ARZ_SEMBOL_ISIM = {h["sembol"]: h["isim"] for h in HALKA_ARZ_LISTESI}
TOPLU_SEMBOL_ISIM = {**SEMBOL_ISIM, **HALKA_ARZ_SEMBOL_ISIM}

# ---------------------------
# CACHE İLE VERİ ÇEKME
# ---------------------------
@st.cache_data(ttl=3600)
def veri_cek(sembol, baslangic, bitis):
    return yf.download(sembol, start=baslangic, end=bitis, progress=False)

# ---------------------------
# HİSSE SEÇİM ARAYÜZÜ
# ---------------------------
def hisse_secim_arayuzu():
    # Halka arz listesi bölümü
    st.subheader("🆕 Yeni Halka Arz Hisseleri")
    with st.expander("Halka arz listesini göster (son 1-2 yıl)"):
        st.write("Listeden seçmek için butona tıklayın:")
        for i in range(0, len(HALKA_ARZ_LISTESI), 4):
            cols = st.columns(4)
            for j in range(4):
                idx = i + j
                if idx < len(HALKA_ARZ_LISTESI):
                    h = HALKA_ARZ_LISTESI[idx]
                    with cols[j]:
                        st.button(
                            f"{h['sembol']} - {h['isim']}",
                            key=f"halka_arz_{h['sembol']}",
                            on_click=lambda s=h['sembol']: st.session_state.update({"secili_sembol": s}),
                            use_container_width=True
                        )

    # Arama kutusu
    arama_metni = st.text_input("Hisse adı veya kodu yazın:", placeholder="Örn: THYAO veya Türk Hava")
    if arama_metni:
        arama_lower = arama_metni.lower()
        oneriler = []
        # BIST 100 listesinden
        for h in HISSE_LISTESI:
            if arama_lower in h["sembol"].lower() or arama_lower in h["isim"].lower():
                oneriler.append(h)
        # Halka arz listesinden
        for h in HALKA_ARZ_LISTESI:
            if arama_lower in h["sembol"].lower() or arama_lower in h["isim"].lower():
                if h not in oneriler:
                    oneriler.append(h)
        # Manuel giriş
        oneriler.insert(0, {"sembol": arama_metni.strip().upper(), "isim": "Manuel giriş"})
        st.write("**Bulunan hisseler:**")
        for i in range(0, len(oneriler), 2):
            cols = st.columns(2)
            for j in range(2):
                idx = i + j
                if idx < len(oneriler):
                    h = oneriler[idx]
                    with cols[j]:
                        st.button(
                            f"{h['sembol']} - {h['isim']}",
                            key=f"arama_sonuc_{h['sembol']}",
                            on_click=lambda s=h['sembol']: st.session_state.update({"secili_sembol": s}),
                            use_container_width=True
                        )
    else:
        st.info("Hisse aramaya başlayın veya halka arz listesinden seçin.")

# ---------------------------
# TÜM HESAPLAMALARI YAPAN FONKSİYON
# ---------------------------
def tahmin_hesapla_ve_sakla(secili, tahmin_tarihi, reg_model, sinif_model):
    baslangic = tahmin_tarihi - timedelta(days=365)
    veri = veri_cek(secili, baslangic, tahmin_tarihi)
    if veri.empty:
        st.error("Hisse bulunamadı.")
        return False

    ind_df = ind_hesapla(veri).dropna()
    if len(ind_df) < 30:  # Halka arz için esnek
        st.error(f"Yeterli veri yok. En az 30 işlem günü gerekli, mevcut: {len(ind_df)}")
        return False

    son_kapanis = ind_df['Close'].iloc[-1]

    tahmin_gun = fiyat_aralik_tahmini(ind_df, son_kapanis, 1)
    tahmin_hafta = fiyat_aralik_tahmini(ind_df, son_kapanis, 5)
    olasilik = hedef_olasilik(veri)
    ml_sonuc = tahmin_araligi(ind_df, model_secimi=reg_model)
    kesişim = kesişim_dedektoru(ind_df)
    yon_tahmin = yon_tahmini(ind_df, model_secimi=sinif_model)
    teknik_puan = teknik_puanlama(ind_df)
    guclu_destek, guclu_direnc = destek_direnc_bul(veri.tail(90))

    st.session_state["tahmin_gun"] = tahmin_gun
    st.session_state["tahmin_hafta"] = tahmin_hafta
    st.session_state["olasilik"] = olasilik
    st.session_state["ml_sonuc"] = ml_sonuc
    st.session_state["ind_df"] = ind_df
    st.session_state["son_kapanis"] = son_kapanis
    st.session_state["veri"] = veri
    st.session_state["kesişim_sonuc"] = kesişim
    st.session_state["yon_tahmin"] = yon_tahmin
    st.session_state["teknik_puan"] = teknik_puan
    st.session_state["destek_direnc"] = (guclu_destek, guclu_direnc)
    return True

# ---------------------------
# ANALİZ SEKMELERİNİ GÖSTER
# ---------------------------
def tum_sekmeleri_goster():
    # (Bu fonksiyonun içeriği öncekiyle aynı; sadece ML sonuçları başlığında model adı gösterilebilir)
    # ... (önceki ui.py'daki ile aynı)
