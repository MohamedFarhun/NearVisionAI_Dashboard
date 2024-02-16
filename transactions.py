import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from datetime import timedelta
# Import necessary functions from prompts.py
from prompts import generate_summary_with_openai_transactions,generate_summary_with_openai

# Function to determine the base URL
def get_base_url(network):
    return "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"

# Function to fetch transactions for the table
@st.cache_data(ttl=1, max_entries=200, show_spinner=True)  # Cache for 1 second
def fetch_transactions(network, page):
    base_url = get_base_url(network)
    params = {"page": page, "per_page": 10, "order": "desc"}
    response = requests.get(f"{base_url}/v1/txns", params=params)
    return response.json()["txns"] if response.status_code == 200 else []

@st.cache_data(ttl=1, max_entries=200, show_spinner=True)  # Cache for 1 second
def fetch_blocks(network, page):
    base_url = get_base_url(network)
    params = {"page": page, "per_page": 10, "order": "desc"}
    response = requests.get(f"{base_url}/v1/blocks", params=params)
    return response.json()["blocks"] if response.status_code == 200 else []

# Utility function to truncate content and append '...'
def truncate_content(content, max_length):
    return content[:max_length] + "..." if len(content) > max_length else content

def search_transaction(network, keyword):
    base_url = get_base_url(network)
    response = requests.get(f"{base_url}/v1/search", params={"keyword": keyword})
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to search transactions"}

def display_transactions(network, page):
    transactions = fetch_transactions(network, page)
    data = []
    for txn in transactions:
        tx_hash = truncate_content(txn["transaction_hash"], 10)
        txn_time = datetime.fromtimestamp(int(txn["block_timestamp"]) / 1e9).strftime("%Y-%m-%d %H:%M:%S")
        signer_id = truncate_content(txn["signer_account_id"], 15)
        receiver_id = truncate_content(txn["receiver_account_id"], 15)
        txn_fees = f'{txn["outcomes_agg"]["transaction_fee"] / 1e24:.6f} Ⓝ'

        data.append({
            "TX": "TX",
            "Transaction Hash": tx_hash,
            "Transaction Time": txn_time,
            "Signer Account ID": signer_id,
            "Receiver Account ID": receiver_id,
            "Transaction Fees": txn_fees
        })
    df = pd.DataFrame(data)
    df['Transaction Time'] = pd.to_datetime(df['Transaction Time'])
    df = df.sort_values(by='Transaction Time', ascending=False)

    # Custom CSS for the table
    st.markdown("""
        <style>
        /* Apply to all tables created with DataFrame.to_html() */
        .dataframe {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 0.8em;
            font-family: sans-serif;
            min-width: 400px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        }
        .dataframe thead tr {
            background: linear-gradient(90deg, #18184a 0%, #193785 50%, #18184a 100%);
            color: #ffffff;
            text-align: left;
        }
        .dataframe th,
        .dataframe td {
            padding: 4px 6px ;
        }
        .dataframe tbody tr{
            border-bottom: 1px solid #dddddd;
        }
        .dataframe tbody tr:nth-of-type(even) {
           background-color: #e8ebf3 !important;
           border-bottom: #eee 1px solid;
           border-top: #eee 1px solid;
        }
        .dataframe tbody tr:hover {
            background-color: whitesmoke !important;
            transition: 0.4s;
    }
        </style>
        """, unsafe_allow_html=True)
    
    # Display the DataFrame as an HTML table with custom styling
    st.markdown(df.to_html(index=False, escape=False, classes='dataframe'), unsafe_allow_html=True)

    # Custom CSS for pagination
    st.markdown("""
        <style>
        .pagination-container {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 30px;
        }
        .stButton>button {
        width: 180px; /* Fixed width for both buttons */
        border: 2px solid #4E2A84;
        border-radius: 20px;
        color: white;
        background-color: #193785;
        padding: 6px 12px;
        font-size: 14px;
        font-weight: bold;
        transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            border-color: #372c6f;
            background-color: #372c6f;
        }
        .page-info {
            margin: 0 20px; /* Space around page info */
            font-size: 16px;
            font-weight: bold;
            color: #333; /* Text color */
            text-align: center;
        }
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        .animate-fade-in {
            animation: fadeIn 1s ease-in-out;
        }
        </style>
        """, unsafe_allow_html=True)

    # Pagination
    cols = st.columns([1, 2, 1])  # Adjust ratios as needed
    with cols[0]:
        if page > 1:
            prev_page = page - 1
            st.button("Previous", key="prev_transactions", on_click=lambda: update_page_transactions(network, prev_page))

    with cols[1]:
        # Display current page info
        total_pages = 200  # Placeholder for the actual total pages calculation
        st.markdown(f'<div class="page-info animate-fade-in">Page {page} of {total_pages}</div>', unsafe_allow_html=True)

    with cols[2]:
        if page < total_pages:
            next_page = page + 1
            st.button("Next Transactions", key="next_transactions", on_click=lambda: update_page_transactions(network, next_page))
        st.markdown('</div>', unsafe_allow_html=True)

