import os
import uuid
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("AIzaSyDHTP7a2bBOPBJtgSHO8J2DnwPA1wx0I0s"))
#demo :AIzaSyAtdPFpb2ZFWibkbvHTuLvHxRclmTGw5qg
#AIzaSyDHTP7a2bBOPBJtgSHO8J2DnwPA1wx0I0s

# Supported diseasesstreamlit run app.py
DISEASES = {
    "cross eyes": {
        "symptoms": ["Misalignment of the eyes", "Double vision", "Poor depth perception"],
        "precautions": ["Consult an ophthalmologist", "Vision therapy", "Corrective surgery if needed"]
    },
    "conjunctivitis": {
        "symptoms": ["Redness in the eye", "Itching or burning sensation", "Discharge from the eye"],
        "precautions": ["Avoid touching eyes", "Use prescribed eye drops", "Maintain proper hygiene"]
    },
    "cataract": {
        "symptoms": ["Blurred or cloudy vision", "Sensitivity to light", "Difficulty seeing at night"],
        "precautions": ["Wear UV-protected sunglasses", "Regular eye check-ups", "Surgery if recommended"]
    },
    "glaucoma": {
        "symptoms": ["Loss of peripheral vision", "Severe eye pain", "Halos around lights"],
        "precautions": ["Regular eye pressure checks", "Avoid smoking", "Healthy diet rich in antioxidants"]
    },
    "uveitis": {
        "symptoms": ["Eye redness", "Pain and sensitivity to light", "Blurred vision"],
        "precautions": ["Seek immediate medical attention", "Use prescribed anti-inflammatory medications", "Avoid eye strain"]
    },
    "bulging eyes": {
        "symptoms": ["Protruding eyeball", "Eye pain", "Dry eyes", "Double vision", "Thyroid-related symptoms"],
        "precautions": ["Consult an endocrinologist", "Protect eyes from injury", "Regular thyroid function tests", "Use artificial tears"]
    }
}

def generate_pdf_report(user_details, disease_detected, image):
    pdf_filename = f"eye_disease_report_{uuid.uuid4()}.pdf"
    
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    
    # Add title
    pdf.set_font_size(16)
    pdf.cell(200, 10, 'Eye Disease Detection Medical Report', ln=True, align='C')
    pdf.ln(10)
    
    # User details
    pdf.set_font_size(14)
    pdf.cell(0, 10, 'Patient Information', ln=True)
    pdf.set_font_size(12)
    for key, value in user_details.items():
        pdf.cell(0, 10, f"{key}: {value}", ln=True)
    pdf.ln(5)
    
    # Disease details
    if disease_detected in DISEASES:
        pdf.set_font_size(14)
        pdf.cell(0, 10, 'Diagnosis Details', ln=True)
        pdf.set_font_size(12)
        
        # Disease Name
        pdf.cell(0, 10, f"Detected Condition: {disease_detected.title()}", ln=True)
        
        # Symptoms
        pdf.ln(5)
        pdf.cell(0, 10, 'Key Symptoms:', ln=True)
        for symptom in DISEASES[disease_detected]["symptoms"]:
            pdf.cell(0, 10, f"- {symptom}", ln=True)
        
        # Precautions
        pdf.ln(5)
        pdf.cell(0, 10, 'Recommended Precautions:', ln=True)
        for precaution in DISEASES[disease_detected]["precautions"]:
            pdf.cell(0, 10, f"- {precaution}", ln=True)
        
        # Medical Advice
        pdf.ln(5)
        pdf.cell(0, 10, 'Medical Recommendation:', ln=True)
        pdf.multi_cell(0, 10, f"It is crucial to consult an ophthalmologist for a comprehensive examination and personalized treatment plan for {disease_detected}.")
    else:
        pdf.cell(0, 10, 'No specific eye disease detected', ln=True)
        pdf.multi_cell(0, 10, 'While no specific condition was identified, regular eye check-ups are recommended for maintaining optimal eye health.')
    
    # Add image
    pdf.ln(10)
    if image:
        image_path = f"uploaded_image_{uuid.uuid4()}.png"
        image.save(image_path)
        pdf.image(image_path, x=10, y=pdf.get_y(), w=100)
    
    # Save to file
    pdf.output(pdf_filename)
    return pdf_filename

