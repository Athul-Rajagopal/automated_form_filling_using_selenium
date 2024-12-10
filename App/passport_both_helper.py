from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def passport_both_helper(driver, user_data):
    try:
        wait = WebDriverWait(driver, 120)
        print("passport both helper")
        radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CurrentHaveBoth"]')))
        driver.execute_script("arguments[0].click();", radio)

        # passport book details and passport card details
        passport_book_details = user_data.get("passportHistory").get("passportBookDetails", False)
        passport_card_details = user_data.get("passportHistory").get("passportCardDetails", False)
        
        if not passport_book_details:
            print("passport book details not found")
        
        if not passport_card_details:
            print("passport card details not found")

        # card details
        passport_card_status = user_data.get("passportHistory", {}).get("passportCardDetails", {}).get("status")
        if passport_card_status == "lost":
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CardLost"]')))
        elif passport_card_status == "stolen":
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CardStolen"]')))
        elif passport_card_details == 'yes':
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CardYes"]')))
        elif passport_card_status == "damaged":
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_CardDamaged"]')))
        driver.execute_script("arguments[0].click();", radio)

        # card issue date
        if passport_card_status in ["lost", "stolen"]:
            card_has_reported = user_data.get("passportHistory").get("passportCardDetails").get("hasReportedLostOrStolen")
            if card_has_reported:
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_ReportLostCardYesRadioButton"]')))
            else:
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_ReportLostCardNoRadioButton"]')))
            driver.execute_script("arguments[0].click();", radio)


        card_issue_date = user_data.get("passportHistory").get("passportCardDetails").get("issueDate", False)
        if card_issue_date:
            card_issue_date_str = card_issue_date.get("$date")
            card_issue_date = datetime.strptime(card_issue_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_card_issue_date = card_issue_date.strftime("%m-%d-%Y")
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_CardIssueDate'))).send_keys(formatted_card_issue_date)

        # card first and middle name and card number check if passport card status is yes
        card_first_name_and_middle_name = user_data.get("passportHistory").get("passportCardDetails").get("firstNameAndMiddleName", False)
        card_number = user_data.get("passportHistory").get("passportCardDetails").get("number", False)
        if passport_card_status == "yes":
            if not card_first_name_and_middle_name or not card_number:
                print("first name and middle name and card number not found")
                raise ValueError("First name and middle name and card number are required when passport card status is 'yes'.")

        # first name and middle name
        if card_first_name_and_middle_name:
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_firstNameOnCard'))).send_keys(card_first_name_and_middle_name)
        
        # last name
        card_last_name = user_data.get("passportHistory").get("passportCardDetails").get("lastName", False)
        if card_last_name:
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_lastNameOnCard'))).send_keys(card_last_name)

        # card number
        if card_number:
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_ExistingCardNumber'))).send_keys(card_number)
        
        # book details
        passport_book_status = user_data.get("passportHistory").get("passportBookDetails").get("status")
        if passport_book_status == "lost":
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_BookLost"]')))
        elif passport_book_status == "stolen":
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_BookStolen"]')))
        elif passport_book_status == "damaged":
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_BookDamaged"]')))
        elif passport_book_status == "yes":
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_BookYes"]')))
        driver.execute_script("arguments[0].click();", radio)


        # book issue date
        if passport_book_status in ["lost", "stolen"]:
            book_has_reported = user_data.get("passportHistory").get("passportBookDetails").get("hasReportedLostOrStolen")
            if book_has_reported:
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_ReportLostBookYesRadioButton"]')))
            else:
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_mostRecentPassport_ReportLostBookNoRadioButton"]')))
            driver.execute_script("arguments[0].click();", radio)

            book_issue_date = user_data.get("passportHistory").get("passportBookDetails").get("issueDate", False)
            if book_issue_date:
                book_issue_date_str = book_issue_date.get("$date")
                book_issue_date = datetime.strptime(book_issue_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_book_issue_date = book_issue_date.strftime("%m-%d-%Y")
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_BookIssueDate'))).send_keys(formatted_book_issue_date)
            else:
                print('book issue date not found')
                next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
                driver.execute_script("arguments[0].click();", next_button)
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
            book_issue_date = user_data.get("passportHistory").get("passportBookDetails").get("issueDate", False)
            if book_issue_date:
                book_issue_date_str = book_issue_date.get("$date")
                book_issue_date = datetime.strptime(book_issue_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_book_issue_date = book_issue_date.strftime("%m-%d-%Y")
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_BookIssueDate'))).send_keys(formatted_book_issue_date)
        
        # book first and middle name and book number check if passport book status is yes
        book_first_name_and_middle_name = user_data.get("passportHistory").get("passportBookDetails").get("firstNameAndMiddleName", False)
        book_number = user_data.get("passportHistory").get("passportBookDetails").get("number", False)
        if passport_book_status == "yes":
            if not book_first_name_and_middle_name or not book_number:
                print("first name and middle name and book number not found")
                raise ValueError("First name and middle name and book number are required when passport book status is 'yes'.")

        # first name and middle name
        if book_first_name_and_middle_name:
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_firstNameOnBook'))).send_keys(book_first_name_and_middle_name)
        
        # last name
        book_last_name = user_data.get("passportHistory").get("passportBookDetails").get("lastName", False)
        if book_last_name:
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_lastNameOnBook'))).send_keys(book_last_name)

        # book number
        if book_number:
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_mostRecentPassport_ExistingBookNumber'))).send_keys(book_number)

        

    except Exception as e:
        print(f"Error in passport_both_helper: {e}")
        # raise e
    