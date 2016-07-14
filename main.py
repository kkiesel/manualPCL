#!/usr/bin/env python

class settings:

    #millepde config:
    globalTag = "80X_dataRun2_Prompt_ICHEP16_Queue"
    magnetOn = True
    cosmics = False

    #data config
    datasets = "/StreamExpress/Run2016C-TkAlMinBias-Express-v2/ALCARECO", "/StreamExpress/Run2016D-TkAlMinBias-Express-v2/ALCARECO"
    minNumberEvents = 20000

    #user config
    mail = "kiesel@cern.ch" # empty if no mail wished
    pubDir = "/afs/cern.ch/user/k/kiesel/public/manualPCLforReReco"
    cmsswBase = "/cvmfs/cms.cern.ch/slc6_amd64_gcc530/cms/cmssw/CMSSW_8_0_12"

    #PCL config
    runInfoConfigName = "runInfos.cfg"

import ConfigParser
import glob
import os
import numpy
import re
import ROOT
import string
import subprocess
import sys
import time

def sendMail(adress, subject="", body=""):
    os.system("echo \"{}\" | mail -s \"[manualPCL] {}\" {}".format(body, subject, adress))

def log(s):
    print time.strftime("%Y-%m-%d %H-%m-%S: ") + s

def isStreamDone(run):
    out = subprocess.check_output(["curl", "-k", "-s", "https://cmsweb.cern.ch/t0wmadatasvc/prod/run_stream_done?run={}&stream=Express".format(run)])
    m = re.match('{"result": \[\n (.*)\]}\n', out)
    if m:
        return m.group(1) == "true"
    else:
        print "Could not get correct info for run", run
        return False

def getField(run):
    bfield = subprocess.check_output(["das_client", "--limit", "0",  "--query", "run={} | grep run.bfield".format(run)])
    return -1 if bfield == "[]\n" else float(bfield)

def getNEvents(run, dataset):
    nEvents = subprocess.check_output(["das_client", "--limit", "0", "--query", "summary run={} dataset={} | grep summary.nevents".format(run, dataset)])
    return 0 if nEvents == "[]\n" else int(nEvents)

def getRunEndTime(run):
    out = subprocess.check_output(["das_client", "--limit", "0", "--query", "run={} | grep run.end_time".format(run)])
    return 0 if out == "[]\n" else out[:-1]

def getAllRuns(dataset):
    out = subprocess.check_output(["das_client", "--limit", "0", "--query", "run dataset={} | grep run.run_number".format(dataset)])
    allRuns = [ x for x in out.split("\n") if x ]
    allRuns.sort()
    return allRuns

def getFileNames(run, dataset):
    out = subprocess.check_output(["das_client", "--limit", "0", "--query", "file run={} dataset={} | grep file.name".format(run, dataset)])
    return [f for f in out.split("\n") if f]

def checkMagneticFieldSetting(run, info):
    bfield = float(info["magneticfield"])
    if settings.magnetOn and bfield < 3.7 or not settings.magnetOn and bfield > 0.25:
        msg = "\"WARNING: Mismatch between setting of the magnetic field ({}) and the actual field in this run ({})\"".format("on" if settings.magnetOn else "off", bfield)
        log(msg)
        if settings.mail:
            sendMail(settings.mail, "WARNING: Wrong magnetic field settings in alignment", msg)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

def copyTemplate(source, destination, replacements):
    with open(source) as f:
        cfg_template = string.Template(f.read())
    with open(destination, "w") as f:
      f.write(cfg_template.safe_substitute(replacements))

def readConfig():
    runInfo = ConfigParser.ConfigParser()
    if not os.path.exists(settings.runInfoConfigName):
        open(settings.runInfoConfigName, 'w').close()
    runInfo.read(settings.runInfoConfigName)
    return runInfo

def writeConfig(cfg):
    with open(settings.runInfoConfigName, 'w') as configfile:
        cfg.write(configfile)