def format_gas_value(gas_value):
    # Assuming 1 gwei = 1e9 wei
    if gas_value >= 1e9:
        return f"{gas_value / 1e9:.4g} gwei"
    else:
        return f"{gas_value:.4g} wei"

def display_blocks(network, page):
    blocks = fetch_blocks(network, page)
    data = []
    for block in blocks:
        block_height = block["block_height"]
        block_hash = truncate_content(block["block_hash"], 10)
        block_timestamp = datetime.fromtimestamp(int(block["block_timestamp"]) / 1e9).strftime("%Y-%m-%d %H:%M:%S")
        author_account_id=truncate_content(block["author_account_id"],15)
        gas_used = format_gas_value(block["chunks_agg"]["gas_used"])
        gas_limit = format_gas_value(block["chunks_agg"]["gas_limit"])
        transactions_count = block["transactions_agg"]["count"]
        receipts_count = block["receipts_agg"]["count"]

        data.append({
            "Block Height": block_height,
            "Block Hash": block_hash,
            "Block Timestamp": block_timestamp,
            "Author Account Id": author_account_id,
            "Gas Used": gas_used,
            "Gas Limit":gas_limit,
            "Transactions Count": transactions_count,
            "Receipts Count": receipts_count
        })

    df = pd.DataFrame(data)
    df['Block Timestamp'] = pd.to_datetime(df['Block Timestamp'])
    df = df.sort_values(by='Block Height', ascending=False)

    st.markdown(df.to_html(index=False, escape=False, classes='dataframe'), unsafe_allow_html=True)

    # Pagination
    cols = st.columns([1, 2, 1])  # Adjust ratios as needed
    with cols[0]:
        if page > 1:
            prev_page = page - 1
            st.button("Previous", key="prev_blocks", on_click=lambda: update_page_blocks(network, prev_page))

    with cols[1]:
        # Display current page info
        total_pages = 200  # Placeholder for the actual total pages calculation
        st.markdown(f'<div class="page-info animate-fade-in">Page {page} of {total_pages}</div>', unsafe_allow_html=True)

    with cols[2]:
        if page < total_pages:
            next_page = page + 1
            st.button("Next Blocks", key="next_block", on_click=lambda: update_page_blocks(network, next_page))
        st.markdown('</div>', unsafe_allow_html=True)

def update_page_transactions(network, page):
    st.session_state['current_page_transactions'] = page
    st.session_state['page_changed_transactions'] = True  # Add a flag to indicate the page change

def update_page_blocks(network, page):
    st.session_state['current_page_blocks'] = page
    st.session_state['page_changed_blocks'] = True  # Add a flag to indicate the page change

def fetch_all_transactions_for_summary(network,start_time,end_time):
    transactions = []
    total_pages = 200  # This should ideally be dynamic based on the total count of transactions available
    for page in range(1, total_pages + 1):
        transactions.extend(fetch_transactions(network, page))
    return transactions

