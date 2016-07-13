#!/usr/bin/env python
import glob
import numpy
import os
import re
import ROOT
import subprocess
import sys
from main import *

if __name__ == "__main__":
    run = sys.argv[1]
    os.chdir("Results{}".format(run))
    log("Create histogram")
    if os.path.exists("millepede.res"):
        txtToHist("millepede.res", "pede.dump", "Run{}.root".format(run))
        if triggerUpdate("millepede.res"):
            if settings.mail:
                sendMail(settings.mail, "Upload conditions", "Please upload conditions of Run {}".format(run))
            subprocess.call(["uploadConditions.py", "TkAlignment.db"])
    os.chdir("..")
    log("Clean up")
    cleanUp(run)