def updateRunInfo(datasets):
    for dataset in datasets:
        for run in getAllRuns(dataset):
            runInfo = readConfig()
            if not runInfo.has_section(run):
                runInfo.add_section(run)
            if not runInfo.has_option(run, "dataset"):
                runInfo.set(run, "dataset", dataset)
            if not runInfo.has_option(run, "nevents"):
                runInfo.set(run, "nevents", getNEvents(run, dataset))
            if not runInfo.has_option(run, "magneticfield"):
                runInfo.set(run, "magneticfield", getField(run))
            if not runInfo.has_option(run, "streamdone") or not runInfo.getboolean(run, "streamdone"):
                runInfo.set(run, "streamdone", isStreamDone(run))
            if not runInfo.has_option(run, "endtime") or not runInfo.get(run, "endtime"):
                runInfo.set(run, "endtime", getRunEndTime(run))
            writeConfig(runInfo)

def getRunToProcess():
    updateRunInfo(settings.datasets)
    runInfo = readConfig()
    foundRun = False
    for run in runInfo.sections():
        if runInfo.has_option(run, "status") and runInfo.get(run, "status") == "started":
            log("Run {} is not finished yet, exiting".format(run))
            sys.exit()
        if int(runInfo.get(run, "nevents")) > settings.minNumberEvents and runInfo.getboolean(run, "streamdone") and not runInfo.has_option(run, "status"):
            runInfo.set(run, "status", "started")
            foundRun = True
            break
    writeConfig(runInfo)
    if not foundRun:
        log("No suitable run found")
        sys.exit()
    return run, runInfo._sections[run]

def writeExecutable(name, pyCfg, additional=[]):
    with open(name, "w") as f:
        f.write( "\n".join( ["#!/bin/sh",
            "cd {} && eval `scram runtime -sh`".format(settings.cmsswBase),
            "cd {} && cmsRun {}\n".format(os.path.abspath("."), pyCfg)
            ]+additional))
    os.system("chmod +x {}".format(name))

def writeDBmetaFile(run):
    with open("TkAlignment.txt", "w") as f:
        f.write("""
{
    "destinationDatabase": "oracle://cms_orcon_prod/CMS_CONDITIONS",
    "destinationTags": {
        "TrackerAlignment_v17_offline" : {}
    },
    "inputTag": "testTag",
    "since": %s,
    "userText": "pseudo-PCL workflow"
}
"""%run)

def writeNumberToFile(name, x):
    vec = ROOT.TVectorF(1)
    vec[0] = x
    vec.Write(name)

def txtToHist(inName, inName2, outName):
    hists = [
        ROOT.TH1F("Xpos", ";;#Delta x (#mum)", 6, 0, 6),
        ROOT.TH1F("Ypos", ";;#Delta y (#mum)", 6, 0, 6),
        ROOT.TH1F("Zpos", ";;#Delta z (#mum)", 6, 0, 6),
        ROOT.TH1F("Xrot", ";;#Delta#theta_{x} (#murad)", 6, 0, 6),
        ROOT.TH1F("Yrot", ";;#Delta#theta_{y} (#murad)", 6, 0, 6),
        ROOT.TH1F("Zrot", ";;#Delta#theta_{z} (#murad)", 6, 0, 6)
    ]
    binLabels = ["FPIX(x+,z-)", "FPIX(x-,z-)", "BPIX(x+)", "BPIX(x-)", "FPIX(x+,z+)", "FPIX(x-,z+)"]
    bins = [2726, 3212, 6, 878, 1752, 2238]
    out = numpy.genfromtxt(inName, skip_header=1, skip_footer=48)
    for objId, x, x, val, err in out:
        objId = int(objId)
        hist = objId%10-1
        multiplier = 1e4 if hist in [0,1,2] else 1e6 # unit conversion to 'mu m' and 'mu rad'
        val, err = float(val)*multiplier, float(err)*multiplier
        bin = bins.index(objId/10) + 1
        hists[hist].SetBinContent(bin, val)
        hists[hist].SetBinError(bin, err)

    with open(inName2) as f:
        lines = f.readlines()
        for iline, line in enumerate(lines):
            if 'NREC =' in line:
                nrec = float(line.split("=")[1])
            m = re.match(".*Fraction of rejects =\s+([.\d])+\s*%.*", line)
            frec = m.group(1) if m else -1.
            if iline > 2 and "Sum(Chi^2)/Sum(Ndf)" in lines[iline-2]:
                chi2 = float(line.split("=")[1])

    f = ROOT.TFile(outName, "recreate")
    for h in hists:
        for ibinLabel, binLabel in enumerate(binLabels):
            h.GetXaxis().SetBinLabel(ibinLabel+1, binLabel)
        h.Write()
    writeNumberToFile("chi2overNdf", chi2)
    writeNumberToFile("numberOfRecords", nrec)
    writeNumberToFile("fractionOfReject", frec)
    f.Write()
    f.Close()

