from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dropdown_helper import *
from datetime import datetime
import logging
from flask import jsonify
from download_helper import wait_for_downloads
from utils import send_failure_response
from lost_or_stolen import lost_or_stolen
from most_recent_passport_details import most_recent_passport_details
from date_calculation_helper import is_within_8_years_6_days, is_name_change_needed
from passport_both_helper import passport_both_helper
from passport_utils import passport_route_flow_helper

from selenium.webdriver.common.action_chains import ActionChains


def fill_form(user_data, webhook_url):
    chrome_options = Options()
    
    # chrome_options.page_load_strategy = 'eager'
    chrome_options.page_load_strategy = 'normal' 
    
    # download_dir = r"C:\Users\athul\Downloads\passport"  # Change this to your desired download directory
    download_dir = "/root/passport-automation/downloads"
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")  # Disable GPU rendering to avoid issues
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")  # Disable all extensions
    chrome_options.add_argument("--disable-plugins")  # Disable plugins
    chrome_options.add_argument("--disable-infobars")  # Disable infobars
    
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,  # Set download directory
        "download.prompt_for_download": False,  # Disable the download prompt
        "plugins.always_open_pdf_externally": True  # Open PDFs externally
    })

    # Use the Service class to specify the driver path
    # chrome_service = Service(r"C:\chromw\chromedriver.exe")
    chrome_service = Service("/usr/local/bin/chromedriver-linux64/chromedriver") 
    # Pass the service object to the Chrome WebDriver
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options) 
    driver.set_page_load_timeout(60)
    
    try:
# Page 1
        # Navigate to the form page
        driver.get("https://pptform.state.gov/")  
        WebDriverWait(driver, 60).until(lambda d: d.execute_script('return document.readyState') == 'complete')   
        
        # Locate the checkbox using XPath and click it
        wait = WebDriverWait(driver, 120)  # Wait up to 60 seconds
        privacy_checkbox = wait.until(EC.element_to_be_clickable((By.ID, 'chkPrivacy')))
        privacy_checkbox.click()
        
        # Locate the submit button using XPath and click it
        submit_button = wait.until(EC.element_to_be_clickable((By.ID, 'btnSubmit')))
        submit_button.click()  
   
        wait.until(EC.url_to_be("https://pptform.state.gov/PassportWizardMain.aspx"))
        
# Page 2
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_portalStep_ApplyButton"]')))
        
        form_fill_select_submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_portalStep_ApplyButton"]')))
        form_fill_select_submit_button.click()  
        
        print('waiting for page 3')
        
        
        
# Page 3
        try:
            current_url = driver.current_url
            
            print(current_url)
            
            wait.until(EC.url_to_be(current_url))
            
            # first name
            wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$firstNameTextBox'))).send_keys(user_data['personalInfo']['firstName'])
            
            # middle name
            middle_name = user_data['personalInfo'].get('middleName', '').strip()
            if middle_name:
                wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$middleNameTextBox'))).send_keys(user_data['personalInfo']['middleName'])
            
            # last name
            wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$lastNameTextBox'))).send_keys(user_data['personalInfo']['lastName'])
            
            # suffix
            suffix = user_data['personalInfo'].get('suffix')
            if suffix:
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_aboutYouStep_suffixNameTextBox"]'))).send_keys(suffix)

            # dob
            date_of_birth_str = user_data['personalInfo']['dateOfBirth']['$date']
            date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_dob = date_of_birth.strftime("%m-%d-%Y")
            wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$dobTextBox'))).send_keys(formatted_dob) 
                    
            # city of birth
            wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$pobCityTextBox'))).send_keys(user_data['personalInfo']['cityOfBirth'])
            
            # country of birth
            country_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_aboutYouStep_pobCountryList"]')))
            select_country(country_dropdown, user_data["personalInfo"]["countryOfBirth"], driver)
            
            # state of birth
            country = user_data["personalInfo"].get("countryOfBirth").upper()
            if country in ['CAN', 'USA']:

                sst = user_data["personalInfo"]
                cc = sst.get('stateOfBirth')
                print(cc)
                
                try:
                    select_country_and_state(
                        country_code=country, 
                        state_abbreviation=cc, 
                        driver=driver, 
                        country_xpath='//*[@id="PassportWizard_aboutYouStep_pobCountryList"]',  # Country dropdown XPath
                        state_xpath='//*[@id="PassportWizard_aboutYouStep_pobStateList"]'       # State dropdown XPath
                    )
                except Exception as e :
                    print(str(e))

            
            # social security number
            wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$ssnTextBox'))).send_keys(user_data['personalInfo']['socialSecurityNumber'])
            
            # gender dropdown
            gender_dropdown = wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$sexList')))  # Adjust the locator as needed
            select_gender(gender_dropdown, user_data['personalInfo']['gender'])
            
            if user_data['personalInfo'].get('changingGenderMarker', False):    
                sex_gender_marker_checkbox = wait.until(EC.element_to_be_clickable((By.ID, 'PassportWizard_aboutYouStep_SexChanging')))
                sex_gender_marker_checkbox.click() 
            
            # height data
            height_feet_dropdown = wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_aboutYouStep_heightFootList')))
            feet_height = user_data['personalInfo']['height']['feet']
            select_height_feet(height_feet_dropdown, feet_height)
                
            
            height_inches_dropdown = wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_aboutYouStep_heightInchList')))
            inches_height = user_data['personalInfo']['height']['inches']
            select_height_inches(height_inches_dropdown, inches_height)

        
            # hair color
            hair_color_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_aboutYouStep_hairList"]')))
            select_hair_color(hair_color_dropdown, user_data['personalInfo']['hairColor'])
            
            # eye color
            eye_color_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_aboutYouStep_eyeList"]')))     
            select_eye_color(eye_color_dropdown, user_data['personalInfo']['eyeColor'])
            
            # occupation
            wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$occupationTextBox'))).send_keys(user_data['personalInfo']['occupation'])
            
            employer_or_school = user_data["personalInfo"].get("employerOrSchool", "").strip()
            if employer_or_school:
                wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$employerTextBox'))).send_keys(user_data['personalInfo']['employerOrSchool'])
            
            
            # submit
            # Wait for any overlays to disappear
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, 'TransparentDiv'))
            )
            
            # Find and wait for the button
            about_form_submit_button = wait.until(
                EC.presence_of_element_located((By.ID, 'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton'))
            )
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", about_form_submit_button)
            time.sleep(1)  # Allow time for scrolling

            driver.execute_script("arguments[0].click();", about_form_submit_button)
            
            print("waiting for page 4")
        
        except Exception as e:
            print(f"Failed to filled personal details. Please try again. Error: {e}")
            send_failure_response(webhook_url, "Failed to filled personal details. Please try again.", str(e)) 
            driver.quit()
        
