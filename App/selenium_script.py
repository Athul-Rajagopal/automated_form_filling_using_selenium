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





def fill_form(user_data):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    
    # Use the Service class to specify the driver path
    chrome_service = Service(r"C:\chromedriver.exe")
    chrome_options.page_load_strategy = 'eager' 
    
    download_dir = r"C:\Users\athul\Downloads\passport"  # Change this to your desired download directory
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,  # Set download directory
        "download.prompt_for_download": False,  # Disable the download prompt
        "plugins.always_open_pdf_externally": True  # Open PDFs externally
    })

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
        
        # country of birth
        country_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_aboutYouStep_pobCountryList"]')))
        select_country(country_dropdown, user_data["personalInfo"]["countryOfBirth"], driver)
        
        # state of birth
        country = user_data["personalInfo"].get("countryOfBirth").upper()
        if country in ['CANADA', 'UNITED STATES']:
            # state_dropdown = wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_aboutYouStep_pobStateList')))
            
            select_country_and_state(
                country=country, 
                state_abbreviation=user_data["personalInfo"]["stateOfBirth"], 
                driver=driver, 
                country_xpath='//*[@id="PassportWizard_aboutYouStep_pobCountryList"]',  # Country dropdown XPath
                state_xpath='//*[@id="PassportWizard_aboutYouStep_pobStateList"]'       # State dropdown XPath
            )
        
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
        about_form_submit_button = wait.until(EC.element_to_be_clickable((By.ID, 'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
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
            # state_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_mailStateList"]')))
            select_country_and_state(
                country=country, 
                state_abbreviation=user_data["addressInfo"]["state"], 
                driver=driver, 
                country_xpath='//*[@id="PassportWizard_addressStep_mailCountryList"]',  # Country dropdown XPath
                state_xpath='//*[@id="PassportWizard_addressStep_mailStateList"]'       # State dropdown XPath
            )
        
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
                # state_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_permanentStateList"]')))
                # select_state(state_dropdown, user_data["permanentAddress"]["state"], driver)
                select_country_and_state(
                country=country, 
                state_abbreviation=user_data["permanentAddress"]["state"], 
                driver=driver, 
                country_xpath='//*[@id="PassportWizard_addressStep_permanentCountryList"]',  # Country dropdown XPath
                state_xpath='//*[@id="PassportWizard_addressStep_permanentStateList"]'       # State dropdown XPath
            )
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
        
        additional_phone_number = user_data["contactInfo"].get("additionalPhoneNumber", '').strip()
        if additional_phone_number:
            add_phone_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_addressStep_addPhoneNumberButton"]')))
            add_phone_button.click()
            # fill 
            phone_type = user_data["contactInfo"].get("additionalPhoneNumberType").strip().lower()
            
            # Ensure overlay is not present
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'TransparentDiv')))
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_addressStep_addPhoneNumberTextBox"]'))).send_keys(user_data['contactInfo']['additionalPhoneNumber'])
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
        
        print("waiting for page 5") 
         
