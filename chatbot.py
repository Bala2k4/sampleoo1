import streamlit as st
import google.generativeai as genai
import json
from fpdf import FPDF
import time

# Configure Google AI API
API_KEY = "AIzaSyDGYHByPrdiXWDgA-u6snt2ryA41QcadhA"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")  # Updated model name

# Function to generate interview-related details
def generate_interview_details(topic):
    prompt = f"""
    Provide comprehensive details about {topic} in the context of technical interviews.
    Include:
    - Key concepts
    - Common questions
    - Best practices
    - Tips for mastering the topic
    - Relevant external resources with links
    - Suggested referral video links
    """
    response = model.generate_content(prompt)
    return response.text if response else "Failed to retrieve interview details."

# Function to generate external resource links
def generate_external_links(topic):
    links = {
        "Data Structures": "https://www.geeksforgeeks.org/data-structures/",
        "Algorithms": "https://www.khanacademy.org/computing/computer-science/algorithms",
        "System Design": "https://roadmap.sh/system-design",
        "OOP": "https://www.w3schools.com/cpp/cpp_oop.asp",
        "DBMS": "https://www.javatpoint.com/dbms-tutorial",
        "Operating Systems": "https://www.geeksforgeeks.org/operating-system/",
        "Computer Networks": "https://www.tutorialspoint.com/computer_networking/index.htm",
        "Software Engineering": "https://www.tutorialspoint.com/software_engineering/index.htm",
        "Cybersecurity": "https://www.cyber.gov.au/",
        "Machine Learning": "https://www.coursera.org/learn/machine-learning",
        "Artificial Intelligence": "https://www.ibm.com/cloud/learn/artificial-intelligence",
        "Cloud Computing": "https://aws.amazon.com/what-is-cloud-computing/",
        "DevOps": "https://www.atlassian.com/devops",
        "Database Management": "https://www.w3schools.com/sql/"
    }
    return links.get(topic, "No external link available.")

# Function to generate PDF
def generate_pdf(history):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Interview Sensei History", ln=True, align='C')
    pdf.ln(10)
    for item in history:
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, f"Topic: {item['topic']}", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 10, item['details'])
        pdf.ln(5)
    return pdf

# Streamlit UI
st.set_page_config(page_title="Interview Sensei", layout="wide", initial_sidebar_state="expanded")

# Sidebar for history and history download
with st.sidebar:
    st.title("About Interview Sensei")
    st.write("Interview Sensei is your AI-powered assistant for mastering technical interviews. Get topic insights, practice questions, and expert tips!")
    st.write("## History")
    if "history" not in st.session_state:
        st.session_state.history = []
    
    if st.button("View History"):
        if not st.session_state.history:
            st.write("No recent searches.")
        else:
            for item in st.session_state.history:
                st.write(f"- {item['topic']}")
                st.write(item['details'])
                st.write(f"[Learn more]({item['link']})")
    
    if st.button("Download History as PDF"):
        if not st.session_state.history:
            st.write("No history available to download.")
        else:
            pdf = generate_pdf(st.session_state.history)
            pdf_path = "history.pdf"
            pdf.output(pdf_path, "F")
            with open(pdf_path, "rb") as file:
                st.download_button("Download PDF", file, "history.pdf", "application/pdf")

st.title("Interview Sensei: AI-Powered Interview Prep")

# User selects a topic
topic = st.selectbox("Choose a topic:", ["Data Structures", "Algorithms", "System Design", "OOP", "DBMS", "Operating Systems", "Computer Networks", "Software Engineering", "Cybersecurity", "Machine Learning", "Artificial Intelligence", "Cloud Computing", "DevOps", "Database Management"])

if st.button("Get Interview Details"):
    with st.spinner("Searching for the best insights... 📚"):
        time.sleep(2)
        details = generate_interview_details(topic)
        external_link = generate_external_links(topic)
        st.session_state.details = details
        st.write(f"### Here's everything you need to know about {topic}!")
        st.write(details)
        st.write(f"[Click here for more resources on {topic}]({external_link})")
        
        # Save history with details and links
        st.session_state.history.append({"topic": topic, "details": details, "link": external_link})
        
# User query input
st.write("## Ask Interview Sensei")
user_query = st.text_area("Ask any interview-related question:")
if st.button("Get Answer") and user_query:
    with st.spinner("Let me think... 🤔"):
        time.sleep(2)
        query_response = model.generate_content(user_query)
        answer = query_response.text if query_response else "No response available."
        st.write("### Here’s what I found for you:")
        st.write(answer)
        
        # Save user queries and answers
        st.session_state.history.append({"topic": "User Query", "details": answer, "link": ""})

        # Follow-up question handling
        follow_up = st.text_input("Would you like more details or references?")
        if st.button("Submit Follow-up") and follow_up:
            with st.spinner("Fetching more details..."):
                time.sleep(2)
                follow_up_response = model.generate_content(follow_up)
                follow_up_answer = follow_up_response.text if follow_up_response else "No additional information available."
                st.write("### Additional Information:")
                st.write(follow_up_answer)
                st.session_state.history.append({"topic": "Follow-up Query", "details": follow_up_answer, "link": ""})
