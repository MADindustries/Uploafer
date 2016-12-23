#!/usr/bin/env python
from abc import ABCMeta, abstractmethod

gazelle_url = 'https://passtheheadphones.me/'
releaseTable = {8: 19, 22: 18, 23: 17} #8 = DJ Mix, 22 = Concert Recording, 23 = Demo

#Gazelle Format ArtistInfo
class artistInfo(object):
    def __init__(self, artist):
        self.id = artist['id']
        self.name = artist['name']
        self.notificationsEnabled = artist['notificationsEnabled']
        self.hasBookmarked = artist['hasBookmarked']
        self.image = artist['image']
        self.body = artist['body']
        self.vanityHouse = artist['vanityHouse']
        self.tags = []
        for tag in artist['tags']:
            self.tags.append(artistTag(tag))
        self.similarArtists = []
        for similar in artist['similarArtists']:
            self.similarArtists.append(similarArtist(similar))
        self.statistics = artistStats(artist['statistics'])
        self.torrentgroup = []
        for group in artist['torrentgroup']:
            self.torrentgroup.append(artistTG(group))
        self.requests = []
        for request in artist['requests']:
            self.requests.append(artistRequest(request))
        self.url = '{0}artist.php?id={1}'.format(gazelle_url, artist['id'])

class artistTag(object):
    def __init__(self, tag):
        self.name = tag['name']
        self.count = tag['count']

class similarArtist(object):
    def __init__(self, artist):
        self.score = artist['score']
        self.similarId = artist['similarId']
        self.name = artist['name']
        self.artistId = artist['artistId']

class artistStats(object):
    #Statistics
    def __init__(self, stats):
        self.numGroups = stats['numGroups']
        self.numTorrents = stats['numTorrents']
        self.numSeeders = stats['numSeeders']
        self.numLeechers = stats['numLeechers']
        self.numSnatches = stats['numSnatches']

class artistTG(object):
    #Torrent Group
    def __init__(self, tg):
        self.groupId = tg['groupId']
        self.groupName = tg['groupName']
        self.groupYear = tg['groupYear']
        self.groupRecordLabel = tg['groupRecordLabel']
        self.groupCatalogueNumber = tg['groupCatalogueNumber']
        self.tags = tg['tags']
        self.releaseType = tg['releaseType']
        self.groupVanityHouse = tg['groupVanityHouse']
        self.hasBoookmarked = tg['hasBookmarked']
        self.torrent = []
        for torrent in tg['torrent']:
            self.torrent.append(artistTorrent(torrent))
        self.url = '{0}torrents.php?id={1}'.format(gazelle_url, tg['groupId'])

class artistTorrent(object):
    def __init__(self, ti):
        self.id = ti['id']
        self.groupId = ti['groupId']
        self.media = ti['media']
        self.format = ti['format']
        self.encoding = ti['encoding']
        self.remasterYear = ti['remasterYear']
        self.remastered = ti['remastered']
        self.remasterTitle = ti['remasterTitle']
        self.remasterRecordLabel = ti['remasterRecordLabel']
        self.scene = ti['scene']
        self.hasLog = ti['hasLog']
        self.hasCue = ti['hasCue']
        self.logScore = ti['logScore']
        self.fileCount = ti['fileCount']
        self.freetorrent = ti['freeTorrent']
        self.size = ti['size']
        self.leechers = ti['leechers']
        self.seeders = ti['seeders']
        self.snatched = ti['snatched']
        self.time = ti['time']
        self.hasFile = ti['hasFile']

class artistRequest(object):
    def __init__(self, rq):
        self.requestId = rq['requestId']
        self.categoryId = rq['categoryId']
        self.title = rq['title']
        self.year = rq['year']
        self.timeAdded = rq['timeAdded']
        self.votes = rq['votes']
        self.bounty = rq['bounty']

class torrentGroup(object):
    def __init__(self, tg):
        self.group = releaseGroup(tg['group'])
        self.torrents = []
        for i, torrent in enumerate(tg['torrents']):
            self.torrents.append(torrentInfo(torrent))


#WM2 Format ReleaseInfo
class releaseInfo(object):
    def __init__(self, ri):
        self.group = releaseGroup(ri['group'])
        self.torrent = torrentInfo(ri['torrent'], True)
        