# page 5     
        # travel plans
        
        date_of_trip_str = user_data['travelPlans']['travelDate']['$date']
        date_of_trip = datetime.strptime(date_of_trip_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_dot = date_of_trip.strftime("%m-%d-%Y")
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_travelPlans_TripDateTextBox'))).send_keys(formatted_dot)
        
        date_of_return_str = user_data['travelPlans']['returnDate']['$date']
        date_of_return = datetime.strptime(date_of_return_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_dor = date_of_return.strftime("%m-%d-%Y")
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_travelPlans_TripDateTextBox'))).send_keys(formatted_dor)
        
        # click next
        next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
        next_button.click()
        
        print("waiting for page 6")  
        
# page 6
        # emergency contact
        # name
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_emergencyContacts_ecNameTextBox'))).send_keys(user_data['emergencyContact']['emergencyContactName'])
        
        # street
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_emergencyContacts_ecAddressTextBox'))).send_keys(user_data['emergencyContact']['street'])
        
        # appartment
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_emergencyContacts_ecApartmentTextBox'))).send_keys(user_data['emergencyContact']['apartmentOrUnit'])
        
        # city
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_emergencyContacts_ecCityTextBox'))).send_keys(user_data['emergencyContact']['city'])
        
        
        # zip code
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_emergencyContacts_ZipCodeTextBox"]'))).send_keys(user_data['emergencyContact']['zipCode'])
        
        # phone
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_emergencyContacts_ecPhoneTextBox'))).send_keys(user_data['emergencyContact']['emergencyContactPhone'])
        
        # relationship
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_emergencyContacts_ecRelationshipTextBox'))).send_keys(user_data['emergencyContact']['emergencyContactRelationship'])
        
        # state 
        state_abbreviation = user_data["emergencyContact"]["state"]
        state_xpath = '//*[@id="PassportWizard_emergencyContacts_ecStateList"]'
        select_state_without_country(driver=driver, 
                                     state_abbreviation=state_abbreviation, 
                                     state_xpath=state_xpath)
        # click next
        next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
        driver.execute_script("arguments[0].click();", next_button)
        
        print("waiting for page 7")
        
# page 7

        type_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CurrentHaveNone"]')))
        driver.execute_script("arguments[0].click();", type_radio)
        
        next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
        driver.execute_script("arguments[0].click();", next_button)
        
        print("waiting for page 8")
        
# page 8

        # parent and spouse information
        # parent 1
        # first name and middle name
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent1FirstNameTextBox'))).send_keys(user_data['parentInfo']['parent1']["firstName"])
        # last name
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent1LastNameTextBox'))).send_keys(user_data['parentInfo']['parent1']["lastName"])
        # dob
        parent1_dob_str = user_data['parentInfo']['parent1']["dateOfBirth"]["$date"]
        parent1_dob = datetime.strptime(parent1_dob_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_dob1 = parent1_dob.strftime("%m-%d-%Y")
        print(formatted_dob1)
        # wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent1BirthDateTextBox'))).send_keys(formatted_dob)
        parent1_dob_input = wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent1BirthDateTextBox')))
        parent1_dob_input.click()  # Focus the field
        parent1_dob_input.clear()   # Clear any existing value
        parent1_dob_input.send_keys(formatted_dob1)  # Send formatted DOB
        time.sleep(0.5) 
        # place of birth
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent1BirthPlaceTextBox'))).send_keys(user_data['parentInfo']['parent1']["placeOfBirth"])
        # gender

        gender = user_data["parentInfo"]['parent1'].get("gender").strip().lower()

        if gender == "male":
            gender_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent1SexList_0"]')))  # Male radio button
            driver.execute_script("arguments[0].click();", gender_radio)
        elif gender == "female":
            gender_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent1SexList_1"]')))  # Female radio button
            driver.execute_script("arguments[0].click();", gender_radio)
        else:
            gender_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent1SexList_2"]')))  # Other/Unspecified
            driver.execute_script("arguments[0].click();", gender_radio)
            
        # citizenship
        citizenship = user_data["parentInfo"]['parent1'].get("isUSCitizen")
        if citizenship:
            citizenship_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent1CitizenList_0"]')))  # Other/Unspecified
            driver.execute_script("arguments[0].click();", citizenship_radio)
        else:
            citizenship_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent1CitizenList_1"]')))  # Other/Unspecified
            driver.execute_script("arguments[0].click();", citizenship_radio)
            
        # parent 2
        # first name and middle name
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent2FirstNameTextBox'))).send_keys(user_data['parentInfo']['parent2']["firstName"])
        # last name
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent2LastNameTextBox'))).send_keys(user_data['parentInfo']['parent2']["lastName"])
        # dob
        parent2_dob_str = user_data['parentInfo']['parent2']["dateOfBirth"]["$date"]
        parent2_dob = datetime.strptime(parent2_dob_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_dob2 = parent2_dob.strftime("%m-%d-%Y")
        
        print(formatted_dob2)
        # wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent2BirthDateTextBox'))).send_keys(formatted_dob)
        parent2_dob_input = wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent2BirthDateTextBox')))
        parent2_dob_input.click()  # Focus the field
        parent2_dob_input.clear()   # Clear any existing value
        parent2_dob_input.send_keys(formatted_dob2)  # Send formatted DOB
        time.sleep(0.5)
        # place of birth
        wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_parent2BirthPlaceTextBox'))).send_keys(user_data['parentInfo']['parent2']["placeOfBirth"])
        # gender

        gender = user_data["parentInfo"]['parent2'].get("gender").strip().lower()

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
        citizenship = user_data["parentInfo"]['parent1'].get("isUSCitizen")
        if citizenship:
            citizenship_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent2CitizenList_0"]')))  # Other/Unspecified
            driver.execute_script("arguments[0].click();", citizenship_radio)
        else:
            citizenship_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_parent2CitizenList_1"]')))  # Other/Unspecified
            driver.execute_script("arguments[0].click();", citizenship_radio)
            
        # marriage info
        marriage_info = user_data["marriageInfo"].get("isMarried")
        if marriage_info:
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_marriedList_0"]')))  # Other/Unspecified
            driver.execute_script("arguments[0].click();", radio)
            
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_spouseNameTextBox'))).send_keys(user_data['marriageInfo']['marriageDetails']["firstName"])
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_spouseLastNameTextBox'))).send_keys(user_data['marriageInfo']['marriageDetails']["lastName"])
            # dob
            spouse_dob_str = user_data['marriageInfo']['marriageDetails']["dateOfBirth"]["$date"]
            spouse_dob = datetime.strptime(spouse_dob_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_dob = spouse_dob.strftime("%m-%d-%Y")
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_spouseBirthDateTextBox'))).send_keys(formatted_dob)
            # place of birth
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_spouseBirthplaceTextBox'))).send_keys(user_data['marriageInfo']['marriageDetails']["placeOfBirth"])
            # citizenship
            citizenship = user_data['marriageInfo']['marriageDetails'].get("isUSCitizen")
            if citizenship:
                citizenship_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_spouseCitizenList_0"]')))  # Other/Unspecified
                driver.execute_script("arguments[0].click();", citizenship_radio)
            else:
                citizenship_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_spouseCitizenList_1"]')))  # Other/Unspecified
                driver.execute_script("arguments[0].click();", citizenship_radio)
                
            # date of marriage
            date_of_marriage_str = user_data['marriageInfo']['marriageDetails']["dateOfMarriage"]["$date"]
            date_of_marriage = datetime.strptime(date_of_marriage_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_dom = date_of_marriage.strftime("%m-%d-%Y")
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_moreAboutYouStep_marriedDateTextBox'))).send_keys(formatted_dom)
            
            # widow or divorce
            widow_or_divorce = user_data['marriageInfo']['marriageDetails'].get("isWidowOrDivorced")
            if widow_or_divorce:
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_divorcedList_0"]'))) 
                driver.execute_script("arguments[0].click();", radio)
                ## want to fill divorced date
            else:
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_divorcedList_1"]')))  
                driver.execute_script("arguments[0].click();", radio)
        
        else:
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_moreAboutYouStep_marriedList_1"]')))  # Other/Unspecified
            driver.execute_script("arguments[0].click();", radio)
            
        next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
        driver.execute_script("arguments[0].click();", next_button)

        
        print("waiting for page 9")
        
# page 9
        # other names
        input_id='PassportWizard_otherNameStep_addOtherFirstTextBox'
        wait.until(EC.presence_of_element_located((By.ID, input_id)))
        input_field = driver.find_element(By.ID, input_id)
        input_field.send_keys(Keys.TAB)
        
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton"]')))
        driver.execute_script("arguments[0].click();", next_button)
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
        
# page 11

        # payment selection
        # second option
        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_feesStep_cardFee"]'))) 
        driver.execute_script("arguments[0].click();", radio)
        
        button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_FinishNavigationTemplateContainerID_FinishButton')))
        driver.execute_script("arguments[0].scrollIntoView();", button)
        time.sleep(1) 
        driver.execute_script("arguments[0].click();", button)
        
        print("waiting for page 12")

# page 12

        # printing pdf
        acknowledgment_checkbox = wait.until(EC.element_to_be_clickable((By.ID, 'PassportWizard_nextStepsStep_ConfirmationCheckBox')))
        driver.execute_script("arguments[0].scrollIntoView();", acknowledgment_checkbox)
        acknowledgment_checkbox.click()
        
        wait.until(EC.element_to_be_clickable((By.ID, 'PassportWizard_nextStepsStep_printFormButton')))
        next_button = driver.find_element(By.ID, 'PassportWizard_nextStepsStep_printFormButton')
        # driver.execute_script("arguments[0].scrollIntoView();", next_button)
        driver.execute_script("arguments[0].click();", next_button)
        
        wait_for_downloads(download_dir)
        
        time.sleep(10)
        print("pdf downloaded")
        
        
                
        
        
            
    except Exception as e:
        print(f"An error occurred: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

    finally:
        driver.quit()