def fetch_all_blocks_for_summary(network,start_time,end_time):
    blocks = []
    total_pages = 200  # This should ideally be dynamic based on the total count of transactions available
    for page in range(1, total_pages + 1):
        blocks.extend(fetch_blocks(network, page))
    return blocks

def create_summary_prompt(total_transactions, unique_signers):
    prompt = f"There were a total of {total_transactions} transactions conducted by {unique_signers} unique individuals within a second. Please summarize this high-frequency transaction data in a concise and informative manner suitable for a general audience."
    return prompt

def create_summary_prompt_with_blocks(total_blocks, unique_signers):
    prompt = f"There were a total of {total_blocks} blocks conducted by {unique_signers} unique individuals within a second. Please summarize this high-frequency blocks data in a concise and informative manner suitable for a general audience."
    return prompt

def get_total_transactions_count(network):
    base_url = "https://api-testnet.nearblocks.io/v1/txns/count" if network == 'Testnet' else "https://api.nearblocks.io/v1/txns/count"
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        return data['txns'][0]['count']
    else:
        return "Unknown"
    
def get_total_blocks_count(network):
    base_url = "https://api-testnet.nearblocks.io/v1/blocks/count" if network == 'Testnet' else "https://api.nearblocks.io/v1/blocks/count"
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        return data['blocks'][0]['count']
    else:
        return "Unknown"

# Function to fetch transaction count from NEARBlocks API
def get_transaction_count(account_id, network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    url = f"{base_url}/v1/account/{account_id}/txns/count"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"error": "Failed to retrieve transaction count"}

# Function to display transaction count
def handle_transaction_count(transaction_count_info):
    if "error" not in transaction_count_info:
        count = transaction_count_info.get("txns", [{}])[0].get("count", "Unknown")
        st.markdown(f"### 🔢 Transaction Count: {count}")
    else:
        st.error(transaction_count_info["error"])

def get_ft_txn_count(account_id, network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    url = f"{base_url}/v1/account/{account_id}/ft-txns/count"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"error": "Failed to retrieve FT transaction count"}

def get_nft_txn_count(account_id, network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    url = f"{base_url}/v1/account/{account_id}/nft-txns/count"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"error": "Failed to retrieve NFT transaction count"}

