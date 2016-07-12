#!/usr/bin/env python

import main
import sys

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

def cleanUp(run):
    for f in glob.glob("Results{}/MinBias_2016_*/milleBinary_*.dat".format(run)):
        os.remove(f)
    resultDir = os.path.join(main.settings.pubDir, "Results{}".format(run))
    os.mkdir(resultDir)
    os.system("mv Results{0}/TkAlignment.db Results{0}/Run{0}.root {1}".format(run, resultDir))
    subprocess.call(["tar", "-zcvf", "{}/archive.tar.gz".format(resultDir), "Results{}".format(run)])
    os.system("rm -r Results{0}".format(run))

if __name__ == "__main__":
    run = sys.argv[1]
    main.log("Create histogram")
    txtToHist("millepede.res", "pede.dump", "Run{}.root".format(run))
    if triggerUpdate("millepede.res"):
        if main.settings.mail:
            sendMail(settings.mail, "Upload conditions", "Please upload conditions of Run {}".format(run))
        #subprocess.call(["uploadConditions.py", "TkAlignment.db"])

    os.chdir("..")

    main.log("clean up")
    cleanUp(run)

    if settings.mail:
        sendMail(settings.mail, "New Prompt Alignment Update", "New Alignment Updated for Run {}".format(run))

    main.log('Job Finished')
