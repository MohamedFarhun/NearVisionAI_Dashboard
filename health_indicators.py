import streamlit as st
import requests
from streamlit import secrets  # Import secrets to access your API key
import openai
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from prompts import generate_network_summary_prompt, generate_ai_response

def fetch_chart_data(network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    response = requests.get(f"{base_url}/v1/charts/latest")
    if response.status_code == 200:
        return pd.DataFrame(response.json()["charts"])
    else:
        st.error("Failed to fetch chart data")
        return pd.DataFrame()

def display_charts(df):
    # Transaction Volume Chart
    fig_txns = px.line(df, x='date', y='txns')
    animate_and_style_chart(fig_txns, "Transaction Volume Over Time")

    # NEAR Price Chart
    fig_price = px.line(df, x='date', y='near_price')
    animate_and_style_chart(fig_price, "NEAR Price Over Time")

def calculate_and_display_metrics(df_blocks):
    # Transactions Per Block
    fig_transactions = px.bar(df_blocks, x='block_height', y='transactions_count')
    animate_and_style_chart(fig_transactions, "Transactions Per Block")

    # Gas Used Per Block
    fig_gas = px.bar(df_blocks, x='block_height', y='gas_used')
    animate_and_style_chart(fig_gas, "Gas Used Per Block")

def animate_and_style_chart(fig, title):
    fig.update_layout(transition_duration=500, title="")
    st.markdown(f"<h3 style='text-align: center; color: #b34317;'>{title}</h3>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

def calculate_avg_block_times(df_blocks):
    df_blocks = df_blocks.copy()  # Make a copy to avoid modifying the original DataFrame in place
    if not pd.api.types.is_datetime64_any_dtype(df_blocks['block_timestamp']):
        df_blocks['block_timestamp'] = df_blocks['block_timestamp'].apply(lambda x: datetime(1970, 1, 1) + timedelta(seconds=int(x) // 1e9))
    df_blocks = df_blocks.sort_values('block_timestamp')
    df_blocks['block_time_diff'] = df_blocks['block_timestamp'].diff().dt.total_seconds().fillna(0)
    avg_block_time = df_blocks['block_time_diff'].mean()

    fig_block_times = px.line(df_blocks, x='block_timestamp', y='block_time_diff')
    animate_and_style_chart(fig_block_times, "Block Time Differences Over Time")
    # Styling for the average block time box
    st.markdown(f"""
            <div style="
                padding: 10px;
                border-radius: 10px;
                background-color: #f0f2f6;
                border-left: 5px solid #4CAF50;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                animation: fadeIn 1s ease-in-out;
                ">
                <h5 style="margin: 0; color: #333;">Average Block Time</h5>
                <h3 style="margin: 5px 0; color: #4CAF50;">{avg_block_time:.2f} seconds</h3>
            </div>
            <style>
            @keyframes fadeIn {{
                0% {{ opacity: 0; }}
                100% {{ opacity: 1; }}
            }}
            </style>
        """, unsafe_allow_html=True)
    return df_blocks, avg_block_time

def fetch_blocks_data(network, limit=9):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    response = requests.get(f"{base_url}/v1/blocks/latest?limit={limit}")
    if response.status_code == 200:
        data = response.json()["blocks"]
        # Flatten nested JSON structures
        for block in data:
            block['gas_used'] = block['chunks_agg']['gas_used']
            block['transactions_count'] = block['transactions_agg']['count']
        return pd.DataFrame(data)
    else:
        st.error("Failed to fetch blocks data")
        return pd.DataFrame()

def fetch_stats_data(network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    response = requests.get(f"{base_url}/v1/stats")
    if response.status_code == 200:
        data = response.json()["stats"][0]  # Assuming there's only one stats object
        return data
    else:
        st.error("Failed to fetch stats data")
        return {}

def visualize_block_activity(df_blocks):
    # Using transactions_count as a proxy for block activity/size
    fig_block_activity = px.line(df_blocks, x='block_timestamp', y='transactions_count', title='Block Activity Over Time')
    animate_and_style_chart(fig_block_activity, "Block Activity Over Time")

def visualize_block_producers(df_blocks):
    # Count of unique block producers over time
    unique_producers = df_blocks['author_account_id'].nunique()
    st.markdown(f"""
        <div style="
            padding: 10px;
            border-radius: 10px;
            background-color: #f0f2f6;
            border-left: 5px solid #4CAF50;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            animation: fadeIn 1s ease-in-out;
            ">
            <h5 style="margin: 0; color: #333;">Unique Block Producers </h5>
            <h3 style="margin: 5px 0; color: #4CAF50;">{unique_producers}</h3>
        </div>
        <style>
        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
        </style>
    """, unsafe_allow_html=True)

def visualize_online_nodes(nodes_online):
    # Visualize Online Nodes
    fig_nodes_online = px.bar(x=['Online Nodes'], y=[int(nodes_online)], 
                              labels={'x': '', 'y': 'Count'})
    animate_and_style_chart(fig_nodes_online, "Online Nodes")
    st.markdown(f"""
        <div style="
            padding: 10px;
            border-radius: 10px;
            background-color: #f0f2f6;
            border-left: 5px solid #4CAF50;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            animation: fadeIn 1s ease-in-out;
            ">
            <h5 style="margin: 0; color: #333;">Nodes Online </h5>
            <h3 style="margin: 5px 0; color: #4CAF50;">{nodes_online}</h3>
        </div>
        <style>
        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
        </style>
    """, unsafe_allow_html=True)

def visualize_total_transactions(total_txns):
    # Visualize Total Transactions
    fig_total_txns = px.bar(x=['Total Transactions'], y=[int(total_txns)], 
                            labels={'x': '', 'y': 'Count'})
    animate_and_style_chart(fig_total_txns, "Total Transactions")
    st.markdown(f"""
        <div style="
            padding: 10px;
            border-radius: 10px;
            background-color: #f0f2f6;
            border-left: 5px solid #4CAF50;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            animation: fadeIn 1s ease-in-out;
            ">
            <h5 style="margin: 0; color: #333;">Total Transactions </h5>
            <h3 style="margin: 5px 0; color: #4CAF50;">{total_txns}</h3>
        </div>
        <style>
        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
        </style>
    """, unsafe_allow_html=True)

def visualize_market_cap(market_cap):
    market_cap_float = float(market_cap)  # Convert string to float
    # Display Market Cap in styled box
    st.markdown(f"""
        <div style="
            padding: 10px;
            border-radius: 10px;
            background-color: #f0f2f6;
            border-left: 5px solid #668cff;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            animation: fadeIn 1s ease-in-out;
            ">
            <h5 style="margin: 0; color: #333;">Market Cap</h5>
            <h3 style="margin: 5px 0; color: #668cff;">${market_cap_float:,.2f}</h3> Formatted as currency with commas
        </div>
        <style>
        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
        </style>
    """, unsafe_allow_html=True)

def visualize_volume(volume):
    volume_float = float(volume)  # Convert string to float
    # Display Volume in styled box
    st.markdown(f"""
        <div style="
            padding: 10px;
            border-radius: 10px;
            background-color: #f0f2f6;
            border-left: 5px solid #ff8c1a;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            animation: fadeIn 1s ease-in-out;
            ">
            <h5 style="margin: 0; color: #333;">Volume</h5>
            <h3 style="margin: 5px 0; color: #ff8c1a;">${volume_float:,.2f}</h3> Formatted as currency with commas
        </div>
        <style>
        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
        </style>
    """, unsafe_allow_html=True)

def fetch_fts_count(network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    response = requests.get(f"{base_url}/v1/fts/count")
    if response.status_code == 200:
        data = response.json()
        return data["tokens"][0]["count"]
    else:
        st.error("Failed to fetch Fungible Tokens count")
        return 0

def fetch_fts_txns_count(network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    response = requests.get(f"{base_url}/v1/fts/txns/count")
    if response.status_code == 200:
        data = response.json()
        return data["txns"][0]["count"]
    else:
        st.error("Failed to fetch Fungible Tokens transactions count")
        return 0

def visualize_fts_data(fts_count, fts_txns_count):
    # Display Fungible Tokens Count
    st.markdown(f"""
        <div style="padding: 10px; border-radius: 10px; background-color: #f0f2f6;
            border-left: 5px solid #D4AF37; margin: 10px 0; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <h5 style="margin: 0; color: #333;">Fungible Tokens Count</h5>
            <h3 style="margin: 5px 0; color: #D4AF37;">{fts_count}</h3>
        </div>
    """, unsafe_allow_html=True)

    # Display Fungible Tokens Transactions Count
    st.markdown(f"""
        <div style="padding: 10px; border-radius: 10px; background-color: #f0f2f6;
            border-left: 5px solid #8f428a; margin: 10px 0; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <h5 style="margin: 0; color: #333;">Fungible Tokens Transactions Count</h5>
            <h3 style="margin: 5px 0; color: #8f428a;">{fts_txns_count}</h3>
        </div>
    """, unsafe_allow_html=True)

def fetch_nfts_count(network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    response = requests.get(f"{base_url}/v1/nfts/count")
    if response.status_code == 200:
        data = response.json()
        return data["tokens"][0]["count"]
    else:
        st.error("Failed to fetch Non-Fungible Tokens count")
        return 0

def fetch_nfts_txns_count(network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    response = requests.get(f"{base_url}/v1/nfts/txns/count")
    if response.status_code == 200:
        data = response.json()
        return data["txns"][0]["count"]
    else:
        st.error("Failed to fetch Non-Fungible Tokens transactions count")
        return 0

def visualize_nfts_data(nfts_count, nfts_txns_count):
    # Display Non-Fungible Tokens Count
    st.markdown(f"""
        <div style="padding: 10px; border-radius: 10px; background-color: #f0f2f6;
            border-left: 5px solid #366e80; margin: 10px 0; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <h5 style="margin: 0; color: #333;">Non-Fungible Tokens Count</h5>
            <h3 style="margin: 5px 0; color: #366e80;">{nfts_count}</h3>
        </div>
    """, unsafe_allow_html=True)

    # Display Non-Fungible Tokens Transactions Count
    st.markdown(f"""
        <div style="padding: 10px; border-radius: 10px; background-color: #f0f2f6;
            border-left: 5px solid #aaad39; margin: 10px 0; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <h5 style="margin: 0; color: #333;">Non-Fungible Tokens Transactions Count</h5>
            <h3 style="margin: 5px 0; color: #aaad39;">{nfts_txns_count}</h3>
        </div>
    """, unsafe_allow_html=True)

def display_network_health_analysis(stats_data, fts_count, fts_txns_count, nfts_count, nfts_txns_count, avg_block_time, unique_block_producers, market_cap, volume):
    # Convert market_cap and volume to float before formatting
    try:
        market_cap_float = float(market_cap)  # Ensure market_cap is treated as float
    except ValueError:
        market_cap_float = 0  # Default to 0 if conversion fails

    try:
        volume_float = float(volume)  # Ensure volume is treated as float
    except ValueError:
        volume_float = 0  # Default to 0 if conversion fails
    # Modify the prompt generation to include market cap and volume
    prompt = generate_network_summary_prompt(stats_data, fts_count, fts_txns_count, nfts_count, nfts_txns_count, avg_block_time, unique_block_producers, market_cap_float, volume_float)
    
    # Assuming you have an API key for OpenAI in your secrets
    api_key = secrets["API_KEY"]
    ai_response = generate_ai_response(prompt, api_key)

    # Display the prompt and AI response in Streamlit
    st.markdown(f"<div class='user_prompt'>👤 <strong>You:</strong><br>{prompt}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ai_response'>🤖 <strong>NearVision AI:</strong><br>{ai_response}</div>", unsafe_allow_html=True)
    
def app(network='Select Network'):
    if network == 'Select Network':
        st.info("Please select a network to view stats.")
        return
    
    # Your existing style and header setup here...
    st.markdown("""
        <style>
            .big-font {
                font-size:30px !important;
                font-weight: bold;
                color: #ff6347;
                text-align: center;
                margin-bottom: 30px;
            }
            .chart-title {
                text-align: center;
                margin-top: 40px;
                font-weight: bold;
                font-size: 24px;
                color: #193785;
            }
            .user_prompt, .ai_response {
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 10px;
            }
            .user_prompt {
                background-color: #e1f5fe;  /* Light blue background */
            }
            .ai_response {
                background-color: #f0f4c3;  /* Light green background */
            }
            @media (prefers-color-scheme: dark) {
                .user_prompt {
                    background-color: #333;  /* Darker background for dark mode */
                }
                .ai_response {
                    background-color: #444;  /* Even darker background for dark mode */
                }
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown('<p class="big-font">👨🏻‍💻 Health Indicators Ⓝ</p>', unsafe_allow_html=True)
    
    df = fetch_chart_data(network)
    if not df.empty:
            df['date'] = pd.to_datetime(df['date']).dt.date  # Convert to date for better readability
            display_charts(df)
        
    df_blocks = fetch_blocks_data(network)
    stats_data = fetch_stats_data(network)
    fts_count = fetch_fts_count(network)
    fts_txns_count = fetch_fts_txns_count(network)
    nfts_count = fetch_nfts_count(network)
    nfts_txns_count = fetch_nfts_txns_count(network)

    if not df_blocks.empty:
        # Calculate average block times and update df_blocks with block time differences
        df_blocks, avg_block_time = calculate_avg_block_times(df_blocks)
        # Display metrics for transactions per block and gas used per block
        calculate_and_display_metrics(df_blocks)
        # Visualize block activity and unique block producers
        visualize_block_activity(df_blocks)
        visualize_block_producers(df_blocks)
        unique_block_producers = df_blocks['author_account_id'].nunique()
    else:
        avg_block_time = 0
        unique_block_producers = 0
        
    if stats_data:
        market_cap = stats_data.get('market_cap', 0)  # Use 0 or another default value as fallback
        volume = stats_data.get('volume', 0)
        visualize_online_nodes(stats_data['nodes_online'])
        visualize_total_transactions(stats_data['total_txns'])
        visualize_market_cap(market_cap)  # Use the extracted value
        visualize_volume(volume)  # Use the extracted value
        
    st.markdown(f"<h3 style='text-align: center; color: #b34317;'>NEAR Fungible Tokens Overview</h3>", unsafe_allow_html=True)
    visualize_fts_data(fts_count, fts_txns_count)

    st.markdown(f"<h3 style='text-align: center; color: #b34317;'>NEAR Non-Fungible Tokens Overview</h3>", unsafe_allow_html=True)
    visualize_nfts_data(nfts_count, nfts_txns_count)

    st.markdown(f"<h3 style='text-align: center; color: #b34317'>✍️ Health of NEAR blockchain network - Summary </h3>", unsafe_allow_html=True)

    # Display network health analysis after all other content, ensuring no duplication
    if stats_data:
        display_network_health_analysis(stats_data, fts_count, fts_txns_count, nfts_count, nfts_txns_count, avg_block_time, unique_block_producers, market_cap, volume)

if __name__ == "__main__":
    app('')  # Example call with Testnet