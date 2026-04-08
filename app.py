import streamlit as st
from diagnox import diagnox_chat
import json
import tempfile
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="DiagNoX", page_icon="🩺", layout="wide")

# =========================
# 🎨 UI
# =========================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #020617, #000000);
    color: #e2e8f0;
}
.card {
    background: rgba(255,255,255,0.04);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 15px;
    border: 1px solid rgba(255,255,255,0.08);
}
.alert {
    background: rgba(255,0,0,0.1);
    border: 1px solid red;
    padding: 12px;
    border-radius: 10px;
    animation: blink 1s infinite;
}
@keyframes blink {
    50% { opacity: 0.4; }
}
.ecg {
    height: 80px;
    background: black;
    border-radius: 10px;
    overflow: hidden;
}
.ecg::before {
    content: "";
    width: 200%;
    height: 2px;
    background: #22c55e;
    position: relative;
    top: 50%;
    animation: ecgMove 2s linear infinite;
}
@keyframes ecgMove {
    from { left: -100%; }
    to { left: 100%; }
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("## 🩺 DiagNoX")
st.caption("AI Clinical Decision Support System")

# =========================
# CHAT MEMORY
# =========================
if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# INPUT
# =========================
user_input = st.chat_input("Enter clinical case...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})

    with st.spinner("Analyzing clinical data..."):
        response = diagnox_chat(user_input)

    st.session_state.history.append({"role": "assistant", "content": response})

# =========================
# DISPLAY CHAT
# =========================
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# LAST RESPONSE
# =========================
if st.session_state.history and st.session_state.history[-1]["role"] == "assistant":

    response = st.session_state.history[-1]["content"]

    try:
        parsed = json.loads(response)

        if "error" in parsed:
            st.error(parsed["error"])

        else:
            diagnoses = parsed.get("differential_diagnoses", [])
            if not diagnoses:
                st.warning("No diagnoses returned")
                st.stop()

            top = diagnoses[0]
            prob = int(top["probability"] * 100)

            # =========================
            # 🔥 DYNAMIC VITALS
            # =========================
            vitals = parsed.get("extracted_vitals", {})

            hr = vitals.get("heart_rate", "--")
            bp = vitals.get("blood_pressure", "--")
            spo2 = vitals.get("spo2", "--")

            # =========================
            # 🚨 SMART ALERTS
            # =========================
            if top["urgency"] == "Emergency":
                st.markdown('<div class="alert">⚠️ CRITICAL CONDITION DETECTED</div>', unsafe_allow_html=True)

            if spo2 != "--" and int(spo2) < 90:
                st.markdown('<div class="alert">⚠️ LOW OXYGEN LEVEL</div>', unsafe_allow_html=True)

            if hr != "--" and int(hr) > 120:
                st.markdown('<div class="alert">⚠️ TACHYCARDIA DETECTED</div>', unsafe_allow_html=True)

            # =========================
            # GRID
            # =========================
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="card">
                <h4>Vitals Monitor</h4>
                HR: {hr} bpm<br>
                BP: {bp}<br>
                SpO2: {spo2}%
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="ecg"></div>', unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="card">
                <h4>Top Diagnosis</h4>
                <h3 style="color:#38bdf8;">{top['name']}</h3>
                Likelihood: {top['likelihood']}<br>
                Probability: {prob}%<br>
                Urgency: {top['urgency']}
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="card">
                <h4>Risk Score</h4>
                <h2 style="color:#38bdf8;">{prob}%</h2>
                </div>
                """, unsafe_allow_html=True)

            # =========================
            # 🤖 AI EXPLANATION
            # =========================
            st.markdown("### AI Clinical Explanation")

            with st.expander("View reasoning"):

                st.markdown("#### Supporting Evidence")
                for s in top.get("reasoning", {}).get("supporting", []):
                    st.write(f"✔ {s}")

                if top.get("reasoning", {}).get("contradicting"):
                    st.markdown("#### Contradictions")
                    for c in top["reasoning"]["contradicting"]:
                        st.write(f"✖ {c}")

            # =========================
            # 📊 CONFIDENCE
            # =========================
            st.markdown("### Diagnosis Confidence")

            for dx in diagnoses:
                p = int(dx["probability"] * 100)
                st.progress(p/100)
                st.write(f"{dx['name']} — {p}%")

            # =========================
            # 📋 DETAILS
            # =========================
            st.markdown("### Differential Diagnoses")

            for dx in diagnoses:
                with st.expander(dx["name"]):
                    st.write(f"Likelihood: {dx['likelihood']}")
                    st.write(f"Probability: {int(dx['probability']*100)}%")
                    st.write(f"Urgency: {dx['urgency']}")

                    st.write("Supporting:")
                    for s in dx.get("reasoning", {}).get("supporting", []):
                        st.write(f"- {s}")

            # =========================
            # 📄 PDF
            # =========================
            def generate_pdf(data):
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                doc = SimpleDocTemplate(temp.name)
                styles = getSampleStyleSheet()

                content = []
                content.append(Paragraph("DiagNoX Clinical Report", styles["Title"]))

                for dx in data:
                    content.append(Paragraph(dx["name"], styles["Heading2"]))

                    for s in dx.get("reasoning", {}).get("supporting", []):
                        content.append(Paragraph(f"✔ {s}", styles["Normal"]))

                doc.build(content)
                return temp.name

            pdf_path = generate_pdf(diagnoses)

            with open(pdf_path, "rb") as f:
                st.download_button("Download Report", f)

    except Exception as e:
        st.error(f"Invalid JSON: {e}")