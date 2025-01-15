import re

from email_validator import validate_email, EmailNotValidError
import dns.resolver



def validate_password(password: str) -> bool:
    """
    Validates a password based on the following criteria:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one number
    - Contains at least one special character
    Returns True if valid, otherwise False.
    """
    if len(password) < 8:
        return False, "Password needs to be longer than 8 characters."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password requires at least one upper case letter."
    
    if not re.search(r'\d', password):
        return False, "Password requires at least one number."
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password requires at least one special character."

    return True, "Password approved."

def validate_user_email(email: str) -> bool:
    """Validate email format and MX records."""
    try:
		####################################
        # Step 1: Validate email format
        ####################################

        validate_email(email)
        
        ####################################
        # Step 2: Check MX records
        ####################################

        domain = email.split('@')[1]
        mx_records = dns.resolver.resolve(domain, 'MX')

    except EmailNotValidError as e:
        return False, "Email is not valid."

    except Exception as e:
        return False, "Domain is invalid."

    if len(mx_records) > 0:
        return True, "Email is valid"

    return False, "Email domain is invalid."
