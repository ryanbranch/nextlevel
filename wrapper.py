# LIBRARY IMPORTS
import logging
import os
from pathlib import Path
import csv
import boto3
from botocore.exceptions import ClientError


# LOCAL IMPORTS
import nextlevel_config as nc
import nextlevel_strings as nstrings

# WRAPPER CLASS DEFINITION
class Wrapper():

    def __init__(self):

        # Make the local directories for saving (if they don't already exist)
        self.saveDirString = "/".join(nc.SAVE_DIRECTORY)
        if not os.path.exists(str(Path.cwd() / self.saveDirString)):
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("No save directory detected.")
            for i in range(len(nc.SAVE_DIRECTORY)):
                os.makedirs(Path.cwd() / ("/".join(nc.SAVE_DIRECTORY[0:i + 1])))
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("Save directory created.")

        # INSTANTIABLE MEMBER VARIABLES
        # s3: boto3 client instance
        self.s3 = boto3.client("s3")
        # token: The unique authentication token from the "Bot" section of your Discord App
        self.token = "" # The empty string is a placeholder; the true value will be loaded from a file

        # DEFAULT AND PLACEHOLDER VALUES OF MEMBER VARIABLES
        # The total number of unique wallet addresses which have been submitted through the application
        self.allAddressCount = 0
        # The total number of discord users who have submitted an address to the application
        self.userCount = 0
        # userList is a list of lists. The internal lists have the following indices
        # USERLIST COLUMN INDICES
        # 0: Discord User ID
        # 1: Storage Index
        # 2: First Timestamp
        # 3: Last Timestamp
        # 4: Wallet Address
        # 5: First Discord Username
        # 6: Current Discord Username
        self.userList = []
        # userDict is a dictionary mapping string keys (Discord User ID) to integer values (user index integer)
        self.userDict = {}
        # allAddressDict is a dictionary mapping string keys (ALL-UPPERCASE address) to integer values (user index integer)
        self.allAddressDict = {}

        # AMAZON WEB SERVICES S3 BUCKET NAME RETRIEVAL
        self.bucketName = None
        # AWS bucket name retrieval
        # Gets the name of the S3 bucket based on Heroku configuration
        self.bucketName = os.environ.get('S3_BUCKET')
        # Fixes this if running locally
        if not nc.FLAG_HEROKU:
            # CHECK FOR EXISTENCE OF BUCKET FILE
            if not os.path.exists(str(Path.cwd() / (nc.BUCKET_FILE_NAME + nc.BUCKET_FILE_EXTENSION))):
                print("ERROR: Please create a {}{} file containing your AWS Bucket Name.".format(nc.BUCKET_FILE_NAME, nc.BUCKET_FILE_EXTENSION))
                print("Program will now exit before any attempt to establish an AWS connection")
                # Exit early if not found.
                exit(1001)
            # OPEN BUCKET FILE
            with open(str(Path.cwd() / (nc.BUCKET_FILE_NAME + nc.BUCKET_FILE_EXTENSION)), newline="") as bucketFile:
                self.bucketName = bucketFile.readline()

        # DOWNLOADING CONTENT FROM AWS S3 BUCKET
        self.downloadS3()

        # Loading USER and ADDRESS content from newly-downloaded local files
        self.loadUsers()
        self.loadAddresses()

        # Wrapper creation success message
        if nc.ENABLE_CONSOLE_OUTPUT:
            print("Wrapper instance created successfully!")


    # setToken
    # Set method for the self.token value
    def setToken(self, inVal):
        self.token = inVal


    # downloadS3
    # Downloads the USER and ADDRESS files from the designated S3 bucket (regardless of public or private ACL settings)
    def downloadS3(self):
        # Build path strings
        userFilepath = str(Path.cwd() / self.saveDirString / (nc.USER_FILE_NAME + nc.FILE_EXTENSION))
        addressFilepath = str(Path.cwd() / self.saveDirString / (nc.ADDRESS_FILE_NAME + nc.FILE_EXTENSION))
        # AMAZON WEB SERVICES S3 FILE RETRIEVAL
        # Attempt to download the USER file from S3
        try:
            self.s3.download_file(self.bucketName, (self.saveDirString + "/" + (nc.USER_FILE_NAME + nc.FILE_EXTENSION)), userFilepath)
        except ClientError as e:
            logging.error(e)
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("ERROR: Failed to download USER information file from AWS S3 Bucket.\nThe bot will proceed as a fresh instance.")
                if e.response['Error']['Code'] == "404":
                    print("\tCODE 404: The object does not exist.")
        else:
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("Downloaded USER information file from AWS S3 Bucket.")
        # Attempt to download the ADDRESS file from S3
        try:
            self.s3.download_file(self.bucketName, (self.saveDirString + "/" + (nc.ADDRESS_FILE_NAME + nc.FILE_EXTENSION)), addressFilepath)
        except ClientError as e:
            logging.error(e)
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("ERROR: Failed to download ADDRESS information file from AWS S3 Bucket.\nThe bot will proceed as a fresh instance.")
                if e.response['Error']['Code'] == "404":
                    print("\tCODE 404: The object does not exist.")
        else:
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("Downloaded ADDRESS information file from AWS S3 Bucket.")


    # uploadS3
    # Uploads the USER and ADDRESS files to the designated S3 bucket (and gives them public-read permissions)
    def uploadS3(self):
        # Build path strings
        userFilepath = str(Path.cwd() / self.saveDirString / (nc.USER_FILE_NAME + nc.FILE_EXTENSION))
        addressFilepath = str(Path.cwd() / self.saveDirString / (nc.ADDRESS_FILE_NAME + nc.FILE_EXTENSION))

        # Save copies of the existing files before uploading
        self.saveUsers()
        self.saveAddresses()

        # AMAZON WEB SERVICES S3 BUCKET SAVING (UPLOADING)
        # Attempt to upload the USER file to S3
        try:
            self.s3.upload_file(userFilepath, self.bucketName, (self.saveDirString + "/" + (nc.USER_FILE_NAME + nc.FILE_EXTENSION)), ExtraArgs={'ACL':'public-read'})
        except ClientError as e:
            logging.error(e)
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("ERROR: Failed to upload USER information file to AWS S3 Bucket.")
        else:
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("Uploaded USER information file to AWS S3 Bucket.")
        # Attempt to upload the ADDRESS file to S3
        try:
            self.s3.upload_file(addressFilepath, self.bucketName, (self.saveDirString + "/" + (nc.ADDRESS_FILE_NAME + nc.FILE_EXTENSION)), ExtraArgs={'ACL':'public-read'})
        except ClientError as e:
            logging.error(e)
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("ERROR: Failed to upload ADDRESS information file to AWS S3 Bucket.")
        else:
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("Uploaded ADDRESS information file to AWS S3 Bucket.")


    # saveUsers
    # Saves, according to app_config.py, a file of USER information from local storage
    def saveUsers(self):
        # Open the USER save file for WRITING
        with open(str(Path.cwd() / self.saveDirString / (nc.USER_FILE_NAME + nc.FILE_EXTENSION)), "w", newline="") as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=",")
            # Iterate through each user in the userList
            for sublist in self.userList:
                csvWriter.writerow([str(elt) for elt in sublist])
            # Print information about the successful write operation
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("Successfully saved USER file with " + str(self.userCount) + " rows.")


    # saveAddresses
    # Saves, according to app_config.py, a file of ADDRESS information from local storage
    def saveAddresses(self):
        # Open the ADDRESS save file for WRITING
        with open(str(Path.cwd() / self.saveDirString / (nc.ADDRESS_FILE_NAME + nc.FILE_EXTENSION)), "w", newline="") as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=",")
            # Iterate through each user in the allAddressDict
            # KEY = ADDRESS (STRING), VALUE = DISCORD USER ID (INT, but cast to string before saving)
            for address in self.allAddressDict:
                csvWriter.writerow([address, str(self.allAddressDict[address])])
            # Print information about the successful write operation
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("Successfully saved ADDRESS file with " + str(self.allAddressCount) + " rows.")


    # loadUsers
    # Loads, according to app_config.py, a file of USER information from local storage
    def loadUsers(self):
         # CHECK FOR LOCAL SAVE FILE INPUT (now that the content has been downloaded)
        if os.path.exists(str(Path.cwd() / self.saveDirString / (nc.USER_FILE_NAME + nc.FILE_EXTENSION))):
            # Open the USER save file
            with open(str(Path.cwd() / self.saveDirString / (nc.USER_FILE_NAME + nc.FILE_EXTENSION)), newline="") as csvFile:
                csvReader = csv.reader(csvFile, delimiter=",")
                # Iterates through each row in the input file
                for row in csvReader:
                    # Appends a new list into the userList, casting string into integers where appropriate
                    self.userList.append([int(row[0]), int(row[1]), row[2], row[3], row[4], row[5]])
                    # Adds the corresponding element into userDict
                    self.userDict[int(row[0])] = int(row[1])
            # Set the user count
            self.userCount = len(self.userDict)
            # Print information about the successful read operation
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("Successfully read from USER file with " + str(self.userCount) + " rows.")
        # If the file does not yet exist, print a warning to the console
        else:
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("WARNING: There is no USER save file present in the local working directory!")


    # loadAddresses
    # Loads, according to app_config.py, a file of ADDRESS information from local storage
    def loadAddresses(self):
         # CHECK FOR LOCAL SAVE FILE INPUT (now that the content has been downloaded)
        if os.path.exists(str(Path.cwd() / self.saveDirString / (nc.ADDRESS_FILE_NAME + nc.FILE_EXTENSION))):
            # Open the ADDRESS save file
            with open(str(Path.cwd() / self.saveDirString / (nc.ADDRESS_FILE_NAME + nc.FILE_EXTENSION)), newline="") as csvFile:
                csvReader = csv.reader(csvFile, delimiter=",")
                # Iterates through each row in the input file
                for row in csvReader:
                    # Adds the corresponding element into allAddressDict
                    # KEY = ADDRESS (STRING), VALUE = DISCORD USER ID (INT)
                    self.allAddressDict[row[0]] = int(row[1])
            # Set the address count
            self.allAddressCount = len(self.allAddressDict)
            # Print information about the successful read operation
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("Successfully read from ADDRESS file with " + str(self.allAddressCount) + " rows.")
        # If the file does not yet exist, print a warning to the console
        else:
            if nc.ENABLE_CONSOLE_OUTPUT:
                print("WARNING: There is no ADDRESS save file present in the local working directory!")