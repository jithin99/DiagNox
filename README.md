# DiagNoX

## Overview
DiagNoX is an AI-powered clinical decision support system designed to assist healthcare professionals in analyzing patient data and generating differential diagnoses. The system leverages a large language model to interpret clinical inputs and provide structured outputs including reasoning, risk assessment, and recommended next steps.

---

## Features
- Generates differential diagnoses based on clinical input  
- Provides supporting and contradicting clinical reasoning  
- Identifies potential red flag conditions  
- Displays confidence scores for each diagnosis  
- Extracts and visualizes patient vitals  
- Generates downloadable clinical reports in PDF format  
- Interactive and modern user interface  

---

## Technology Stack
- Frontend: Streamlit  
- Backend: Python  
- Model Runtime: Ollama  
- Language Model: Llama 3  
- Libraries: Requests, JSON, ReportLab  

---

## System Workflow
1. User enters clinical case details  
2. Input is preprocessed and structured  
3. Prompt is generated and sent to the model  
4. Model returns structured JSON output  
5. Response is parsed and validated  
6. Results are displayed in an interactive UI  
7. Clinical report is generated for download  

---

## AI Capabilities
- Interprets unstructured clinical text  
- Performs pattern-based reasoning  
- Generates explainable outputs with justification  
- Maintains structured and consistent responses  

---

## Output Structure
The system produces structured outputs including:
- Differential diagnoses  
- Probability and urgency levels  
- Supporting and contradicting findings  
- Clinical justification  
- Recommended next steps  
- Confidence score  

---

## Challenges Addressed
- Ensured consistent JSON output through prompt engineering  
- Implemented robust parsing and error handling  
- Optimized response time for complex inputs  
- Improved UI for better clinical usability  
- Integrated reasoning for explainable AI  

---

## Future Enhancements
- Integration with real-time clinical databases  
- Advanced risk scoring models  
- Improved accuracy using fine-tuned medical datasets  
- Deployment on cloud for wider accessibility  

## Disclaimer
This system is intended for educational and assistive purposes only. It does not replace professional medical diagnosis or clinical judgment.

---
## Some Example Ui images 

<img width="1680" height="1050" alt="image" src="https://github.com/user-attachments/assets/2e56c02b-7378-4a53-b978-d7479060c825" />
<img width="1680" height="298" alt="image" src="https://github.com/user-attachments/assets/d22a769e-93c7-4723-a864-af6ed6f878db" />
<img width="1680" height="1050" alt="image" src="https://github.com/user-attachments/assets/9dedac33-24ec-4a98-bb0f-068c298a8812" />
<img width="1680" height="1050" alt="image" src="https://github.com/user-attachments/assets/806635b1-0be0-48c7-bc92-733608f0508c" />
<img width="764" height="1062" alt="image" src="https://github.com/user-attachments/assets/3e802187-17dd-45ca-ab01-c533c831d1ec" />
<img width="1680" height="1050" alt="image" src="https://github.com/user-attachments/assets/cbfc4a1f-2ec6-447a-bef5-b542be7f5f0e" />








