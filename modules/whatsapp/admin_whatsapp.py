from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def days_until_expiration():
    exp = os.getenv("TOKEN_EXPIRATION_DATE")  # format YYYY-MM-DD
    exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
    today = datetime.today().date()
    return (exp_date - today).days
