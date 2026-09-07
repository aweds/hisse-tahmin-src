import streamlit as st
from datetime import datetime, timedelta
from src.ui import (hisse_secim_arayuzu, tahmin_hesapla_ve_sakla,
                    tum_sekmeleri_goster, TOPLU_SEMBOL_ISIM)

st.set_page_config(page_title="Hisse Fiyat Tahmini Pro", layout="wide")
st.title("📈 Hisse Senedi Fiyat Tahmin Uygulaması (Pro)")
st.markdown("8 indikatör + ML (RF, XGBoost, LightGBM, KNN, SVM, Lojistik) + olasılık + Al/Sat + Kesişim + Sağlık + Destek/Direnç + Halka Arz")

if "secili_sembol" not in st.session_state:
    st.session_state.secili_sembol = None

st.subheader("🔍 Hisse Seçimi")
hisse_secim_arayuzu()

if st.session_state.secili_sembol:
    secili = st.session_state.secili_sembol
    isim = TOPLU_SEMBOL_ISIM.get(secili, "Manuel hisse")
    st.success(f"✅ Seçili hisse: **{secili}** – {isim}")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 Farklı hisse seç"):
            for key in list(st.session_state.keys()):
                if key != "secili_sembol":
                    del st.session_state[key]
            st.session_state.secili_sembol = None
            st.rerun()
    with col2:
        tahmin_tarihi = st.date_input("Tahmin tarihi:", value=datetime.today(), max_value=datetime.today())

    def temizle_ml():
        for key in ["ml_sonuc", "yon_tahmin"]:
            st.session_state.pop(key, None)

    st.subheader("🤖 Makine Öğrenmesi Model Seçimi")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        reg_model = st.selectbox("Regresyon Modeli", ["Random Forest", "XGBoost", "LightGBM", "KNN", "SVM"],
                                 key="reg_model_select", on_change=temizle_ml)
    with col_m2:
        sinif_model = st.selectbox("Sınıflandırma Modeli", ["Random Forest", "XGBoost", "LightGBM", "Lojistik Regresyon", "KNN", "SVM"],
                                   key="sinif_model_select", on_change=temizle_ml)

    if st.button("📊 Tahmini Hesapla", type="primary"):
        with st.spinner("Hesaplanıyor..."):
            basarili = tahmin_hesapla_ve_sakla(secili, tahmin_tarihi, st.session_state.reg_model_select, st.session_state.sinif_model_select)
            if basarili:
                st.rerun()

    if "tahmin_gun" in st.session_state:
        tum_sekmeleri_goster()
