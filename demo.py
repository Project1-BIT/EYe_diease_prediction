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
        return f"Detected Disease: {disease.title()}\n\n**Symptoms:**\n{symptoms}\n\n**Precautions:**\n{precautions}"
    else:
        return "This image does not correspond to any of the listed diseases. Please upload an eye image."

# Function to extract and display image details
def get_image_details(image):
    # This can be expanded with more complex analysis or just a more detailed description
    description = """
    This is a detailed image analysis of the uploaded eye image. The image contains key characteristics that could help identify various eye diseases, including but not limited to, cross eyes, conjunctivitis, cataracts, glaucoma, or uveitis. 
    It is crucial to analyze these conditions as they can affect vision and overall eye health. In particular, conditions like glaucoma may not present immediate symptoms but can lead to vision loss if untreated. 
    Cataracts cause blurry or cloudy vision, and uveitis is often associated with inflammation, leading to symptoms like eye redness and pain. Early detection through eye images can provide vital information for healthcare providers to make informed decisions.
    By analyzing the current image, we can attempt to identify symptoms that match any of these conditions. A closer examination of pupil alignment, eye redness, and discharge can give critical insights.
    """
    return description

# Initialize Streamlit app
st.set_page_config(page_title="Eye Disease Detection", page_icon="🦠")
st.title("🩺 Eye Disease Detection App")

# Sidebar with form for personal and health details
st.sidebar.header("📝 Personal and Health Details")

# Form for personal details with st.sidebar.form(key="personal_details_form"):
with st.sidebar.form(key="personal_details_form"):
    name = st.text_input("Name:", key="name")
    age = st.number_input("Age:", min_value=0, max_value=120, key="age")
    gender = st.selectbox("Gender:", ["Male", "Female", "Other"], key="gender")
    location = st.text_input("Location:", key="location")

    # General Health Information
    st.subheader("General Health Information")
    chronic_illnesses = st.checkbox("Do you have any chronic illnesses?", key="chronic_illnesses")
    diabetes = st.checkbox("Diabetes", key="diabetes")
    high_blood_pressure = st.checkbox("High Blood Pressure", key="high_blood_pressure")
    thyroid_disorders = st.checkbox("Thyroid Disorders", key="thyroid_disorders")
    other_illness = st.text_input("Other (if any):", key="other_illness")
    smoke_alcohol = st.selectbox("Do you smoke or consume alcohol?", ["Yes", "No"], key="smoke_alcohol")

    # Family Medical History
    st.subheader("Family Medical History")
    family_eye_diseases = st.selectbox("Is there a family history of eye diseases?", ["Yes", "No"], key="family_eye_diseases")
    if family_eye_diseases == "Yes":
        family_condition = st.selectbox("If Yes, specify:", ["Glaucoma", "Cataract", "Other"], key="family_condition")
        if family_condition == "Other":
            family_other_condition = st.text_input("Other (specify):", key="family_other_condition")

    # Eye Health Information
    st.subheader("Eye Health Information")
    wear_glasses = st.selectbox("Do you wear glasses or contact lenses?", ["Yes", "No"], key="wear_glasses")
    had_eye_surgery = st.selectbox("Have you had eye surgery before?", ["Yes", "No"], key="had_eye_surgery")
    eye_strain = st.selectbox("Do you experience frequent eye strain?", ["Yes", "No"], key="eye_strain")

    # Symptoms
    st.subheader("Current Eye Symptoms")
    blurry_vision = st.checkbox("Blurry vision", key="blurry_vision")
    redness = st.checkbox("Redness", key="redness")
    double_vision = st.checkbox("Double vision", key="double_vision")
    eye_pain = st.checkbox("Eye pain", key="eye_pain")
    light_sensitivity = st.checkbox("Light sensitivity", key="light_sensitivity")
    itching = st.checkbox("Itching", key="itching")
    swelling = st.checkbox("Swelling", key="swelling")
    discharge = st.checkbox("Discharge", key="discharge")
    trouble_night_vision = st.checkbox("Trouble seeing at night", key="trouble_night_vision")
    other_symptoms = st.text_input("Other (if any):", key="other_symptoms")

    # Past Eye Diseases
    st.subheader("Past Eye Diseases")
    past_eye_disease = st.selectbox("Have you been diagnosed with an eye disease before?", ["Yes", "No"], key="past_eye_disease")
    if past_eye_disease == "Yes":
        past_eye_condition = st.text_input("If Yes, specify:", key="past_eye_condition")

    # Lifestyle and Work Details
    st.subheader("Lifestyle and Work Details")
    screen_use = st.selectbox("Do you frequently use digital screens (e.g., computer, mobile)?", ["Yes", "No"], key="screen_use")
    screen_hours = st.number_input("How many hours per day do you use screens?", min_value=0, key="screen_hours")
    work_environment = st.selectbox("Do you work in an environment with high exposure to dust, chemicals, or bright light?", ["Yes", "No"], key="work_environment")

    # Additional Information
    st.subheader("Additional Information")
    autoimmune_disorders = st.selectbox("Do you have any autoimmune disorders?", ["Yes", "No"], key="autoimmune_disorders")
    migraines = st.selectbox("Do you suffer from frequent migraines?", ["Yes", "No"], key="migraines")
    medications = st.text_input("Do you take any regular medications?", key="medications")

    # Submit button for the form
    submit_button = st.form_submit_button(label="Submit")
    if submit_button:
        # Save or process the form data (e.g., display a confirmation or handle the data)
        st.success("Form submitted successfully!")

# Default prompt for the AI
input_prompt = """ You are an expert in identifying eye diseases. Detect if the input image shows one of the following conditions: cross eyes, conjunctivitis, cataract, glaucoma, or uveitis. If it is not an eye image or if the disease is not listed, respond with "This is not an eye image or an unsupported condition." """

# File uploader for images
uploaded_file = st.file_uploader("Upload an eye image...", type=["jpg", "jpeg", "png"])

# Display uploaded image if uploaded_file is not None:
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

    # Display image details
    image_details = get_image_details(image)
    st.subheader("Image Details:")
    st.write(image_details)

    # Submit button for analyzing the image
    submit = st.button("Analyze Image")

    # On submit, process the image and get the response
    if submit:
        if uploaded_file:
            try:
                image_data = input_image_setup(uploaded_file)
                response = detect_disease(input_prompt, image_data)

                # Check for disease in response
                disease_found = None
                for disease in DISEASES.keys():
                    if disease in response:
                        disease_found = disease
                        report = generate_report(disease)
                        break

                # Displaying predicted disease report with image
                if disease_found:
                    st.subheader(f"Predicted Disease: {disease_found.title()}")
                    st.markdown(f'<div class="chat-bubble bot">{report}</div>', unsafe_allow_html=True)
                else:
                    st.warning("This is not an eye image or an unsupported condition.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("No image uploaded.")
st.subheader("3D Model Viewer")
st.components.v1.iframe("https://huggingface.co/spaces/Wuvin/Unique3D", height=600, scrolling=True)
