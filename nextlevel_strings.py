# LIBRARY IMPORTS
import os

# LOCAL IMPORTS
import nextlevel_config as nc

# Takes a Discord username as input and returns a tuple containing two strings:
#   1. The discord username (excluding the suffix "#" and 4-digit integer)
#   2. The 4-digit integer at the end of their username
def splitDiscordName(discordName):
    return(discordName[0:-5], discordName[-5:])