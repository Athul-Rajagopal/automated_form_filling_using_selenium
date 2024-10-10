from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
import time


def select_gender(select_element, gender):
    """Selects gender from the dropdown."""
    select = Select(select_element)
    if gender.lower() == 'male':
        select.select_by_visible_text('M')  # Adjust the text to match the dropdown options
    elif gender.lower() == 'female':
        select.select_by_visible_text('F')  # Adjust the text to match the dropdown options
    else:
        select.select_by_visible_text('X')  # Use 'X' for unspecified

def select_height_feet(select_element, feet_height):
    """Selects height in feet from the dropdown."""
    select = Select(select_element)
    select.select_by_visible_text(str(feet_height))  # Converts to string for selection

def select_height_inches(select_element, inches_height):
    """Selects height in inches from the dropdown."""
    select = Select(select_element)
    select.select_by_visible_text(str(inches_height))  # Converts to string for selection

def select_hair_color(select_element, hair_color):
    """Selects hair color from the dropdown."""
    select = Select(select_element)
    hair_color = hair_color.lower()
    
    if hair_color == 'black':
        select.select_by_visible_text('BLACK')
    elif hair_color == 'blonde':
        select.select_by_visible_text('BLONDE')
    elif hair_color == 'brown':
        select.select_by_visible_text('BROWN')
    elif hair_color == 'red':
        select.select_by_visible_text('RED')
    elif hair_color == 'gray':
        select.select_by_visible_text('GRAY')
    elif hair_color == 'bald':
        select.select_by_visible_text('BALD')
    else:
        select.select_by_visible_text('OTHER')
        
def select_eye_color(select_element, eye_color,):
    """ Select eye color from the dropdown """
    select = Select(select_element)
    eye_color = eye_color.lower()
    
    if eye_color == "amber":
        select.select_by_visible_text('AMBER')
    elif eye_color == "black":
        select.select_by_visible_text('BLACK')
    elif eye_color == "blue":
        select.select_by_visible_text('BLUE')
    elif eye_color == "brown":
        select.select_by_visible_text('BROWN')
    elif eye_color == "gray":
        select.select_by_visible_text('GRAY')
    elif eye_color == "green":
        select.select_by_visible_text('GREEN')
    else : 
        select.select_by_visible_text('HAZEL')


def select_country(select_element, country, driver):
    """ Select country from dropdown (case-sensitive matching) """
    select = Select(select_element)
    
    # Scroll the dropdown into view
    driver.execute_script("arguments[0].scrollIntoView(true);", select_element)

    try:
        # Ensure the country name is in upper case to match the options
        country_name = country.strip().upper()
        
        # Match the country with the available options
        for option in select.options:
            if option.text.strip() == country_name:
                option.click()  # Select the matching option
                return
        
        raise Exception(f"Country '{country_name}' not found in dropdown.")
    
    except Exception as e:
        print(f"Could not find the country: {country}. Error: {e}")



def select_state(select_element, state_abbreviation, driver, state_xpath):
    """Select state from dropdown with abbreviation (case-sensitive matching)"""
    state_abbreviation = state_abbreviation.strip().upper()

    # Try to select the state in a loop, handling stale element references
    for attempt in range(3):  # Retry up to 3 times
        try:
            select = Select(select_element)

            # Scroll the dropdown into view
            driver.execute_script("arguments[0].scrollIntoView(true);", select_element)
            print(f"Trying to select state: {state_abbreviation}")

            # Iterate through options in the select dropdown
            for option in select.options:
                option_value = option.get_attribute("value").strip()
                option_text = option.text.strip()

                # Print diagnostic information for debugging
                print(f"Option Value: {option_value}, Option Text: {option_text}")

                # Match either the option value or text with the abbreviation
                if state_abbreviation == option_value or option_text.startswith(state_abbreviation):
                    option.click()  # Select the matching option
                    print(f"Selected state: {state_abbreviation}")
                    return

            raise Exception(f"State abbreviation '{state_abbreviation}' not found in dropdown.")

        except StaleElementReferenceException as e:
            print(f"StaleElementReferenceException caught on attempt {attempt + 1}. Retrying...")
            # Re-find the dropdown element to refresh its reference
            state_dropdown = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, state_xpath)))
            select_element = state_dropdown
        except Exception as e:
            print(f"Could not find the state: {state_abbreviation}. Error: {e}")
            break  # Break the loop after other types of errors (non-retryable)

def select_country_and_state(country, state_abbreviation, driver, country_xpath, state_xpath):
    """Select a country, wait for the state dropdown to update, then select the state."""
    try:
        # Select the country first
        country_dropdown = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, country_xpath))
        )
        select_country = Select(country_dropdown)
        select_country.select_by_visible_text(country)
        print(f"Selected country: {country}")

        # Wait for the state dropdown to refresh
        WebDriverWait(driver, 60).until(
            EC.staleness_of(driver.find_element(By.XPATH, state_xpath))
        )
        
        # Wait for the state dropdown to be reloaded and visible
        state_dropdown = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, state_xpath))
        )
        print("State dropdown refreshed and ready.")

        # Select the state after it refreshes
        select_state(state_dropdown, state_abbreviation, driver, state_xpath)

    except TimeoutException as e:
        print(f"Timeout waiting for dropdown to update. Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
        

def select_state_without_country(driver, state_abbreviation, state_xpath):
    """Select state from dropdown using abbreviation, handling dynamic dropdowns."""
    print("######################################")
    state_abbreviation = state_abbreviation.strip().upper()

    for attempt in range(3):  # Retry up to 3 times in case of stale elements
        try:
            # Wait for the page to fully load before interacting with the dropdown
            # WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="PassportWizard_emergencyContacts_ecStateList"]')))  # Adjust to a parent container or any reliable element
            
            # Wait for the state dropdown to be present
            state_dropdown = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, state_xpath)))
            select = Select(state_dropdown)

            # Scroll the dropdown into view for visibility
            driver.execute_script("arguments[0].scrollIntoView(true);", state_dropdown)
            print(f"Attempting to select state: {state_abbreviation}")

            # Iterate through the options in the dropdown to find the correct state
            for option in select.options:
                option_value = option.get_attribute("value").strip()
                option_text = option.text.strip()

                # Debugging: Print available options for checking
                print(f"Option Value: {option_value}, Option Text: {option_text}")

                # Match based on abbreviation (case-sensitive match for option value)
                if state_abbreviation == option_value or option_text.startswith(state_abbreviation):
                    option.click()  # Click the matching option
                    print(f"Successfully selected state: {option_text}")
                    return

            raise Exception(f"State abbreviation '{state_abbreviation}' not found in dropdown.")
        
        except UnexpectedAlertPresentException:
            # Handle and dismiss the unexpected alert
            alert = Alert(driver)
            print(f"Unexpected alert present: {alert.text}")
            alert.dismiss()  # Dismiss the alert and retry

        except StaleElementReferenceException as e:
            print(f"StaleElementReferenceException caught on attempt {attempt + 1}. Retrying...")
            time.sleep(2)  # Add small delay before retrying to avoid rapid retries
        except TimeoutException as e:
            print(f"Timeout while waiting for state dropdown. Error: {e}")
            driver.save_screenshot("state_dropdown_timeout.png")  # Save a screenshot for debugging
            break  # Break the loop if the dropdown never appears
        except Exception as e:
            print(f"Error selecting state '{state_abbreviation}': {e}")
            break 