def detect_disease(input_prompt, image_data):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input_prompt, image_data[0]])
        return response.text.strip().lower()
    except Exception as e:
        return f"Error: {str(e)}"

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit App Configuration
st.set_page_config(page_title="Eye Disease Detection", page_icon="🦠")
st.title("🩺 Eye Disease Detection App")

# Sidebar with form for personal and health details
st.sidebar.header("📝 Personal and Health Details")

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Personal Details Form
with st.sidebar.form(key="personal_details_form"):
    name = st.text_input("Name:", key="name")
    age = st.number_input("Age:", min_value=0, max_value=90, key="age")
    gender = st.selectbox("Gender:", ["Male", "Female", "Other"], key="gender")
    location = st.text_input("Location:", key="location")
    
    # Symptoms
    st.subheader("Current Eye Symptoms")
    blurry_vision = st.checkbox("Blurry vision", key="blurry_vision")
    redness = st.checkbox("Redness", key="redness")
    double_vision = st.checkbox("Double vision", key="double_vision")
    eye_pain = st.checkbox("Eye pain", key="eye_pain")
    light_sensitivity = st.checkbox("Light sensitivity", key="light_sensitivity")
    other_symptoms = st.text_input("Other (if any):", key="other_symptoms")
    
    # Specific conditions
    st.subheader("Additional Factors")
    sugar = st.checkbox("Sugar (Diabetes)", key="sugar")
    none = st.checkbox("None", key="none")
    
    # Submit button for the form
    submit_button = st.form_submit_button(label="Submit")
    
    if submit_button:
        if not name or age == 0 or not gender or not location:
            st.error("All fields are required. Please fill in all the details.")
        else:
            st.session_state.submitted = True
            st.success("Form submitted successfully!")

# AI Prompt for Disease Detection
input_prompt = """
You are an expert in identifying eye diseases. 
Detect if the input image shows one of these conditions: 
cross eyes, conjunctivitis, cataract, glaucoma, uveitis, or bulging eyes. 
For bulging eyes, look for protrusion of one or both eyeballs, potential thyroid-related signs, and surrounding tissue swelling.
If it is not an eye image or if the disease is not listed, respond with "This is not an eye image or an unsupported condition."
"""

# File uploader for images
uploaded_file = st.file_uploader("Upload an eye image...", type=["jpg", "jpeg", "png"])

# Display uploaded image
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

# Submit button for analyzing the image
submit = st.button("Analyze Image")

# Image Analysis and Report Generation
if submit:
    if not st.session_state.submitted:
        st.error("Please fill out the personal details form first.")
    elif uploaded_file:
        try:
            # Prepare user details
            user_details = {
                "Name": name,
                "Age": age,
                "Gender": gender,
                "Location": location,
                "Symptoms": ", ".join([
                    symptom for symptom, selected in zip(
                        ["Blurry vision", "Redness", "Double vision", "Eye pain", "Light sensitivity"],
                        [blurry_vision, redness, double_vision, eye_pain, light_sensitivity]
                    ) if selected
                ]) or "None",
                "Additional Factors": "Sugar" if sugar else "None"
            }
            
            # Check user input conditions
            if sugar:
                disease_found = "glaucoma"
            elif none:
                disease_found = None
            else:
                image_data = input_image_setup(uploaded_file)
                response = detect_disease(input_prompt, image_data)
                disease_found = next((disease for disease in DISEASES if disease in response), None)
            
            # Generate report
            pdf_buffer = generate_pdf_report(user_details, disease_found, image)
            
            # Provide download link
            with open(pdf_buffer, 'rb') as pdf_file:
                st.download_button(
                    label="Download Report",
                    data=pdf_file,
                    file_name="Eye_Disease_Report.pdf",
                    mime="application/pdf"
                )
            
            if disease_found:
                st.success(f"Predicted Disease: {disease_found.title()} detected!")
            else:
                st.success("The uploaded eye image shows  Healthy Eye")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please upload an image to proceed.")
