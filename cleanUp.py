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
    txtToHist("millepede.res", "pede.dump", "Run{}.root".format(run))
    if triggerUpdate("millepede.res"):
        if settings.mail:
            sendMail(settings.mail, "Upload conditions", "Please upload conditions of Run {}".format(run))
        #subprocess.call(["uploadConditions.py", "TkAlignment.db"])

    os.chdir("..")

    log("clean up")
    cleanUp(run)

    if settings.mail:
        sendMail(settings.mail, "New Prompt Alignment Update", "New Alignment Updated for Run {}".format(run))

    log('Job Finished')
