from datetime import datetime
import openai
from streamlit import secrets  # Import secrets to access your API key
import re  # Import regular expression module
import base64

def format_for_openai(key_info):
    """Format key information for OpenAI prompt."""
    if not key_info or "keys" not in key_info or len(key_info["keys"]) == 0:
        return "No key information available."

    key_entry = key_info["keys"][0]
    account_id = key_entry.get("account_id", "Unknown")
    name = account_id.split(".")[0]  # Extracting name from account_id

    permission_kind = key_entry.get("permission_kind", "Unknown")
    transaction_hash = key_entry["created"].get("transaction_hash", "Unknown")
    
    block_timestamp = key_entry["created"].get("block_timestamp", "Unknown")
    if block_timestamp != "Unknown":
        block_timestamp = datetime.utcfromtimestamp(block_timestamp / 1e9).strftime('%Y-%m-%d %H:%M:%S UTC')

    deleted = "not deleted" if key_entry["deleted"].get("transaction_hash") is None else "deleted"

    # Format the input for OpenAI with a clearer introduction
    prompt = f"Hi {name},\n\n"  # Personalized greeting
    prompt = f"Hi {name}, here's a summary of your NEAR account information:\n\n"
    prompt += f"- Account ID: {account_id}\n"
    prompt += f"- Permission Kind: {permission_kind}\n"
    prompt += f"- Transaction Hash: {transaction_hash}\n"
    prompt += f"- Block Timestamp: {block_timestamp}\n"
    prompt += f"- Key Status: {deleted}\n"
    prompt += "\nPlease explain this information in a simple and clear manner."

    return prompt

def format_for_openai_inventory(inventory_info):
    """Format inventory information for OpenAI prompt."""
    if not inventory_info or "inventory" not in inventory_info:
        return "No inventory information available."

    prompt = "Here's your NEAR account inventory information:\n\n"
    for item_type in ['fts', 'nfts']:  # Handle both Fungible Tokens (FTs) and Non-Fungible Tokens (NFTs)
        items = inventory_info["inventory"].get(item_type, [])
        if items:
            prompt += f"- {item_type.upper()}:\n"
            for item in items:
                prompt += f"  - Name: {item.get('name', 'Unknown')}, Quantity: {item.get('amount', 'Unknown')}\n"
        else:
            prompt += f"- No {item_type.upper()} found.\n"

    prompt += "\nPlease explain this information in simple terms."
    return prompt

def decode_base64_to_file(base64_string, output_path):
    """Decode base64 string to a file."""
    with open(output_path, "wb") as output_file:
        decoded_data = base64.b64decode(base64_string.split(",")[1])
        output_file.write(decoded_data)

def format_for_openai_account(account_info):
    """Format account information for OpenAI prompt."""
    if not account_info or "account" not in account_info or len(account_info["account"]) == 0:
        return "No account information available."

    account_entry = account_info["account"][0]
    name = account_entry.get("account_id", "").split(".")[0]

    amount = account_entry.get("amount", "Unknown")
    block_hash = account_entry.get("block_hash", "Unknown")
    block_height = account_entry.get("block_height", "Unknown")
    code_hash = account_entry.get("code_hash", "Unknown")
    storage_paid_at = account_entry.get("storage_paid_at", "Unknown")
    storage_usage = account_entry.get("storage_usage", "Unknown")

    prompt = f"Hi {name},\n\nHere's a detailed summary of your NEAR account:\n\n"
    prompt += f"- Account ID: {account_entry.get('account_id', 'Unknown')}\n"
    prompt += f"- Balance: {amount} testnet tokens\n"
    prompt += f"- Block Hash: {block_hash}\n"
    prompt += f"- Block Height: {block_height}\n"
    prompt += f"- Code Hash: {code_hash}\n"
    prompt += f"- Storage Paid At: {storage_paid_at}\n"
    prompt += f"- Storage Usage: {storage_usage} bytes\n\n"
    prompt += "Please provide a concise explanation of this information."

    return prompt

