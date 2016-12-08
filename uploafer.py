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
resumeList = set([])
potential_uploads = 0

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

        #TODO: Below may not be necessary. See ri.torrent.filePath for a possible replacement
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

def requestUpload(ri, remoteGrp, artist, auto=False):
    global potential_uploads
    potential_uploads += 1
    print('')
    print('{4} - No match found for "{0}" [{1}/{2}]:  {3}'.format(ri.group.name, ri.torrent.media, ri.torrent.encoding, ri.group.path, str(potential_uploads)))
    print('Closest match ({0}% likeness): {1}'.format(remoteGrp.match, remoteGrp.groupName))
    #Next line, what if more than one artist or secondary artist identifier?
    if auto:
        log.info("Upload not yet implemented.")
        return False
    if query_yes_no('Do you want to upload to artist "{0}" [{1}]?'.format(ri.group.musicInfo.artists[0].name, artist.url)):
        return True
    else:
        return False

def buildUpload(ri, artist, remoteGrp):
    artists = album_artists(album)
    remaster = remaster_status(album)
    data = [
        ("submit", "true"),  # the submit button
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
        ("format", ri.torrent.format),
        ("bitrate", ri.torrent.encoding),
        ("other_bitrate", ""),  # n/a
        ("media", ri.torrent.media),  # Media source
        ("genre_tags", tags[0]),  # blank - this is the dropdown of official tags
        ("tags", ", ".join(ri.group.tags)),  # classical, hip.hop, etc. (comma separated)
        ("image", ri.group.wikiImage),  #TODO: What if this is a whatimg link??
        ("album_desc", ri.torrent.description),
        ("release_desc", "UPLOAFED!") #TODO: You are better than this
    ]
    for artist in artists:
        importance = 1
        if " feat. " in artist:
            artist = artist.split(" feat. ")[1]
            importance = 2
        data.append(("artists[]", artist))
        data.append(("importance[]", importance))
    files = []
    for logfile in logfiles:
        files.append(("logfiles[]", logfile))
    files.append(("file_input", torrent))
    return data, files

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
    for file in riList:
        log.debug('Currently processing: {0}'.format(file))

        #Load the local torrent group we are working with
        ri = loadReleaseInfo(file)
        if ri.group.categoryId != 1:
            log.info('Group "{0}" is not a music group. Skipping..'.format(ri.group.name))
            continue
        if ri.torrent.encoding == 'V2 (VBR)':
            log.info('Group "{0}" is in MP3 V2 format. Skipping..'.format(ri.group.name))
            continue
        #Open session
        session = whatapi.WhatAPI(USERNAME, PASSWORD)
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
            log.error('Artist not found: {0}'.format(ri.group.musicInfo.artists[0].name))
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
        elif requestUpload(ri, remoteGrp, artist, args.auto):
            buildUpload(ri, artist, remoteGrp)
        else:
            print('Moving on..')
        
        resumeList.add(file)
        saveResume()
            
    print('Potential Uploads: {0}'.format(str(potential_uploads)))


if __name__ == "__main__":
    main()
