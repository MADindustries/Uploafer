import argparse
import whatapi
import json
import os
import sys
import pickle
import logging as log
from fuzzywuzzy import fuzz
from wmapi import ReleaseInfo
from settings import USERNAME, PASSWORD, ANNOUNCE, WM2_ROOT, WM2_MEDIA, WORKING_ROOT, FUZZ_RATIO

pthurl = 'https://passtheheadphones.me/'

# TODO: Proper error handling

class group(object):
    def __init__(self, id=None, name=None, path=None):
        self.id = id
        self.name = name
        self.path = path
        self.match = 00
        self.groupUrl = ''
        self.artistUrl = ''
        self.artistName = ''
        self.mediaPath = ''

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

def findRiFiles(wm2media):
    try:
        riList = []
        for dir in os.listdir(wm2media):
            path = os.path.join(wm2media, dir) + '/ReleaseInfo2.txt'
            if os.path.isfile(path):
                riList.append(path)
            else:
                log.warning('No ReleaseInfo file found for path "{0}"'.format(path))
        return sorted(riList)
    except:
        raise

def resumeRiFiles(riList):
    path = './resume.wm2'
    try:
        with open(path, 'wb') as resFile:
            pickle.dump(resumeList, resFile)
        riList = set(riList) - set(resumeList)
        return sorted(list(riList))
    except:
        raise

def loadReleaseInfo(path):
    try:
        riFile = open(path, 'r')
        riJson = json.loads(riFile.read())
        ri = ReleaseInfo(riJson)
    except:
        raise
    return ri

def retrieveArtistId(pth, artist):
    log.debug("Artist search: {0}".format(artist))
    try:
        artistId = pth.request('artist', artistname=artist) #What if more than one?
    except Exception:
        raise
    return artistId['id']

def findBestGroup(localGrp, artistGroups):
    #TODO: Check catalogue numbers!
    bestGrp = group() #placeholder
    for grp in artistGroups:
        remoteGrp = group(grp, artistGroups[grp])
        remoteGrp.match = fuzz.ratio(localGrp.name, remoteGrp.name)
        if remoteGrp.match > bestGrp.match:
            bestGrp = remoteGrp
            if bestGrp.match == 100:
                break
    bestGrp.groupUrl = pthurl + 'torrents.php?id=' + str(bestGrp.id)
    return bestGrp

def requestUpload(localGroup, remoteGroup):
    print('')
    print('No match found for "{0}"!'.format(localGroup.name))
    print('Closest match ({0}% likeness): {1}'.format(remoteGroup.match, remoteGroup.name))
    #Next line, what if more than one artist or secondary artist identifier?
    if query_yes_no('Do you want to upload to artist "{0}" "{1}"?'.format(localGroup.musicInfo.artists[0].name, remoteGroup.artistUrl)):
        make_torrent(localGroup, remoteGroup)
        print('Uploading..')
    else:
        print('Moving on..')

def make_torrent(localGroup, remoteGroup):
    #TODO: This is mess. Make it not mess
    m_root = os.path.join(WORKING_ROOT, str(remoteGroup.id))
    m_root = os.path.join(m_root, localGroup.mediaPath)
    torrent = os.path.join(WORKING_ROOT, str(remoteGroup.id)) + ".torrent"
    if os.path.exists(torrent):
        os.remove(torrent)
    if not os.path.exists(os.path.dirname(torrent)):
        os.path.makedirs(os.path.dirname(torrent))
    command = ["mktorrent", "-p", "-s", "PTH", "-a", ANNOUNCE, "-o", torrent, m_root]
    quit()
    return torrent

def uploadTorrent(localGroup, remoteGroup):
    pass


def main():
    #Get args
    args = parseArgs()
    #Open PTH session
    pth = whatapi.WhatAPI(USERNAME, PASSWORD)
    groupUrl = pthurl + 'torrents.php?id='
    #Load file list and skip completed if required
    riList = findRiFiles(WM2_MEDIA)
    if args.resume:
        riList = resumeRiFiles(riList)
    #Check for existing torrents
    for file in riList:
        log.debug('Currently processing: ' + file)
        ri = loadReleaseInfo(file)
        artistId = retrieveArtistId(pth, ri.group.musicInfo.artists[0].name) #What if more than one?
        artistGroups = pth.get_groups(artistId)
        localGrp = ri.group #Group stored on disk
        localGrp.path = os.path.join(WM2_MEDIA,str(ri.torrent.id))
        #Get media directory
        media = next(os.walk(localGrp.path))[1]
        if len(media) == 1:
            localGrp.mediaPath = media[0]
        else:
            log.error('Multiple directories in "{0}". Halting..'.format(localGrp.path)) #FIX THIS SHIT, ITS DUMB
        #TODO: Make proper class for PTH group info
        remoteGrp = findBestGroup(localGrp, artistGroups) #Closest matching group by artist
        remoteGrp.artistUrl = pthurl + 'artist.php?id=' + str(artistId)
        if remoteGrp.match == 100:
            log.info('Exact match found for "{0}": {1}'.format(localGrp.name, remoteGrp.groupUrl))
            #TODO: Check for possible seeding/trumping opportunity
        elif remoteGrp.match > FUZZ_RATIO:
            log.info('Probable ({0}%) match found for "{1}": {2}'.format(remoteGrp.match, localGrp.name, remoteGrp.groupUrl))
            #TODO: Add to list of potential trumping opportunities
        else:
            requestUpload(localGrp, remoteGrp)


if __name__ == "__main__":
    main()
