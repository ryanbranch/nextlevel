# LIBRARY IMPORTS
import os

# WALLET ADDRESS SEARCH PROPERTIES
# ADDRESS_STRING_LENGTH: INTEGER length of valid address strings
ADDRESS_STRING_LENGTH = 42
# ADDRESS_STRING_PREFIX: STRING (case-insensitive) prefix which all valid address strings must contain
ADDRESS_STRING_PREFIX = "0X"
# ADDRESS_STRING_CHARS: CASE-SENSITIVE STRING containing all characters allowed within a valid address
ADDRESS_STRING_CHARS = "0123456789ABCDEFabcdef"
# ASSET_SYMBOL_STRING: For cosmetic purposes (output into the chat)
ASSET_SYMBOL_STRING = "ETH"

# ENABLE_CONSOLE_OUTPUT: A value of False will disable any print() statements within the code
ENABLE_CONSOLE_OUTPUT = True
# TOKEN_FILE_NAME: File name containing Discord Bot Token
TOKEN_FILE_NAME = "token"
# TOKEN_FILE_EXTENSION: File extension specifically for file containing Discord Bot Token
TOKEN_FILE_EXTENSION = ".txt"
# BUCKET_FILE_NAME: File name containing AWS Bucket Name
#     (only necessary for non-Heroku deployments, otherwise it can be stored in the Heroku config)
BUCKET_FILE_NAME = "bucket"
# BUCKET_FILE_EXTENSION: File extension specifically for file containing AWS Bucket Name
BUCKET_FILE_EXTENSION = ".txt"
# USER_FILE_NAME: File name to save userList (and effectively userDict) into
USER_FILE_NAME = "nextlevel-users"
# ADDRESS_FILE_NAME: File name to save allAddressDict into
ADDRESS_FILE_NAME = "nextlevel-addresses"
# FILE_EXTENSION: File extension to save to (default CSV for proper behavior)
FILE_EXTENSION = ".csv"
# FILE_TYPE: Standard "File type" string for the save content, as defined by web browser standards
FILE_TYPE = "text/csv"

# DIFFERENTIATION BETWEEN LOCAL TESTING AND HEROKU APP DEPLOYMENT
# FLAG_HEROKU: This variable will evaluate to True when running as a Heroku app, but False on my local environment
FLAG_HEROKU = not "FLAG_NOT_HEROKU" in os.environ