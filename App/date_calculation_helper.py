from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta

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
        raise e

def normalize_date(date: datetime) -> datetime:
    """Normalize a date to exclude the time component."""
    return datetime(date.year, date.month, date.day)

def get_current_date_in_dc() -> datetime:
    """Get the current date in America/New_York timezone."""
    # Get current UTC time
    utc_now = datetime.utcnow()
    # Convert to America/New_York timezone
    ny_tz = pytz.timezone("America/New_York")
    ny_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ny_tz)
    # Normalize to exclude time component
    return normalize_date(ny_now)

def is_recent_issue(issue_date: str) -> bool:
    """Check if the issue date is within the past two years."""
    issue_date_obj = normalize_date(datetime.strptime(issue_date, "%Y-%m-%dT%H:%M:%S.%fZ"))
    current_date = get_current_date_in_dc()
    two_years_ago = current_date.replace(year=current_date.year - 2)
    return issue_date_obj >= two_years_ago


def is_correct_details_needed(dob: str, issue_date: str) -> bool:
    try:
        print("is_correct_details_needed")
        """Determine if correct details questions should be shown."""
        dob_date = normalize_date(datetime.strptime(dob, "%Y-%m-%dT%H:%M:%S.%fZ"))
        issue_date_obj = normalize_date(datetime.strptime(issue_date, "%Y-%m-%dT%H:%M:%S.%fZ"))
        current_date = get_current_date_in_dc()

        # Calculate age at the time of issue
        age_at_issue = (
            issue_date_obj.year - dob_date.year -
            (1 if (issue_date_obj.month < dob_date.month or
                (issue_date_obj.month == dob_date.month and issue_date_obj.day < dob_date.day)) else 0)
        )

        # Determine validity duration based on age at issue
        validity_years = 5 if age_at_issue < 16 else 10
        expiration_date = issue_date_obj.replace(year=issue_date_obj.year + validity_years)

        # Logic for showing correct details question
        one_year_after_expiration = expiration_date.replace(year=expiration_date.year + 1)
        return current_date <= expiration_date or current_date <= one_year_after_expiration
    except Exception as e:
        print(f"Error checking correct details: {e}")
        raise e



def is_name_change_needed(dob: str, issue_date: str) -> bool:
    try:
        print("is_name_change_needed")
        print(f"DOB: {dob}, Issue Date: {issue_date}")

        # Parse input dates
        dob_date = normalize_date(datetime.strptime(dob, "%Y-%m-%dT%H:%M:%S.%fZ"))
        issue_date_obj = normalize_date(datetime.strptime(issue_date, "%Y-%m-%dT%H:%M:%S.%fZ"))
        current_date = get_current_date_in_dc()

        # Calculate age at the time of issue
        age_at_issue = (
            issue_date_obj.year - dob_date.year -
            (1 if (issue_date_obj.month < dob_date.month or
                   (issue_date_obj.month == dob_date.month and issue_date_obj.day < dob_date.day)) else 0)
        )
        print(f"Age at issue: {age_at_issue}")

        # Determine validity duration based on age at issue
        validity_years = 5 if age_at_issue < 16 else 10
        expiration_date = issue_date_obj + relativedelta(years=validity_years)
        print(f"Expiration Date: {expiration_date}")

        # Logic for showing name change question
        five_years_after_expiration = expiration_date + relativedelta(years=5)
        print(f"Five years after expiration: {five_years_after_expiration}")

        # Check if name change is needed
        # name_change_needed = expiration_date < current_date <= five_years_after_expiration
        if current_date >= expiration_date and current_date <= five_years_after_expiration:
            name_change_needed = True
        else:
            name_change_needed = False

        print(f"Name change needed: {name_change_needed}")
        print(f"current date {current_date}")

        return name_change_needed
    except Exception as e:
        print(f"Error checking name change: {e}")
        raise e
