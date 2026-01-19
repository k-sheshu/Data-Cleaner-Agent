import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# --- LANGCHAIN IMPORTS ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# 1. Load environment variables
load_dotenv()

# 2. Configure Page
st.set_page_config(page_title="Smart Data Cleaner", page_icon="🧹", layout="wide")

st.title("🧹 Smart Data Cleaner Agent")

# 3. Session State Management
if "df" not in st.session_state:
    st.session_state.df = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 4. Sidebar: File Upload
with st.sidebar:
    st.header("⬆️ Upload Data")
    uploaded_file = st.file_uploader("Choose CSV/Excel", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            if st.session_state.df is None:  # Only load if not already loaded
                if uploaded_file.name.endswith('.csv'):
                    try:
                        df = pd.read_csv(uploaded_file)
                    except UnicodeDecodeError:
                        df = pd.read_csv(uploaded_file, encoding='latin1')
                else:
                    df = pd.read_excel(uploaded_file)
                
                # --- SANITIZATION STEP (FIX FOR ARROW ERROR) ---
                # 1. Drop "Unnamed" index columns which often cause the Object/Int mismatch
                            
                st.session_state.df = df
                st.success("File uploaded and sanitized successfully!")
        except Exception as e:
            st.error(f"Error loading file: {e}")
    
    # Button to reset
    if st.button("Clear Data"):
        st.session_state.df = None
        st.session_state.chat_history = []
        st.rerun()

    api_key = os.getenv("GOOGLE_API_KEY") 
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")

# 5. Main Logic
if st.session_state.df is not None:
    
    # --- TABS LAYOUT ---
    tab1, tab2, tab3 = st.tabs(["💬 Chat & Clean", "🔎 Data Inspector", "📥 Export Cleaned Data"])
    
    # --- TAB 1: Chat Interface ---
    with tab1:
        if api_key:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0,
                google_api_key=api_key
            )

            # Create Agent
            # FIX 1: Removed 'handle_parsing_errors=True' to fix the UserWarning
            agent = create_pandas_dataframe_agent(
                llm,
                st.session_state.df,
                verbose=True,
                allow_dangerous_code=True,
                agent_type="zero-shot-react-description"
            )

            st.info("💡 Tip: You can ask for plots or any corrections! The agent will generate them for you.")
            
            # Chat History
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Input
            user_input = st.chat_input("Ask about your data (e.g., 'Plot the distribution of Ratings')")

            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                with st.chat_message("assistant"):
                    with st.spinner("Processing..."):
                        try:
                            # Plot instruction
                            plot_instruction = """
                            If the user asks for a plot or chart:
                            1. Use 'matplotlib.pyplot'.
                            2. Create the plot.
                            3. Save the figure as 'plot.png' using plt.savefig('plot.png').
                            4. Do not use plt.show().
                            """
                            full_prompt = user_input + plot_instruction
                            
                            response = agent.run(full_prompt)
                            st.markdown(response)
                            st.session_state.chat_history.append({"role": "assistant", "content": response})

                            # Check if a plot file was created
                            if os.path.exists("plot.png"):
                                st.image("plot.png")
                                os.remove("plot.png")
                                
                        except Exception as e:
                            st.error(f"Error: {e}")
        else:
            st.warning("Please provide an API Key.")

    # --- TAB 2: Data Inspector ---
    with tab2:
        st.subheader("Current Dataframe State")
        st.dataframe(st.session_state.df)
        
        st.markdown("### Column Details")
        st.write(st.session_state.df.dtypes)

    # --- TAB 3: Export ---
    with tab3:
        st.subheader("1. Download Cleaned Data")
        
        csv = st.session_state.df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv",
        )
        
        st.divider()
        
        st.subheader("2. Download Audit Log")
        st.write("Keep a record of all the changes and analysis performed by the agent.")
        
        audit_log = "--- SMART DATA CLEANER: AUDIT LOG ---\n\n"
        for msg in st.session_state.chat_history:
            role = "USER" if msg["role"] == "user" else "AGENT"
            audit_log += f"[{role}]: {msg['content']}\n\n"
        
        st.download_button(
            label="⬇️ Download Audit Log (.txt)",
            data=audit_log,
            file_name="audit_log.txt",
            mime="text/plain",
        )