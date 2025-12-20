from werkzeug.security import check_password_hash

# This must be the full hashed password, including method, salt, etc.
# Not permanently stored for obvious reasons
hashed_password = ""


# Also not stored for obvious reasons
plain_password = ""

#passed last time checked Friday 19th December 2025
if check_password_hash(hashed_password, plain_password):
    print("Password matches the hash!")
else:
    print("Password does NOT match the hash.")