# page 4

        try:
            # mailing address
            ADDRESS_CHAR_LIMIT = 40
            
            mailing_address_line1 = user_data['contactInfo']['mailing']['line1']
            
            mail_street_1 = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_mailStreetTextBox"]')))
        
            mail_street_1.send_keys(mailing_address_line1)
            
            mailing_address_line2 = user_data['contactInfo'].get('mailing').get('line2')    
            if mailing_address_line2:    
                
                # Fill the second field with the remaining address
                mail_street_2 = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_mailStreet2TextBox"]')))
                mail_street_2.send_keys(mailing_address_line2)
            
            # city
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_mailCityTextBox"]'))).send_keys(user_data['contactInfo']['mailing']['city'])
            
            # country
            country_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_mailCountryList"]')))
            select_country(country_dropdown, user_data["contactInfo"]["mailing"]["country"], driver)
            
            # state
            country = user_data["contactInfo"].get("mailing").get("country").upper()
            # if country in ['CAN', 'USA']:

                
            select_country_and_state(
                country_code=country, 
                state_abbreviation=user_data["contactInfo"]["mailing"]["state"], 
                driver=driver, 
                country_xpath='//*[@id="PassportWizard_addressStep_mailCountryList"]',  # Country dropdown XPath
                state_xpath='//*[@id="PassportWizard_addressStep_mailStateList"]'       # State dropdown XPath
            )
            
            time.sleep(3)
                # Zip Code - Only fill if country is CAN or USA
            WebDriverWait(driver, 60).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            zip_code_field = wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_addressStep_mailZipTextBox')))
            zip_code_field.send_keys(user_data['contactInfo']['mailing']['zipCode'])
            
            # incare of
            incare_of = user_data["contactInfo"].get("mailing").get("inCareOf")
            if incare_of:
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_addressStep_mailCareOfTextBox'))).send_keys(incare_of)
                     
            
        except Exception as e:
            send_failure_response(webhook_url, "Failed to fill mailing address. Please try again.", str(e)) 
            driver.quit()
            
        same_as_mailing = user_data["contactInfo"].get("sameAsMailing", False)
        if same_as_mailing:
            
            yes_radio_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentAddressList_0"]')))
            yes_radio_button.click()
            print("yes button clicked")
            
            WebDriverWait(driver, 60).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, 'TransparentDiv'))
            )
            
        # permanent address
        else:
            try:
                no_radio_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentAddressList_1"]')))
                no_radio_button.click()
                
                permanent_address = user_data["contactInfo"].get("permanent").get("line1")
                permanent_address = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentStreetTextBox"]'))).send_keys(permanent_address)
                
                permanent_address_line2 = user_data["contactInfo"].get("permanent").get("line2")
                if permanent_address_line2:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentApartmentTextBox"]'))).send_keys(permanent_address_line2)
                # city
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentCityTextBox"]'))).send_keys(user_data['contactInfo']['permanent']['city'])
                
                # country
                country_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentCountryList"]')))
                select_country(country_dropdown, user_data["contactInfo"]["permanent"]["country"], driver)
                
                country = user_data["contactInfo"].get("permanent").get("country").upper()

                print(f"country_permanent : {country}")
                # if country in ['CAN', 'USA']:
                add_info = user_data['contactInfo']['permanent']
                sts = add_info.get("state")
                print(f"permanent_state {sts}")
                
                # # Wait for the state list to load before selecting country and state
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentStateList"]'))
                )
                
                select_country_and_state(
                country_code=country, 
                state_abbreviation=sts, 
                driver=driver, 
                country_xpath='//*[@id="PassportWizard_addressStep_permanentCountryList"]',  # Country dropdown XPath
                state_xpath='//*[@id="PassportWizard_addressStep_permanentStateList"]',       # State dropdown XPath
                permanent_address=True
                )
                # zipcode
                # Wait for JavaScript to finish executing
                WebDriverWait(driver, 60).until(lambda d: d.execute_script('return document.readyState') == 'complete')
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_addressStep_permanentZipTextBox'))).send_keys(user_data['contactInfo']['permanent']['zipCode'])

            except Exception as e:
                send_failure_response(webhook_url, "Failed to fill permanent address. Please try again.", str(e)) 
                driver.quit()
        # choosing preferred communication medium
            
        try:
            mail_preference_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_CommunicateMail"]')))
            mail_preference_radio.click()
            print("mail button clicked")
        except Exception as e:
            print(f"Mail preference radio button click error: {e}")
            # Retry clicking after a short wait
            time.sleep(2)  # Small delay before retry
            mail_preference_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_CommunicateMail"]')))
            mail_preference_radio.click()
            print("mail button clicked after retry")
        
        try:    
            # filling email
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_emailTextBox"]'))).send_keys(user_data['contactInfo']['emailAddress'])
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_confirmEmailTextBox"]'))).send_keys(user_data['contactInfo']['emailAddress'])  
                
            # filling phone number
            phone_number = user_data["contactInfo"].get("phoneNumber", '').strip()
            if phone_number:
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_addPhoneNumberTextBox"]'))).send_keys(phone_number)
                phone_type = user_data["contactInfo"].get("phoneNumberType").strip().lower()

                # Ensure overlay is not present
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'TransparentDiv')))
                
                if phone_type == "home":
                    type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_PhoneNumberType_0"]')))
                    driver.execute_script("arguments[0].click();", type_radio)
                elif phone_type == "work":
                    type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_PhoneNumberType_1"]')))
                    driver.execute_script("arguments[0].click();", type_radio)
                else:
                    type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_PhoneNumberType_2"]')))
                    driver.execute_script("arguments[0].click();", type_radio)
            
            additional_phone_numbers = user_data["contactInfo"].get("additionalPhoneNumbers", [])
            if additional_phone_numbers and phone_number:
                for additional_phone_number in additional_phone_numbers:
                    print('additional phone number', additional_phone_number)
                    add_phone_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_addPhoneNumberButton"]')))
                    add_phone_button.click()

                    print('button clicked ')
                    # fill 
                    phone_type = additional_phone_number.get('type').strip().lower()
                    
                    # Ensure overlay is not present
                    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'TransparentDiv')))
                    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_addPhoneNumberTextBox"]'))).send_keys(additional_phone_number['phone'])
                    if phone_type == "home":
                        type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_PhoneNumberType_0"]')))
                        driver.execute_script("arguments[0].click();", type_radio)
                    elif phone_type == "work":
                        type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_PhoneNumberType_1"]')))
                        driver.execute_script("arguments[0].click();", type_radio)
                    else:
                        type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_PhoneNumberType_2"]')))
                        driver.execute_script("arguments[0].click();", type_radio)
            
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton"]')))
            next_button.click()
            print('entering to page 5 success')
        except Exception as e:
            send_failure_response(webhook_url, "Failed to fill email address and phone number, please check your date before entering.", str(e)) 
            driver.quit()
        
        print("waiting for page 5") 
         
