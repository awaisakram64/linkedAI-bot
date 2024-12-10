import requests
# import json
# from pathlib import Path

# ssh_path = Path('ssh')

# linkedin_token = json.loads(open(ssh_path / 'linkedin_creds.json').read())

def refresh_linkedin_token(linkedin_token):
    """
    Refresh LinkedIn OAuth access token
    
    Returns:
        dict: Token refresh response
    """
    
    print('Refreshing LinkedIn token')
    
    # LinkedIn OAuth token refresh endpoint
    url = 'https://www.linkedin.com/oauth/v2/accessToken'
    
    # Request payload
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': linkedin_token['refresh_token'],
        'client_id': linkedin_token['client_id'],
        'client_secret': linkedin_token['client_secret']
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        # Send POST request
        response = requests.post(url, data=payload, headers=headers)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse and return JSON response
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error refreshing token: {e}")
        return None

# # Example usage
# def main():
#     # Refresh the token
#     token_response = refresh_linkedin_token(linkedin_token)
    
#     if token_response:
#         print("Token Refresh Successful:")
#         print(f"Access Token: {token_response.get('access_token')}")
#         print(f"Expires In: {token_response.get('expires_in')} seconds")

# if __name__ == '__main__':
#     main()