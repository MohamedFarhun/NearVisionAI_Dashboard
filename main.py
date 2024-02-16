import streamlit as st
import about, analytics,health_indicators, home, nearvision_ai, smart_contracts, transactions

def main():
    st.set_page_config(page_title="NearVision Dashboard ", page_icon="👁️", layout="wide")
    st.sidebar.title('📊 NearVision Analytics Dashboard Ⓝ')
    # Network selection in the sidebar, with an option for pages that don't require network selection
    network_options = ['Select Network', 'Testnet', 'Mainnet']
    network = st.sidebar.selectbox("Select Network", network_options, key='network_radio')

    # Dictionary mapping page names to their app functions
    PAGES = {
        "🏠 Home": home.app,
        "❓ About": about.app,
        "⏰ Real Time Insights and Anomaly detection": analytics.app,
        "🗺️ NEAR Explorer Pro": smart_contracts.app,
        "💱 NEAR Transactions Monitoring": transactions.app,
        "💖 Health Indicators": health_indicators.app,
        "🧔 Personalized NearVisionAI": nearvision_ai.app  # NearVisionAI does not require a network parameter
    }

    # Page navigation using radio buttons
    selection = st.sidebar.radio("Navigate", list(PAGES.keys()), key='page_radio')

    # Determine if the selected page requires a network parameter
    if selection in ["❓ About", "⏰ Real Time Insights and Anomaly detection", "🧔 Personalized NearVisionAI"]:
        PAGES[selection]()  # Call without the network parameter
    else:
        PAGES[selection](network)  # Call with the network parameter

    # Display a popup message at the start of the app
    st.sidebar.markdown(
        """
        <div style='padding: 10px; border-radius: 10px; background-color: #FFF3CD; color: #856404; margin-bottom: 10px;'>
            <strong>Note:</strong> For the best experience, please ensure your theme is set to light. 
            You can change this in the settings menu at the top-right of this page.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar for User Guide
    st.sidebar.title("👇 User Guide & Overview")
    with st.sidebar.expander("Getting Started"):
        st.markdown("""
        -  <span style="font-weight:bold; font-size:16px;"> Select a Network:</span> Begin by choosing either 'Mainnet' or 'Testnet' to view data relevant to each NEAR network.
        """, unsafe_allow_html=True)

    with st.sidebar.expander("Home Page"):
        st.markdown("""
        - <span style="font-weight:bold; font-size:16px;"> Overview:</span> The home page provides a snapshot of the latest NEAR protocol statistics including transactions, blocks, and node information.
        - <span style="font-weight:bold; font-size:16px;"> AI Insights:</span> Gain AI-generated insights by interacting with the AI response sections, where you can ask questions or get summaries based on the displayed statistics.
        """, unsafe_allow_html=True)

    with st.sidebar.expander("Transactions & Blocks"):
        st.markdown("""
        - <span style="font-weight:bold; font-size:16px;"> Transactions:</span> Navigate to the 'Transactions' section to view the latest transactions, search for specific transactions, and explore transaction summaries.
        - <span style="font-weight:bold; font-size:16px;"> Blocks:</span> In the 'Blocks' section, you'll find details about the latest blocks, including their height, timestamp, and more.
        """, unsafe_allow_html=True)

    with st.sidebar.expander("Health Indicators & Smart Contracts"):
        st.markdown("""
        - <span style="font-weight:bold; font-size:16px;"> Health Indicators:</span> Access this section to assess the health of the NEAR network through various metrics.
        - <span style="font-weight:bold; font-size:16px;"> Smart Contracts:</span> Explore deployed smart contracts, their details, and functionalities.
        """, unsafe_allow_html=True)

    with st.sidebar.expander("Analytics & NEARVision AI"):
        st.markdown("""
        - <span style="font-weight:bold; font-size:16px;"> Analytics:</span> Dive deeper into NEAR's analytics for an in-depth look at trading patterns, anomalies, and market indicators.
        - <span style="font-weight:bold; font-size:16px;"> NEARVision AI:</span> Leverage AI-driven insights for a comprehensive analysis of your NEAR account, including security, asset holdings, and overall health.
        """, unsafe_allow_html=True)
    
    with st.sidebar.expander("Unique Features and Advantages"):
        st.markdown("""
        - <span style="font-weight:bold; font-size:16px;"> Unified Access:</span> Unlike the separation between Testnet and Mainnet on the official NEAR Blocks,My  dashboard provides a seamless experience by allowing users to switch between Testnet and Mainnet within the same interface. This unified access simplifies the user experience and makes it more convenient to monitor different network environments.
        - <span style="font-weight:bold; font-size:16px;"> Personalized Insights with LLM:</span> Integration of Large Language Models (LLM) for providing personalized insights and summaries is a distinctive feature not present in the official NEAR Blocks dashboards. This allows for more advanced analytics, summaries, and potentially predictive analytics tailored to the user's specific queries and interests, adding a layer of personalized intelligence to blockchain analytics.
        - <span style="font-weight:bold; font-size:16px;"> Comprehensive Health Indicators:</span> My dashboard includes a dedicated section for health indicators of the NEAR protocol. This feature could provide users with a quick overview of the network's performance, security, and reliability metrics, offering a more holistic view of the network's health compared to the basic statistical information available on the official dashboards.
        - <span style="font-weight:bold; font-size:16px;"> Real-Time Anomaly Detection: </span>The feature of real-time insights and anomaly detection in my dashboard could provide significant value by alerting users to unusual activities or potential issues within the network in real time, which is a proactive approach to network monitoring and security.
        """, unsafe_allow_html=True)
    
    with st.sidebar.expander("Feedback & Support"):
        st.markdown("""
        - <span style="font-weight:bold; font-size:16px;"> User Feedback:</span> Your feedback is valuable. Share your thoughts and suggestions to help us improve your experience.
        - <span style="font-weight:bold; font-size:16px;"> Support:</span> Need help? Reach out through the provided support channels for assistance with any queries or issues.
        """, unsafe_allow_html=True)
    
    # Collecting User Feedback
    st.sidebar.title("Feedback")
    rating = st.sidebar.slider("Rate your experience", 1, 5, 3)
    if st.sidebar.button("Submit Rating"):
        st.sidebar.success(f"Thanks for rating us {rating} stars!")
        st.sidebar.markdown(
            "Do visit my [Github profile](https://github.com/MohamedFarhun)"
        )

if __name__ == "__main__":
    main()