def triggerUpdate(fname):
    # x, y, z, theta_x, theta_y, theta_z
    cuts = [ 5e-5, 10e-5, 15e-5, 30e-6, 30e-6, 30e-6]
    # significance cut
    sigCut = 2.5
    # sanity cuts
    maxMoveCut = 200
    maxErrCut = 10
    update = False
    out = numpy.genfromtxt(fname, skip_header=1, skip_footer=48)
    for objInt, x, x, val, err in out:
        varInt = int(objInt%10-1)
        cut = cuts[varInt]
        val, err = abs(val), abs(err)
        if val < maxMoveCut and err < maxErrCut and val > cut and err and val/err > sigCut: update = True
    return update

def changeRunInfo(run, option, value):
    runInfo = readConfig()
    runInfo.set(run, option, value)
    writeConfig(runInfo)

def cleanUp(run):
    for f in glob.glob("Results{}/MinBias_2016_*/milleBinary_*.dat".format(run)):
        os.remove(f)
    resultDir = os.path.join(settings.pubDir, "Results{}".format(run))
    os.mkdir(resultDir)
    os.system("mv Results{0}/TkAlignment.db Results{0}/Run{0}.root {1}".format(run, resultDir))
    subprocess.call(["tar", "-zcf", "{}/archive.tar.gz".format(resultDir), "Results{}".format(run)])
    os.system("rm -r Results{0}".format(run))
    changeRunInfo(run, "status", "finished")

if __name__ == "__main__":
    log("Start new job")
    run, thisRunInfo = getRunToProcess()
    log("Run to process: {}".format(run))
    checkMagneticFieldSetting(run, thisRunInfo)

    directory = "Results" + run
    if os.path.exists(directory):
        command = "rm -rf "+directory
        os.system(command)
    os.mkdir(directory)
    os.chdir(directory)

    filenames = getFileNames(run, thisRunInfo["dataset"])
    jobids = []
    for iChunk, chunk in enumerate(chunks(filenames, 10)):
        # create files
        dirName = "MinBias_2016_{}".format(iChunk)
        os.mkdir(dirName)
        os.chdir(dirName)
        writeExecutable("executable_mille.sh", "alignment_mille_cfg.py")
        copyTemplate("../../alignment_mille_template_cfg.py", "alignment_mille_cfg.py", \
            {
              "globalTag": settings.globalTag,
              "magneticFieldOn": "True" if settings.magnetOn else "False",
              "cosmics": "True" if settings.cosmics else "False",
              "binaryFile": "milleBinary_{}.dat".format(iChunk),
              "input": "\""+"\",\"".join(chunk)+"\"",
              "run": run,
            })

        output = subprocess.check_output(["bsub -q cmsexpress -o output_{0}.txt -e error_{0}.txt -J MinBias_2016_{0} executable_mille.sh".format(iChunk)], shell=True)
        jobids.append( " ended({}) ".format(output.split("<")[1].split(">")[0]))
        os.chdir("..")

    writeExecutable("executable_pede.sh", "alignment_pede_cfg.py", ["cd .. && python cleanUp.py {} \n".format(run)])
    writeDBmetaFile(run)
    copyTemplate("../alignment_pede_template_cfg.py","alignment_pede_cfg.py", \
        {
              "globalTag": settings.globalTag,
              "magneticFieldOn": "True" if settings.magnetOn else "False",
              "cosmics": "True" if settings.cosmics else "False",
              "mergeBinaryFiles": "\"{}\"".format("\",\"".join(["MinBias_2016_{0}/milleBinary_{0}.dat".format(iChunk) for iChunk in range(len(jobids))])),
              "input": "\"{}\"".format(filenames[0]),
        })

    command = "bsub -q cmsexpress -o output_pede.txt -e error_pede.txt -J Pede_2016 -w \"" \
      + "&&".join(jobids) \
      + "\" executable_pede.sh"
    subprocess.check_output([command], shell=True)
    os.chdir("..")
    log('Job Finished')
