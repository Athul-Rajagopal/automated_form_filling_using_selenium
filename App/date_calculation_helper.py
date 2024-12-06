from datetime import datetime, timedelta

def is_within_8_years_6_days(date_str):
    try:
        # Parse the date string
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Get current date
        current_date = datetime.now()
        
        # Calculate 8 years and 6 days ago
        eight_years_six_days_ago = current_date - timedelta(days=(8 * 365 + 6))
        
        # Check if the date is after 8 years and 6 days ago
        return date > eight_years_six_days_ago
    except Exception as e:
        print(f"Error checking date range: {e}")