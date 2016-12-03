import argparse
import whatapi
import json
import os
import logging as log
from fuzzywuzzy import fuzz
from wmapi import ReleaseInfo

pthurl = 'https://passtheheadphones.me/'

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
    groupUrl=pthurl + 'torrents.php?id='
    artistUrl=pthurl + 'artist.php?id='
    pth = whatapi.WhatAPI(args.username, args.password)
    # make a way to continue where left off
    for file in findRiFiles(args.wm2media):
        ri = loadReleaseInfo(file)
        #debug
        log.debug("Artist search: {0}".format(ri.group.musicInfo.artists.name))
        try:
            artist = pth.request('artist', artistname=ri.group.musicInfo.artists.name)
            #what if more than one artist?
        except:
            print 'POTENTIAL UPLOAD: Failed to find artist "{0}"'.format(ri.group.musicInfo.artists.name)
            continue
        groups = pth.get_groups(artist['id'])
        best_group = {'match': 0, 'group': ''}
        for group in groups:
            name = groups[group]
            match = fuzz.ratio(ri.group.name, name)
            # Add match intelligence
            if match > best_group['match']:
                best_group['group'] = group
                best_group['match'] = match
                best_group['name'] = name
                if match == 100:
                    break
        if best_group['match'] == 100:
            log.info('Exact match found for "{0}": {1}{2}'.format(ri.group.name, groupUrl, group))
        elif best_group['match'] > args.fuzzratio:
            log.info('Possible ({0}%) match found for "{1}": {2}{3}'.format(match, ri.group.name, groupUrl, group))
        else:
            print 'POTENTIAL UPLOAD: Closest match for "{0}" ({1}) scored {2}.'.format(ri.group.name, ri.group.id, best_group['match'])
            print '   Closest match: "{0}"'.format(best_group['name'])
            print '   Artist page for "{0}": {1}{2}'.format(artist['name'], artistUrl, artist['id'])
            




if __name__ == "__main__":
    main()
