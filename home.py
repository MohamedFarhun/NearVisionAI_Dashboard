import streamlit as st
import requests
import openai
from prompts import format_stats_for_prompt_home,generate_ai_response

openai.api_key = st.secrets["API_KEY"]

def fetch_stats(network):
    if network == 'Testnet':
        url = "https://api-testnet.nearblocks.io/v1/stats"
    else:
        url = "https://api.nearblocks.io/v1/stats"
    response = requests.get(url)
    return response.json()["stats"][0] if response.status_code == 200 else {}

def app(network):
    if network == 'Select Network':
        st.info("Please select a network to view stats of NEAR blocks.")
        return
    
    st.title('👋 NEARVision Ⓝ')
    # Styles for the prompts
    user_prompt_style = """
        <style>
            .user_prompt, .ai_response {
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 10px;
            }
            .user_prompt {
                background-color: #e1f5fe;
            }
            .ai_response {
                background-color: #f0f4c3;
            }
            @media (prefers-color-scheme: dark) {
                .user_prompt {
                    background-color: #333;
                }
                .ai_response {
                    background-color: #444;
                }
            }
            .header {
            color: #ff4f8b; /* Change the color */
            font-size: 3rem; /* Change the font size */
            text-shadow: 2px 2px #ffcccb; /* Add a shadow effect */
            font-weight: bold;
            margin-bottom: 1rem;
            }
            .sub-header {
            color: #30336b; /* Change the color */
            font-size: 2rem; /* Change the font size */
            text-shadow: 1px 1px #dfe6e9; /* Add a shadow effect */
            font-weight: bold;
            margin-bottom: 1rem;
            }
            .near-symbol {
            font-size: 1.5rem; /* Change the size of the symbol */
            color: #6c5ce7; /* Change the color of the symbol */
            }
        </style>
    """
    st.markdown(user_prompt_style, unsafe_allow_html=True)

    stats = fetch_stats(network)
    if stats:
        display_stats_with_style(stats)
        formatted_prompt = format_stats_for_prompt_home(stats,network)
        st.markdown(f"<div class='user_prompt'>👤 <strong>Stats for {network}:</strong><br>{formatted_prompt}</div>", unsafe_allow_html=True)
        
        ai_response = generate_ai_response(formatted_prompt, st.secrets["API_KEY"])
        st.markdown(f"<div class='ai_response'>🤖 <strong>AI Response:</strong><br>{ai_response}</div>", unsafe_allow_html=True)
    else:
        st.error("Failed to fetch data. Please try again.")

def display_stats_with_style(stats):
    # Injecting custom styles
    st.markdown("""
    <style>
            .st-emotion-cache-1isgx0k{
                width:800px !important;
            }
            .metric-container {
            border-radius: 10px;
            background-color: #f0f2f6;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            padding: 20px;
            height: 150px;  /* Fixed height for uniform size */
            display: flex;
            flex-direction: column;
            justify-content: space-around;  /* Distribute space above and below content */
            transition: transform 0.2s;
            cursor: pointer;
            margin : 10px 0px;
        }
        .metric-container h3 {
            font-size: 16px;  /* Adjust title font size */
            margin: 0;
            padding: 0;
            text-align: center;
        }
        .metric-container p {
            font-size: 24px;  /* Adjust value font size */
            margin: 0;
            padding: 0;
            text-align: center;
            word-wrap: break-word;  /* Ensure long words do not overflow */
        }
        .metric-container:hover {
            transform: scale(1.05);
        }
    </style>
    """, unsafe_allow_html=True)

    # Display metrics with enhanced styles
    metrics_layout(stats)

def metrics_layout(stats):
    metrics = [
        ("Total Transactions in Near", f'{int(stats["total_txns"])/1e6:.2f}M'),
        ("Total No of Blocks", stats["block"]),
        ("NEAR Price in dollars($)", f'${float(stats["near_price"]):.2f}'),
        ("Avg Block Time (s)", f'{float(stats["avg_block_time"]):.2f}s'),
        ("1 BTC to NEAR", f"{1 / float(stats['near_btc_price']):.2f}"),
        ("Nodes Online", stats["nodes_online"]),
        ("Gas Price (Ⓝ / Tgas)", f'{float(stats["gas_price"])/1e12:.7f}'),
        ("Market Cap", f'${float(stats["market_cap"])/1e6:.2f}M'),
        ("Volume Capacity", f'{float(stats["volume"])/1e6:.2f}M'),
        ("Price change(24 hrs)", f'{float(stats["change_24"]):.2f}%'),
        ("Highest price(24 hrs)", f'${float(stats["high_24h"]):.2f}'),
        ("Lowest price(24 hrs)", f'${float(stats["low_24h"]):.2f}'),
        ("All Time Highest price", f'${float(stats["high_all"]):.2f}'),
        ("All Time Lowest price", f'${float(stats["low_all"]):.2f}'),
        ("Total Supply", f'{int(stats["total_supply"]):.3e}')
    ]

    for i in range(0, len(metrics), 5):
        cols = st.columns(5)
        for col, metric in zip(cols, metrics[i:i+5]):
            label, value = metric
            metric_html = f"""
            <div class="metric-container">
                <h3 style="margin:0;">{label}</h3>
                <p style="margin:0; font-size:20px;"><strong>{value}</strong></p>
            </div>
            """
            col.markdown(metric_html, unsafe_allow_html=True)

if __name__ == "__main__":
    app()