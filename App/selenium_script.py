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





def fill_form(user_data):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    
    # Use the Service class to specify the driver path
    chrome_service = Service(r"C:\chromedriver.exe")

    
    # Pass the service object to the Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)  
    
    try:
# Page 1
        # Navigate to the form page
        driver.get("https://pptform.state.gov/")     
        
        # Locate the checkbox using XPath and click it
        wait = WebDriverWait(driver, 60)  # Wait up to 60 seconds
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
        # wait.until(EC.url_contains("https://pptform.state.gov/PassportWizardMain.aspx"))
        
        
        
# Page 3
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
        
        # dob
        date_of_birth_str = user_data['personalInfo']['dateOfBirth']['$date']
        date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_dob = date_of_birth.strftime("%m-%d-%Y")
        wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$dobTextBox'))).send_keys(formatted_dob) 
                
        # city of birth
        wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$pobCityTextBox'))).send_keys(user_data['personalInfo']['placeOfBirth'])
        
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
        feet_height = user_data['physicalDescription']['height']['feet']
        select_height_feet(height_feet_dropdown, feet_height)
            
        
        height_inches_dropdown = wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_aboutYouStep_heightInchList')))
        inches_height = user_data['physicalDescription']['height']['inches']
        select_height_inches(height_inches_dropdown, inches_height)

        
        # hair color
        hair_color_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_aboutYouStep_hairList"]')))
        select_hair_color(hair_color_dropdown, user_data['physicalDescription']['hairColor'])
        
        # eye color
        eye_color_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_aboutYouStep_eyeList"]')))     
        select_eye_color(eye_color_dropdown, user_data['physicalDescription']['eyeColor'])
        
        # occupation
        wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$occupationTextBox'))).send_keys(user_data['personalInfo']['occupation'])
        
        employer_or_school = user_data["personalInfo"].get("employerOrSchool", "").strip()
        if employer_or_school:
            wait.until(EC.presence_of_element_located((By.NAME, 'PassportWizard$aboutYouStep$employerTextBox'))).send_keys(user_data['personalInfo']['employerOrSchool'])
        
        
        # submit
        about_form_submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton"]')))
        about_form_submit_button.click()
        
        # Wait for the next page to load
        # wait.until(EC.url_changes(driver.current_url))
        print("waiting for page 4")
        
# page 4
        # mailing address
        ADDRESS_CHAR_LIMIT = 40
        
        mailing_address = user_data['addressInfo']['mailingAddress']
        
        mail_street_1 = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_mailStreetTextBox"]')))
        
        if len(mailing_address) <= ADDRESS_CHAR_LIMIT:
            mail_street_1.send_keys(mailing_address)
        else:
            # Split the address if it exceeds the limit
            mail_street_1.send_keys(mailing_address[:ADDRESS_CHAR_LIMIT])
            
            # Fill the second field with the remaining address
            mail_street_2 = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_mailStreet2TextBox"]')))
            mail_street_2.send_keys(mailing_address[ADDRESS_CHAR_LIMIT:])
        
        # city
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_mailCityTextBox"]'))).send_keys(user_data['addressInfo']['city'])
        
        # country
        country_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_mailCountryList"]')))
        select_country(country_dropdown, user_data["addressInfo"]["country"], driver)
        
        # state
        country = user_data["addressInfo"].get("country").upper()
        if country in ['CANADA', 'UNITED STATES']:
            state_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_mailStateList"]')))
            select_state(state_dropdown, user_data["addressInfo"]["state"], driver)
        
        # zip code
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_addressStep_mailZipTextBox'))).send_keys(user_data['addressInfo']['zipCode'])
        
        # compare mailing address with permanant address
        mailing_address = user_data['addressInfo']['mailingAddress'].strip()
        permanent_address = user_data['permanentAddress']['permanentAddress'].strip()
        if mailing_address == permanent_address:
            yes_radio_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentAddressList_0"]')))
            yes_radio_button.click()
        # permanent address
        else:
            no_radio_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentAddressList_1"]')))
            no_radio_button.click()
            
            permanent_address = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentStreetTextBox"]'))).send_keys(permanent_address)
            
            # city
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentCityTextBox"]'))).send_keys(user_data['permanentAddress']['city'])
            
            # country
            country_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentCountryList"]')))
            select_country(country_dropdown, user_data["permanentAddress"]["country"], driver)
            
            country = user_data["permanentAddress"].get("country").upper()
            if country in ['CANADA', 'UNITED STATES']:
                state_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentStateList"]')))
                select_state(state_dropdown, user_data["permanentAddress"]["state"], driver)
            
            # zipcode
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_addressStep_permanentZipTextBox'))).send_keys(user_data['permanentAddress']['zipCode'])
        
        # choosing prefered communication medium    
        mail_prefference_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_CommunicateMail"]')))
        mail_prefference_radio.click()
            
        # filling email
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_emailTextBox"]'))).send_keys(user_data['contactInfo']['emailAddress'])
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_confirmEmailTextBox"]'))).send_keys(user_data['contactInfo']['emailAddress'])  
            
        # filling phone number
        phone_number = user_data["contactInfo"].get("phoneNumber", '').strip()
        if phone_number:
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_addPhoneNumberTextBox"]'))).send_keys(user_data['contactInfo']['phoneNumber'])
            phone_type = user_data["contactInfo"].get("phoneNumberType").strip().lower()
            if phone_type == "home":
                type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_PhoneNumberType_0"]')))
                type_radio.click()
            elif phone_type == "work":
                type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_PhoneNumberType_1"]')))
                type_radio.click()
            else:
                type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_PhoneNumberType_2"]')))
                type_radio.click()
        
        additional_phone_number = user_data["contactInfo"].get("additionalPhoneNumber", '').strip()
        if additional_phone_number:
            add_phone_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_addPhoneNumberButton"]')))
            add_phone_button.click()
            # fill 
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_addPhoneNumberTextBox"]'))).send_keys(user_data['contactInfo']['additionalPhoneNumber'])
            phone_type = user_data["contactInfo"].get("additionalPhoneNumberType").strip().lower()
            if phone_type == "home":
                type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_PhoneNumberType_0"]')))
                type_radio.click()
            elif phone_type == "work":
                type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_PhoneNumberType_1"]')))
                type_radio.click()
            else:
                type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_PhoneNumberType_2"]')))
                type_radio.click()
        
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton"]')))
        next_button.click()
        
        print("waiting for page 4") 
         
# page 5     
            
        
           
            
    except Exception as e:
        print(f"An error occurred: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

    finally:
        driver.quit()