# page 5     
        # travel plans 
        try:

            body = driver.find_element(By.TAG_NAME, 'body')
            driver.execute_script("arguments[0].click();", body)

            # Check and handle travel date
            travel_date = user_data.get('travelPlans', {}).get('travelDate', None)
            if travel_date:
                print("entered in travel date")
                date_of_trip_str = user_data.get('travelPlans').get('travelDate').get("$date")
                date_of_trip = datetime.strptime(date_of_trip_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_dot = date_of_trip.strftime("%m-%d-%Y")
                travel_date_input = wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_travelPlans_TripDateTextBox')))
                travel_date_input.send_keys(formatted_dot)
                driver.find_element(By.TAG_NAME, 'body').click()
                time.sleep(2)
            else:
                print("Travel date is not provided, skipping.")
                body = driver.find_element(By.TAG_NAME, 'body')
                driver.execute_script("arguments[0].click();", body)

            # Check and handle return date
            return_date = user_data.get('travelPlans', {}).get('returnDate', None)
            if return_date:
                date_of_return_str = user_data.get('travelPlans').get('returnDate').get("$date")
                date_of_return = datetime.strptime(date_of_return_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_dor = date_of_return.strftime("%m-%d-%Y")
                return_date_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_travelPlans_TripDateReturnTextBox"]')))
                return_date_input.click()
                return_date_input.send_keys(formatted_dor)
                time.sleep(2)
            else:
                print("Return date is not provided, skipping.")

            # Check and handle travel destination
            travel_destination = user_data.get('travelPlans', {}).get("travelDestination", "")
            travel_destination_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_travelPlans_CountriesTextBox"]')))
            travel_destination_input.click()
            if travel_destination:
                travel_destination_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_travelPlans_CountriesTextBox"]')))
                travel_destination_input.click()
                travel_destination_input.send_keys(travel_destination)
            else:
                print("Travel destination is not provided, skipping.")

            body = driver.find_element(By.TAG_NAME, 'body')
            driver.execute_script("arguments[0].click();", body)

            # Check for any overlay and remove it
            overlays = driver.find_elements(By.CLASS_NAME, 'overlay-class')  # Replace with the actual class of overlays
            for overlay in overlays:
                driver.execute_script("arguments[0].style.display = 'none';", overlay)

            # Then click the "Next" button again
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton"]')))
            driver.execute_script("arguments[0].click();", next_button)


        except Exception as e:
            print(f"An error occurred: {e}")
            send_failure_response(webhook_url, "Failed to fill travel plans. Please try again.", str(e)) 
            driver.quit()

        print("Waiting for page 6...")

        
# page 6
        # emergency contact
        try:

            driver.find_element(By.TAG_NAME, 'body').click()
            time.sleep(2)
            # wait_for_page_load(driver)
            print('entered in emergency contact')
            print(user_data['emergencyContact'].get('emergencyContactName'))
            if  user_data['emergencyContact'].get('emergencyContactName'):
                # name
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_emergencyContacts_ecNameTextBox'))).send_keys(user_data['emergencyContact'].get('emergencyContactName', 'N/A'))
                
                # street
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_emergencyContacts_ecAddressTextBox'))).send_keys(user_data['emergencyContact'].get('street', 'N/A'))
                
                # apartment
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_emergencyContacts_ecApartmentTextBox'))).send_keys(user_data['emergencyContact'].get('apartmentOrUnit', 'N/A'))
                
                # city
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_emergencyContacts_ecCityTextBox'))).send_keys(user_data['emergencyContact'].get('city', 'N/A'))
                
                
                # zip code
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_emergencyContacts_ZipCodeTextBox"]'))).send_keys(user_data['emergencyContact'].get('zipCode'))
                
                # phone
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_emergencyContacts_ecPhoneTextBox'))).send_keys(user_data['emergencyContact'].get('emergencyContactPhone'))
                
                # relationship
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_emergencyContacts_ecRelationshipTextBox'))).send_keys(user_data['emergencyContact'].get('emergencyContactRelationship'))
                
                # state 
                state_abbreviation = user_data["emergencyContact"]["state"]
                state_xpath = '//*[@id="PassportWizard_emergencyContacts_ecStateList"]'
                select_state_without_country(driver=driver, 
                                            state_abbreviation=state_abbreviation, 
                                            state_xpath=state_xpath)

            
            else:
                # Unfocus the field by clicking somewhere else (e.g., body)
                driver.find_element(By.TAG_NAME, 'body').click()
                time.sleep(2)

            next_button = wait.until(EC.presence_of_element_located((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
            
            # click next
            next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
            driver.execute_script("arguments[0].click();", next_button)
            print('next button clicked')
        
        except Exception as e:
            print(f"An error occurred: {e}")
            send_failure_response(webhook_url, "Failed to fill emergency contact information. Please try again", str(e)) 
            driver.quit()
        
        print("waiting for page 7")
        
# page 7  
        # Your Most Recent Passport
        try:
            passport_history = user_data.get("passportHistory", False).get('hasPassportCardOrBook', False)
            want_to_call_helper_function = True
            # Passport Book
            if passport_history == "book":
                print("book")
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CurrentHaveBook"]')))
                driver.execute_script("arguments[0].click();", radio)
                passport_book_status = user_data.get("passportHistory", {}).get("passportBookDetails", {}).get("status", False)

                # Lost or Stolen
                if passport_book_status == "lost" or passport_book_status == "stolen":
                    print("lost or stolen")
                    if passport_book_status == "lost":
                        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_BookLost"]')))
                    elif passport_book_status == "stolen":
                        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_BookStolen"]')))
                    driver.execute_script("arguments[0].click();", radio)

                    has_reported = user_data.get("passportHistory").get("passportBookDetails").get("hasReportedLostOrStolen")
                    print('has_reported')
                    if has_reported:
                        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_ReportLostBookYesRadioButton"]')))
                    else:
                        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_ReportLostBookNoRadioButton"]')))
                    driver.execute_script("arguments[0].click();", radio)

                    # first name and middle name
                    first_name_and_middle_name = user_data.get("passportHistory").get("passportBookDetails").get("firstNameAndMiddleName", False)
                    if first_name_and_middle_name:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_firstNameOnBook'))).send_keys(first_name_and_middle_name)
                    
                    # last name
                    last_name = user_data.get("passportHistory").get("passportBookDetails").get("lastName", False)
                    if last_name:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_lastNameOnBook'))).send_keys(last_name)

                    # book number
                    book_number = user_data.get("passportHistory").get("passportBookDetails").get("number", False)
                    if book_number:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_ExistingBookNumber'))).send_keys(book_number)

                    # issue date
                    date_issue = user_data.get("passportHistory").get("passportBookDetails").get("issueDate", False)
                    print('issue date reached')
                    if date_issue:
                        issue_date_str = user_data.get("passportHistory").get("passportBookDetails").get("issueDate").get("$date")
                        issue_date = datetime.strptime(issue_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        formatted_issue_date = issue_date.strftime("%m-%d-%Y")
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_BookIssueDate'))).send_keys(formatted_issue_date)
                    else:
                        next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
                        driver.execute_script("arguments[0].click();", next_button)

                        stolen_reported = user_data['passportHistory'].get('passportBookDetails').get('hasReportedLostOrStolen', False)
                        if not stolen_reported:
                            alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
                            alert.accept()

                            is_older_than_15_years = user_data.get("passportHistory").get("passportBookDetails").get("isOlderThan15Years")
                            print(f"is_older_than_15_years: {is_older_than_15_years}")
                            if is_older_than_15_years == 'yes':
                                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_BookExpiredYesRadioButton"]')))
                            elif is_older_than_15_years == 'no':
                                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_BookExpiredNoRadioButton"]')))
                            elif is_older_than_15_years == 'unknown':
                                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_BookExpiredUnknownRadioButton"]')))
                            driver.execute_script("arguments[0].click();", radio)
                        else:
                            want_to_call_helper_function = False

                # Damaged
                elif passport_book_status == "damaged":
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_BookDamaged"]')))
                    driver.execute_script("arguments[0].click();", radio)

                     # first name and middle name
                    first_name_and_middle_name = user_data.get("passportHistory").get("passportBookDetails").get("firstNameAndMiddleName", False)
                    if first_name_and_middle_name:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_firstNameOnBook'))).send_keys(first_name_and_middle_name)
                    
                    # issue date
                    date_issue_damaged = user_data.get("passportHistory").get("passportBookDetails").get("issueDate", False)
                    if date_issue_damaged:
                        issue_date_str = user_data.get("passportHistory").get("passportBookDetails").get("issueDate").get("$date")
                        issue_date = datetime.strptime(issue_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        formatted_issue_date = issue_date.strftime("%m-%d-%Y")
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_BookIssueDate'))).send_keys(formatted_issue_date)

                    # last name
                    last_name = user_data.get("passportHistory").get("passportBookDetails").get("lastName", False)
                    if last_name:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_lastNameOnBook'))).send_keys(last_name)

                    # book number
                    book_number = user_data.get("passportHistory").get("passportBookDetails").get("number", False)
                    if book_number:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_ExistingBookNumber'))).send_keys(book_number)
                
                # Yes
                elif passport_book_status == "yes":
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_BookYes"]')))
                    driver.execute_script("arguments[0].click();", radio)

                    issue_date_str = user_data.get("passportHistory").get("passportBookDetails").get("issueDate").get("$date")
                    issue_date = datetime.strptime(issue_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    formatted_issue_date = issue_date.strftime("%m-%d-%Y")
                    wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_BookIssueDate'))).send_keys(formatted_issue_date)

                    # first name and middle name
                    first_name_and_middle_name = user_data.get("passportHistory").get("passportBookDetails").get("firstNameAndMiddleName", False)
                    if first_name_and_middle_name:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_firstNameOnBook'))).send_keys(first_name_and_middle_name)

                    # last name
                    last_name = user_data.get("passportHistory").get("passportBookDetails").get("lastName", False)
                    if last_name:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_lastNameOnBook'))).send_keys(last_name)

                    # book number
                    book_number = user_data.get("passportHistory").get("passportBookDetails").get("number")
                    wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_ExistingBookNumber'))).send_keys(book_number)

                    date_of_birth_str = user_data.get('personalInfo').get('dateOfBirth').get('$date')
                    print(f"name change needed out {is_name_change_needed(date_of_birth_str, issue_date_str)}")
                    if is_name_change_needed(date_of_birth_str, issue_date_str):
                        print("name change needed in")
                        most_recent_passport_details(driver, user_data)

            elif passport_history == "card":
                print("card")
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CurrentHaveCard"]')))
                driver.execute_script("arguments[0].click();", radio)

                passport_card_status = user_data.get("passportHistory", {}).get("passportCardDetails", {}).get("status", False)

                if passport_card_status == "lost" or passport_card_status == "stolen":
                    if passport_card_status == "lost":
                        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CardLost"]')))
                    elif passport_card_status == "stolen":
                        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CardStolen"]')))
                    driver.execute_script("arguments[0].click();", radio)

                    has_reported = user_data.get("passportHistory").get("passportCardDetails").get("hasReportedLostOrStolen")
                    if has_reported:
                        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_ReportLostCardYesRadioButton"]')))
                    else:
                        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_ReportLostCardNoRadioButton"]')))
                    driver.execute_script("arguments[0].click();", radio)

                    #issue date
                    issue_date_lost_or_stolen = user_data.get("passportHistory").get("passportCardDetails").get("issueDate", False)
                    if issue_date_lost_or_stolen:
                        issue_date_str = issue_date_lost_or_stolen.get("$date")
                        issue_date = datetime.strptime(issue_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        formatted_issue_date = issue_date.strftime("%m-%d-%Y")
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_CardIssueDate'))).send_keys(formatted_issue_date)


                    # first name and middle name
                    first_name_and_middle_name = user_data.get("passportHistory").get("passportCardDetails").get("firstNameAndMiddleName", False)
                    if first_name_and_middle_name:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_firstNameOnCard'))).send_keys(first_name_and_middle_name)
                    
                    # last name
                    last_name = user_data.get("passportHistory").get("passportCardDetails").get("lastName", False)
                    if last_name:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_lastNameOnCard'))).send_keys(last_name)

                    # book number
                    card_number = user_data.get("passportHistory").get("passportCardDetails").get("number", False)
                    if card_number:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_ExistingCardNumber'))).send_keys(card_number)
                elif passport_card_status == "damaged":

                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CardDamaged"]')))
                    driver.execute_script("arguments[0].click();", radio)

                    # issue date
                    date_issue_damaged = user_data.get("passportHistory").get("passportCardDetails").get("issueDate", False)
                    if date_issue_damaged:
                        issue_date_str = user_data.get("passportHistory").get("passportCardDetails").get("issueDate").get("$date")
                        issue_date = datetime.strptime(issue_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        formatted_issue_date = issue_date.strftime("%m-%d-%Y")
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_CardIssueDate'))).send_keys(formatted_issue_date)

                     # first name and middle name
                    first_name_and_middle_name = user_data.get("passportHistory").get("passportCardDetails").get("firstNameAndMiddleName", False)
                    if first_name_and_middle_name:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_firstNameOnCard'))).send_keys(first_name_and_middle_name)
                    

                    # last name
                    last_name = user_data.get("passportHistory").get("passportCardDetails").get("lastName", False)
                    if last_name:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_lastNameOnCard'))).send_keys(last_name)

                    # book number
                    card_number = user_data.get("passportHistory").get("passportCardDetails").get("number", False)
                    if card_number:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_ExistingCardNumber'))).send_keys(card_number)
                elif passport_card_status == "yes":
                    print("card status is yes")
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CardYes"]')))
                    driver.execute_script("arguments[0].click();", radio)

                    issue_date_str = user_data.get("passportHistory").get("passportCardDetails").get("issueDate").get("$date")
                    issue_date = datetime.strptime(issue_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    formatted_issue_date = issue_date.strftime("%m-%d-%Y")
                    wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_CardIssueDate'))).send_keys(formatted_issue_date)

                    # first name and middle name
                    first_name_and_middle_name = user_data.get("passportHistory").get("passportCardDetails").get("firstNameAndMiddleName", False)
                    if first_name_and_middle_name:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_firstNameOnCard'))).send_keys(first_name_and_middle_name)

                    # last name
                    last_name = user_data.get("passportHistory").get("passportCardDetails").get("lastName", False)
                    if last_name:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_lastNameOnCard'))).send_keys(last_name)

                    # book number
                    card_number = user_data.get("passportHistory").get("passportCardDetails").get("number")
                    wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_ExistingCardNumber'))).send_keys(card_number)
                    #partially finished
                    date_of_birth_str = user_data.get('personalInfo').get('dateOfBirth').get('$date')
                    if is_name_change_needed(date_of_birth_str, issue_date_str):
                        most_recent_passport_details(driver, user_data)
                    
            elif passport_history == "both":
                want_to_call_helper_function = passport_both_helper(driver, user_data)
                
            else:
                type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CurrentHaveNone"]')))
                driver.execute_script("arguments[0].click();", type_radio)

            
            # passport_history_details = user_data.get("passportHistory", {})
            # passport_book_details = passport_history_details.get("passportBookDetails", False)
            # passport_card_details = passport_history_details.get("passportCardDetails", False)

            # # if passport_book_details and passport_history != "both":
            # if passport_history == "book":
            #     passport_book_status = passport_book_details.get("status")
            #     if passport_book_status in ["lost", "stolen"]:
            #         is_older_than_15_years = user_data.get("passportHistory").get("passportBookDetails").get("isOlderThan15Years", False)
                    
            #         # If passport is not older than 15 years OR issue date exists AND has not been reported
            #         if (is_older_than_15_years == 'no' or is_older_than_15_years == 'unknown' or date_issue) and not has_reported:
            #             print("indide")
            #             # Handle lost/stolen passport flow
            #             lost_or_stolen(driver, user_data)
            #         else:
            #             # Continue to next page
            #             next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
            #             driver.execute_script("arguments[0].click();", next_button)
            #     else:
            #         next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
            #         driver.execute_script("arguments[0].click();", next_button)

            # # elif passport_card_details and passport_history != "both":
            # elif passport_history == "card":
            #     passport_card_status = passport_card_details.get("status")
            #     has_reported_lost_or_stolen = passport_card_details.get("hasReportedLostOrStolen")
            #     if passport_card_status in ["lost", "stolen"] and not has_reported_lost_or_stolen:  
            #         lost_or_stolen(driver, user_data)
            #     else:
            #         next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
            #         driver.execute_script("arguments[0].click();", next_button)

            # elif passport_history == "none":
            #     print("continue to next page hai")
            #     next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
            #     driver.execute_script("arguments[0].click();", next_button)
            print("waiting for page 8 before")
            if want_to_call_helper_function:
                passport_route_flow_helper(driver, user_data)

            print("waiting for page 8")
        except Exception as e:
            print("error",str(e))
            send_failure_response(webhook_url, "Failed to fill passport history. Please try again.", str(e)) 
            driver.quit()
        
# page 8
        print('page 8 reached')
        # Check if passport is valid and issued within 8 years 6 days only passport status is yes
        date_of_birth_str = user_data.get('personalInfo').get('dateOfBirth').get('$date')
        passport_history = user_data.get("passportHistory", {})
        book_details = passport_history.get("passportBookDetails", {})
        card_details = passport_history.get("passportCardDetails", {})
        passport_card_status = card_details.get("status") if card_details else None
        passport_book_status = book_details.get("status") if book_details else None

        print('initial check point')

        # Try to get issue date from book details first, then card details if book details don't have it
        # issue_date = None
        # if passport_book_details:
        #     issue_date = passport_book_details.get("issueDate")
        # if not issue_date and passport_card_details:
        #     issue_date = passport_card_details.get("issueDate")
        # issue_date_str = issue_date.get("$date") if issue_date and isinstance(issue_date, dict) else None

        # Handle missing issueDate field
        book_issue_date  = {}
        card_issue_date = {}
        if book_details:
            book_issue_date = book_details.get("issueDate", {}) 
        if card_details:
            card_issue_date = card_details.get("issueDate", {}) 
        
        print('2 check point')
        
        book_issue_date_str = book_issue_date.get("$date") if book_issue_date else False
        card_issue_date_str = card_issue_date.get("$date") if card_issue_date else False

        is_book_name_change_needed = is_name_change_needed(date_of_birth_str, book_issue_date_str) if book_issue_date_str else False
        is_card_name_change_needed = is_name_change_needed(date_of_birth_str, card_issue_date_str) if card_issue_date_str else False
        print('KK')
        print(is_book_name_change_needed)

        book_condition = (
            passport_book_status != "yes" if passport_book_status else False
        ) or (
            not is_book_name_change_needed if book_issue_date_str else False
        )

        card_condition = (
            passport_card_status != "yes" if passport_card_status else False
        ) or (
            not is_card_name_change_needed if card_issue_date_str else False
        )

        both_condition = (
            passport_history == "both" and 
            (passport_book_status in ["lost", "stolen"] or 
            passport_card_status in ["lost", "stolen"])
        )
        enter = True   
        print('hello') 
        if book_condition or card_condition or both_condition:
    # Do something

            # parent and spouse information
            print("inside parent and spouse information")
            try:
                # unfocus = wait.until(
                #     EC.element_to_be_clickable((By.ID, 'Table1'))
                # )
                # unfocus.click()

                time.sleep(2)
                print('inside try block')
                is_parent1_unknown = user_data['parentAndMarriageInfo']['isParent1Unknown']
                print('parent 1 known',is_parent1_unknown)
                if not is_parent1_unknown:
                    # first name and middle name
                    print('first condition satisfied')
                    # First Name
                    try:
                        first_name_input = wait.until(
                            EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent1FirstNameTextBox'))
                        )
                        first_name_input.send_keys(user_data['parentAndMarriageInfo']['parent1']["firstName"])
                    except TimeoutException:
                        driver.quit() 
                        print("Error: First name field not found or timeout occurred.")

                    # Last Name
                    try:
                        last_name_input = wait.until(
                            EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent1LastNameTextBox'))
                        )
                        last_name_input.send_keys(user_data['parentAndMarriageInfo']['parent1']["lastName"])
                    except TimeoutException:
                        driver.quit() 
                        print("Error: Last name field not found or timeout occurred.")
                    
                    # date of birth     
                    print(f"hai {user_data['parentAndMarriageInfo']['parent1']}")
                    is_parent1_dob = user_data['parentAndMarriageInfo']['parent1'].get("dateOfBirth")
                    if is_parent1_dob is not None and is_parent1_dob is not False:
                        parent1_dob_str = user_data['parentAndMarriageInfo']['parent1']["dateOfBirth"]["$date"]
                        parent1_dob = datetime.strptime(parent1_dob_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        formatted_dob1 = parent1_dob.strftime("%m-%d-%Y")
                        print(formatted_dob1)

                        parent1_dob_input = wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent1BirthDateTextBox')))
                        parent1_dob_input.click()  # Focus the field
                        parent1_dob_input.clear()   # Clear any existing value
                        parent1_dob_input.send_keys(formatted_dob1)  # Send formatted DOB
                        time.sleep(0.5) 
                        print('nice')

                    print('nice2')
                    # place of birth
                    is_parent1_pob = user_data['parentAndMarriageInfo']['parent1'].get("placeOfBirth")
                    if is_parent1_pob is not None and is_parent1_pob is not False:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent1BirthPlaceTextBox'))).send_keys(user_data['parentAndMarriageInfo']['parent1']["placeOfBirth"])
                    
                    print('nice3')
                    # gender
                    gender = user_data["parentAndMarriageInfo"]['parent1'].get("gender").strip().lower()

                    if gender == "male":
                        gender_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent1SexList_0"]')))  # Male radio button
                        driver.execute_script("arguments[0].click();", gender_radio)
                    elif gender == "female":
                        gender_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent1SexList_1"]')))  # Female radio button
                        driver.execute_script("arguments[0].click();", gender_radio)
                    else:
                        gender_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent1SexList_2"]')))  # Other/Unspecified
                        driver.execute_script("arguments[0].click();", gender_radio)
                    
                    print('nice4')
                    # citizenship
                    citizenship = user_data["parentAndMarriageInfo"]['parent1'].get("isUSCitizen")
                    if citizenship:
                        citizenship_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent1CitizenList_0"]')))  # Other/Unspecified
                        driver.execute_script("arguments[0].click();", citizenship_radio)
                    else:
                        citizenship_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent1CitizenList_1"]')))  # Other/Unspecified
                        driver.execute_script("arguments[0].click();", citizenship_radio)
                    
                    print('nice5')
                else:
                    is_parent1_unknown_checkbox = wait.until(EC.element_to_be_clickable((By.ID, 'PassportWizard_moreAboutYouStep_unknownParent1CheckBox')))
                    is_parent1_unknown_checkbox.click() 
                
                    # Wait for any loading overlays to disappear
                    WebDriverWait(driver, 10).until(
                        EC.invisibility_of_element_located((By.CLASS_NAME, 'TransparentDiv'))
                    )
                    time.sleep(0.5)


                # parent 2
                is_parent2_unknown = user_data['parentAndMarriageInfo']['isParent2Unknown']
                if not is_parent2_unknown:
                    # first name and middle name
                    wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent2FirstNameTextBox'))).send_keys(user_data['parentAndMarriageInfo']['parent2']["firstName"])
                    # last name
                    wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent2LastNameTextBox'))).send_keys(user_data['parentAndMarriageInfo']['parent2']["lastName"])
                    # dob
                    print(user_data['parentAndMarriageInfo']['parent2'])
                    is_parent2_dob = user_data['parentAndMarriageInfo']['parent2'].get("dateOfBirth")
                    if is_parent2_dob is not None and is_parent2_dob is not False:
                        parent2_dob_str = user_data['parentAndMarriageInfo']['parent2']["dateOfBirth"]["$date"]
                        parent2_dob = datetime.strptime(parent2_dob_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        formatted_dob2 = parent2_dob.strftime("%m-%d-%Y")
                        
                        print(formatted_dob2)
                        
                        parent2_dob_input = wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent2BirthDateTextBox')))
                        parent2_dob_input.click()  # Focus the field
                        parent2_dob_input.clear()   # Clear any existing value
                        parent2_dob_input.send_keys(formatted_dob2)  # Send formatted DOB
                        time.sleep(0.5)
                    # place of birth
                    is_parent2_pob = user_data['parentAndMarriageInfo']['parent2'].get("placeOfBirth")
                    if is_parent2_pob is not None and is_parent2_pob is not False:
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent2BirthPlaceTextBox'))).send_keys(user_data['parentAndMarriageInfo']['parent2']["placeOfBirth"])
                    # gender

                    gender = user_data["parentAndMarriageInfo"]['parent2'].get("gender").strip().lower()

                    if gender == "male":
                        gender_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent2SexList_0"]')))  # Male radio button
                        driver.execute_script("arguments[0].click();", gender_radio)
                    elif gender == "female":
                        gender_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent2SexList_1"]')))  # Female radio button
                        driver.execute_script("arguments[0].click();", gender_radio)
                    else:
                        gender_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent2SexList_2"]')))  # Other/Unspecified
                        driver.execute_script("arguments[0].click();", gender_radio)
                        
                    # citizenship
                    citizenship = user_data["parentAndMarriageInfo"]['parent2'].get("isUSCitizen")
                    if citizenship:
                        citizenship_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent2CitizenList_0"]')))  # Other/Unspecified
                        driver.execute_script("arguments[0].click();", citizenship_radio)
                    else:
                        citizenship_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent2CitizenList_1"]')))  # Other/Unspecified
                        driver.execute_script("arguments[0].click();", citizenship_radio)
                else:
                    is_parent2_unknown_checkbox = wait.until(EC.element_to_be_clickable((By.ID, 'PassportWizard_moreAboutYouStep_unknownParent2CheckBox')))
                    is_parent2_unknown_checkbox.click() 

                    # Wait for any loading overlays to disappear
                    WebDriverWait(driver, 10).until(
                        EC.invisibility_of_element_located((By.CLASS_NAME, 'TransparentDiv'))
                    )
                    time.sleep(0.5)

            except Exception as e:
                print(f"Error in parent and spouse information: {e}")
                send_failure_response(webhook_url, "Failed to fill parent information. Please try again.", str(e)) 
                driver.quit()
        
            try: 
                # marriage info
                marriage_info = user_data["parentAndMarriageInfo"].get("isMarried")
                print(f"marriage_info {marriage_info}")
                if marriage_info:
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_marriedList_0"]')))  # Other/Unspecified
                    driver.execute_script("arguments[0].click();", radio)
                    
                    wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_spouseNameTextBox'))).send_keys(user_data['parentAndMarriageInfo']['marriageDetails']["spouseFirstName"])
                    wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_spouseLastNameTextBox'))).send_keys(user_data['parentAndMarriageInfo']['marriageDetails']["spouseLastName"])
                    # dob
                    spouse_dob_str = user_data['parentAndMarriageInfo']['marriageDetails']["spouseDateOfBirth"]["$date"]
                    spouse_dob = datetime.strptime(spouse_dob_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    formatted_dob = spouse_dob.strftime("%m-%d-%Y")
                    wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_spouseBirthDateTextBox'))).send_keys(formatted_dob)
                    # place of birth
                    wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_spouseBirthplaceTextBox'))).send_keys(user_data['parentAndMarriageInfo']['marriageDetails']["spousePlaceOfBirth"])
                    # citizenship
                    citizenship = user_data['parentAndMarriageInfo']['marriageDetails'].get("spouseIsUSCitizen")
                    if citizenship:
                        citizenship_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_spouseCitizenList_0"]')))  # Other/Unspecified
                        driver.execute_script("arguments[0].click();", citizenship_radio)
                    else:
                        citizenship_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_spouseCitizenList_1"]')))  # Other/Unspecified
                        driver.execute_script("arguments[0].click();", citizenship_radio)
                        
                    # date of marriage
                    date_of_marriage_str = user_data['parentAndMarriageInfo']['marriageDetails']["marriageDate"]["$date"]
                    date_of_marriage = datetime.strptime(date_of_marriage_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    formatted_dom = date_of_marriage.strftime("%m-%d-%Y")
                    wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_marriedDateTextBox'))).send_keys(formatted_dom)
                    
                    # widow or divorce
                    widow_or_divorce = user_data['parentAndMarriageInfo']['marriageDetails'].get("isWidowedOrDivorced")
                    if widow_or_divorce:
                        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_divorcedList_0"]'))) 
                        driver.execute_script("arguments[0].click();", radio)
                        # divorced date
                        marriage_or_divorce_date_str = user_data['parentAndMarriageInfo']['marriageDetails']["widowOrDivorceDate"]
                        marriage_or_divorce_date = datetime.strptime(marriage_or_divorce_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        formatted_dod = marriage_or_divorce_date.strftime("%m-%d-%Y")
                        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_divorcedDateTextBox'))).send_keys(formatted_dod)
                
                        
                    else:
                        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_divorcedList_1"]')))  
                        driver.execute_script("arguments[0].click();", radio)
                
                else:
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_marriedList_1"]')))  # Other/Unspecified
                    driver.execute_script("arguments[0].click();", radio)
                    
                next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
                driver.execute_script("arguments[0].click();", next_button)
            
            except Exception as e:
                send_failure_response(webhook_url, "Failed to fill marriage info. Please try again.", str(e)) 
                driver.quit()

            
            print("waiting for page 9")
        
# page 9
        # other names
        
        try:
            other_names = user_data.get("personalInfo").get("allPreviousNames", [])
            
            if other_names:
                for index, name in enumerate(other_names):
                    
                    first_name = name.get("firstName", "")
                    last_name = name.get("lastName", "")

                    # Wait for the first name field and fill it
                    first_name_input = wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_otherNameStep_addOtherFirstTextBox')))
                    first_name_input.send_keys(first_name)

                    # Wait for the last name field and fill it
                    last_name_input = wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_otherNameStep_addOtherLastTextBox')))
                    last_name_input.send_keys(last_name)

                    time.sleep(2)
                    # If there are more names to enter, click the 'Add More' button
                    if index < len(other_names) - 1:
                        add_button = wait.until(EC.element_to_be_clickable((By.ID, 'PassportWizard_otherNameStep_addButton')))
                        add_button.click()

                        # Wait for the new fields to appear and stabilize before the next iteration
                        time.sleep(3)
                        wait.until(EC.presence_of_element_located((By.ID, f'PassportWizard_otherNameStep_addOtherFirstTextBox')))
                    
            
            
            input_id='PassportWizard_otherNameStep_addOtherFirstTextBox'
            wait.until(EC.presence_of_element_located((By.ID, input_id)))
            input_field = driver.find_element(By.ID, input_id)
            input_field.send_keys(Keys.TAB)
            
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton"]')))
            driver.execute_script("arguments[0].click();", next_button)
        
        except Exception as e:
            send_failure_response(webhook_url, "Failed to fill other names, Please try again.", str(e)) 
            driver.quit()
        print("waiting for page 10")
        
# page 10
        # preview of filled forms
        
        try:
            div_id='PassportWizard_reviewStep_GotoPersonalDetails'
            wait.until(EC.presence_of_element_located((By.ID, div_id)))
            div_field = driver.find_element(By.ID, div_id)
            div_field.send_keys(Keys.TAB)
            
            # Wait until the button is clickable, then fetch it again for clicking
            wait.until(EC.element_to_be_clickable((By.ID, 'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
            next_button = driver.find_element(By.ID, 'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            time.sleep(1)  # Allow time for any overlays to settle
            driver.execute_script("arguments[0].click();", next_button)
        except Exception as e:
            print(f"Error clicking next button: {e}")
            send_failure_response(webhook_url, "Some error occurred", str(e)) 
            driver.quit()
        
# page 11
        try:
            # Passport Options
            passport_option = user_data.get('productInfo',False).get('passportOption',False)
            if passport_option:
                # book
                if passport_option == "book":
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_bookFee"]'))) 
                    driver.execute_script("arguments[0].click();", radio)
                    is_large_book = user_data.get('productInfo').get('largeBook',False)
                    
                    if is_large_book:
                       # First wait for the element to be present in DOM
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_feesStep_bookType52"]'))
                        )
                        
                        # Then wait for it to be visible
                        WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.XPATH, '//*[@id="PassportWizard_feesStep_bookType52"]'))
                        )
                        
                        # Finally wait for it to be clickable
                        checkbox = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_bookType52"]'))
                        )
                        
                        # Ensure any loading overlays are gone
                        WebDriverWait(driver, 10).until(
                            EC.invisibility_of_element_located((By.CLASS_NAME, 'TransparentDiv'))
                        )
                        
                        # Scroll into view and click
                        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                        time.sleep(0.5)  # Wait for any animations
                        checkbox.click()
                # card
                elif passport_option == "card":
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_cardFee"]'))) 
                    driver.execute_script("arguments[0].click();", radio)
                # both
                elif passport_option == "both":
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_bookCardFee"]'))) 
                    driver.execute_script("arguments[0].click();", radio)
                    is_large_book = user_data.get('productInfo').get('largeBook',False)
                    if is_large_book:
                       # First wait for the element to be present in DOM
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_feesStep_bothBookType52"]'))
                        )
                        
                        # Then wait for it to be visible
                        WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.XPATH, '//*[@id="PassportWizard_feesStep_bothBookType52"]'))
                        )
                        
                        # Finally wait for it to be clickable
                        checkbox = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_bothBookType52"]'))
                        )
                        
                        # Ensure any loading overlays are gone
                        WebDriverWait(driver, 10).until(
                            EC.invisibility_of_element_located((By.CLASS_NAME, 'TransparentDiv'))
                        )
                        
                        # Scroll into view and click
                        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                        time.sleep(0.5)  # Wait for any animations
                        checkbox.click()
            else:
                print("not getting passport options")
                send_failure_response(webhook_url, "not getting passport options", "not getting passport options") 
                driver.quit()

            # Processing Methods
            process_method = user_data.get('productInfo', False).get('processingMethod', False)
            if process_method:
                if process_method == 'routine':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_routineService"]'))) 
                elif process_method == 'expedited':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_expeditedService"]'))) 
                elif process_method == 'agency':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_expeditedAgencyService"]'))) 

                driver.execute_script("arguments[0].click();", radio)
            else:
                print("not getting processing method")
                send_failure_response(webhook_url, "not getting processing method", "not getting processing method") 
                driver.quit()
                
            # Delivery Methods
            book_delivery_method = user_data.get('productInfo', False).get('deliveryMethod', False).get('book', False)
            passport_option = user_data.get('productInfo', False).get('passportOption', False)


            if passport_option == "both":
                
                if book_delivery_method == 'standard':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_bookPriorityMail"]'))) 
                elif book_delivery_method == 'one-two-day':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_bookOverniteMail"]'))) 
                driver.execute_script("arguments[0].click();", radio)

                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_cardFirstClassRadioButton"]'))) 
                driver.execute_script("arguments[0].click();", radio)

            elif passport_option == "book":

                if book_delivery_method == 'standard':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_bookPriorityMail"]'))) 
                elif book_delivery_method == 'one-two-day':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_bookOverniteMail"]'))) 
                driver.execute_script("arguments[0].click();", radio)

            elif passport_option == "card":

                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_cardFirstClassRadioButton"]'))) 
                driver.execute_script("arguments[0].click();", radio)

            # Additional Fees
            passport_history = user_data.get("passportHistory", {})
            book_details = passport_history.get("passportBookDetails") or {}
            card_details = passport_history.get("passportCardDetails") or {}
            passport_card_status = card_details.get("status") if card_details is not None else None
            passport_book_status = book_details.get("status") if book_details is not None else None
            additional_fees = user_data.get('productInfo', False).get('additionalFees', False).get('fileSearch', False)
            if additional_fees and (passport_card_status != "yes" if passport_card_status else False or passport_book_status != "yes" if passport_book_status else False):
                # checkbox = wait.until(EC.element_to_be_clickable((By.NAME, 'PassportWizard$feesStep$addOptFileSearchCheckBox')))
                # checkbox.click()
                print("additional fees")
                 # Wait for any overlay to disappear first
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, 'TransparentDiv'))
                )

                print("additional fees 2")
                
                # Wait for the checkbox to be present and visible
                checkbox = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'PassportWizard$feesStep$addOptFileSearchCheckBox'))
                )

                # checkbox = wait.until(EC.element_to_be_clickable((By.NAME, 'PassportWizard$feesStep$addOptFileSearchCheckBox')))
                # checkbox.click()

                print("additional fees 3")
                
                # Scroll the checkbox into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                # print("additional fees 4")
                time.sleep(1)  # Allow time for scrolling
                print("additional fees 5")
                driver.execute_script("arguments[0].click();", checkbox)
                print("additional fees 6")

            print("buttond")
            button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_FinishNavigationTemplateContainerID_FinishButton')))
            driver.execute_script("arguments[0].scrollIntoView();", button)
            time.sleep(1) 
            driver.execute_script("arguments[0].click();", button)

# (passport_history != 'both' and passport_option != 'both' and passport_history != passport_option)

            print("ddddaee")
            # Check for alert
            passport_history = user_data.get("passportHistory", False).get('hasPassportCardOrBook', False)
            if passport_history:
                if passport_history == 'card':
                    passport_history_card_status = user_data['passportHistory']['passportCardDetails'].get('status')
                else:
                    passport_history_book_status = user_data['passportHistory']['passportBookDetails'].get('status')
            
            passport_option = user_data['productInfo'].get('passportOption', False)

            if ((passport_book_status != 'yes' and passport_option not in ['book', 'both'])
            or (passport_card_status != 'yes' and passport_option not in ['card', 'both'])):
                print("alert")
                alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
                alert.accept()

        except Exception as e:
            print(f"Error filling passport options: {e}")
            send_failure_response(webhook_url, "Failed to fill passport options. Please try again.", str(e)) 
            driver.quit()
        
        print("waiting for page 12")

        # Electronic Signature
        passport_history_details = user_data.get("passportHistory", {})
        passport_book_details = passport_history_details.get("passportBookDetails", False)
        passport_card_details = passport_history_details.get("passportCardDetails", False)
        
        if ((passport_book_details and passport_book_details.get("status") in ["lost", "stolen"] and not passport_book_details.get("hasReportedLostOrStolen")) or 
            (passport_card_details and passport_card_details.get("status") in ["lost", "stolen"] and not passport_card_details.get("hasReportedLostOrStolen"))):
            print("electronic signature")
            lost_info = user_data.get('lostInfo',{})
            is_own_passport = lost_info.get('isOwnPassport',False)
            if is_own_passport:
                try:
                    print("electronic signature")
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_esignatureStep_lostOrStolenDelivery_1"]'))) 
                    driver.execute_script("arguments[0].click();", radio)
                    next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
                    driver.execute_script("arguments[0].click();", next_button)
                except Exception as e:
                    print(f"Error filling electronic signature: {e}")
                    send_failure_response(webhook_url, "Failed to fill electronic signature. Please try again.", str(e)) 
                    driver.quit()


# page 12

        # printing pdf
        #Locate the checkbox using an explicit wait
        acknowledgment_checkbox = wait.until(
            EC.presence_of_element_located((By.ID, 'PassportWizard_nextStepsStep_ConfirmationCheckBox'))
        )

        # Scroll to the element using JavaScript to ensure visibility
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", acknowledgment_checkbox)

        # Wait until the element is clickable
        acknowledgment_checkbox = wait.until(
            EC.element_to_be_clickable((By.ID, 'PassportWizard_nextStepsStep_ConfirmationCheckBox'))
        )

        # Click the checkbox
        acknowledgment_checkbox.click()
        
        wait.until(EC.element_to_be_clickable((By.ID, 'PassportWizard_nextStepsStep_printFormButton')))
        next_button = driver.find_element(By.ID, 'PassportWizard_nextStepsStep_printFormButton')
        # driver.execute_script("arguments[0].scrollIntoView();", next_button)
        driver.execute_script("arguments[0].click();", next_button)
        
        # Wait for the download to complete and get the result
        download_result = wait_for_downloads(download_dir)
        print(download_result)
        # time.sleep(10)
        print("pdf downloaded")
        
        return download_result
        
             
            
    except Exception as e:
        print(f"An error occurred: {e}", flush=True)
        send_failure_response(webhook_url, "Application not submitted. Please try again later.", str(e))

    finally:
        driver.quit()