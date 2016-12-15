#!/usr/bin/env python3

import argparse
import json
import logging as log
import os
import pickle
import shutil
import subprocess
import sys

from fuzzywuzzy import fuzz
from html2bbcode.parser import HTML2BBCode
from settings import (ANNOUNCE, FUZZ_RATIO, PASSWORD, USERNAME, WM2_MEDIA,
                      WM2_ROOT, WORKING_ROOT)
from whatapi import WhatAPI, ext_matcher, locate
from wmapi import artistInfo, releaseInfo, torrentGroup

html_to_bbcode = HTML2BBCode()

VERSION = "0.3b"
gazelle_url = 'https://passtheheadphones.me/'
resumeList = set([])
potential_uploads = 0
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3)'\
        'AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.79'\
        'Safari/535.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9'\
        ',*/*;q=0.8',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'}

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
    argparser.add_argument('-a', '--auto', help='Don\'t use this.', action="store_true")
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
            if os.path.isdir(path):
                if os.path.isfile(os.path.join(path, 'ReleaseInfo2.txt')):
                    riList.append(path)
                else:
                    log.warning('No ReleaseInfo file found for path "{0}"'.format(path))
            else:
                log.warning('"{0}" is not a directory.'.format(path))
        path = os.path.join(WORKING_ROOT, 'resume.wm2')
        if os.path.isfile(path):
            with open(path, 'rb') as resFile:
                resumeList = set(pickle.load(resFile))
                if resume:
                    riList = list(set(riList) - resumeList)
        else:
            log.warning('Cannot access "{0}"'.format(path))
        return sorted(riList)
    except:
        raise

def loadReleaseInfo(path):
    try:
        riFile = open(os.path.join(path, 'ReleaseInfo2.txt'), 'r')
        riJson = json.loads(riFile.read())
        ri = releaseInfo(riJson)
        ri.group.path = path
    except:
        raise
    return ri

def loadData(ri):
    #TODO: Below may not be necessary. See ri.torrent.filePath for a possible replacement
    try:
        contents = next(os.walk(ri.group.path))[1]
        if len(contents) == 1:
            if ri.torrent.filePath != contents[0]:
                log.warn('Original path "{0}" does not match directory "{1}"'.format(ri.torrent.filePath, contents[0]))
                ri.torrent.filePath = contents[0]
            ri.torrent.fullPath = os.path.join(ri.group.path, ri.torrent.filePath)
            ri.torrent.logFiles = locate(ri.group.path, ext_matcher('.log'))
            ri.torrent.logFiles = [(str(i) + '.log', open(logfile, 'rb'), "application/octet-stream") for i, logfile in enumerate(ri.torrent.logFiles)]
        elif len(contents) < 1:
            log.error('Missing or malformed media directory in "{0}". Skipping..'.format(ri.group.path))
            #TODO: Raise custom error here
        else:
            log.error('Multiple directories in "{0}". Skipping..'.format(ri.group.path))
            #TODO: Raise custom error here
    except:
        raise

def killDSStore(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.DS_Store'):
                path = os.path.join(root, file)
                if os.remove(path):
                    log.warn("Unable to delete .DS_Store files")

def retrieveArtist(session, artist):
    log.debug("Artist search: {0}".format(artist))
    try:
        artist = artistInfo(session.request('artist', artistname=artist)) #What if more than one?
    except Exception:
        raise
    return artist

def findBestGroup(ri, artist):
    #TODO: Check catalogue numbers!
    bestGrp = ri.group #placeholder
    bestGrp.match = -1
    for group in artist.torrentgroup:
        if (ri.group.catalogueNumber != '') and (ri.group.catalogueNumber == group.groupCatalogueNumber):
            bestGrp = group
            bestGrp.match = 101
            break
        else:
            group.match = fuzz.ratio(ri.group.name, group.groupName)
            if group.match > bestGrp.match:
                bestGrp = group
                if bestGrp.match == 100:
                    break
    return bestGrp

def requestUpload(ri, remoteGrp=None, artist=None, auto=False):
    global potential_uploads
    potential_uploads += 1
    if auto:
        log.info("Auto mode disables upload.")
        return False
    print('')
    if remoteGrp == None or artist == None:
        print('{4} - No artist match found for "{0}" [{1}/{2}]:  {3}'.format(ri.group.name, ri.torrent.media, ri.torrent.encoding, ri.group.path, str(potential_uploads)))
        if query_yes_no('Do you want to upload and create new artist page "{0}"?'.format(ri.group.musicInfo.artists[0].name)):
            return True
        else:
            return False
    else:
        print('{4} - No match found for "{0}" [{1}/{2}]:  {3}'.format(ri.group.name, ri.torrent.media, ri.torrent.encoding, ri.group.path, str(potential_uploads)))
        print('Closest match ({0}% likeness): {1}'.format(remoteGrp.match, remoteGrp.groupName))
        #Next line, what if more than one artist or secondary artist identifier?
        if query_yes_no('Do you want to upload to artist "{0}" [{1}]?'.format(ri.group.musicInfo.artists[0].name, artist.url)):
            return True
        else:
            return False

def uploadTorrent(ri, session):
    try:
        dataPath = os.path.join(WORKING_ROOT, ri.torrent.filePath)
        if os.path.exists(dataPath):
            shutil.rmtree(dataPath)
        dataPath = shutil.copytree(ri.torrent.fullPath, dataPath)
        torrent, torrentPath = make_torrent(dataPath)
        auth = session.request("index")['authkey']
        data, files = buildUpload(ri, torrent, auth)
        url = os.path.join(gazelle_url, 'upload.php')
        upload_headers = dict(headers)
        upload_headers["referer"] = url
        upload_headers["origin"] = url.rsplit("/", 1)[0]
        r = session.session.post(url, data=data, files=files, headers=upload_headers)
        if "torrent_comments" not in r.text:
            log.error('Upload failed!')
            return None
        else:
            log.info('Upload successful.')
            #TODO: Run import script here!!
            return torrentPath
    except:
        raise

def make_torrent(dataPath):
    killDSStore(dataPath) #Because Macs
    torrentPath = dataPath + ".torrent"
    if os.path.exists(torrentPath):
        os.remove(torrentPath)
    command = ["mktorrent", "-p", "-s", "PTH", "-a", ANNOUNCE, "-o", torrentPath, dataPath]
    subprocess.check_output(command, stderr=subprocess.STDOUT)
    torrent = ('torrent.torrent', open(torrentPath, 'rb'), "application/octet-stream")
    return torrent, torrentPath

def buildUpload(ri, torrent, auth):
    data = [
        ("submit", "true"),  # the submit button
        ("auth", auth),
        ("type", "0"),  # music
        ("title", ri.group.name), # album name
        ("year", ri.group.year), # album year
        ("record_label", ri.group.recordLabel),
        ("catalogue_number", ri.group.catalogueNumber),
        ("releasetype", ri.group.releaseType), #this may need to be shifted for zero based index
        ("remaster", ri.torrent.remastered),
        ("remaster_year", ri.torrent.remasterYear),
        ("remaster_title", ri.torrent.remasterTitle),
        ("remaster_record_label", ri.torrent.remasterRecordLabel),
        ("remaster_catalogue_number", ri.torrent.remasterCatalogueNumber),
        ("scene", ri.torrent.scene),
        ("format", ri.torrent.format),
        ("bitrate", ri.torrent.encoding),
        ("other_bitrate", ""),  # n/a
        ("media", ri.torrent.media),  # Media source
        ("genre_tags", ri.group.tags[0]),  # blank - this is the dropdown of official tags
        ("tags", ", ".join(ri.group.tags)),  # classical, hip.hop, etc. (comma separated)
        ("image", ri.group.wikiImage),  #TODO: What if this is a whatimg link??
        ("album_desc", html_to_bbcode.feed(ri.group.wikiBody).replace('\n\n', '\n')),
        ("release_desc", "Uploafed using version {0} from WCDID: {1}. ReleaseInfo available.".format(VERSION, ri.group.id))
    ]
    data.extend(ri.group.musicInfo.uploaddata)
    files = []
    for logfile in ri.torrent.logFiles:
        files.append(("logfiles[]", logfile))
    files.append(("file_input", torrent))
    return data, files

def importTorrent(torrentPath):
    try:
        if torrentPath is not None:
            log.info('Importing torrent into WM..')
            importExternal = os.path.join(WM2_ROOT, 'manage.py')
            command = [importExternal, 'import_external_what_torrent.py', '--base-dir', WORKING_ROOT, torrentPath]
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
            print(output)
            # Cleanup
            #os.remove(torrentPath)
            #shutil.rmtree(dataPath)
        else:
            raise
    except:
        log.error('Error importing torrent into WM')
        raise

def saveResume():
    #TODO: 
    path = os.path.join(WORKING_ROOT, 'resume.wm2')
    with open(path, 'wb') as resFile:
        pickle.dump(resumeList, resFile)

def main():
    #Get args
    args = parseArgs()

    #Load file list and skip completed if required
    riList = findRiFiles(WM2_MEDIA, args.resume)
    #Check for existing torrents
    current = 0
    for file in riList:
        current += 1
        log.debug('Currently processing [{1}/{2}]: {0}'.format(file, current, len(riList)))
        sys.stdout.write('Progress: {0}/{1} \r'.format(current, len(riList))) #TODO: Track progress count better = faster
        sys.stdout.flush()

        #Load the local torrent group we are working with and filter exceptions
        ri = loadReleaseInfo(file)
        if ri.group.categoryId != 1:
            log.info('Group "{0}" is not a music group. Skipping..'.format(ri.group.name))
            continue
        if ri.torrent.format != 'FLAC':
            log.info('Group "{0}" is not in FLAC format. Skipping..'.format(ri.group.name))
            continue
        if ri.torrent.size > (5 * (1024 ** 3)): #Larger than 5GB
            log.info('Group "{0}" is larger than 5GB in size. Skipping..'.format(ri.group.name))
            continue
        if ri.group.wikiBody == "":
            log.info('Group "{0}" does not have an album description. Skipping..'.format(ri.group.name))
            continue
        
        #Open session
        session = WhatAPI(USERNAME, PASSWORD)
            #TODO: Store/retrieve cookie

        #Load the best remote group to compare with
        try:
            if len(ri.group.musicInfo.artists) > 0:
                artist = retrieveArtist(session, ri.group.musicInfo.artists[0].name) #What if more than one?
            elif len(ri.group.musicInfo.composers) > 0:
                artist = retrieveArtist(session, ri.group.musicInfo.composers[0].name)
            else:
                log.error('Neither Artist nor Composer provided for ID "{0}". Skipping..'.format(ri.group.categoryId))
                continue
        except:
            log.info('Artist not found: {0}'.format(ri.group.musicInfo.artists[0].name))
            if requestUpload(ri, auto=args.auto):
                loadData(ri)
                dataPath = uploadTorrent(ri, session)
                importTorrent(dataPath)
            #TODO: Put better reporting / handling here (It's an UPLOAD!')
            continue
        remoteGrp = findBestGroup(ri, artist) #Closest matching group by artist

        #Update user
        if remoteGrp.match == 101:
            log.info('Exact catalogue match found for "{0}" [{1}/{2}]: {3}'.format(ri.group.name, ri.torrent.media, ri.torrent.encoding, remoteGrp.url))
        elif remoteGrp.match == 100:
            log.info('Exact title match found for "{0}" [{1}/{2}]: {3}'.format(ri.group.name, ri.torrent.media, ri.torrent.encoding, remoteGrp.url))
            #TODO: Check for possible seeding/trumping opportunity
        elif remoteGrp.match >= FUZZ_RATIO:
            log.info('Probable ({0}%) match found for "{1}" [{2}/{3}]: {4}'.format(remoteGrp.match, ri.group.name, ri.torrent.media, ri.torrent.encoding, remoteGrp.url))
            #TODO: Add to list of potential trumping opportunities
        elif requestUpload(ri, remoteGrp, artist, auto=args.auto):
            loadData(ri)
            dataPath = uploadTorrent(ri, session)
            importTorrent(dataPath)
        else:
            print('Moving on..')
        
        resumeList.add(file)
        saveResume()
            
    print('Potential Uploads: {0}'.format(str(potential_uploads)))


if __name__ == "__main__":
    main()
