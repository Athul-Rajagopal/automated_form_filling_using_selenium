from selenium.webdriver.support.ui import Select

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
    """ Select country from dropdown """
    select = Select(select_element)
    country_name = country.upper()
    
    # Scroll the dropdown into view
    driver.execute_script("arguments[0].scrollIntoView(true);", select_element)
    
    try:
        # Select the country by visible text
        select.select_by_visible_text(country_name)
    except Exception as e:
        print(f"Could not find the country: {country_name}. Error: {e}")

def select_state(select_element, state_abbreviation, driver):
    """ Select state from dropdown with abbreviation """
    select = Select(select_element)
    
    driver.execute_script("arguments[0].scrollIntoView(true);", select_element)
    
    state_abbreviation = state_abbreviation.upper()
    
    try:
        # Loop through all options and select the one that starts with the abbreviation
        for option in select.options:
            if option.text.startswith(state_abbreviation):
                option.click()  # Select the option that matches the abbreviation
                return
        
        raise Exception(f"State abbreviation {state_abbreviation} not found in dropdown.")
    
    except Exception as e:
        print(f"Could not find the state: {state_abbreviation}. Error: {e}")