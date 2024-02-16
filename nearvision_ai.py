import streamlit as st
import requests
from near_api.signer import KeyPair
import base58
from prompts import format_for_openai,format_for_openai_account,format_for_openai_inventory,generate_summary_prompt
import openai

def generate_openai_response(prompt, name):
    """Generate a response from OpenAI based on the given prompt."""
    openai.api_key = st.secrets["API_KEY"]
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",  # Choose the appropriate engine for your use case
        prompt=prompt,
        max_tokens=600,
        temperature=0.7,
    )
    greeting = f"Hi {name},\n\n"  # Personalized greeting
    full_response = greeting + response.choices[0].text.strip()  # Prepending the greeting to the OpenAI response
    return full_response

def get_public_key_from_private(private_key_base58):
    """Generate a public key from a private key."""
    if ':' in private_key_base58:
        _, key_part = private_key_base58.split(':', 1)  # Extract the key part
    else:
        key_part = private_key_base58

    try:
        private_key_bytes = base58.b58decode(key_part)  # Decode the key part
    except Exception as e:
        st.error(f"Error decoding private key: {e}")
        return None
    
    # Extract the first 32 bytes as the seed for NEAR KeyPair
    seed = private_key_bytes[:32]

    try:
        key_pair = KeyPair(secret_key=seed)
        # Replace get_public_key() with the actual method or property to access the public key
        public_key_bytes = key_pair._secret_key.verify_key.encode()
    except Exception as e:
        st.error(f"Error initializing key pair or retrieving public key: {e}")
        return None
    
    # Prepend the 'ed25519:' prefix to the base58-encoded public key
    public_key_base58 = "ed25519:" + base58.b58encode(public_key_bytes).decode('utf-8')
    return public_key_base58

def fetch_keys_info(public_key_base58):
    """Fetch information associated with the public key from NearBlocks API."""
    url = f"https://api-testnet.nearblocks.io/v1/keys/{public_key_base58}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return None
    else:
        st.error(f"Failed to fetch data. Status code: {response.status_code}")
        return None
    
def fetch_account_info(account_id):
    """Fetch account information from NearBlocks API."""
    url = f"https://api-testnet.nearblocks.io/v1/account/{account_id}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return None
    else:
        st.error(f"Failed to fetch account data. Status code: {response.status_code}")
        return None

def fetch_inventory_info(account_id):
    """Fetch inventory information from NearBlocks API."""
    url = f"https://api-testnet.nearblocks.io/v1/account/{account_id}/inventory"  
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return None
    else:
        st.error(f"Failed to fetch inventory data. Status code: {response.status_code}")
        return None

def app():
    st.title("🖥️ Personalized NearVisionAI Ⓝ")
    # Define the styles with CSS variables
    user_prompt_style = """
        <style>
            .user_prompt, .ai_response,.ai_response_summary {
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
            .ai_response_summary {
                background-color: #F5D6D0;  /* Light green background */
            }
            @media (prefers-color-scheme: dark) {
                .user_prompt {
                    background-color: #333;  /* Darker background for dark mode */
                }
                .ai_response {
                    background-color: #444;  /* Even darker background for dark mode */
                }
                .ai_response_summary {
                    background-color: #444;  /* Even darker background for dark mode */
                }
            }
        </style>
        """
    # Include the styles in your Streamlit app
    st.markdown(user_prompt_style, unsafe_allow_html=True)

    private_key_base58 = st.secrets["NEAR_PRIVATE_KEY"]
    public_key_generated = get_public_key_from_private(private_key_base58)

    if public_key_generated:
        st.write(f"Generated Public Key: {public_key_generated}")
        public_key_input = st.text_input("Enter or Confirm the Public Key:", public_key_generated)

        if public_key_input:
            keys_info = fetch_keys_info(public_key_input)
            if keys_info and "keys" in keys_info and len(keys_info["keys"]) > 0:
                account_id = keys_info["keys"][0].get("account_id")  # Extracting account_id from keys_info
                name = account_id.split(".")[0]  # Extracting name from account_id
                formatted_key_prompt = format_for_openai(keys_info)  # Assuming this formats key info for OpenAI
                openai_response_key = generate_openai_response(formatted_key_prompt, name)
                # Displaying the formatted prompt to the user
                st.markdown(f"<div class='user_prompt'>👤 <strong>You:</strong><br>{formatted_key_prompt}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='ai_response'>🤖 <strong>NearVision AI:</strong><br>{openai_response_key}</div>", unsafe_allow_html=True)

                # Fetching and displaying account information dynamically based on account_id
                if account_id:
                    account_info = fetch_account_info(account_id)  # Fetch account info dynamically
                    if account_info:
                        formatted_account_prompt = format_for_openai_account(account_info)
                        openai_response_account = generate_openai_response(formatted_account_prompt, name)
                        st.markdown(f"<div class='user_prompt'>👤 <strong>You:</strong><br>{formatted_account_prompt}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='ai_response'>🤖 <strong>NearVision AI:</strong><br>{openai_response_account}</div>", unsafe_allow_html=True)
                    else:
                        st.error("Failed to fetch account information.")
                if account_id:
                    # Fetching and displaying inventory information
                    inventory_info = fetch_inventory_info(account_id)
                    if inventory_info:
                        formatted_inventory_prompt = format_for_openai_inventory(inventory_info)
                        openai_response_inventory = generate_openai_response(formatted_inventory_prompt, name)
                        st.markdown(f"<div class='user_prompt'>👤 <strong>You:</strong><br>{formatted_inventory_prompt}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='ai_response'>🤖 <strong>NearVision AI:</strong><br>{openai_response_inventory}</div>", unsafe_allow_html=True)
                        # Generate a summary prompt based on the consolidated responses
                        summary_prompt = generate_summary_prompt(openai_response_key, openai_response_account, openai_response_inventory)

                        # Generate a summary response from OpenAI
                        openai_summary_response = generate_openai_response(summary_prompt, name)

                        # Display the summary response
                        st.markdown(f"<h3 style='text-align: center; color: #b34317;'>📈 Account Activity Analysis & Prediction</h3>", unsafe_allow_html=True)
                        st.markdown(f"<div class='ai_response_summary'>🤖 <strong>NearVision AI Summary and Activity Prediction:</strong><br>{openai_summary_response}</div>", unsafe_allow_html=True)
                    else:
                        st.error("Failed to fetch inventory information.")
            else:
                st.error("No key information found for the provided public key.")