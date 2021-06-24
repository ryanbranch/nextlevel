# LIBRARY IMPORTS
import time
import os
from pathlib import Path
import re
import discord
from discord.ext.commands import Bot
from discord import Intents

# LOCAL IMPORTS
import nextlevel_config as nc
import wrapper


# GLOBAL VARIABLES
# Global Wrapper instance
WRAPPER = wrapper.Wrapper()
# intents and bot (used by discord.py)
intents = Intents.all()
bot = Bot(intents=intents, command_prefix="!")


# Executes upon first initialization of bot
@bot.event
async def on_ready():
    # Define the scope of GLOBAL VARIABLES
    global WRAPPER
    if nc.ENABLE_CONSOLE_OUTPUT:
        print("Bot connected as {}".format(bot.user))

# Executes whenever a new message appears on a server in which the bot has membership
@bot.event
async def on_message(message):
    # Define the scope of GLOBAL VARIABLES
    global WRAPPER

    # DEFAULT alert message (sent by bot into channel)
    alertMessage = "Thanks {}! Your ETH address has been detected and stored!".format(message.author.mention)
    # failedRegistration: Default False, but will be set to True if anything about the user registration process fails
    failedRegistration = False

    # Check if the mesage is the proper length
    if (len(message.content) == nc.ADDRESS_STRING_LENGTH):
        # If the message FAILS the full set of address checks
        if not checkAddressValidity(message.content):
            # Warn the user if their message was not a valid address despite the correct length
            await message.channel.send("Hey {}, you posted a {}-character message beginning with \"{}\", but it is not a valid {} address.\nDid you mean to share your {} address? If so, please try again!".format(message.author.mention, nc.ADDRESS_STRING_LENGTH, nc.ADDRESS_STRING_PREFIX, nc.ASSET_SYMBOL_STRING, nc.ASSET_SYMBOL_STRING))
        # If the message PASSES all address checks
        else:
            # Optional print statement for output readability
            if nc.ENABLE_CONSOLE_OUTPUT:
                print()

            # Stores an all-uppercase version of the user's submitted address
            compAddress = message.content.upper()
            # Placeholder for overwriting userList contents
            overwriteIndex = -1
            # Placeholder for previous LastTimestamp, if overwritten
            prevLastTimestamp = ""
            # Placeholder for previous WalletAddress, if overwritten
            prevWalletAddress = ""

            # Get the current timestamp
            currentTimestamp = str(time.time())

            # If the Discord User ID already exists within the userDict
            if message.author.id in WRAPPER.userDict:
                # Set the overwriteIndex equal to the user's index within userList
                overwriteIndex = WRAPPER.userDict[message.author.id]
                # Set the values of the prev variables
                prevLastTimestamp = WRAPPER.userList[overwriteIndex][3]
                prevWalletAddress = WRAPPER.userList[overwriteIndex][4]
                # Update the LastTimestamp (index 3) and WalletAddress (index 4) values within the relevant row of userList
                WRAPPER.userList[overwriteIndex][3] = currentTimestamp
                WRAPPER.userList[overwriteIndex][4] = compAddress
                # Alert the user that they've successfully updated their wallet address
                alertMessage = "Hello {}! You have successfully updated your wallet address!".format(message.author.mention)
            # If the Discord User has never submitted their address before
            else:
                # Add the user's Discord User ID to the userDict
                WRAPPER.userDict[message.author.id] = WRAPPER.userCount
                # A 1-D list (of mixed types) which holds the elements to be inserted into userList
                # NOTE: Be aware that this list stores the ALL-UPPERCASE version of the user's wallet address
                userInfo = [message.author.id, WRAPPER.userCount, currentTimestamp, currentTimestamp, compAddress, str(message.author)]
                # Append this new "user row" to the userList list
                WRAPPER.userList.append(userInfo)

                # Increment userCount
                WRAPPER.userCount += 1
                # Alert the user that they've been successfully added to the system for the first time
                alertMessage = "Welcome {}! You have successfully registered your wallet address for the first time!".format(message.author.mention)

            # If the submitted wallet address does not exist within the allAddressDict, it has not previously been submitted
            if compAddress not in WRAPPER.allAddressDict:
                # Add the user's address to allAddressDict, paired with the Storage Index for this user
                WRAPPER.allAddressDict[compAddress] = WRAPPER.userDict[message.author.id]

                # Increment allAddressCount
                WRAPPER.allAddressCount += 1
            # Otherwise, this is a special case handled dependent on whether the wallet address already belongs to the current user
            else:
                # If the user is resubmitting their own existing wallet address
                if compAddress == prevWalletAddress:
                    # Alert the user of successful detection and storage of their ETH address
                    alertMessage = "Hello {}! You are already registered under that address, there's no need to resubmit!".format(message.author.mention)
                # If the user is resubmitting an address which is not currently theirs, but which they PREVIOUSLY submitted
                elif WRAPPER.allAddressDict[compAddress] == WRAPPER.userDict[message.author.id]:
                    # Alert the user of successful reversion back to a previously-used address
                    alertMessage = "Hello {}! You have successfully updated your wallet address (back to a value which you previously used)!".format(message.author.mention)
                # If another user is trying to submit an already-claimed wallet address
                else:
                    # Reset the changed values within userList
                    # If the user was attempting to overwrite their own existing value, just revert the change
                    if overwriteIndex != -1:
                        WRAPPER.userList[WRAPPER.userDict[message.author.id]][3] = prevLastTimestamp
                        WRAPPER.userList[WRAPPER.userDict[message.author.id]][4] = prevWalletAddress
                        # Set failedRegistration to True
                        failedRegistration = True
                        # Print information (to the console) about the failed registration
                        if nc.ENABLE_CONSOLE_OUTPUT:
                            print("EXISTING USER FAILED TO UPDATE ADDRESS DUE TO UNAVAILABILITY OF WALLET ADDRESS.\nUSER INFORMATION REMAINS AS PREVIOUS, SHOWN BELOW:")
                            print(WRAPPER.userList[WRAPPER.userDict[message.author.id]])
                        # Alert the user of successful detection and storage of their ETH address
                        alertMessage = "Hello {}! You tried to change your address to an address which has already been claimed!\nThis is prohibited, so your address will instead remain its previous value of {}.".format(message.author.mention, prevWalletAddress)
                    # Otherwise, the user was trying to newly join with an already-used address
                    else:
                        # As a result, we remove this user's entire record
                        WRAPPER.userList.pop()
                        # Decrement the userCount
                        WRAPPER.userCount -= 1
                        # Remove the user from userDict
                        WRAPPER.userDict.pop(message.author.id, None)
                        # Set failedRegistration to True
                        failedRegistration = True
                        # Print information (to the console) about the failed registration
                        if nc.ENABLE_CONSOLE_OUTPUT:
                            print("NEW USER FAILED TO REGISTER DUE TO UNAVAILABILITY OF WALLET ADDRESS.")
                        # Alert the user of successful detection and storage of their ETH address
                        alertMessage = "Hello {}! You tried to register with an address which has already been claimed!\nThis is prohibited, so you haven't yet been added to the system. Please submit a unique address of your own!".format(message.author.mention)
            # If registration DID NOT FAIL
            if not failedRegistration:
                # Print information (to the console) about the new data
                if nc.ENABLE_CONSOLE_OUTPUT:
                    print("NEW WALLET ADDRESS RECEIVED AND ASSIGNED TO THE FOLLOWING ROW:")
                    print(WRAPPER.userList[WRAPPER.userDict[message.author.id]])

                # Save the USER and ADDRESS files locally
                WRAPPER.saveUsers()
                WRAPPER.saveAddresses()
                # AMAZON WEB SERVICES S3 BUCKET SAVING (UPLOADING)
                WRAPPER.uploadS3()

            # Alert the user of successful detection and storage of their ETH address
            await message.channel.send(alertMessage)
            await bot.process_commands(message)


