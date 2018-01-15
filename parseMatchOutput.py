import os

localDir = os.getcwd()
logDir = os.path.join(localDir,'logs')
inputPath = os.path.join(logDir,'rawOutput.txt')

if not os.path.isfile(inputPath):
    print("ERROR! logs/rawOutput.txt does not exist!")
    exit()

redEarthLog = []
redMarsLog = []
blueEarthLog = []
blueMarsLog = []

startLogging = [False,False,False,False]

with open(inputPath,'r') as fin:
    for line in fin.readlines():
        if '[earth:red]' in line:
            if startLogging[0]:
                redEarthLog.append(line.replace('[earth:red]','').strip())
            elif '$START_LOGGING' in line:
                startLogging[0] = True
        elif '[mars:red]' in line:
            if startLogging[1]:
                redMarsLog.append(line.replace('[mars:red]','').strip())
            elif '$START_LOGGING' in line:
                startLogging[1] = True
        elif '[earth:blue]' in line:
            if startLogging[2]:
                blueEarthLog.append(line.replace('[earth:blue]','').strip())
            elif '$START_LOGGING' in line:
                startLogging[2] = True
        elif '[mars:blue]' in line:
            if startLogging[3]:
                blueMarsLog.append(line.replace('[mars:blue]','').strip())
            elif '$START_LOGGING' in line:
                startLogging[3] = True
    
redEarthLog = list(filter(None, redEarthLog))
redMarsLog  = list(filter(None, redMarsLog))
blueEarthLog = list(filter(None, blueEarthLog))
blueMarsLog  = list(filter(None, blueMarsLog))
#here we can either analyze data, or output to indexed log files for another script to analyze in batches

#get the next log number
logIndex = 1
filenameTemplate = 'matchLog_{:03d}.txt'
logName = '{:03d}_redEarth.csv'.format(logIndex)
logPath = os.path.join(logDir,logName)
while(os.path.isfile(logPath)):
    logIndex += 1
    logName = '{:03d}_redEarth.csv'.format(logIndex)
    logPath = os.path.join(logDir,logName)
print('generating CSVs at index: {:03d}'.format(logIndex))
with open(logPath,'a+') as fout:
    for l in redEarthLog:
        fout.write(l + '\n')

logName = '{:03d}_redMars.csv'.format(logIndex)
logPath = os.path.join(logDir,logName)
with open(logPath,'a+') as fout:
    for l in redMarsLog:
        fout.write(l + '\n')

logName = '{:03d}_blueEarth.csv'.format(logIndex)
logPath = os.path.join(logDir,logName)
with open(logPath,'a+') as fout:
    for l in blueEarthLog:
        fout.write(l + '\n')

logName = '{:03d}_blueMars.csv'.format(logIndex)
logPath = os.path.join(logDir,logName)
with open(logPath,'a+') as fout:
    for l in blueMarsLog:
        fout.write(l + '\n')