def generate_summary_prompt(key_response, account_response, inventory_response):
    """Format a summary prompt for OpenAI based on key, account, and inventory information, and ask for an activity prediction."""
    prompt = "Analyze the following details about a NEAR account and predict the account's activity status (Active/Inactive):\n\n"
    prompt += "1. Security Status (based on key information):\n" + key_response + "\n\n"
    prompt += "2. Asset Holdings (from inventory information):\n" + inventory_response + "\n\n"
    prompt += "3. Transaction Activity (derived from account information):\n" + account_response + "\n\n"
    prompt += "4. Overall Account Health (combining all aspects).\n\n"
    prompt += "Please provide a concise summary of the account's activity, focusing on key aspects such as security, asset holdings, and overall account health. Conclude with a prediction of the account's activity status (Active/Inactive)."
    return prompt

def format_stats_for_prompt(stats, network):
    """Format NEAR network stats for OpenAI prompt."""
    prompt = f"Here's a detailed summary of the {network} NEAR network stats:\n\n"
    for key, value in stats.items():
        prompt += f"- {key.replace('_', ' ').title()}: {value}\n"
    # Encourage a conclusive statement at the end
    prompt += "\n Can you provide a concise and complete explanation of this information, ensuring to conclude any points made?,and also ensure that no sentence is incomplete and it should end as a complete sentence."
    return prompt

def generate_ai_response(prompt, api_key):
    """Generate a response from OpenAI based on the given prompt."""
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=600,  # Adjust max_tokens if necessary
        temperature=0.5,  # Lower for more deterministic responses
    )
    return response.choices[0].text.strip()
    
def generate_ai_response_with_icons(prompt, api_key, fts=None, nfts=None):
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=600,  # Adjust max_tokens if necessary
        temperature=0.5,  # Lower for more deterministic responses
    )
    text_response = response.choices[0].text.strip()

    # Start the HTML for the table and initialize a counter
    icon_html = '<table>'
    counter = 0

    # Helper function to add an icon cell
    def add_icon_cell(item, item_type):
        nonlocal counter, icon_html
        icon = item.get("icon")
        name = item.get("name")
        if counter % 4 == 0:  # Check if we need to start a new row
            if counter > 0:  # Close the previous row if it's not the first entry
                icon_html += '</tr>'
            icon_html += '<tr>'  # Start a new row
        # Add the cell for the icon
        if icon and "data:image" in icon:
            icon_html += f'<td style="text-align: center;">{item_type} icon:<br><img src="{icon}" style="max-width: 100px; max-height: 100px;"><br>{name}</td>'
        else:
            icon_html += f'<td style="text-align: center;">{item_type} icon:<br>[Image cannot be displayed]<br>{name}</td>'
        counter += 1

    # Process FT icons and names
    for ft in fts:
        add_icon_cell(ft, "FT")

    # Process NFT icons and names
    for nft in nfts:
        add_icon_cell(nft, "NFT")

    # Close the HTML table if any icons were added
    if counter > 0:
        icon_html += '</tr></table>'

    # Append the HTML table to the response text
    text_response += icon_html

    return text_response
    

def format_stats_for_prompt(summary):
    prompt = f"Given the analysis summary of NEAR-USD cryptocurrency with the following key metrics:\n{summary}\nWhat is the potential investment outcome over the next period? Please categorize the outcome as 'Higher Profit', 'Slight Profit', 'Slight Loss', or 'Higher Loss'."
    return prompt

def format_stats_for_prompt_home(stats, network):
    # Assuming 'name' is available within the scope, or replace with appropriate variable

    # Start building the prompt with a personalized greeting
    prompt = f"Hi {network} user,\n\nHere's a detailed summary of the {network} NEAR network stats:\n\n"

    # Add stats information in key-value format
    for key, value in stats.items():
        # Format the key a bit better by replacing underscores with spaces and capitalizing words
        formatted_key = ' '.join(word.capitalize() for word in key.replace('_', ' ').split())
        prompt += f"- {formatted_key}: {value}\n"

    # Add a closing sentence to the prompt
    prompt += "\nCan you provide a concise and complete explanation of this information, ensuring to conclude any points made?"
    return prompt

