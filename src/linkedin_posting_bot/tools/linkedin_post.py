import re
import json
import requests
from pathlib import Path

class Posts():
    """Class to create a Post object for LinkedIn and post it on LinkedIn (Personal Profile or Organization Page)"""

    def __init__(self, author_id, post_text, token, post_headline='', media_url=None, media_title='', visibility="PUBLIC", lifecycleState="PUBLISHED", is_page=False) -> None:
        """Setting required parameters"""
        
        self.base_url = 'https://api.linkedin.com/rest'
        self.post_headline = post_headline
        self.post_text = post_text
        self.token = token
        self.is_page = is_page  # Flag to determine if the post is for a page
        self.author = f"urn:li:person:{author_id}" if not is_page else f"urn:li:organization:{author_id}"
        self.visibility = visibility  # ['CONNECTIONS', 'PUBLIC', 'LOGGED_IN', 'CONTAINER']
        self.lifecycleState = lifecycleState  # ['DRAFT', 'PUBLISHED', 'PUBLISH_REQUESTED', 'PUBLISH_FAILED']
        self.media_url = media_url
        self.media_title = media_title
        self.distribution = {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        }
        self.media_urn = None
        self.post_response_headers = None

    def create_post(self):
        """Create a LinkedIn post for either a personal profile or a page"""
        if self.media_url:
            self.media_urn = self.upload_image()
        payload = self.create_post_payload()
        url = f'{self.base_url}/posts'
        try:
            response = self.get_requests_request(
                url=url,
                method="POST",
                payload=payload
            )
            self.post_response_headers = response.headers
            print(response.status_code)
            print(response.text)
            print(response.headers)
            
            if response.ok:
                return response
        except Exception as e:
            print(f'Error: {e}')
    
    def upload_image(self):
        """Upload an image from a public URL to LinkedIn"""
        # Step 1: Initialize the upload
        url = f"{self.base_url}/images?action=initializeUpload"
        payload = {"initializeUploadRequest": {"owner": self.author}}
        response = self.get_requests_request(url, payload=payload, method="POST")
        upload_url = response.json()['value']['uploadUrl']
        image_urn = response.json()['value']['image']
        
        # Step 2: Upload the image data
        image_response = requests.get(self.media_url, stream=True, verify=False)
        if not image_response.ok:
            raise Exception(f"Failed to download image from URL: {image_response.status_code}")
        upload_response = requests.put(upload_url, data=image_response.content)
        if not upload_response.ok:
            raise Exception(f"Image upload failed: {upload_response.text}")
        print("Image uploaded successfully.")
        
        return image_urn

    def get_post_by_urn(self):
        """Retrieve a post by its URN"""
        urn_of_recent_post = self.post_response_headers['x-linkedin-id']
        url = f"{self.base_url}/post/{urn_of_recent_post}"
        print(url)
        response = self.get_requests_request(url=url)
        return response

    def get_auth_headers(self):
        """Generate authorization headers"""
        headers = {
            'Authorization': f'Bearer {self.token}',
            'LinkedIn-Version': '202404',
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        return headers

    def get_requests_request(self, url, payload=None, method='GET', **params):
        """Handle HTTP requests"""
        headers = self.get_auth_headers()
        response = requests.request(
            url=url, method=method,
            headers=headers, params=params,
            json=payload
        )
        if not response.ok:
            print(response.text)
            response.reason
            print(response.headers)
            raise Exception(response)
        return response

    def create_post_payload(self):
        """Merge elements to create a LinkedIn post"""
        post_dict_obj = {}
        post_dict_obj['author'] = self.author
        post_dict_obj['commentary'] = self.complete_post_text()
        post_dict_obj["visibility"] = self.visibility
        post_dict_obj["distribution"] = self.distribution
        post_dict_obj["lifecycleState"] = self.lifecycleState
        if self.is_page:
            # For LinkedIn pages, use UGC-specific fields
            # post_dict_obj["lifecycleState"] = self.lifecycleState
            pass
        else:
            # For personal profiles
            pass
            # post_dict_obj["lifecycleState"] = self.lifecycleState
            # post_dict_obj['isReshareDisabledByAuthor'] = False
        if self.media_urn:
            post_dict_obj['content'] = {
                "media": {
                    "altText": self.media_title,
                    "id": self.media_urn,
                }
            }
        return post_dict_obj

    def complete_post_text(self):
        
        bold_headline = ''
        if self.post_headline:
            bold_headline = self.bold_text(self.post_headline)
        
        complete_post = f"{bold_headline} \n\n{self.post_text}"
        
        return self.formate_commentary_text(complete_post)
    
    def formate_commentary_text(self, post_text):
        """Format text according to LinkedIn requirements"""
        return re.sub(r'[{}@[\]()<>#*_~\\]', r'\\\g<0>', post_text)
    
    def bold_text(self, text: str) -> str:
        """
        Convert regular text to bold using Unicode bold characters.
        """
        bold_unicode_start = 0x1D400  # Unicode start for bold A
        bold_text = ""
        for char in text:
            if "A" <= char <= "Z":  # Uppercase letters
                bold_text += chr(bold_unicode_start + (ord(char) - ord("A")))
            elif "a" <= char <= "z":  # Lowercase letters
                bold_text += chr(bold_unicode_start + (ord(char) - ord("a") + 26))
            else:
                bold_text += char  # Non-alphabetic characters remain unchanged
        return bold_text