def app(network):
    # Initialize session state variables for pagination
    if 'current_page_transactions' not in st.session_state:
        st.session_state['current_page_transactions'] = 1
    # Initialize session state variables for pagination
    if 'current_page_blocks' not in st.session_state:
        st.session_state['current_page_blocks'] = 1
    if 'current_network_transactions' not in st.session_state:
        st.session_state['current_network_transactions'] = network
    if 'current_network_blocks' not in st.session_state:
        st.session_state['current_network_blocks'] = network
    if 'input_prompt_transactions' not in st.session_state:
        st.session_state['input_prompt_transactions'] = ""
    if 'input_prompt_blocks' not in st.session_state:
        st.session_state['input_prompt_blocks'] = ""
    if 'ai_response_transactions' not in st.session_state:
        st.session_state['ai_response_transactions'] = ""
    if 'ai_response_blocks' not in st.session_state:
        st.session_state['ai_response_blocks'] = ""
    if 'summary_generated_transactions' not in st.session_state:
        st.session_state['summary_generated_transactions'] = False  # Track if summary has been generated
    if 'summary_generated_blocks' not in st.session_state:
        st.session_state['summary_generated_blocks'] = False  # Track if summary has been generated
     # Initialize session state variables for current action
    if 'current_action' not in st.session_state:
        st.session_state['current_action'] = 'show_transactions'  # Default action
    if network != 'Select Network':
        st.markdown("""
        <style>
            .big-font {font-size:30px !important; font-weight: bold; color: #ff6347;}
            .small-font {font-size:18px !important;}
            .animate {animation: fadeIn ease 3s; animation-iteration-count: 1; animation-fill-mode: forwards;}
            @keyframes fadeIn {0% {opacity:0;} 100% {opacity:1;}}
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
            </style>
            """, unsafe_allow_html=True)
     
        st.markdown('<p class="big-font animate">🧐 NEAR Transactions Overview</p>', unsafe_allow_html=True)
        st.markdown('<p class="big-font">Latest Transactions</p>', unsafe_allow_html=True)

        display_transactions(network, st.session_state['current_page_transactions'])

        # In your app() function or main script body, after calling display_transactions():
        if 'page_changed_transactions' in st.session_state and st.session_state['page_changed_transactions']:
            st.session_state['page_changed_transactions'] = False  # Reset the flag
            st.experimental_rerun()  # Now it's safe to call rerun

        st.markdown('<p class="big-font">Latest Blocks</p>', unsafe_allow_html=True)
        # Display transactions after the buttons, so they have the chance to update the page first
        display_blocks(network, st.session_state['current_page_blocks'])

        # In your app() function or main script body, after calling display_transactions():
        if 'page_changed_blocks' in st.session_state and st.session_state['page_changed_blocks']:
            st.session_state['page_changed_blocks'] = False  # Reset the flag
            st.experimental_rerun()  # Now it's safe to call rerun
        
        st.markdown('<p class="big-font animate"> 📝 NEAR Blocks And Transactions Summary</p>', unsafe_allow_html=True)
        
        if network != st.session_state['current_network_blocks'] or not st.session_state['summary_generated_blocks']:
            total_blocks_count = get_total_blocks_count(network)
            # Display a message to wait for transaction summary
            st.warning("Please wait for a minute or two to view the blocks summary for the last second.")    
            api_key = st.secrets["API_KEY"]
            start_time = datetime.now() - timedelta(seconds=1)
            end_time = start_time + timedelta(seconds=1)
            blocks = fetch_all_blocks_for_summary(network,start_time,end_time)
            total_blocks = len(blocks)
            unique_signers = len(set(block["author_account_id"] for block in blocks))

            # Format the input prompt as a structured summary
            input_prompt = f"Hi there, here's a brief summary of blocks generated in NEAR {network} within the last second:\n\n"
            input_prompt += f"- Total Blocks: {total_blocks}\n\n"
            input_prompt += f"- Unique Signers: {unique_signers}\n\n"
            input_prompt += f"- Total blocks on the {network}: {total_blocks_count}\n\n"
            input_prompt += "Please provide a concise explanation of this high-frequency blocks data."

            formatted_prompt = create_summary_prompt_with_blocks(total_blocks, unique_signers)
            ai_response = generate_summary_with_openai(formatted_prompt, api_key)

            # Store the generated summary in session state
            st.session_state['input_prompt_blocks'] = input_prompt
            st.session_state['ai_response_blocks'] = ai_response
            st.session_state['current_network_blocks'] = network
            st.session_state['summary_generated_blocks'] = True  # Indicate that summary has been generated
            st.experimental_rerun()

        # Display the stored summary
        st.markdown(f"<div class='user_prompt'>👤 <strong>You:</strong><br>{st.session_state['input_prompt_blocks']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai_response'>🤖 <strong>NearVision AI:</strong><br>{st.session_state['ai_response_blocks']}</div>", unsafe_allow_html=True)
        
        if network != st.session_state['current_network_transactions'] or not st.session_state['summary_generated_transactions'] and st.session_state['current_action'] == 'show_transaction_summary':
            total_transactions_count = get_total_transactions_count(network)
            api_key = st.secrets["API_KEY"]
            start_time = datetime.now() - timedelta(seconds=1)
            end_time = start_time + timedelta(seconds=1)
            transactions = fetch_all_transactions_for_summary(network, start_time, end_time)

            if transactions:  # Check if the transactions list is not empty
                total_transactions = len(transactions)
                unique_signers = len(set(txn["signer_account_id"] for txn in transactions))
                input_prompt = f"Hi there, here's a brief summary of transactions generated in NEAR {network} within the last second:\n\n"
                input_prompt += f"- Total Transactions: {total_transactions}\n\n"
                input_prompt += f"- Unique Signers: {unique_signers}\n\n"
                input_prompt += f"- Total Transactions on the {network}: {total_transactions_count}\n\n"
                input_prompt += "Please provide a concise explanation of this high-frequency transaction data."
                formatted_prompt = create_summary_prompt(total_transactions, unique_signers)
                ai_response = generate_summary_with_openai_transactions(formatted_prompt, api_key)
                st.session_state['input_prompt_transactions'] = input_prompt
                st.session_state['ai_response_transactions'] = ai_response
            else:  # If the transactions list is empty, display the message for no transactions
                st.session_state['input_prompt_transactions'] = "No Transactions Input"
                st.session_state['ai_response_transactions'] = "No transactions were found in the last second. No Transactions Summary available."

            st.session_state['current_network_transactions'] = network
            st.session_state['summary_generated_transactions'] = True
            st.session_state['current_action'] = 'show_transaction_summary'
            st.experimental_rerun()

        # Display the stored summary or the no transactions message
        st.markdown(f"<div class='user_prompt'>👤 <strong>You:</strong><br>{st.session_state['input_prompt_transactions']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai_response'>🤖 <strong>NearVision AI:</strong><br>{st.session_state['ai_response_transactions']}</div>", unsafe_allow_html=True)

        st.markdown('<p class="big-font animate"> 🤵🏻 Personalized Summary</p>', unsafe_allow_html=True)
        st.markdown('<p class="small-font">Enter your NEAR account ID:', unsafe_allow_html=True)
        placeholder = "Ex:-farhun.testnet" if network == 'Testnet' else "Ex:-zavodil.poolv1.near"
        account_id = st.text_input("", placeholder=placeholder)
        if account_id:
            # Define custom CSS for the boxes
                box_css = """
                    <style>
                        .category-box {
                            padding: 10px;
                            margin: 5px 0px;
                            border-radius: 10px;
                            background-color: #6C63FF;  /* Attractive purple shade for category */
                            color: white;
                            text-align: center;
                        }

                        .data-box {
                            border: 2px solid #FFC107;  /* Golden border */
                            border-radius: 10px;
                            padding: 10px;
                            margin: 5px 0px;
                            background-color: #FFECB3;  /* Light golden background for data */
                            text-align: center;
                            transition: transform .2s;  /* Smooth scaling animation */
                        }

                        .data-box:hover {
                            transform: scale(1.05);  /* Slightly larger on hover */
                            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                        }

                        .data-value {
                            font-size: 1.5rem;
                            font-weight: bold;
                            color: #FF5722;  /* Deep orange for value */
                        }
                    </style>
                """

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(box_css + '<div class="category-box">Total Transactions</div>', unsafe_allow_html=True)
                    txn_count_info = get_transaction_count(account_id, network)
                    count = txn_count_info.get("txns", [{}])[0].get("count", "Unknown")
                    st.markdown(box_css + f'<div class="data-box"><p class="data-value">🔢 {count}</p></div>', unsafe_allow_html=True)
                    
                with col2:
                    st.markdown(box_css + '<div class="category-box">FT Transactions</div>', unsafe_allow_html=True)
                    ft_txn_count_info = get_ft_txn_count(account_id, network)
                    count_ft = ft_txn_count_info.get("txns", [{}])[0].get("count", "Unknown")
                    st.markdown(box_css + f'<div class="data-box"><p class="data-value">🎭 {count_ft}</p></div>', unsafe_allow_html=True)

                with col3:
                    st.markdown(box_css + '<div class="category-box">NFT Transactions</div>', unsafe_allow_html=True)
                    nft_txn_count_info = get_nft_txn_count(account_id, network)
                    count_nft = nft_txn_count_info.get("txns", [{}])[0].get("count", "Unknown")
                    st.markdown(box_css + f'<div class="data-box"><p class="data-value">🖼️ {count_nft}</p></div>', unsafe_allow_html=True)
    else:
        st.info("Please select a network to view transactions.")

if __name__ == "__main__":
    app('')