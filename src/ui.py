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
# YENİ HALKA ARZ HİSSELERİ (2024-2025 bilinenler)
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
# ÖZEL HİSSE LİSTESİ ARAYÜZÜ
# ---------------------------
def ozel_liste_arayuzu():
    st.subheader("📝 Özel Hisse Listeniz")
    st.write("Aşağıya hisse sembollerini girin (her satıra bir tane veya virgülle ayırın).")
    kullanici_girdisi = st.text_area(
        "Sembol listesi",
        placeholder="THYAO.IS\nGARAN.IS\nASELS.IS\n...",
        height=150,
        key="ozel_liste_text"
    )

    if kullanici_girdisi:
        semboller = []
        for satir in kullanici_girdisi.splitlines():
            satir = satir.strip()
            if satir:
                for s in satir.split(','):
                    s = s.strip().upper()
                    if s and s not in semboller:
                        semboller.append(s)

        if semboller:
            st.success(f"✅ {len(semboller)} hisse eklendi.")
            st.session_state["ozel_liste"] = semboller

            st.write("**Özel listenizdeki hisseler:**")
            for i in range(0, len(semboller), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    if idx < len(semboller):
                        sembol = semboller[idx]
                        with cols[j]:
                            st.button(
                                f"{sembol}",
                                key=f"ozel_{sembol}",
                                on_click=lambda s=sembol: st.session_state.update({"secili_sembol": s}),
                                use_container_width=True
                            )
        else:
            st.info("Henüz bir sembol girilmedi.")
    else:
        st.info("Yukarıya hisse sembollerini yazın.")

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
        for h in HISSE_LISTESI:
            if arama_lower in h["sembol"].lower() or arama_lower in h["isim"].lower():
                oneriler.append(h)
        for h in HALKA_ARZ_LISTESI:
            if arama_lower in h["sembol"].lower() or arama_lower in h["isim"].lower():
                if h not in oneriler:
                    oneriler.append(h)
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

    # Özel liste bölümünü göster
    st.markdown("---")
    ozel_liste_arayuzu()

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
    if len(ind_df) < 30:
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
    tahmin_gun = st.session_state["tahmin_gun"]
    tahmin_hafta = st.session_state["tahmin_hafta"]
    olasilik = st.session_state["olasilik"]
    ml_sonuc = st.session_state["ml_sonuc"]
    ind_df = st.session_state["ind_df"]
    son_kapanis = st.session_state["son_kapanis"]
    veri = st.session_state["veri"]
    kesişim = st.session_state.get("kesişim_sonuc", None)
    yon_tahmin = st.session_state.get("yon_tahmin", None)
    teknik_puan = st.session_state.get("teknik_puan", None)
    guclu_destek, guclu_direnc = st.session_state.get("destek_direnc", ([], []))

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Tahmin Sonuçları",
        "📈 İleri Analiz",
        "📊 İndikatörler",
        "📉 Strateji Simülasyonu",
        "🏥 Sağlık Karnesi"
    ])

    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("📊 Son Kapanış")
            st.metric("Fiyat", f"{son_kapanis:.2f} TL")
        with col2:
            st.subheader("🔮 1 Gün Sonrası")
            st.markdown(f"**Yön:** {tahmin_gun['yon']} (Güven: %{tahmin_gun['guven_skoru']:.0f})")
            st.metric("Aralık", f"{tahmin_gun['dusuk']} - {tahmin_gun['yuksek']}")
        with col3:
            st.subheader("🗓️ 1 Hafta Sonrası")
            st.markdown(f"**Yön:** {tahmin_hafta['yon']} (Güven: %{tahmin_hafta['guven_skoru']:.0f})")
            st.metric("Aralık", f"{tahmin_hafta['dusuk']} - {tahmin_hafta['yuksek']}")

        st.subheader("📅 Haftalık Bant Geçmişi ve Tahmin")
        df_haftalik = veri['Close'].resample('W').ohlc().dropna().tail(10)
        fig = go.Figure()
        for i, row in df_haftalik.iterrows():
            fig.add_trace(go.Scatter(x=[i, i], y=[row['low'], row['high']],
                                     mode='lines', line=dict(color='gray', width=2), showlegend=False))
        gelecek = df_haftalik.index[-1] + pd.Timedelta(weeks=1)
        fig.add_trace(go.Scatter(x=[gelecek, gelecek],
                                 y=[tahmin_hafta['dusuk'], tahmin_hafta['yuksek']],
                                 mode='lines+markers', line=dict(color='orange', width=4, dash='dash'),
                                 name='Tahmin'))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("🎯 Koşullu Olasılık Analizi")
        st.metric(f"50 Günlük Ort. Üstünde İken 5 Gün Sonra %5 Yükseliş Olasılığı",
                  f"%{olasilik:.1f}")

        if ml_sonuc:
            st.subheader("🤖 ML 5 Günlük Güven Aralığı")
            st.metric("Tahmini Fiyat", f"{ml_sonuc['tahmini_fiyat']} TL")
            st.write(f"**Alt sınır:** {ml_sonuc['alt_fiyat']} TL / **Üst sınır:** {ml_sonuc['ust_fiyat']} TL")
        else:
            st.warning("ML güven aralığı için yeterli veri yok.")

        st.subheader("🧠 Yön Tahmini Modeli")
        if yon_tahmin is None:
            st.warning("Yön tahmini için yeterli veri yok (en az 200 gün).")
        else:
            col_yt1, col_yt2 = st.columns(2)
            with col_yt1:
                st.metric("Test Doğruluğu", f"%{yon_tahmin['dogruluk']}")
                st.caption(f"Test verisi: son {yon_tahmin['test_boyutu']} işlem günü")
            with col_yt2:
                st.metric("5 Günlük Yön Tahmini", yon_tahmin['son_tahmin'])

        st.subheader("⚡ Hareketli Ortalama Kesişim Dedektörü")
        if kesişim is None:
            st.warning("Kesişim analizi için yeterli veri yok.")
        elif kesişim['tip'] == 'none':
            st.info("Yakın zamanda bir kesişim beklenmiyor.")
        elif kesişim['tip'] == 'Belirsiz':
            st.info("Kesişim yönü belirsiz, ancak ortalamalar birbirine yaklaşıyor olabilir.")
        else:
            if kesişim['tip'] == 'Golden Cross':
                st.success(f"🔔 **{kesişim['tip']}** yaklaşıyor! Tahmini {kesişim['gun']} işlem günü içinde.")
            elif kesişim['tip'] == 'Death Cross':
                st.error(f"⚠️ **{kesişim['tip']}** yaklaşıyor! Tahmini {kesişim['gun']} işlem günü içinde.")
            st.caption(f"Son fark (SMA50 - SMA200): {kesişim['son_fark']:.4f}")

        st.subheader("📊 Basit Hacim Profili (Son 90 Gün)")
        son_veri = veri.tail(90)
        fiyat_aralik = np.linspace(son_veri['Low'].min(), son_veri['High'].max(), 15)
        hacimler = []
        for i in range(len(fiyat_aralik)-1):
            alt, ust = fiyat_aralik[i], fiyat_aralik[i+1]
            hacimler.append(son_veri[(son_veri['Close'] >= alt) & (son_veri['Close'] < ust)]['Volume'].sum())
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=hacimler, y=[(fiyat_aralik[i]+fiyat_aralik[i+1])/2 for i in range(len(hacimler))],
                             orientation='h', marker=dict(color='blue', opacity=0.5)))
        fig2.update_layout(xaxis_title="Hacim", yaxis_title="Fiyat", height=400)
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("🏗️ Otomatik Destek/Direnç Seviyeleri")
        if not guclu_destek and not guclu_direnc:
            st.info("Son 90 günde yeterli pivot noktası bulunamadı.")
        else:
            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(x=veri.index[-90:], y=veri['Close'].iloc[-90:], name='Kapanış'))
            for destek in guclu_destek:
                fig_dd.add_hline(y=destek['fiyat'], line=dict(color='green', width=2, dash='dot'),
                                 annotation_text=f"Destek ({destek['sayi']})")
            for direnc in guclu_direnc:
                fig_dd.add_hline(y=direnc['fiyat'], line=dict(color='red', width=2, dash='dot'),
                                 annotation_text=f"Direnç ({direnc['sayi']})")
            fig_dd.update_layout(height=500)
            st.plotly_chart(fig_dd, use_container_width=True)
            if guclu_destek:
                en_yakin_destek = min(guclu_destek, key=lambda x: abs(x['fiyat'] - son_kapanis))
                st.write(f"🟢 En yakın güçlü destek: **{en_yakin_destek['fiyat']:.2f}** TL ({en_yakin_destek['sayi']} dokunuş)")
            if guclu_direnc:
                en_yakin_direnc = min(guclu_direnc, key=lambda x: abs(x['fiyat'] - son_kapanis))
                st.write(f"🔴 En yakın güçlü direnç: **{en_yakin_direnc['fiyat']:.2f}** TL ({en_yakin_direnc['sayi']} dokunuş)")

    with tab3:
        st.subheader("📋 Tüm İndikatör Değerleri")
        ind_son = ind_df.iloc[-1]
        tablo = pd.DataFrame({
            'İndikatör': ['SMA 50', 'SMA 200', 'MACD', 'MACD Sinyal', 'RSI', 'Bollinger Üst',
                          'Bollinger Alt', 'ATR', 'OBV', 'Stokastik %K', 'Stokastik %D', 'ADX'],
            'Son Değer': [round(ind_son['SMA_50'],2), round(ind_son['SMA_200'],2),
                          round(ind_son['MACD'],2), round(ind_son['MACD_Sinyal'],2),
                          round(ind_son['RSI'],2), round(ind_son['Bollinger_Ust'],2),
                          round(ind_son['Bollinger_Alt'],2), round(ind_son['ATR'],2),
                          round(ind_son['OBV'],2), round(ind_son['Stokastik_K'],2),
                          round(ind_son['Stokastik_D'],2), round(ind_son['ADX'],2)]
        })
        st.table(tablo)
        st.subheader("📈 Bollinger Bantları")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=ind_df.index, y=ind_df['Close'], name='Kapanış'))
        fig3.add_trace(go.Scatter(x=ind_df.index, y=ind_df['Bollinger_Ust'], line=dict(dash='dash'), name='Üst'))
        fig3.add_trace(go.Scatter(x=ind_df.index, y=ind_df['Bollinger_Alt'], line=dict(dash='dash'), name='Alt'))
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)

    with tab4:
        st.subheader("📉 MACD + RSI Al/Sat Simülasyonu (Geçmiş Veri)")
        if st.button("🔄 Simülasyonu Çalıştır", key="sim_run"):
            with st.spinner("Simülasyon yapılıyor..."):
                try:
                    sim_tarih = st.session_state.get("tahmin_tarihi", datetime.today() - timedelta(days=1))
                    baslangic_sim = sim_tarih - timedelta(days=3*365)
                    secili = st.session_state["secili_sembol"]
                    veri_sim = veri_cek(secili, baslangic_sim, sim_tarih)
                    if veri_sim.empty:
                        st.error("Simülasyon için yeterli veri yok.")
                    else:
                        ind_sim = ind_hesapla(veri_sim).dropna()
                        islemler, metrikler = strateji_simulasyonu(ind_sim)
                        st.session_state["sim_islemler"] = islemler
                        st.session_state["sim_metrikler"] = metrikler
                        st.session_state["sim_ind_sim"] = ind_sim
                        st.rerun()
                except Exception as e:
                    st.error(f"Simülasyon hatası: {e}")

        if "sim_metrikler" in st.session_state and st.session_state["sim_metrikler"]:
            metrikler = st.session_state["sim_metrikler"]
            islemler = st.session_state["sim_islemler"]
            st.success("Simülasyon tamamlandı!")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Toplam Getiri", f"%{metrikler['Toplam Getiri (%)']}")
            with col2:
                st.metric("İşlem Sayısı", metrikler['İşlem Sayısı'])
            with col3:
                st.metric("Kazanma Oranı", f"%{metrikler['Kazanma Oranı (%)']}")
            with col4:
                st.metric("Maks. Drawdown", f"%{metrikler['Maksimum Drawdown (%)']}")

            if islemler and "sim_ind_sim" in st.session_state:
                ind_sim = st.session_state["sim_ind_sim"]
                fig_sim = go.Figure()
                fig_sim.add_trace(go.Scatter(x=ind_sim.index, y=ind_sim['Close'], name='Kapanış'))
                al_noktalari = [i for i in islemler if i['Tip'] == 'AL']
                sat_noktalari = [i for i in islemler if i['Tip'] == 'SAT']
                fig_sim.add_trace(go.Scatter(
                    x=[i['Tarih'] for i in al_noktalari],
                    y=[i['Fiyat'] for i in al_noktalari],
                    mode='markers', marker=dict(color='green', size=10, symbol='triangle-up'),
                    name='AL'))
                fig_sim.add_trace(go.Scatter(
                    x=[i['Tarih'] for i in sat_noktalari],
                    y=[i['Fiyat'] for i in sat_noktalari],
                    mode='markers', marker=dict(color='red', size=10, symbol='triangle-down'),
                    name='SAT'))
                fig_sim.update_layout(height=500)
                st.plotly_chart(fig_sim, use_container_width=True)

                st.subheader("İşlem Geçmişi")
                islem_df = pd.DataFrame(islemler)
                st.dataframe(islem_df, use_container_width=True)

    with tab5:
        st.subheader("🏥 Teknik Sağlık Karnesi (0-10 Puan)")
        if teknik_puan is None:
            st.warning("Henüz bir analiz yapılmadı.")
        else:
            genel = teknik_puan['genel']
            st.markdown(f"### Genel Teknik Puan: **{genel} / 10**")
            st.progress(genel / 10)

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown("**Trend Puanı**")
                st.progress(teknik_puan['trend'] / 10)
                st.write(f"{teknik_puan['trend']}/10")

                st.markdown("**Momentum Puanı**")
                st.progress(teknik_puan['momentum'] / 10)
                st.write(f"{teknik_puan['momentum']}/10")
            with col_p2:
                st.markdown("**Volatilite/Destek-Direnç Puanı**")
                st.progress(teknik_puan['volatilite'] / 10)
                st.write(f"{teknik_puan['volatilite']}/10")

                st.markdown("**Hacim Puanı**")
                st.progress(teknik_puan['hacim'] / 10)
                st.write(f"{teknik_puan['hacim']}/10")

            st.caption("Puanlama: 0-3 Zayıf, 4-6 Orta, 7-10 Güçlü")
