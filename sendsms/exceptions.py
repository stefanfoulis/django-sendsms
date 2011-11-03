
class InvalidPhoneNumber(Exception):
    """
    The backends can use this exception to raise a standardized exception, if the
    backend returns an error code related to the phone number.
    """
    pass