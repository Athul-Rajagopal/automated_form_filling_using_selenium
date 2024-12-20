import os
import time
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from bson import ObjectId
import uuid

from PyPDF2 import PdfReader, PdfWriter


# Load environment variables
load_dotenv()

# AWS credentials and S3 configuration
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_REGION = os.getenv('AWS_REGION')

# print({"accesskey": AWS_ACCESS_KEY, "secret": AWS_SECRET_KEY, "bucket": S3_BUCKET_NAME, "region": S3_REGION})

def upload_to_s3(file_path, file_name):
    """
    Uploads a file to S3 and returns the public URL.
    """
    try:
        # Generate a unique filename by appending a UUID
        unique_filename = f"{uuid.uuid4()}_{file_name}"
        
        # Initialize the S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=S3_REGION
        )
        
        # Upload the file
        s3_client.upload_file(file_path, S3_BUCKET_NAME, unique_filename, ExtraArgs={'ContentType': 'application/pdf'})
        print(f"Successfully uploaded {file_path} to S3 as {unique_filename}.")

        # Generate the file URL
        file_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{unique_filename}"
        return file_url

    except Exception as e:
        error_message = f"Failed to upload to S3: {str(e)}"
        print(error_message)
        return {"success": False, "error": error_message}

    
    
# removing unwanted pages
def remove_first_four_pages(input_pdf_path, output_pdf_path):
    """
    Remove the first four pages from a PDF.
    
    :param input_pdf_path: Path to the input PDF.
    :param output_pdf_path: Path to save the modified PDF.
    """
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Copy all pages except the first four
    for page_num in range(4, len(reader.pages)):
        writer.add_page(reader.pages[page_num])

    with open(output_pdf_path, 'wb') as output_pdf:
        writer.write(output_pdf)




def wait_for_downloads(download_dir, timeout=300):
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
                    modified_file_path = os.path.join(download_dir, f"modified_{filename}")
                    
                    # Check if the file is still being written to
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        time.sleep(1)  # Wait a moment to see if it is still downloading
                        if os.path.getsize(file_path) > 0:  # Still has content
                            print(f"Downloaded: {filename}")

                            
                            # Remove the first four pages of the PDF
                            # remove_first_four_pages(file_path, modified_file_path)
                            # print("removed 4 pages")
                            
                             # Upload the file to S3
                            file_url = upload_to_s3(file_path, filename)
                            print("file uploaded")
                            if file_url:
                                # Generate a unique ObjectId for the document
                                document_id = str(ObjectId())
                                

                                # Clean up local files after upload
                                os.remove(file_path)
                                # os.remove(modified_file_path)

                                # Return ObjectId and file URL
                                return {
                                    "success": True,
                                    "document_id": document_id,
                                    "s3_link": file_url
                                }
                                

                                
                            else:
                                os.remove(file_path)
                                os.remove(modified_file_path)
                                

                                return {
                                    "success": False,
                                    "error": upload_result['error']
                                }
                            
        time.sleep(1)  # Wait before checking again
        seconds_elapsed += 1
    print("Download did not complete in the expected time frame.")
    return {
        "success": False,
        "error": "Download did not complete in the expected time frame."
    }