def checkAddressValidity(stringIn):
    # Gets the length of the prefix and remainder
    prefixLength = len(nc.ADDRESS_STRING_PREFIX)
    remainderLength = nc.ADDRESS_STRING_LENGTH - prefixLength

    # CHECK 1: STRING LENGTH
    if not (len(stringIn) == nc.ADDRESS_STRING_LENGTH):
        return False
    # CHECK 2: PREFIX MATCHING
    if not (stringIn[0:prefixLength].upper() == nc.ADDRESS_STRING_PREFIX.upper()):
        return False
    # CHECK 3: REGULAR EXPRESSION ON REMAINDER OF STRING
    reString = "([" + nc.ADDRESS_STRING_CHARS + "]{" + str(remainderLength) + "})"
    reResult = re.search(reString, stringIn[prefixLength:])
    # This statement is entered if re.search() returned None (did not find a match)
    if not reResult:
        return False

    # Returns True now that all checks have passed
    return True


def loadBotToken():
    # DISCORD BOT AUTHENTICATION TOKEN LOADING
    # If the token file does not exist
    if not os.path.exists(str(Path.cwd() / (nc.TOKEN_FILE_NAME + nc.TOKEN_FILE_EXTENSION))):
        print("ERROR: Please create a {}{} file containing your Discord Bot Authentication Token.".format(nc.TOKEN_FILE_NAME, nc.TOKEN_FILE_EXTENSION))
        print("Program will now exit before any attempt to establish a bot connection")
        # Exit early if not found.
        exit(1000)
    # Otherwise, proceed with opening the token file
    outVal = ""
    with open(str(Path.cwd() / (nc.TOKEN_FILE_NAME + nc.TOKEN_FILE_EXTENSION)), newline="") as tokenFile:
        outVal = tokenFile.readline()
    return outVal


def main():
    # Use the GLOBAL value of WRAPPER
    global WRAPPER
    # Load the value of the authentication token
    WRAPPER.setToken(loadBotToken())

    bot.run(WRAPPER.token)


main()