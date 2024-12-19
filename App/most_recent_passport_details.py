from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from date_calculation_helper import is_recent_issue, is_correct_details_needed

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

        date_of_birth_str = user_data.get('personalInfo').get('dateOfBirth').get('$date')
         # Safely get issue dates with multiple fallbacks
        passport_history = user_data.get("passportHistory", {})
        if passport_history:
            book_details = passport_history.get("passportBookDetails", {})
            card_details = passport_history.get("passportCardDetails", {})
        

        is_book_correct_details_needed = False
        is_card_correct_details_needed = False
        # Handle missing issueDate field
        if book_details:
            book_issue_date = book_details.get("issueDate")
            book_issue_date_str = book_issue_date.get("$date", None)
            is_book_correct_details_needed = is_correct_details_needed(date_of_birth_str, book_issue_date_str)
        if card_details:
            card_issue_date = card_details.get("issueDate")
            card_issue_date_str = card_issue_date.get("$date", None)
            is_card_correct_details_needed = is_correct_details_needed(date_of_birth_str, card_issue_date_str) 
        


        if is_book_correct_details_needed or is_card_correct_details_needed:
            # Check the data correctness
            name_change_info_exist = user_data.get('nameChangeInfo', False)
            if name_change_info_exist:
                data_correctness = name_change_info_exist.get('dataCorrectness')
                if data_correctness == 'correct':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_dataIncorrectNone"]')))
                    driver.execute_script("arguments[0].click();", radio)
                elif data_correctness == 'incorrectBook':
                    print("incorrect book")
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_dataIncorrectBook"]')))
                    driver.execute_script("arguments[0].click();", radio)

                    # Incorrect fields
                    incorrect_fields = user_data.get('nameChangeInfo').get('incorrectFields')
                    if incorrect_fields:
                        for field in incorrect_fields:
                            checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, check_box_items_xpath[field])))
                            driver.execute_script("arguments[0].click();", checkbox)

                elif data_correctness == 'incorrectCard':
                    print("incorrect card")
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_dataIncorrectCard"]')))
                    driver.execute_script("arguments[0].click();", radio)

                    # Incorrect fields
                    incorrect_fields = user_data.get('nameChangeInfo').get('incorrectFields')
                    if incorrect_fields:
                        for field in incorrect_fields:
                            checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, check_box_items_xpath[field])))
                            driver.execute_script("arguments[0].click();", checkbox)

                elif data_correctness == 'incorrectBoth':
                    print("incorrect both")
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_dataIncorrectBoth"]')))
                    driver.execute_script("arguments[0].click();", radio)

                    # Incorrect fields
                    incorrect_fields = user_data.get('nameChangeInfo').get('incorrectFields')
                    if incorrect_fields:
                        for field in incorrect_fields:
                            checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, check_box_items_xpath[field])))
                            driver.execute_script("arguments[0].click();", checkbox)
        
        name_change_info_exist = user_data.get('nameChangeInfo', False)
        if name_change_info_exist:
            name_changed = name_change_info_exist.get('nameChanged')
            if name_changed == 'noChange':
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_nameChangeNone"]')))
                driver.execute_script("arguments[0].click();", radio)

            elif name_changed == 'changedBook':
                print("changed book")
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_nameChangeBook"]')))
                driver.execute_script("arguments[0].click();", radio)
                
                # Reason for name change
                reason = name_change_info_exist.get('nameChangeDetails').get('reason')
                if reason == 'marriage':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_NameChangeReason_0"]')))
                elif reason == 'courtOrder':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_NameChangeReason_1"]')))
                driver.execute_script("arguments[0].click();", radio)

                # Date of name change
                name_change_date_str = name_change_info_exist.get('nameChangeDetails').get('date').get('$date')
                name_change_date = datetime.strptime(name_change_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_name_change_date = name_change_date.strftime("%m-%d-%Y")
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassportContinued_NameChangeDate'))).send_keys(formatted_name_change_date)

                # Place of name change  
                place_of_name_change = name_change_info_exist.get('nameChangeDetails').get('place')
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassportContinued_NameChangePlace'))).send_keys(place_of_name_change)

                # Can provide documentation
                can_provide_documentation = name_change_info_exist.get('nameChangeDetails').get('canProvideDocumentation')
                if can_provide_documentation:
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_NameChangeCertified_0"]')))
                else:
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_NameChangeCertified_1"]')))
                driver.execute_script("arguments[0].click();", radio)
            
            elif name_changed == 'changedCard':
                print("changed card")
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_nameChangeCard"]')))
                driver.execute_script("arguments[0].click();", radio)

                # Reason for name change
                reason = user_data.get('nameChangeInfo').get('nameChangeDetails').get('reason')
                if reason == 'marriage':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_NameChangeReason_0"]')))
                elif reason == 'courtOrder':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_NameChangeReason_1"]')))
                driver.execute_script("arguments[0].click();", radio)

                # Date of name change
                name_change_date_str = user_data.get('nameChangeInfo').get('nameChangeDetails').get('date').get('$date')
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

            elif name_changed == 'changedBoth':
                print("changed both")
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_nameChangeBoth"]')))
                driver.execute_script("arguments[0].click();", radio)

                # Reason for name change
                reason = user_data.get('nameChangeInfo').get('nameChangeDetails').get('reason')
                if reason == 'marriage':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_NameChangeReason_0"]')))
                elif reason == 'courtOrder':
                    radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_NameChangeReason_1"]')))
                driver.execute_script("arguments[0].click();", radio)

                # Date of name change
                name_change_date_str = user_data.get('nameChangeInfo').get('nameChangeDetails').get('date').get('$date')
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

        #is recent issue
        passport_history = user_data.get("passportHistory", False).get('hasPassportCardOrBook')
        if passport_history == "book" or passport_history == "both":
            passport_book_status = user_data.get("passportHistory", {}).get("passportBookDetails", {}).get("status", False)
            if passport_book_status == "yes" :
                issue_date_str = user_data.get("passportHistory", {}).get("passportBookDetails", {}).get("issueDate", {}).get("$date")
                if is_recent_issue(issue_date_str):
                    is_limited_passport = user_data.get("nameChangeInfo", {}).get("isLimitedPassport", False)
                    if is_limited_passport:
                        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_LimitedIssueBook_0"]')))
                        driver.execute_script("arguments[0].click();", radio)

                        paid_for_card = user_data.get("nameChangeInfo", {}).get("paidForCard", False)
                        if paid_for_card:
                            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_paidForCard_0"]')))
                            driver.execute_script("arguments[0].click();", radio)
                        else:
                            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_paidForCard_1"]')))
                            driver.execute_script("arguments[0].click();", radio)
                    else:
                        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassportContinued_LimitedIssueBook_1"]')))
                        driver.execute_script("arguments[0].click();", radio)

            next_button = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton"]')))
            driver.execute_script("arguments[0].click();", next_button)


    except Exception as e:
        print(f"Error in most recent passport details: {e}")
        raise e