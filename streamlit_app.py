import streamlit as st
import requests
from datetime import datetime

# Page config
st.set_page_config(
    page_title="FarmSense",
    page_icon="🌾",
    layout="wide"
)

# Language translations
TRANSLATIONS = {
    "English": {
        "title": "🌾 FarmSense — Crop Advisor",
        "subtitle": "Smart crop recommendations using ML + real-time weather",
        "location": "Your Location (City Name)",
        "nitrogen": "Nitrogen (N)",
        "phosphorus": "Phosphorus (P)",
        "potassium": "Potassium (K)",
        "ph": "Soil pH",
        "predict": "Get Recommendation",
        "loading": "Fetching live weather + running model...",
        "result_title": "Recommended Crop",
        "confidence": "Model Confidence",
        "disease_risk": "Disease Risk",
        "weather_title": "Live Weather Used",
        "temp": "Temperature",
        "humidity": "Humidity",
        "rainfall": "Rainfall",
        "recent": "Recent Predictions",
    },
    "हिंदी": {
        "title": "🌾 फार्मसेंस — फसल सलाहकार",
        "subtitle": "ML + लाइव मौसम का उपयोग करके स्मार्ट फसल सिफारिशें",
        "location": "आपका स्थान (शहर का नाम)",
        "nitrogen": "नाइट्रोजन (N)",
        "phosphorus": "फास्फोरस (P)",
        "potassium": "पोटेशियम (K)",
        "ph": "मिट्टी का pH",
        "predict": "सिफारिश प्राप्त करें",
        "loading": "लाइव मौसम + मॉडल चल रहा है...",
        "result_title": "अनुशंसित फसल",
        "confidence": "मॉडल विश्वास",
        "disease_risk": "रोग जोखिम",
        "weather_title": "उपयोग किया गया मौसम",
        "temp": "तापमान",
        "humidity": "नमी",
        "rainfall": "वर्षा",
        "recent": "हाल की भविष्यवाणियां",
    }
}

# API URL — local for now, will change to Render URL after deploy
API_URL = "https://farmsense-api-oj7k.onrender.com/api"

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/emoji/96/seedling.png", width=60)
    st.markdown("### FarmSense")
    lang = st.selectbox("Language / भाषा", ["English", "हिंदी"])
    T = TRANSLATIONS[lang]
    st.markdown("---")
    st.markdown("**About**")
    st.markdown("FarmSense uses a RandomForest ML model trained on 2,200 crop samples with 99.5% accuracy.")
    st.markdown("---")
    st.markdown(
        f'<span style="color:#2d6a4f;font-size:12px">🟢 Live weather data · {datetime.now().strftime("%d %b %Y, %H:%M")}</span>',
        unsafe_allow_html=True
    )

# Main header
st.title(T["title"])
st.markdown(T["subtitle"])
st.markdown("---")

# Input form
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📍 Location & Soil")
    location = st.text_input(T["location"], value="Mumbai")
    N = st.slider(T["nitrogen"], min_value=0, max_value=140, value=50,
                  help="Nitrogen content in soil (kg/ha)")
    P = st.slider(T["phosphorus"], min_value=5, max_value=145, value=40,
                  help="Phosphorus content in soil (kg/ha)")

with col2:
    st.markdown("#### 🌱 Soil Properties")
    K = st.slider(T["potassium"], min_value=5, max_value=205, value=40,
                  help="Potassium content in soil (kg/ha)")
    ph = st.slider(T["ph"], min_value=3.5, max_value=9.5, value=6.5, step=0.1,
                   help="pH value of soil (3.5 = acidic, 9.5 = alkaline)")

st.markdown("---")

# Predict button
if st.button(T["predict"], type="primary", use_container_width=True):
    with st.spinner(T["loading"]):
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json={"location": location, "N": N, "P": P, "K": K, "ph": ph},
                timeout=10
            )
            result = response.json()

            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                # Results
                st.markdown("---")
                st.markdown("### ✅ Results")

                res_col1, res_col2, res_col3 = st.columns(3)

                with res_col1:
                    st.metric(
                        label=T["result_title"],
                        value=result["recommended_crop"].upper()
                    )

                with res_col2:
                    st.metric(
                        label=T["confidence"],
                        value=f"{result['confidence']}%"
                    )

                with res_col3:
                    risk = result["disease_risk"]["risk_level"]
                    risk_icon = "🔴" if risk == "High" else "🟡" if risk == "Medium" else "🟢"
                    st.metric(
                        label=T["disease_risk"],
                        value=f"{risk_icon} {risk}"
                    )

                # Weather used
                st.markdown(f"#### 🌤️ {T['weather_title']}")
                w = result["weather_used"]
                w_col1, w_col2, w_col3, w_col4 = st.columns(4)
                w_col1.metric(T["temp"], f"{w['temperature']}°C")
                w_col2.metric(T["humidity"], f"{w['humidity']}%")
                w_col3.metric(T["rainfall"], f"{w['rainfall']} mm")
                w_col4.metric("Conditions", w["weather_description"].title())

                # Cache info
                if w.get("cache_hit"):
                    st.caption("⚡ Weather data served from cache (< 1ms)")
                else:
                    st.caption(f"🌐 Live weather fetched in {result['response_ms']}ms")

                # Active diseases warning
                if result["disease_risk"]["active_diseases"]:
                    st.warning(
                        f"⚠️ Watch out for: {', '.join(result['disease_risk']['active_diseases'])}"
                    )

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API. Make sure Flask is running on port 5000.")
        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")

# Recent predictions
st.markdown("---")
st.markdown(f"### 📊 {T['recent']}")
try:
    logs_response = requests.get(f"{API_URL}/recent-requests", timeout=5)
    logs = logs_response.json().get("requests", [])
    if logs:
        import pandas as pd
        df_logs = pd.DataFrame(logs)
        df_logs = df_logs[["timestamp", "location", "prediction", "confidence", "disease_risk", "response_ms"]]
        df_logs.columns = ["Time", "Location", "Crop", "Confidence %", "Disease Risk", "Response ms"]
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.caption("No predictions yet — make your first one above!")
except Exception:
    st.caption("Recent predictions will appear here after your first query.")