class releaseGroup(object):
    def __init__(self, rg):
        self.recordLabel = rg['recordLabel']
        self.name = rg['name']
        self.tags = rg['tags']
        self.catalogueNumber = rg['catalogueNumber']
        if rg['releaseType'] in releaseTable:
            self.releaseType = releaseTable[rg['releaseType']]
            print(self.releaseType)
        else:
            self.releaseType = rg['releaseType']
        self.categoryId = rg['categoryId']
        self.wikiBody = rg['wikiBody']
        if rg['categoryId'] == 1:
            self.musicInfo = musicInfo(rg['musicInfo'])
        else:
            self.musicInfo = None
        self.time = rg['time']
        self.year = rg['year']
        self.wikiImage = rg['wikiImage']
        self.isBookmarked = rg['isBookmarked']
        self.vanityHouse = rg['vanityHouse']
        self.id = rg['id']
        self.categoryName = rg['categoryName']
        self.url = '{0}torrents.php?id={1}'.format(gazelle_url, rg['categoryId'])

class torrentInfo(object):
    def __init__(self, ti, wm2=False):
        self.seeders = ti['seeders']
        self.encoding = ti['encoding']
        self.uderId = ti['userId']
        self.sceneBool = ti['scene']
        if ti['scene'] == True:
            self.scene = 'on'
        else:
            self.scene = None
        self.fileList = ti['fileList']
        self.logScore = ti['logScore']
        self.leechers = ti['leechers']
        self.remasterYear = ti['remasterYear']
        self.snatched = ti['snatched']
        #infoHash goes here
        self.id = ti['id']
        self.size = ti['size']
        self.media = ti['media']
        self.filePath = ti['filePath']
        self.hasCue = ti['hasCue']
        self.username = ti['username']
        self.description = ti['description']
        self.format = ti['format']
        self.remasterCatalogueNumber = ti['remasterCatalogueNumber']
        self.reported = ti['reported']
        self.remasteredBool = ti['remastered']
        if ti['remastered'] == True:
            self.remastered = 'on'
        else:
            self.remastered = None
        self.remasterRecordLabel = ti['remasterRecordLabel']
        self.hasLog = ti['hasLog']
        self.remasterTitle = ti['remasterTitle']
        self.time = ti['time']
        self.freetorrent = ti['freeTorrent']
        self.fileCount = ti['fileCount']
        if wm2:
            self.infoHash = ti['infoHash'] #Do I still need this? Better check...
            self.logFiles = []

class musicInfo(object):
    def __init__(self, mi):
        self.uploaddata = []
        self.composers = []
        self.dj = []
        self.producer = []
        self.conductor = []
        self.remixedBy = []
        self.artists = []
        self.miWith = []
        for i, collab in enumerate(mi['composers']):
            self.composers.append(miComposer(collab))
            self.uploaddata.append(("artists[]", collab['name']))
            self.uploaddata.append(("importance[]", 4))
        for i, collab in enumerate(mi['dj']):
            self.dj.append(miDJ(collab))
            self.uploaddata.append(("artists[]", collab['name']))
            self.uploaddata.append(("importance[]", 6))
        for i, collab in enumerate(mi['producer']):
            self.producer.append(miProducer(collab))
            self.uploaddata.append(("artists[]", collab['name']))
            self.uploaddata.append(("importance[]", 7))
        for i, collab in enumerate(mi['conductor']):
            self.conductor.append(miConductor(collab))
            self.uploaddata.append(("artists[]", collab['name']))
            self.uploaddata.append(("importance[]", 5))
        for i, collab in enumerate(mi['remixedBy']):
            self.remixedBy.append(miRemixedBy(collab))
            self.uploaddata.append(("artists[]", collab['name']))
            self.uploaddata.append(("importance[]", 3))
        for i, collab in enumerate(mi['artists']):
            self.artists.append(miArtists(collab))
            self.uploaddata.append(("artists[]", collab['name']))
            self.uploaddata.append(("importance[]", 1))
        for i, collab in enumerate(mi['with']):
            self.miWith.append(miWith(collab))
            self.uploaddata.append(("artists[]", collab['name']))
            self.uploaddata.append(("importance[]", 2))

class collaborator(object):
    """
        Abstract base class to contain composers, djs, producers, conductors,
        remixers, artists, and other collaborators 
    """

    __metaclass__ = ABCMeta

    def __init__(self, collab):
        if collab:
            self.id = collab['id']
            self.name = collab['name']

    @abstractmethod
    def collab_type(self):
        pass

class miComposer(collaborator):
    def collab_type(self):
        self.importance = 4
        return 'composer'

class miDJ(collaborator):
    def collab_type(self):
        self.importance = 6
        return 'dj'

class miProducer(collaborator):
    def collab_type(self):
        self.importance = 7
        return 'producer'

class miConductor(collaborator):
    def collab_type(self):
        self.importance = 5
        return 'conductor'

class miRemixedBy(collaborator):
    def collab_type(self):
        self.importance = 3
        return 'remixedBy'

class miArtists(collaborator):
    def collab_type(self):
        self.importance = 1
        return 'artists'

class miWith(collaborator):
    def collab_type(self):
        self.importance = 2
        return 'with'

