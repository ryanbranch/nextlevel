# LIBRARY IMPORTS
import logging
import time
from pathlib import Path
import csv
import os
from botocore.exceptions import ClientError
from flask import Flask, render_template

# LOCAL IMPORTS
import nextlevel_config as nc
import wrapper


# GLOBAL VARIABLES
# Global Wrapper instance
WRAPPER = wrapper.Wrapper()
# Global Flask app instance
app = Flask(__name__)


@app.route('/')
def hello_world():
    # Defining scope of global variables
    global WRAPPER

    outList = [WRAPPER.userList, WRAPPER.bucketName, (nc.USER_FILE_NAME + nc.FILE_EXTENSION), (nc.ADDRESS_FILE_NAME + nc.FILE_EXTENSION)]

    return render_template("index.html", data=outList)


def main():
    # Use the GLOBAL value of WRAPPER
    global WRAPPER

    if __name__ == '__main__':
        # Bind to PORT if defined, otherwise default to 5000.
        app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


main()