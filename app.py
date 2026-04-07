import streamlit as st
from diagnox import diagnox_chat
import json
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="DiagNoX", page_icon="🩺", layout="wide")

# =========================
# 🎨 PREMIUM UI
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a, #1e293b);
    color: #e2e8f0;
}

.card {
    padding: 18px;
    border-radius: 12px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 15px;
}

.header {
    font-size: 32px;
    font-weight: 700;
}

.sub {
    color: #94a3b8;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown('<div class="header">🩺 DiagNoX</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Clinical Decision Support System</div>', unsafe_allow_html=True)
st.markdown("---")

# =========================
# CHAT MEMORY
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# DISPLAY CHAT HISTORY
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# INPUT
# =========================
user_input = st.chat_input("Enter clinical case...")

if user_input:

    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # Call model
    with st.spinner("Analyzing clinical data..."):
        response = diagnox_chat(user_input)

    # Save response
    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):

        try:
            parsed = json.loads(response)

            if "error" in parsed:
                st.error(parsed["error"])

            else:

                diagnoses = parsed.get("differential_diagnoses", [])

                # =========================
                # 📊 TABS
                # =========================
                tab1, tab2, tab3, tab4 = st.tabs(
                    ["Overview", "Vitals", "Labs", "Reasoning"]
                )

                # =========================
                # 🧠 OVERVIEW
                # =========================
                with tab1:
                    top = diagnoses[0]
                    prob = int(top["probability"] * 100)

                    st.markdown(f"""
<div class="card">
<b>Top Diagnosis:</b> {top['name']}<br>
Likelihood: {top['likelihood']}<br>
Probability: {prob}%<br>
Urgency: {top['urgency']}
</div>
""", unsafe_allow_html=True)

                    # Chart
                    names = [d["name"] for d in diagnoses]
                    probs = [int(d["probability"] * 100) for d in diagnoses]

                    fig, ax = plt.subplots()
                    ax.barh(names, probs)
                    ax.set_xlabel("Probability (%)")
                    ax.set_title("Diagnosis Confidence")
                    st.pyplot(fig)

                # =========================
                # ❤️ VITALS TAB
                # =========================
                with tab2:
                    st.write("Vitals / Features")
                    st.json(parsed.get("normalized_features", []))

                # =========================
                # 🧪 LABS TAB
                # =========================
                with tab3:
                    st.write("Lab Analysis")
                    st.json(parsed.get("normalized_features", []))

                # =========================
                # 🧠 REASONING TAB
                # =========================
                with tab4:
                    for dx in diagnoses:
                        st.markdown(f"### {dx['name']}")

                        st.markdown("**Supporting Findings:**")
                        for s in dx.get("reasoning", {}).get("supporting", []):
                            st.write(f"• {s}")

                        st.markdown("**Contradicting Findings:**")
                        for c in dx.get("reasoning", {}).get("contradicting", []):
                            st.write(f"• {c}")

                        st.markdown("---")

                # =========================
                # 📄 PDF GENERATION (FIXED)
                # =========================
                def generate_pdf(data):
                    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    doc = SimpleDocTemplate(temp.name)
                    styles = getSampleStyleSheet()

                    content = []

                    # Title
                    content.append(Paragraph("DiagNoX Clinical Report", styles["Title"]))
                    content.append(Paragraph("<br/>", styles["Normal"]))

                    for dx in data:

                        name = dx.get("name", "")
                        likelihood = dx.get("likelihood", "")
                        prob = int(dx.get("probability", 0) * 100)
                        urgency = dx.get("urgency", "")

                        reasoning = dx.get("reasoning", {})
                        supporting = reasoning.get("supporting", [])
                        contradicting = reasoning.get("contradicting", [])

                        # Diagnosis Title
                        content.append(Paragraph(f"<b>{name}</b>", styles["Heading2"]))

                        # Meta Info
                        content.append(Paragraph(
                            f"Likelihood: {likelihood} | Probability: {prob}% | Urgency: {urgency}",
                            styles["Normal"]
                        ))

                        content.append(Paragraph("<br/>", styles["Normal"]))

                        # Supporting
                        if supporting:
                            content.append(Paragraph("<b>Supporting Findings:</b>", styles["Normal"]))
                            for s in supporting:
                                content.append(Paragraph(f"- {s}", styles["Normal"]))

                        # Contradicting
                        if contradicting:
                            content.append(Paragraph("<b>Contradicting Findings:</b>", styles["Normal"]))
                            for c in contradicting:
                                content.append(Paragraph(f"- {c}", styles["Normal"]))

                        content.append(Paragraph("<br/><br/>", styles["Normal"]))

                    doc.build(content)

                    return temp.name

                # Generate PDF
                pdf_path = generate_pdf(diagnoses)

                # Download button
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "Download Clinical Report",
                        f,
                        file_name="diagnox_report.pdf"
                    )

        except Exception as e:
            st.error("Invalid JSON format from model")
            st.markdown(response)