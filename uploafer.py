import argparse
import whatapi
import json
import os
import sys
import pickle
import logging as log
from fuzzywuzzy import fuzz
from wmapi import releaseInfo, torrentGroup, artistInfo
from settings import USERNAME, PASSWORD, ANNOUNCE, WM2_ROOT, WM2_MEDIA, WORKING_ROOT, FUZZ_RATIO

gazelle_url = 'https://passtheheadphones.me/'
resumeList =[]

# TODO: Proper error handling

def parseArgs():
    argparser = argparse.ArgumentParser(description='This is uploafer. Obviously. If you don\'t know what WM2 is, better not to know what uploafer is.')
    #argparser.add_argument('-u', '--username', help='Your PTH username', required=True)
    #argparser.add_argument('-p', '--password', help='Your PTH password', required=True)
    #argparser.add_argument('-i', '--wm2media', help='The directory containing your WM2 downloads. Each subdirectory should contain a "ReleaseInfo2.txt" file.', default='.', required=True)
    #argparser.add_argument('-w', '--wm2root', help='This directory should contain "manage.py". Leave this blank to disable auto-import. Warning: auto-import will MOVE your torrent data!')
    #argparser.add_argument('-o', '--output', help='This is the output directory for torrents and media you wish to upload. This option is overridden if wm2root is specified.')
    #argparser.add_argument('-z', '--fuzzratio', help='Minimum likeness ratio required to consider a match. Anything which scores higher than this will not be eligible for uploading. Default is 90', type=int, default=90)
    argparser.add_argument('-vv', '--debug', help='Highest level of verbosity for debugging', action="store_true")
    argparser.add_argument('-v', '--verbose', help='High level of verbosity for detailed info', action="store_true")
    argparser.add_argument('-r', '--resume', help="Resume where uploafer left off within the WM2 media directory.", action="store_true")
    args = argparser.parse_args()
    if args.debug:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Debug output.")
    elif args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
        log.info("Verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")
    return args

def query_yes_no(question, default="no"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def findRiFiles(wm2media, resume):
    global resumeList
    try:
        riList = []
        for dir in os.listdir(wm2media):
            path = os.path.join(wm2media, dir)
            if os.path.isfile(os.path.join(path, 'ReleaseInfo2.txt')):
                riList.append(path)
            else:
                log.warning('No ReleaseInfo file found for path "{0}"'.format(path))
        if resume:
            path = os.path.join(WORKING_ROOT, 'resume.wm2')
            with open(path, 'rb') as resFile:
                resumeList = pickle.load(resFile)
            riList = list(set(riList) - set(resumeList))
        return sorted(riList)
    except:
        raise

def loadReleaseInfo(path):
    try:
        riFile = open(os.path.join(path, 'ReleaseInfo2.txt'), 'r')
        riJson = json.loads(riFile.read())
        ri = releaseInfo(riJson)
        ri.group.path = path
        contents = next(os.walk(path))[1]
        if len(contents) == 1:
            ri.group.mediaDir = contents[0] #contains only the folder name. no path
        elif len(contents) < 1:
            log.error('Missing or malformed media in "{0}". Skipping..'.format(path))
            #TODO: Raise custom error here
        else:
            log.error('Multiple directories in "{0}". Skipping..'.format(path))
            #TODO: Raise custom error here
    except:
        raise
    return ri

def retrieveArtist(session, artist):
    log.debug("Artist search: {0}".format(artist))
    try:
        artist = artistInfo(session.request('artist', artistname=artist)) #What if more than one?
    except Exception:
        raise
    return artist

def findBestGroup(localGrp, artist):
    #TODO: Check catalogue numbers!
    bestGrp = localGrp #placeholder
    bestGrp.match = 0
    for group in artist.torrentgroup:
        if localGrp.catalogueNumber == group.groupCatalogueNumber:
            bestGrp = group
            bestGrp.match = 101
            break
        else:
            group.match = fuzz.ratio(localGrp.name, group.groupName)
            if group.match > bestGrp.match:
                bestGrp = group
                if bestGrp.match == 100:
                    break
    return bestGrp

def requestUpload(localGrp, remoteGrp, artist):
    print('')
    print('No match found for "{0}"!'.format(localGrp.name))
    print('Closest match ({0}% likeness): {1}'.format(remoteGrp.match, remoteGrp.groupName))
    #Next line, what if more than one artist or secondary artist identifier?
    if query_yes_no('Do you want to upload to artist "{0}" "{1}"?'.format(localGrp.musicInfo.artists[0].name, artist.url)):
        return True
    else:
        return False

def make_torrent(localGroup, remoteGroup):
    #TODO: This is mess. Make it not mess
    m_root = os.path.join(WORKING_ROOT, str(remoteGroup.id))
    m_root = os.path.join(m_root, localGroup.mediaDir)
    torrent = os.path.join(WORKING_ROOT, localGroup.mediaDir) + ".torrent"
    if os.path.exists(torrent):
        os.remove(torrent)
    if not os.path.exists(os.path.dirname(torrent)):
        os.path.makedirs(os.path.dirname(torrent))
    command = ["mktorrent", "-p", "-s", "PTH", "-a", ANNOUNCE, "-o", torrent, m_root]
    subprocess.check_output(command, stderr=subprocess.STDOUT)
    return torrent

def uploadTorrent(localGroup, remoteGroup):
    pass

def saveResume():
    path = os.path.join(WORKING_ROOT, 'resume.wm2')
    with open(path, 'wb') as resFile:
        pickle.dump(resumeList, resFile)

def main():
    #Get args
    args = parseArgs()

    #Load file list and skip completed if required
    riList = findRiFiles(WM2_MEDIA, args.resume)
    #Check for existing torrents
    for file in riList:
        log.debug('Currently processing: ' + file)

        #Load the local torrent group we are working with
        ri = loadReleaseInfo(file)
        localGrp = ri.group
        
        #Open session
        session = whatapi.WhatAPI(USERNAME, PASSWORD)
            #TODO: Store/retrieve cookie

        #Load the best remote group to compare with
        artist = retrieveArtist(session, localGrp.musicInfo.artists[0].name) #What if more than one?
        remoteGrp = findBestGroup(localGrp, artist) #Closest matching group by artist

        #Update user
        if remoteGrp.match == 101:
            log.info('Exact catalogue match found for "{0}": {1}'.format(localGrp.name, remoteGrp.url))
        elif remoteGrp.match == 100:
            log.info('Exact match found for "{0}": {1}'.format(localGrp.name, remoteGrp.url))
            #TODO: Check for possible seeding/trumping opportunity
        elif remoteGrp.match > FUZZ_RATIO:
            log.info('Probable ({0}%) match found for "{1}": {2}'.format(remoteGrp.match, localGrp.name, remoteGrp.url))
            #TODO: Add to list of potential trumping opportunities
        elif requestUpload(localGrp, remoteGrp, artist):
            pth.upload(os.path.join(localGrp.path, localGrp.mediaDir), WORKING_ROOT, )
        else:
            print('Moving on..')

        resumeList.append(file)
        saveResume()
            


if __name__ == "__main__":
    main()