def format_smart_contract_info(contract_info):
    """Formats the smart contract information into a structured summary with a maximum of 10 keys displayed."""
    if not contract_info or "contract" not in contract_info or len(contract_info["contract"]) == 0:
        return "No smart contract information available."

    summary = "Hi, here's a detailed summary of your NEAR smart contract:\n"
    contract_keys = contract_info["contract"][0].get("keys", []) if isinstance(contract_info["contract"], list) and len(contract_info["contract"]) > 0 else []

    # Limit to displaying details of the first 10 keys
    for idx, entry in enumerate(contract_keys[:5], start=1):
        public_key = entry.get("public_key", "Unknown")
        access_key = entry.get("access_key", {})
        nonce = access_key.get("nonce", "Unknown")
        permission = access_key.get("permission", {})
        permission_type = "Unknown"

        if isinstance(permission, dict) and "FunctionCall" in permission:
            permission_type = "FunctionCall"
            allowance = permission["FunctionCall"].get("allowance", "Unknown")
            receiver_id = permission["FunctionCall"].get("receiver_id", "Unknown")
            method_names = ", ".join(permission["FunctionCall"].get("method_names", [])) or "None"
        elif isinstance(permission, str):
            permission_type = permission

        summary += f"\nKey {idx}:\n"  # Ensure new line before each key
        summary += f"- Public Key: {public_key}\n"
        summary += f"- Nonce: {nonce}\n"
        summary += f"- Permission Type: {permission_type}\n"

        if permission_type == "FunctionCall":
            summary += f"- Allowance: {allowance}\n"
            summary += f"- Receiver ID: {receiver_id}\n"
            summary += f"- Method Names: {method_names}\n"

    if len(contract_keys) > 5:
        summary += "\nOnly the first 5 keys are displayed for brevity. The complete summary provides details on all contracts."

    summary += "\nPlease provide a concise explanation of this information."
    return summary

def smart_contract_information(contract_info):
    """Generate a structured sentence for smart contract information."""
    if not contract_info or "contract" not in contract_info or len(contract_info["contract"]) == 0:
        return "No contract information available."

    contract_entries = contract_info["contract"]
    total_keys = sum(len(entry.get("keys", [])) for entry in contract_entries)
    full_access_keys = [key for entry in contract_entries for key in entry.get("keys", []) if "access_key" in key and key["access_key"].get("permission") == "FullAccess"]
    function_call_keys = [key for entry in contract_entries for key in entry.get("keys", []) if "access_key" in key and "permission" in key["access_key"] and "FunctionCall" in key["access_key"]["permission"]]
    method_names = [method for key in function_call_keys for method in key["access_key"]["permission"]["FunctionCall"].get("method_names", [])]

    # Constructing the prompt
    prompt = f"Hi there,\n\nHere's a detailed summary of the smart contract associated with the account:\n\n"
    prompt += f"- Total Access Keys: {total_keys}\n"
    prompt += f"- Full Access Keys: {len(full_access_keys)}\n"
    prompt += f"- Function Call Keys: {len(function_call_keys)}\n"

    if method_names:
        unique_methods = set(method_names)
        prompt += f"- Callable Methods: {', '.join(unique_methods)}\n"
    else:
        prompt += "- Callable Methods: None\n"

    prompt += "This summary indicates the permissions and capabilities set within the smart contract's access keys. Full access keys provide unrestricted access, while function call keys may limit interactions to specific contract methods. A lack of callable methods suggests broader permissions for those keys. Please provide a concise explanation of this information."

    # Call OpenAI API to generate a response based on the prompt
    api_key = secrets["API_KEY"]  # Access API key from secrets
    response = generate_ai_response(prompt, api_key)
    return response

