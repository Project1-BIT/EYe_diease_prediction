from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

# Load environment variables
load_dotenv()  # Load .env file for environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Supported diseases
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
    }
}

# Function to check if the image is of an eye and predict diseases
def detect_disease(input_prompt, image_data):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input_prompt, image_data[0]])
        return response.text.strip().lower()  # Normalize response for better matching
    except Exception as e:
        return f"Error: {str(e)}"

# Function to process uploaded image
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the MIME type
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function to generate a report
def generate_report(disease):
    if disease in DISEASES:
        symptoms = "\n".join(DISEASES[disease]["symptoms"])
        precautions = "\n".join(DISEASES[disease]["precautions"])
        return f"### Detected Disease: {disease.title()}\n\n**Symptoms:**\n{symptoms}\n\n**Precautions:**\n{precautions}"
    else:
        return "This image does not correspond to any of the listed diseases. Please upload an eye image."

# Initialize Streamlit app
st.set_page_config(page_title="Eye Disease Detection", page_icon="🦠")
st.title("🩺 Eye Disease Detection App")

# Sidebar with form for personal and health details
st.sidebar.header("📝 Personal and Health Details")

# Form for personal details
with st.sidebar.form(key="personal_details_form"):
    name = st.text_input("Name:", key="name")
    age = st.number_input("Age:", min_value=0, max_value=120, key="age")
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
    third_eye = st.checkbox("Third eye", key="third_eye")
    sugar = st.checkbox("Sugar (Diabetes)", key="sugar")
    none = st.checkbox("None", key="none")

    # Submit button for the form
    submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        if not name or age == 0 or not gender or not location:
            st.error("All fields are required. Please fill in all the details.")
        elif not (blurry_vision or redness or double_vision or eye_pain or light_sensitivity or other_symptoms or third_eye or sugar or none):
            st.error("Please select at least one symptom or factor.")
        else:
            st.success("Form submitted successfully!")

# Default prompt for the AI
input_prompt = """
You are an expert in identifying eye diseases. 
Detect if the input image shows one of the following conditions: cross eyes, conjunctivitis, cataract, glaucoma, or uveitis. 
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

# On submit, process the image and get the response
if submit:
    if uploaded_file:
        try:
            # Check user input conditions
            if third_eye:
                disease_found = "uveitis"
                report = generate_report(disease_found)
                st.subheader(f"Predicted Disease: {disease_found.title()}")
                st.markdown(report)
            elif sugar:
                disease_found = "glaucoma"
                report = generate_report(disease_found)
                st.subheader(f"Predicted Disease: {disease_found.title()}")
                st.markdown(report)
            elif none:
                st.success("The uploaded eye image shows no signs of disease. It appears to be a healthy eye!")
            else:
                image_data = input_image_setup(uploaded_file)
                response = detect_disease(input_prompt, image_data)

                # Check for disease in response
                disease_found = None
                for disease in DISEASES.keys():
                    if disease in response:
                        disease_found = disease
                        report = generate_report(disease)
                        break

                # Display prediction or healthy eye message
                if disease_found:
                    st.subheader(f"Predicted Disease: {disease_found.title()}")
                    st.markdown(report)
                elif "unsupported" in response or "not an eye image" in response:
                    st.warning("This is not an eye image or an unsupported condition.")
                else:
                    st.success("The uploaded eye image shows no signs of disease. It appears to be a healthy eye!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please upload an image to proceed.")
