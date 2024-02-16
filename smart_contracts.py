import streamlit as st
import base64
import requests
from prompts import smart_contract_information, format_smart_contract_info, generate_deployments_summary,format_deployments_for_openai,generate_ai_response_with_icons,format_inventory_for_openai,format_tokens_for_openai,generate_ai_response

def get_contract_info(account_id, network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    url = f"{base_url}/v1/account/{account_id}/contract"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"error": "Failed to retrieve contract information"}

def get_contract_deployments(account_id, network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    url = f"{base_url}/v1/account/{account_id}/contract/deployments"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"error": "Failed to retrieve contract deployment information"}

def get_inventory(account_id, network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    url = f"{base_url}/v1/account/{account_id}/inventory"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"error": "Failed to retrieve inventory information"}

def get_tokens(account_id, network):
    base_url = "https://api-testnet.nearblocks.io" if network == 'Testnet' else "https://api.nearblocks.io"
    url = f"{base_url}/v1/account/{account_id}/tokens"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"error": "Failed to retrieve tokens information"}

def app(network):
    if network != 'Select Network':
        st.title('🔎 NEAR Explorer Pro')
        st.markdown(user_prompt_style, unsafe_allow_html=True)

        # Set placeholder based on the selected network
        placeholder = "Ex:-farhun.testnet" if network == 'Testnet' else "Ex:-zavodil.poolv1.near"

         # Use a variable that changes with the network to force text_input to reset
        key_id = f"account_id_{network}"
        account_id = st.text_input("Enter your NEAR account ID:", key=key_id,placeholder=placeholder)

        if account_id:
            adjusted_account_id = account_id.replace('.poolv1', '')
            contract_info = get_contract_info(adjusted_account_id, network)
            handle_contract_info(contract_info)

            deployments_info = get_contract_deployments(adjusted_account_id, network)
            handle_deployments_info(deployments_info)

            handle_inventory_info(adjusted_account_id, network)

            handle_tokens_info(adjusted_account_id, network)

            st.subheader('📑 Smart Contract Deployment')
            handle_contract_deployment(account_id)
    else:
        st.info("Please select a network to begin your smart contract analysis.")

def handle_contract_info(contract_info):
    if "error" not in contract_info:
        formatted_contract_info = format_smart_contract_info(contract_info)
        explanation = smart_contract_information(contract_info)
        st.markdown(f"<div class='user_prompt'>👤 <strong>You:</strong><br>{formatted_contract_info}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai_response'>🤖 <strong>NearVision AI:</strong><br>{explanation}</div>", unsafe_allow_html=True)
    else:
        st.error(contract_info["error"])

def handle_deployments_info(deployments_info):
    if "error" not in deployments_info:
        api_key = st.secrets["API_KEY"]
        format_input= format_deployments_for_openai(deployments_info)
        deployments_summary = generate_deployments_summary(deployments_info, api_key)
        st.markdown(f"<div class='user_prompt'>👤 <strong>You:</strong><br>{format_input}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai_response'>🤖 <strong>NearVision AI:</strong><br>{deployments_summary}</div>", unsafe_allow_html=True)
    else:
        st.error(deployments_info["error"])

def handle_inventory_info(account_id, network):
    inventory_info = get_inventory(account_id, network)
    if "error" not in inventory_info:
        api_key = st.secrets["API_KEY"]
        formatted_inventory = format_inventory_for_openai(inventory_info)

        # Extract icons from inventory info
        fts = [{'icon': ft['ft_metas'].get('icon'), 'name': ft['ft_metas'].get('name')} for ft in inventory_info["inventory"]["fts"] if 'ft_metas' in ft and ft['ft_metas'].get('icon')]
        nfts = [{'icon': nft['nft_meta'].get('icon'), 'name': nft['nft_meta'].get('name')} for nft in inventory_info["inventory"]["nfts"] if 'nft_meta' in nft and nft['nft_meta'].get('icon')]

        # Generate the summary including icons for both FTs and NFTs
        inventory_summary = generate_ai_response_with_icons(formatted_inventory, api_key, fts=fts, nfts=nfts)
        st.markdown(f"<div class='user_prompt'>👤 <strong>You:</strong><br>{formatted_inventory}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai_response'>🤖 <strong>NearVision AI:</strong><br>{inventory_summary}</div>", unsafe_allow_html=True)
    else:
        st.error(inventory_info["error"])

def handle_tokens_info(account_id, network):
    tokens_info = get_tokens(account_id, network)
    if "error" not in tokens_info:
        api_key = st.secrets["API_KEY"]
        formatted_tokens = format_tokens_for_openai(tokens_info)
        tokens_summary = generate_ai_response(formatted_tokens, api_key)
        st.markdown(f"<div class='user_prompt'>👤 <strong>You:</strong><br>{formatted_tokens}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai_response'>🤖 <strong>NearVision AI:</strong><br>{tokens_summary}</div>", unsafe_allow_html=True)
    else:
        st.error(tokens_info["error"])

def handle_contract_deployment(account_id):
    uploaded_file = st.file_uploader("Choose a .wasm file for deployment...", type=["wasm"])
    if uploaded_file:
        bytes_data = uploaded_file.getvalue()
        base64_wasm = base64.b64encode(bytes_data).decode("utf-8")
        if st.button("Deploy Contract"):
            deploy_contract(base64_wasm, account_id)
            st.success("Contract deployed successfully!")

def deploy_contract(base64_wasm, account_id):
    html = f"""
    <html>
    <body>
    <script src="https://cdn.jsdelivr.net/npm/near-api-js/dist/near-api-js.js"></script>
    <script>
    async function deployContract() {{
        const wasmFile = "{base64_wasm}";
        const accountId = "{account_id}";
        console.log("Contract deployment simulation for account:", accountId);
    }}
    deployContract();
    </script>
    </body>
    </html>
    """
    st.components.v1.html(html, height=100)

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
    </style>
    """

if __name__ == "__main__":
    app('')  # Default to 'Select Network' as a placeholder