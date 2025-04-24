import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Page configuration
st.set_page_config(
    page_title="Financial Assistant",
    page_icon="💰",
    layout="wide"
)

# Load financial product data
@st.cache_data
def load_data():
    return pd.read_csv("data/investment_products.csv")

products_df = load_data()

# Initialize Gemini model
@st.cache_resource
def get_model():
    return genai.GenerativeModel('gemini-1.5-pro')

model = get_model()

# App header
st.title("💰 Personal Finance Assistant")
st.markdown("Ask questions about investing in India and get personalized recommendations")

# Create two columns
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Chat with Your Financial Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your financial assistant. I can help you with investment advice and finding suitable investment products in India. What would you like to know?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about investing in India..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                products_str = products_df.to_string()
                
                gemini_prompt = f"""
                You are a financial advisor in India helping users make better investment decisions.
                Answer the following question about investing in India:
                
                User Question: {prompt}
                
                Available Investment Products:
                {products_str}
                
                Provide a clear, concise response with practical advice. If recommending products, 
                explain why they might be suitable. Include basic information about risk, expected returns, 
                and minimum investment needed. Avoid giving specific tax advice without disclaimers.
                """
                
                response = model.generate_content(gemini_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

with col2:
    st.subheader("Investment Products")
    
    # Filters
    risk_filter = st.selectbox(
        "Risk Level:",
        ["All Risk Levels", "Very Low", "Low", "Moderate", "High", "Very High"]
    )
    
    max_investment = st.slider(
        "Maximum Investment Amount (₹):",
        min_value=500,
        max_value=10000,
        value=10000,
        step=500
    )
    
    # Filter products
    filtered_df = products_df.copy()
    
    if risk_filter != "All Risk Levels":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]
    
    if max_investment:
        filtered_df = filtered_df[filtered_df['min_investment'] <= max_investment]
    
    # Display filtered products
    if filtered_df.empty:
        st.info("No products match your criteria.")
    else:
        for _, product in filtered_df.iterrows():
            with st.expander(f"{product['name']} ({product['risk_level']} Risk)"):
                st.markdown(f"**Type:** {product['type']}")
                st.markdown(f"**Minimum Investment:** ₹{product['min_investment']:,}")
                st.markdown(f"**Expected Returns:** {product['expected_returns']}")
                st.markdown(f"**Description:** {product['description']}")

# Footer
st.markdown("---")
st.markdown("*This is an MVP financial assistant created for GDG Hackathon. Not financial advice.*")

# In streamlit_app.py

# Initialize chat session
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# Then replace the response generation code with:
chat = st.session_state.chat
response = chat.send_message(gemini_prompt)
st.markdown(response.text)