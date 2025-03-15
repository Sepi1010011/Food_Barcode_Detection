import streamlit as st
import av
import albumentations as A
import numpy as np
import pandas as pd
import os
import datetime
from PIL import Image
from barcode_detection import run_ui, real_time_detection
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
from barcode_query import run_database_search
# streamlit run app.py enableXsrfProtection false

def append_to_csv(report_data, file_name="D:\\Projects\\Food Barcode Object Detection\\Deployments\\flagged\\reports.csv"):
    try:
        new_row = pd.DataFrame([report_data])
        if os.path.exists(file_name):
            df = pd.read_csv(file_name)
        else:
            df = pd.DataFrame(columns=report_data.keys())
            
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(file_name, index=False)
        
    except Exception as e:
        st.error(f"⚠️ Error storing the report: {e}")


def toggle_report_form():
    st.session_state.show_report_form = not st.session_state.show_report_form

def toggle_contact_form():
    st.session_state.show_contact_form = not st.session_state.show_contact_form
    
def reset_contact_form():
    st.session_state.contact_data = {
        "name": None,
        "contact_txt": None,
        "email": None,
        "date_of_report": datetime.datetime.now()
    }


def reset_report_form():
    st.session_state.report_data = {
        "name": None,
        "email": None,
        "feedback": None,
        "report_choice": None,
        "report_text": None,
        "date_of_report": datetime.datetime.now()
    }
    
    
if 'show_report_form' not in st.session_state:
    st.session_state.show_report_form = False
    if "report_data" not in st.session_state:
        st.session_state.report_data = {
        "name": None,
        "email": None,
        "feedback": None,
        "report_choice": None,
        "report_text": None,
        "date_of_report": datetime.datetime.now()
        }
        
    reset_report_form()
    
    
if 'show_contact_form' not in st.session_state:
    st.session_state.show_contact_form = False
    if "contact_data" not in st.session_state:
        st.session_state.contact_data = {
        "name": None,
        "contact_txt": None,
        "email": None,
        "date_of_report": datetime.datetime.now()
        }
        
    reset_report_form()
    

def upload_image_button_report():
    
    st.caption("A quick report form:")
    if st.session_state.show_report_form:
        
        with st.form(key="quick_form"):
            st.subheader("Your Name:")
            st.session_state.report_data["name"] = st.text_input("Enter your full name", value=st.session_state.report_data["name"])
            st.session_state.report_data["feedback"] = st.text_area("Provide your feedback", value=st.session_state.report_data["feedback"])
            
            st.subheader("write your email:")
            st.session_state.report_data["email"] = st.text_input("Enter your email:", value=st.session_state.report_data["email"])
            
            st.session_state.report_data["date_of_report"] = datetime.datetime.now()
            st.subheader("Select Your Problem:")
            st.session_state.report_data["report_choice"] = st.radio(
                "Choose an option",
                ["I upload the image but it will not give me the barcode!",
                "Your system is too slow",
                "I can't upload an image",
                "It can't detect barcode very well",
                "The barcode is not in database!"], index=None, key="report_choice_radio")
            
            
            st.session_state.report_data["report_choice"] = "Was Not A Option"
                
            st.caption("If you can't see your problem in above list write it here:")
            st.session_state.report_data["report_text"] = st.text_input("Write your report!", value=st.session_state.report_data["report_text"])
            
            submit_button = st.form_submit_button(label="Submit")
            if submit_button:
                if not all (st.session_state.report_data.values()):
                    st.warning("Please fill in all of the fields!!")
                
                else:   
                    append_to_csv(st.session_state.report_data)
                    st.balloons()
                    st.success("✅ Your report has been submitted. Thank you for your feedback!")
                    
                    st.session_state.show_report_form = False
                    reset_report_form()
                    
        col1, col2 = st.columns([0.2, 0.2])
        with col1:
            st.button("🔄 New Form", on_click=reset_report_form)
            
        with col2:
            st.button("❌ Cancel Form", on_click=toggle_report_form)
            

