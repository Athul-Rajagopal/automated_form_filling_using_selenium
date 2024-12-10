from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from lost_or_stolen import lost_or_stolen

def passport_route_flow_helper(driver, user_data):
    try:
        print("inside passport_route_flow_helper")
        wait = WebDriverWait(driver, 120)

        passport_history_details = user_data.get("passportHistory", {})
        passport_history = passport_history_details.get('hasPassportCardOrBook', False)
        passport_book_details = passport_history_details.get("passportBookDetails", False)
        passport_card_details = passport_history_details.get("passportCardDetails", False)

        # if passport_book_details and passport_history != "both":
        if passport_history == "book":
            passport_book_status = passport_book_details.get("status")
            if passport_book_status in ["lost", "stolen"]:
                is_older_than_15_years = user_data.get("passportHistory").get("passportBookDetails").get("isOlderThan15Years", False)
                
                has_book_reported_lost_or_stolen = passport_book_details.get("hasReportedLostOrStolen")
                # If passport is not older than 15 years OR issue date exists AND has not been reported
                if (is_older_than_15_years == 'no' or is_older_than_15_years == 'unknown' or date_issue) and not has_book_reported_lost_or_stolen:
                    print("indide")
                    # Handle lost/stolen passport flow
                    lost_or_stolen(driver, user_data)
                else:
                    # Continue to next page
                    next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
                    driver.execute_script("arguments[0].click();", next_button)
            else:
                next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
                driver.execute_script("arguments[0].click();", next_button)

        # elif passport_card_details and passport_history != "both":
        elif passport_history == "card":
            passport_card_status = passport_card_details.get("status")
            has_card_reported_lost_or_stolen = passport_card_details.get("hasReportedLostOrStolen")
            if passport_card_status in ["lost", "stolen"] and not has_card_reported_lost_or_stolen:  
                lost_or_stolen(driver, user_data)
            else:
                next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
                driver.execute_script("arguments[0].click();", next_button)
        
        elif passport_history == "both":
            print("inside both")
            passport_card_status = passport_card_details.get("status")
            passport_book_status = passport_book_details.get("status")
            has_book_reported_lost_or_stolen = passport_book_details.get("hasReportedLostOrStolen")
            has_card_reported_lost_or_stolen = passport_card_details.get("hasReportedLostOrStolen")

            if passport_card_status in ["lost", "stolen"] and not has_card_reported_lost_or_stolen:
                lost_or_stolen(driver, user_data)
            elif passport_book_status in ["lost", "stolen"] and not has_book_reported_lost_or_stolen:
                lost_or_stolen(driver, user_data)
            else:
                print('else case')
                next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
                driver.execute_script("arguments[0].click();", next_button)

        elif passport_history == "none":
            print("continue to next page hai")
            next_button = wait.until(EC.element_to_be_clickable((By.ID,'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton')))
            driver.execute_script("arguments[0].click();", next_button)

    except Exception as e:
        print(f"Error in passport_route_flow_helper: {e}")
        # raise e