def format_deployments_for_openai(deployments_info):
    """Formats the contract deployments information for OpenAI prompt."""
    if not deployments_info or "deployments" not in deployments_info or len(deployments_info["deployments"]) == 0:
        prompt = "No contract deployments have been found."
    else:
        prompt = "Hi there, here's a detailed summary of the smart contract deployments:\n\n"
        for idx, deployment in enumerate(deployments_info["deployments"], start=1):
            transaction_hash = deployment.get('transaction_hash', 'Unknown')
            block_timestamp = datetime.utcfromtimestamp(int(deployment.get('block_timestamp', '0')) / 1e9).strftime('%Y-%m-%d %H:%M:%S UTC')
            receipt_predecessor_account_id = deployment.get('receipt_predecessor_account_id', 'Unknown')

            prompt += f"Deployment {idx}:\n"
            prompt += f"- Transaction Hash: {transaction_hash}\n"
            prompt += f"- Block Timestamp: {block_timestamp}\n"
            prompt += f"- Receipt Predecessor Account ID: {receipt_predecessor_account_id}\n\n"

        prompt += "Please provide a concise explanation of this deployment information."
    return prompt

def format_inventory_for_openai(inventory_info):
    # Check if there's any inventory information
    if not inventory_info or "inventory" not in inventory_info or (not inventory_info["inventory"]["fts"] and not inventory_info["inventory"]["nfts"]):
        # Return a user-friendly message
        return "No inventory information has been recorded for this account."
    else:
        prompt = "Hi, here's a detailed summary of the inventory:\n\n"
        total_fts = len(inventory_info["inventory"].get("fts", []))
        total_nfts = len(inventory_info["inventory"].get("nfts", []))
        combined_tokens = inventory_info["inventory"]["fts"][:5] + inventory_info["inventory"]["nfts"][:5]  # Adjust number here if you want more or less
        displayed_tokens = 0

        for token in combined_tokens:
            if displayed_tokens >= 10:
                break  # Exit loop after 10 tokens
            if 'ft_metas' in token:
                prompt += f"FT: {token['ft_metas']['name']} ({token['ft_metas']['symbol']})\n\n"
                prompt += f"- Amount: {token['amount']}\n\n"
                icon_available = "Icon available." if token['ft_metas'].get('icon') else "No icon available for this token."
                prompt += f" - {icon_available}\n\n"
            else:
                prompt += f"NFT: {token['nft_meta']['name']} ({token['nft_meta']['symbol']})\n\n"
                prompt += f"- Quantity: {token['quantity']}\n\n"
                icon_available = "Icon available." if token['nft_meta'].get('icon') else "No icon available for this NFT."
                prompt += f" - {icon_available}\n\n"
            displayed_tokens += 1

        # Add summary details at the end
        prompt += f"Due to brevity, only the first {displayed_tokens} tokens are displayed here.\n\n"
        prompt += f"There are a total of {total_fts} fungible tokens (FTs) and {total_nfts} non-fungible tokens (NFTs) in the inventory.\n\n"
        prompt += "Please provide a concise explanation of this inventory information."

    return prompt

def generate_deployments_summary(deployments_info, api_key):
    if not deployments_info or "deployments" not in deployments_info or len(deployments_info["deployments"]) == 0:
        return "No smart contract deployments have been recorded for this account."
    prompt = format_deployments_for_openai(deployments_info)

    # If the prompt indicates no deployments found, set a default structured response
    if prompt == "No contract deployments have been found.":
        return "No smart contract deployments have been recorded for this account."
    
    # Define a regular expression pattern to detect unexpected code snippets or irrelevant content
    pattern = re.compile(r'exports\.|\}\);|res\.status|json\(|\);')

    response = generate_ai_response(prompt, api_key)

    # Check if the response matches the pattern of unexpected content
    if pattern.search(response):
        # If unexpected content is detected, provide a default structured response
        structured_response = "The analysis did not identify any smart contract deployments associated with this account. Please verify the account details or try again later."
    else:
        # If the response is clean, use it as the structured response
        structured_response = response

    return structured_response