def contact_dev_sidebar():
    st.sidebar.caption("📝 A quick contact form")
    
    if st.session_state.show_contact_form:
        with st.sidebar.form(key="contact_form"):
            
            st.subheader("Your Name:")
            st.session_state.contact_data["name"] = st.text_input("Enter your name...")
            
            st.subheader("Your Message:")
            st.session_state.contact_data["contact_txt"] = st.text_area("Enter your message...")
            
            st.subheader("Your Email:")
            st.session_state.contact_data["email"] = st.text_input("Enter your email...")
    
            contact_butt = st.form_submit_button(label="📩 Submit")
            
            if contact_butt:
                if not all (st.session_state.contact_data.values()):
                    st.warning("🚨 Please fill in all of the fields!!")
                
                else:   
                    append_to_csv(st.session_state.contact_data, "D:\\Projects\\Food Barcode Object Detection\\Deployments\\flagged\\contact.csv")
                    st.success("✅ Your message has been sent. Thank you!")
                    
                    st.session_state.show_contact_form = False
                    reset_contact_form()
                    
            col1, col2 = st.columns([0.05, 0.06])
    
            with col1:
                st.form_submit_button("🔄 New Form", on_click=reset_contact_form)

            with col2:
                st.form_submit_button(label="❌ Cancel Contact", on_click=toggle_contact_form)
                

st.set_page_config(page_title="Food Barcode Detection", layout="wide")

st.title("📷 Food Barcode Detection")
st.markdown("Use your camera to scan barcodes and get food details instantly.")
st.divider()

st.sidebar.title("🔍 Looking For Something?")
st.sidebar.write("👨‍💻 Developed by **MrAGI**")
st.sidebar.info("""
This app uses an object detection model to scan barcodes in real-time or from images. 
Once detected, it queries a database to retrieve food information.
""")
st.sidebar.markdown("📌 [GitHub Repository](https://github.com/Sepi1010011/Food_Barcode_Detection)")

st.sidebar.divider()
st.sidebar.subheader("💡 Feedback & Support")
st.sidebar.write("Have a suggestion or found an issue?")
st.sidebar.button("📩 Contact Developer", on_click=toggle_contact_form)

if st.session_state.show_contact_form:
    contact_dev_sidebar()
    
            
st.info("""
### 🛠️ How It Works
- 📸 Upload an image or use real-time detection.
- 🏷️ The app will detect and read the barcode.
- 🔍 It will then fetch the corresponding food details.
""")

st.subheader("📂 Upload an Image")
image_file = st.file_uploader("Upload your image here", type=["jpg", "png", "jpeg"])


def process_uploaded_image(image_file):
    
    if not image_file:
        st.warning("⚠️ No image uploaded!")
        return
        
    try:
        
        img = Image.open(image_file)   
        image_np = np.array(img)     
        image_barcode, txt_barcode, bar_txt = run_ui(image_np, image_file.name)
        st.image(image_barcode, caption="✅ Detected Barcode", use_column_width=True, width=300)
        st.success(f"📌 Barcode Detected: \n\n {txt_barcode}")
        
        barcode_table_info = run_database_search(bar_txt)
        
        if not barcode_table_info.empty:
            st.caption("📖 Your Food Info:")
            st.table(barcode_table_info)
        
        else:
            st.warning("❌ No information found for this barcode.\n\n Wanna add barcode to database?")
            st.button("Add Barcode...")
            st.divider()
        
        st.button("🚩 Report Incorrect Detection", key="Upload_Image_Button", on_click=toggle_report_form)
        
        
        if st.session_state.show_report_form:
            upload_image_button_report()
     
    
    except FileNotFoundError:
        st.error("⚠️ Error: Image file not found.")
        
    except ValueError as ve:
        st.error(f"⚠️ Value Error: {ve}")
    
    except Exception as e:
        st.snow()
        st.error(f"⚠️ Unexpected error processing image: {e}")
        
        
if image_file:
    process_uploaded_image(image_file)


st.subheader("🎥 Real-Time Barcode Detection")
st.write("Click 'Start' to begin real-time barcode scanning.")

transform = A.Compose([
    A.Resize(640, 640),
    A.Normalize()
])

def process_frame(frame):
    transformed = transform(image=frame)
    frame_resized = transformed['image']
    return real_time_detection(frame_resized, frame)

def vid_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    processed_img = process_frame(img)
    return av.VideoFrame.from_ndarray(processed_img, format="bgr24")

webrtc_ctx = webrtc_streamer(
    key="barcode-scanner",
    video_frame_callback=vid_callback
)
