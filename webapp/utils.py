import sqlite3
from flask import g
import datetime
import time
import hmac
import hashlib
import base64


def get_db():
    """Connect to the application's configured database. 
    """
    if "db" not in g:
        g.db = sqlite3.connect('database.db')
        g.db.row_factory = sqlite3.Row

    return g.db


def verify(otp, secret_key):
    """
    Generate OTP using secret_key and compare to the given OTP.
    """
    #time = CURRENT_UNIX_TIME() / 30 as default interval is 30 second
    for_time = int(time.mktime(datetime.datetime.now().timetuple()) / 30) 

    #b32decode secret key
    missing_padding = len(secret_key) % 8
    if missing_padding != 0:
        secret_key += "=" * (8 - missing_padding)
    secret = base64.b32decode(secret_key, casefold=True)
    
    #generate HOTP https://datatracker.ietf.org/doc/html/rfc4226#section-5.4
    hasher = hmac.new(secret, for_time.to_bytes(length=8, byteorder='big'), hashlib.sha1)
    hmac_hash = bytearray(hasher.digest())
    offset = hmac_hash[-1] & 0xF
    code = (
        (hmac_hash[offset] & 0x7F) << 24
        | (hmac_hash[offset + 1] & 0xFF) << 16
        | (hmac_hash[offset + 2] & 0xFF) << 8
        | (hmac_hash[offset + 3] & 0xFF)
    )
    return otp == str(code % 10**6)
        