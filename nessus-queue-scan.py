# Standard library imports
import json
import os
import sys
import time
import urllib3

# Third-party imports
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Suppress SSL/TLS warnings (InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define the path to the .env file in the same directory as the Python script
script_dir = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(script_dir, '.env')

# Check if the .env file exists
if not os.path.exists(env_file_path):
    print(f"Error: The '.env' file does not exist.")
    print("Creating an example '.env' file with the required variables...")

    # Example .env content with placeholder values
    example_env_content = """# Example .env file

# Required environment variables for the app
NESSUS_BASE_URL=\"your_nessus_url_and_port\"
# Access & secret key is obtained from Nessus API dashboard generator
ACCESS_KEY=\"your_access_key_here\"
SECRET_KEY=\"your_secret_key_here\"
NESSUS_USER=\"your_nessus_username_here\"
NESSUS_PASSWORD=\"your_nessus_password_here\"
"""

    # Write the example .env content to a new .env file
    with open(env_file_path, 'w') as f:
        f.write(example_env_content)

    print(f"An example '.env' file has been created at '{env_file_path}'. Please fill in the appropriate values.")
    sys.exit(1)  # Exit after creating the .env file

# If the .env file exists, load environment variables from it
load_dotenv()

# List of required environment variables
required_vars = [
    "ACCESS_KEY",
    "SECRET_KEY",
    "NESSUS_BASE_URL",
    "NESSUS_USER",
    "NESSUS_PASS"
]
# API keys provided
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
NESSUS_USER = os.getenv("NESSUS_USER")
NESSUS_PASS = os.getenv("NESSUS_PASS")
NESSUS_BASE_URL = os.getenv("NESSUS_BASE_URL")

# Check if all required variables are set
for var in required_vars:
    if not os.getenv(var):
        print(f"Error: The environment variable '{var}' is not set.")
        sys.exit(1)  # Exit with a non-zero status code

# Headers for authentication
HEADERS = {
    "X-ApiKeys": f"accessKey={ACCESS_KEY}; secretKey={SECRET_KEY}",
    "Content-Type": "application/json"
}

def list_scans():
    """Fetches a list of all Nessus scans from the API 
    and returns it as a formatted JSON string."""

    url = f"{NESSUS_BASE_URL}/scans"
    response = requests.get(url, headers=HEADERS, verify=False)
    if response.status_code == 200:
        scans = response.json()
        return json.dumps(scans, indent=2)
    else:
        print(f"Error listing scans: {response.status_code}")

def launch_scan(scan_id):
    "Triggers the launch of a specific Nessus scan by its scan ID."

    host_url = f"{NESSUS_BASE_URL}/#/scans/reports/{scan_id}/hosts"

    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)

    # Wait for the page to load completely 
    time.sleep(3)
    driver.get(host_url)

    # Wait for the page to load completely
    time.sleep(3)

    # Find the username and password input fields and the sign-in button
    username_input = driver.find_element(By.CLASS_NAME, "login-username")
    password_input = driver.find_element(By.CLASS_NAME, "login-password")
    sign_in_button = driver.find_element(By.CSS_SELECTOR, "button[data-domselect='sign-in']")

    # Simulate typing in the username and password fields
    username_input.send_keys(NESSUS_USER)
    password_input.send_keys(NESSUS_PASS)

    # Click the "Remember Me" 
    remember_me_checkbox = driver.find_element(By.CLASS_NAME, "login-remember")
    remember_me_checkbox.click() 

    # Submit the form by clicking the sign-in button
    sign_in_button.click()

    # wait until scan detail loaded
    time.sleep(10)
    driver.find_element("id", "launch").click()
    time.sleep(10)
    try:
        # Wait for the element to be visible (adjust the selector if necessary)
        status_element = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='right-column-section']//span[text()='Status:']/following-sibling::span"))
        )

        # Get the text content of the status element
        status_text = status_element.text.strip()
        # Check if the status is running
        if status_text.lower() == "running":
            print(f"Scan ID {scan_id} is Running. Closing the browser.")
            driver.quit()
        else:
            print(f"Status is not running. It is: {status_text}")
    finally:
        pass

def monitor_scan(scan_id):
    """
    Monitor the status of a scan with the given scan_id
    Continually check the scan's status by calling `list_scans` until it's completed.
    """
    while True:
        print(f"Checking status of Scan ID {scan_id}...")

        # Fetch the current scan status
        list_scan_result = list_scans()
        data = json.loads(list_scan_result)
        scans = data.get("scans", [])

        # Find the scan with the given ID
        scan = next((scan for scan in scans if scan['id'] == scan_id), None)

        if scan:
            scan_status = scan.get("status")
            if scan_status == "completed":
                #print(f"Scan with ID {scan_id} is completed.")
                return True
            else:
                if scan_status == "empty":
                    print(f"Launching scan for id {scan_id}")
                    launch_scan(scan_id)
                #else:
                    #print(f"Scan with ID {scan_id} is in status: {scan_status}. Rechecking...")
        else:
            print(f"Scan with ID {scan_id} not found.")

        # Wait a short period before checking again
        time.sleep(5)


# Main function
def main():
    print("Listing available scan information...")

    # Fetch the list of scans
    list_scan_result = list_scans()
    data = json.loads(list_scan_result)
    scans = data.get("scans", [])

    # Display available scans
    for scan in scans:
        scan_id = scan.get("id")
        scan_name = scan.get("name")
        scan_status = scan.get("status")
        print(f"ID: {scan_id}, Name: {scan_name}, Status: {scan_status}")

    input_ids = input("Enter the IDs of scans to monitor (comma-separated): ")
    ids_to_monitor = [int(id.strip()) for id in input_ids.split(',')]
    for selected_id in ids_to_monitor:
        # Monitor the selected scan's status
        if monitor_scan(selected_id):
            print(f"Scan with ID {selected_id} is completed. Moving to next scan...")
        else:
            print(f"Scan with ID {selected_id} could not be monitored.")

    print("All selected scans have been checked.")

if __name__ == "__main__":
    main()
