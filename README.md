How to start:
```acrontab -e```
Then enter
```0 * * * * lxplus.cern.ch /afs/cern.ch/user/k/kiesel/alignment/manualPCL/cronExecutable.sh```
so the job is run every hour.

If you first start main.py, it takes a while to gather all information, but for every new run, only updates will be made (takes much less time)

The most important file is runInfos.cfg, which will be created by main.py and contains the current status

