from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from dropdown_helper import select_how_passport_lost

def lost_or_stolen(driver, user_data):
    try:
        wait = WebDriverWait(driver, 120)
        
        next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
        driver.execute_script("arguments[0].click();", next_button)
        print("enter lost or stolen")
        # Are you reporting your own valid lost or stolen U.S. passport? 
        is_own_passport = user_data.get('lostInfo').get('isOwnPassport',False)
        print(f"is_own_passport: {is_own_passport}")
        if is_own_passport:
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_lostStolenStep_reporterYesRadioButton"]')))
            driver.execute_script("arguments[0].click();", radio)
        else:
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_lostStolenStep_reporterNoRadioButton"]')))
            driver.execute_script("arguments[0].click();", radio)

            # reporter first name
            reporter_first_name = user_data.get('lostInfo').get('reporterFirstName')
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_reporterFirstNameTextBox'))).send_keys(reporter_first_name)
            
            # reporter middle name
            reporter_middle_name = user_data.get('lostInfo').get('reporterMiddleName',False)
            if reporter_middle_name:
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_reporterMiddleNameTextBox'))).send_keys(reporter_middle_name)
            
            # reporter last name
            reporter_last_name = user_data.get('lostInfo').get('reporterLastName')
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_reporterLastNameTextBox'))).send_keys(reporter_last_name)
            
            # reporter relationship
            reporter_relationship = user_data.get('lostInfo').get('reporterRelationship')
            wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_reporterRelationshipTextBox'))).send_keys(reporter_relationship)

        #report lost or stolen
        is_police_report = user_data.get('lostInfo').get('policeReport', False)
        if is_police_report:
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_lostStolenStep_policeReportYesRadioButton1"]')))
        else:
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_lostStolenStep_policeReportNoRadioButton1"]')))
        
        driver.execute_script("arguments[0].click();", radio)

        passport_history_details = user_data.get("passportHistory", {})
        passport_history = passport_history_details.get('hasPassportCardOrBook', False)
        passport_book_details = passport_history_details.get("passportBookDetails", False)
        passport_card_details = passport_history_details.get("passportCardDetails", False)
        passport_card_status = passport_card_details.get("status")
        passport_book_status = passport_book_details.get("status")
        has_book_reported_lost_or_stolen = passport_book_details.get("hasReportedLostOrStolen")
        has_card_reported_lost_or_stolen = passport_card_details.get("hasReportedLostOrStolen")

        book_details = user_data.get('lostInfo').get('bookLostDetails')
        card_details = user_data.get('lostInfo').get('cardLostDetails')
        book_location = user_data.get('lostInfo').get('bookLostLocation')
        card_location = user_data.get('lostInfo').get('cardLostLocation')
        book_lost_date_details = user_data.get('lostInfo').get('bookLostDate')
        card_lost_date_details = user_data.get('lostInfo').get('cardLostDate')

        if (passport_card_status in ["lost", "stolen"] and not has_card_reported_lost_or_stolen) and (passport_book_status in ["lost", "stolen"] and not has_book_reported_lost_or_stolen):
            lost_at_same_time = user_data.get('lostInfo').get('lostAtSameTime')
            if lost_at_same_time:
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_lostStolenStep_loseSameYesRadioButton"]')))
                driver.execute_script("arguments[0].click();", radio)

                #book lost details 
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_bookLostHowTextBox'))).send_keys(book_details)
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_bookLostWhereTextBox'))).send_keys(book_location)
                book_lost_date_str = book_lost_date_details.get('$date')
                book_lost_date = datetime.strptime(book_lost_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_book_data = book_lost_date.strftime("%m-%d-%Y")
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_bookLostDateTextBox'))).send_keys(formatted_book_data)
            else:
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_lostStolenStep_loseSameNoRadioButton"]')))  
                driver.execute_script("arguments[0].click();", radio)

                #book lost details
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_bookLostHowTextBox'))).send_keys(book_details)
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_bookLostWhereTextBox'))).send_keys(book_location)
                book_lost_date_str = book_lost_date_details.get('$date')
                book_lost_date = datetime.strptime(book_lost_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_book_data = book_lost_date.strftime("%m-%d-%Y")
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_bookLostDateTextBox'))).send_keys(formatted_book_data)

                #card lost details
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_cardLostHowTextBox'))).send_keys(card_details)
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_cardLostWhereTextBox'))).send_keys(card_location)
                card_lost_date_str = card_lost_date_details.get('$date')
                card_lost_date = datetime.strptime(card_lost_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_card_data = card_lost_date.strftime("%m-%d-%Y")
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_cardLostDateTextBox'))).send_keys(formatted_card_data)

        else:
            #lost details
            if book_details:
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_bookLostHowTextBox'))).send_keys(book_details)
            elif card_details:
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_cardLostHowTextBox'))).send_keys(card_details)
            

            #lost location details
            if book_location:
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_bookLostWhereTextBox'))).send_keys(book_location)
            elif card_location:
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_cardLostWhereTextBox'))).send_keys(card_location)

            
            #lost date
            if book_lost_date_details:
                book_lost_date_str = book_lost_date_details.get('$date')
                book_lost_date = datetime.strptime(book_lost_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_data = book_lost_date.strftime("%m-%d-%Y")
                print(formatted_data)
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_bookLostDateTextBox'))).send_keys(formatted_data)
            elif card_lost_date_details:
                card_lost_date_str = card_lost_date_details.get('$date')
                card_lost_date = datetime.strptime(card_lost_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_data = card_lost_date.strftime("%m-%d-%Y")
                print(formatted_data)
                wait.until(EC.presence_of_element_located((By.ID, 'PassportWizard_lostStolenStep_cardLostDateTextBox'))).send_keys(formatted_data)
        
        #had Previous Lost
        had_previous_lost = user_data.get('lostInfo').get('hadPreviousLost', False)
        if had_previous_lost:
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_lostStolenStep_lostPrevYesRadioButton"]')))
            driver.execute_script("arguments[0].click();", radio)

            #how many passport previously lost
            how_many_passport_lost = user_data.get('lostInfo').get('previousLostCount')
            passport_lost_count_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_lostStolenStep_lostPassportCountList"]')))
            select_how_passport_lost(passport_lost_count_dropdown, how_many_passport_lost)

            #previous lost dates
            passport_lost_dates = user_data.get('lostInfo').get('previousLostDates')
            for idx in range(len(passport_lost_dates)):
                passport_lost_date_str = passport_lost_dates[idx].get('$date')
                passport_lost_date = datetime.strptime(passport_lost_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_data = passport_lost_date.strftime("%m-%d-%Y")
                print(formatted_data)
                wait.until(EC.presence_of_element_located((By.ID, f"PassportWizard_lostStolenStep_prevPassportLostDateTextBox{idx+1}"))).send_keys(formatted_data)

            #had previous lost
            had_previous_lost_police_report = user_data.get('lostInfo').get('previousPoliceReport', False)
            print(f"had_previous_lost_police_report: {had_previous_lost_police_report}")
            if had_previous_lost_police_report:
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_lostStolenStep_policeReportYesRadioButton2"]')))
            else:
                radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_lostStolenStep_policeReportNoRadioButton2"]')))
            
            driver.execute_script("arguments[0].click();", radio)

        else:
            radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PassportWizard_lostStolenStep_lostPrevNoRadioButton"]')))
            driver.execute_script("arguments[0].click();", radio)

        next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
        driver.execute_script("arguments[0].click();", next_button)
    
    except Exception as e:
        print("An error occurred:", str(e))



