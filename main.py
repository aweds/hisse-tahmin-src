import streamlit as st
from datetime import datetime, timedelta

# Modülerleştirilmiş UI fonksiyonlarını içe aktar
from src.ui import (
    hisse_secim_arayuzu,
    tahmin_hesapla_ve_sakla,
    tum_sekmeleri_goster,
    SEMBOL_ISIM
)

# ---------------------------
# SAYFA YAPILANDIRMASI
# ---------------------------
st.set_page_config(page_title="Hisse Fiyat Tahmini Pro", layout="wide")
st.title("📈 Hisse Senedi Fiyat Tahmin Uygulaması (Pro)")
st.markdown("8 indikatör + ML + olasılık + Al/Sat simülasyonu + Kesişim dedektörü + Yön tahmini + Sağlık Karnesi + Destek/Direnç")

# ---------------------------
# SESSION STATE BAŞLANGIÇ
# ---------------------------
if "secili_sembol" not in st.session_state:
    st.session_state.secili_sembol = None

# ---------------------------
# HİSSE SEÇİMİ
# ---------------------------
st.subheader("🔍 Hisse Seçimi")
hisse_secim_arayuzu() 

# ---------------------------
# SEÇİLİ HİSSE VARSA ANA İŞLEMLER
# ---------------------------
if st.session_state.secili_sembol:
    secili = st.session_state.secili_sembol
    isim = SEMBOL_ISIM.get(secili, "Manuel hisse")
    st.success(f"✅ Seçili hisse: **{secili}** – {isim}")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 Farklı hisse seç"):
            # Tüm analiz sonuçlarını temizle
            for key in list(st.session_state.keys()):
                if key not in ["secili_sembol"]:
                    del st.session_state[key]
            st.session_state.secili_sembol = None
            st.rerun()

    with col2:
        tahmin_tarihi = st.date_input(
            "Tahmin tarihi (dünün verisiyle):",
            value=datetime.today() - timedelta(days=1)
        )
    st.session_state["tahmin_tarihi"] = tahmin_tarihi

    if st.button("📊 Tahmini Hesapla", type="primary"):
        with st.spinner("Hesaplanıyor..."):
            basarili = tahmin_hesapla_ve_sakla(secili, tahmin_tarihi)
            if basarili:
                st.rerun()

    # ---------------------------
    # ANALİZ SONUÇLARI VARSA SEKMELERİ GÖSTER
    # ---------------------------
    if "tahmin_gun" in st.session_state:
        tum_sekmeleri_goster()
