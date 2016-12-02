import argparse
import whatapi
import json
import os
import logging as log
from fuzzywuzzy import fuzz
from wmapi import ReleaseInfo

# TODO: Proper error handling

def parseArgs():
    argparser = argparse.ArgumentParser(description='This is uploafer. Obviously. If you don\'t know what WM2 is, better not to know what uploafer is.')
    argparser.add_argument('-u', '--username', help='Your PTH username', required=True)
    argparser.add_argument('-p', '--password', help='Your PTH password', required=True)
    argparser.add_argument('-i', '--wm2media', help='The directory containing your WM2 downloads. Each subdirectory should contain a "ReleaseInfo2.txt" file.', default='.', required=True)
    argparser.add_argument('-w', '--wm2root', help='This directory should contain "manage.py". Leave this blank to disable auto-import. Warning: auto-import will MOVE your torrent data!')
    argparser.add_argument('-r', '--fuzzratio', help='Minimum likeness ratio required to consider a match. Lower this to increase matching paranoia. Default is 90', type=int, default=90)
    argparser.add_argument('-vv', '--debug', help='Highest level of verbosity for debugging', action="store_true")
    argparser.add_argument('-v', '--verbose', help='High level of verbosity for detailed info', action="store_true")
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

def loadReleaseInfo(path):
    riFile = open(path, 'r')
    riJson = json.loads(riFile.read())
    ri = ReleaseInfo(riJson)
    return ri

def findRiFiles(wm2root):
    if os.path.isdir(wm2root):
        riList = []
        for dir in os.listdir(wm2root):
            path = os.path.join(wm2root, dir)
            if os.path.isdir(path):
                path += '/ReleaseInfo2.txt'
                if os.path.isfile(path):
                    riList.append(path)
                else:
                    log.warning('"{0}" does not exist!'.format(path))
            else:
                log.error('"{0}" is not a directory.'.format(path))
        return riList
    else:
        log.error('wm2root "{0}" does not exist! Quitting..'.format(wm2root))
        quit()

def main():
    args = parseArgs()
    pth = whatapi.WhatAPI(args.username, args.password)
    pthurl = 'https://passtheheadphones.me/torrents.php?id='
    for file in findRiFiles(args.wm2media):
        ri = loadReleaseInfo(file)
        artist = pth.request('artist', artistname=ri.group.musicInfo.artists.name)
        groups = pth.get_groups(artist['id'])
        state = 'No match found for "{0}"'.format(ri.group.name)
        for group in groups:
            match = fuzz.ratio(ri.group.name, groups[group])
            if match == 100:
                log.info('Exact match found for "{0}": {1}{2}'.format(ri.group.name, pthurl, group))
                break
            elif match > args.fuzzratio:
                log.info('Possible ({0}%) match found for "{1}": {2}{3}'.format(match, ri.group.name, pthurl, group))
                break





if __name__ == "__main__":
    main()
