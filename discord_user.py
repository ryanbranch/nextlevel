# LIBRARY IMPORTS

# LOCAL IMPORTS
import nextlevel_config as nc

# DISCORDUSER CLASS DEFINITION
class DiscordUser():

    def __init__(self, wr, dataIn):
        # Wrapper instance
        self.wr = wr

        # Information collected upon sign-up
        self.identifier = dataIn[0]
        self.index = dataIn[1]
        self.timestampFirst = dataIn[2]
        self.timestampLast = dataIn[3]
        self.walletAddress = dataIn[4]
        self.usernameFirst = dataIn[5]
        self.username = dataIn[6]

        # User creation success message
        if nc.ENABLE_CONSOLE_OUTPUT:
            print("User instance created successfully!")
