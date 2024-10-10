import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_downloads(download_dir, timeout=60):
    """
    Wait until all files in the download directory are downloaded.

    :param download_dir: Directory where downloads are saved.
    :param timeout: Maximum time to wait for downloads (in seconds).
    """
    seconds_elapsed = 0
    while seconds_elapsed < timeout:
        # Check for any files in the download directory
        if any(filename.endswith('.pdf') for filename in os.listdir(download_dir)):
            # If a PDF file is found, wait for it to finish downloading
            for filename in os.listdir(download_dir):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(download_dir, filename)
                    # Check if the file is still being written to
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        time.sleep(1)  # Wait a moment to see if it is still downloading
                        if os.path.getsize(file_path) > 0:  # Still has content
                            print(f"Downloaded: {filename}")
                            return
        time.sleep(1)  # Wait before checking again
        seconds_elapsed += 1
    print("Download did not complete in the expected time frame.")