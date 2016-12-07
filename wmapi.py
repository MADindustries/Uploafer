#!/usr/bin/env python
from abc import ABCMeta, abstractmethod

gazelle_url = 'https://passtheheadphones.me/'

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
    def __init(self, rq):
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
        for i in range(0,len(tg['torrents'])):
            self.torrents.append(torrentInfo(tg['torrents'][i]))

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
        self.releaseType = rg['releaseType']
        self.categoryId = rg['categoryId']
        self.wikiBody = rg['wikiBody']
        self.musicInfo = musicInfo(rg['musicInfo'])
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
        self.scene = ti['scene']
        self.fileList = ti['fileList']
        self.logScore = ti['logScore']
        self.leechers = ti['leechers']
        self.remasterYear = ti['remasterYear']
        self.snatched = ti['snatched']
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
        self.remastered = ti['remastered']
        self.remasterRecordLabel = ti['remasterRecordLabel']
        self.hasLog = ti['hasLog']
        self.remasterTitle = ti['remasterTitle']
        self.time = ti['time']
        self.freetorrent = ti['freeTorrent']
        self.fileCount = ti['fileCount']
        if wm2:
            self.infoHash = ti['infoHash']

class musicInfo(object):
    def __init__(self, mi):
        self.composers = []
        self.dj = []
        self.producer = []
        self.conductor = []
        self.remixedBy = []
        self.artists = []
        self.miWith = []
        for i in range(0,len(mi['composers'])):
            self.composers.append(miComposer(mi['composers'][i]))
        for i in range(0,len(mi['dj'])):
            self.dj.append(miDJ(mi['dj'][i]))
        for i in range(0,len(mi['producer'])):
            self.producer.append(miProducer(mi['producer'][i]))
        for i in range(0,len(mi['conductor'])):
            self.conductor.append(miConductor(mi['conductor'][i]))
        for i in range(0,len(mi['remixedBy'])):
            self.remixedBy.append(miRemixedBy(mi['remixedBy'][i]))
        for i in range(0,len(mi['artists'])):
            self.artists.append(miArtists(mi['artists'][i]))
        for i in range(0,len(mi['with'])):
            self.miWith.append(miWith(mi['with'][i]))

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
        return 'composer'

class miDJ(collaborator):
    def collab_type(self):
        return 'dj'

class miProducer(collaborator):
    def collab_type(self):
        return 'producer'

class miConductor(collaborator):
    def collab_type(self):
        return 'conductor'

class miRemixedBy(collaborator):
    def collab_type(self):
        return 'remixedBy'

class miArtists(collaborator):
    def collab_type(self):
        return 'artists'

class miWith(collaborator):
    def collab_type(self):
        return 'with'