def format_tokens_for_openai(tokens_info):
    # Check if there's any token information
    if not tokens_info or "tokens" not in tokens_info or (not tokens_info["tokens"]["fts"] and not tokens_info["tokens"]["nfts"]):
        # Return a user-friendly message
        return "There is no token information for this particular account."
    else:
        prompt = "Hi, here's a summary of tokens associated with the account:\n\n"
        total_fts = len(tokens_info["tokens"].get("fts", []))
        total_nfts = len(tokens_info["tokens"].get("nfts", []))
        combined_tokens = tokens_info["tokens"]["fts"][:5] + tokens_info["tokens"]["nfts"][:5]  # Adjust number here if you want more or less
        displayed_tokens = 0

        for token in combined_tokens:
            if displayed_tokens >= 5:
                break  # Exit loop after 5 tokens
            if isinstance(token, dict) and 'name' in token:  # Assuming the token is a dictionary with a 'name' key
                prompt += f"- {token['name']}: {token.get('amount', 'N/A')}\n\n"
            else:
                prompt += f"- {token}\n\n"  # Fallback if token is not a dictionary or does not have 'name'
            displayed_tokens += 1

        # Add summary details at the end
        prompt += f"Due to brevity, only the first {displayed_tokens} tokens are displayed here.\n\n"
        prompt += f"There are a total of {total_fts} fungible tokens (FTs) and {total_nfts} non-fungible tokens (NFTs) associated with the account.\n\n"
        prompt += "Please provide a concise explanation of this token information."

    return prompt

def generate_summary_with_openai(summary_prompt, api_key):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=summary_prompt,
        max_tokens=600,  # Adjust as needed
        temperature=0.5,
        api_key=api_key
    )
    return response.choices[0].text.strip()

def generate_summary_with_openai_transactions(summary_prompt, api_key):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=summary_prompt,
        max_tokens=600,  # Adjust as needed
        temperature=0.5,
        api_key=api_key
    )
    return response.choices[0].text.strip()

def generate_network_summary_prompt(stats_data, fts_count, fts_txns_count, nfts_count, nfts_txns_count, avg_block_time, unique_block_producers, market_cap, volume):
    # Format market cap and volume as currency
    formatted_market_cap = f"${market_cap:,.2f}"
    formatted_volume = f"${volume:,.2f}"

    # Construct the prompt with the additional data
    prompt = (
        "NEAR Blockchain Health Overview:\n\n"
        f"- Online Nodes: {stats_data['nodes_online']}\n\n"
        f"- Total Transactions: {stats_data['total_txns']}\n\n"
        f"- Fungible Tokens Count: {fts_count}\n\n"
        f"- Fungible Tokens Transactions Count: {fts_txns_count}\n\n"
        f"- Non-Fungible Tokens Count: {nfts_count}\n\n"
        f"- Non-Fungible Tokens Transactions Count: {nfts_txns_count}\n\n"
        f"- Average Block Time: {avg_block_time:.2f} seconds\n\n"
        f"- Unique Block Producers: {unique_block_producers}\n\n"
        f"- Market Cap: {formatted_market_cap}\n\n"
        f"- Volume: {formatted_volume}\n\n"
        "Based on the above metrics, provide an analysis of the current health and utilization of the NEAR blockchain network. "
        "Categorize the overall health as 'Excellent', 'Good', 'Moderate', or 'Poor' and explain the reasoning behind your categorization."
    )

    return prompt

def generate_ai_response_anomaly(prompt, api_key):
    """Generate a response from OpenAI based on the given prompt."""
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=800,  # Adjust max_tokens if necessary
        temperature=0.5,  # Lower for more deterministic responses
    )
    return response.choices[0].text.strip()

def generate_anomaly_analytics_prompt(anomaly_dates):
    anomaly_months = [date.strftime('%B %Y') for date in anomaly_dates]
    month_counts = {month: anomaly_months.count(month) for month in set(anomaly_months)}

    sorted_months = sorted(month_counts.items(), key=lambda x: datetime.strptime(x[0], "%B %Y"))

    prompt_parts = []
    for i, (month, count) in enumerate(sorted_months):
        entry = f"{month}: {count} anomalies detected.\n"
        entry += f" ➢ Reason: [Insert brief reason]\n"
        entry += f" ➢ Mitigation: [Insert single step]\n"

        # Add a newline at the beginning of each entry after the first
        if i > 0:
            entry = "\n\n" + entry

        prompt_parts.append(entry)

    # Start with an introduction and append all parts
    prompt = "Provide a concise analysis for each month's detected anomalies in NEAR-USD trading, including a brief reason and a single mitigation step. Here's the data:\n\n" + "".join(prompt_parts)
    prompt += "\n\nFocus on brevity and clarity in your analysis and recommendations."

    return prompt