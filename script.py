import os
import requests

# Retrieve variables from environment variables
windchill_url = os.environ.get('WINDCHILL_URL')        # Base URL of your Windchill server
username = os.environ.get('WINDCHILL_USERNAME')        # Your Windchill username
password = os.environ.get('WINDCHILL_PASSWORD')        # Your Windchill password
part_id = 'OR:wt.part.WTPart:44148884'                 # The Part ID you want to fetch the BOM for
navigation_criteria_id = 'OR:wt.filter.NavigationCriteria:186213'  # Navigation Criteria ID

# Check if essential environment variables are set
if not all([windchill_url, username, password]):
    raise EnvironmentError("Please set the WINDCHILL_URL, WINDCHILL_USERNAME, and WINDCHILL_PASSWORD environment variables.")

# Disable warnings for self-signed certificates if necessary (use with caution)
# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# session.verify = False  # Uncomment this line if you need to disable SSL verification

# Create a session to persist cookies and authentication
session = requests.Session()
session.auth = (username, password)

# If your Windchill server uses form-based authentication, you may need to perform a login
login_url = f"{windchill_url}/Windchill/j_security_check"
login_data = {
    'j_username': username,
    'j_password': password
}
login_response = session.post(login_url, data=login_data)
login_response.raise_for_status()

# Check if login was successful
if 'j_security_check' in login_response.url or login_response.status_code != 200:
    raise Exception("Login failed. Check your credentials.")

# Fetch CSRF NONCE token
csrf_url = f"{windchill_url}/Windchill/servlet/odata/PTC/GetCSRFToken()"
csrf_response = session.get(csrf_url)
csrf_response.raise_for_status()
csrf_data = csrf_response.json()
csrf_nonce = csrf_data['NonceValue']
csrf_key = csrf_data['NonceKey']

# Set headers with the CSRF token
headers = {
    'Content-Type': 'application/json',
    csrf_key: csrf_nonce,
}

# Construct the endpoint URL
endpoint = f"/Windchill/servlet/odata/ProdMgmt/Parts('{part_id}')/PTC.ProdMgmt.GetBOM"
url = f"{windchill_url}{endpoint}"

# Define query parameters
params = {
    '$expand': 'Components($expand=Part($select=Name,Number),PartUse,Occurrences;$levels=max)'
}

# Define the request body
request_body = {
    "NavigationCriteria": {"ID": navigation_criteria_id}
}

# Make the POST request to get the BOM
response = session.post(url, headers=headers, json=request_body, params=params)
response.raise_for_status()  # Check for HTTP errors

# Parse the response JSON data
bom_data = response.json()

# Print the BOM data
print(bom_data)
