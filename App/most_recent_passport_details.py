from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime

check_box_items_xpath = {
    "lastName":'//*[@id="PassportWizard_mostRecentPassportContinued_IncorrectLastName"]',
    "firstName":'//*[@id="PassportWizard_mostRecentPassportContinued_IncorrectFirstName"]',
    "middleName":'//*[@id="PassportWizard_mostRecentPassportContinued_IncorrectMiddleName"]',
    "placeOfBirth":'//*[@id="PassportWizard_mostRecentPassportContinued_IncorrectPlaceOfBirth"]',
    "dateOfBirth":'//*[@id="PassportWizard_mostRecentPassportContinued_IncorrectDateOfBirth"]',
    "gender":'//*[@id="PassportWizard_mostRecentPassportContinued_IncorrectSex"]'
}

def most_recent_passport_details(driver, user_data):
    try:    
        wait = WebDriverWait(driver, 120)
        next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
        driver.execute_script("arguments[0].click();", next_button)
        print("most recent passport details")

        # Check the data correctness
        data_correctness = user_data.get('nameChangeInfo').get('dataCorrectness')
        if data_correctness == 'correct':
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_dataIncorrectNone"]')))
            driver.execute_script("arguments[0].click();", radio)
        elif data_correctness == 'incorrectBook':
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_dataIncorrectBook"]')))
            driver.execute_script("arguments[0].click();", radio)

            # Incorrect fields
            incorrect_fields = user_data.get('nameChangeInfo').get('incorrectFields')
            if incorrect_fields:
                for field in incorrect_fields:
                    checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, check_box_items_xpath[field])))
                    driver.execute_script("arguments[0].click();", checkbox)


        name_changed = user_data.get('nameChangeInfo').get('nameChanged')
        if name_changed == 'noChange':
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_nameChangeNone"]')))
            driver.execute_script("arguments[0].click();", radio)
        elif name_changed == 'changedBook':
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_nameChangeBook"]')))
            driver.execute_script("arguments[0].click();", radio)
            
            # Reason for name change
            reason = user_data.get('nameChangeInfo').get('nameChangeDetails').get('reason')
            if reason == 'marriage':
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_NameChangeReason_0"]')))
            elif reason == 'courtOrder':
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_NameChangeReason_1"]')))
            driver.execute_script("arguments[0].click();", radio)

            # Date of name change
            name_change_date_str = user_data.get('nameChangeInfo').get('nameChangeDetails').get('date')
            name_change_date = datetime.strptime(name_change_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_name_change_date = name_change_date.strftime("%m-%d-%Y")
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassportContinued_NameChangeDate'))).send_keys(formatted_name_change_date)

            # Place of name change  
            place_of_name_change = user_data.get('nameChangeInfo').get('nameChangeDetails').get('place')
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassportContinued_NameChangePlace'))).send_keys(place_of_name_change)

            # Can provide documentation
            can_provide_documentation = user_data.get('nameChangeInfo').get('nameChangeDetails').get('canProvideDocumentation')
            if can_provide_documentation:
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_NameChangeCertified_0"]')))
            else:
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_NameChangeCertified_1"]')))
            driver.execute_script("arguments[0].click();", radio)

    except Exception as e:
        print(f"Error in most recent passport details: {e}")
