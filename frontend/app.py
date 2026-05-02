import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

# Configure accessible UI
st.set_page_config(page_title="VoteEasy", page_icon="🗳️", layout="centered")

st.title("🗳️ VoteEasy")
st.markdown("### Your Beginner-Friendly AI Voting Assistant")
st.write("Navigating elections can be confusing. Let us help you figure out your next steps simply and securely.")

# Accessibility info in sidebar
with st.sidebar:
    st.header("About VoteEasy", anchor="about")
    st.markdown("<p aria-label='Description of VoteEasy'>VoteEasy uses Artificial Intelligence to help you understand voting procedures.</p>", unsafe_allow_html=True)
    st.markdown("**Accessibility Features:**")
    st.write("- Screen reader friendly layouts (HTML5 Semantics)")
    st.write("- Keyboard navigable forms (Enter to Submit)")
    st.write("- High contrast styling enabled via config")

# Efficient Caching to limit unnecessary API hits
@st.cache_data(show_spinner=False, ttl=600)
def fetch_answer(question: str, location: str, status: str):
    """Fetches the answer from the FastAPI backend."""
    try:
        response = requests.post(
            API_URL, 
            json={"question": question, "location": location, "status": status},
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"error": "Could not connect to the assistant. Ensure the backend server is running."}

# Using st.form for "Enter" key submit accessibility
with st.form("voting_query_form"):
    st.subheader("Step 1: Your Context")
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Your Age", min_value=0, max_value=120, value=18, help="You must be at least 18 by Election Day to vote.")
    with col2:
        location = st.text_input("State or City", placeholder="e.g. Texas", help="Voting rules vary by state.")
        
    status = st.selectbox(
        "Registration Status", 
        ["I'm not sure", "Not registered", "Registered"],
        help="Knowing your status helps us give accurate advice."
    )
    
    st.subheader("Step 2: Your Question")
    question = st.text_input("What would you like to know?", placeholder="e.g., How do I register online?")
    
    # Submit button
    submitted = st.form_submit_button("Get Guidance")
    
if submitted:
    if age < 18:
        st.warning("You must be 18 to vote on Election Day, but you may be able to register now.")
        
    if not question.strip() or not location.strip():
        st.error("Please provide both your location and a question so we can assist you.")
    else:
        with st.spinner("Finding the easiest answer for you..."):
            data = fetch_answer(question, location, status)
            
            if "error" in data:
                st.error(data["error"])
            else:
                st.markdown("---")
                st.success("✅ Information Found")
                # High contrast visually distinct outputs
                st.info(f"**Answer:**\n\n{data.get('answer', '')}")
                st.warning(f"**📌 Next Step:**\n\n{data.get('next_step', '')}")
