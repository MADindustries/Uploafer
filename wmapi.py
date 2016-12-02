#!/usr/bin/env python
from abc import ABCMeta, abstractmethod

class ReleaseInfo(object):
    def __init__(self, ri):
        self.group = releaseGroup(ri['group'])
        self.torrent = torrentInfo(ri['torrent'])

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

class torrentInfo(object):
    def __init__(self, ti):
        self.seeders = ti['seeders']
        self.encoding = ti['encoding']
        self.uderId = ti['userId']
        self.scene = ti['scene']
        self.fileList = ti['fileList']
        self.logScore = ti['logScore']
        self.leechers = ti['leechers']
        self.remasterYear = ti['remasterYear']
        self.snatched = ti['snatched']
        self.infoHash = ti['infoHash']
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

class musicInfo(object):
    def __init__(self, mi):
        # TODO: These need to support multiple entries at some point
        self.composers = miComposer(mi['composers'])
        self.dj = miDJ(mi['dj'])
        self.producer = miProducer(mi['producer'])
        self.conductor = miConductor(mi['conductor'])
        self.remixedBy = miRemixedBy(mi['remixedBy'])
        self.artists = miArtists(mi['artists'])
        self.miWith = miWith(mi['with'])

class collaborator(object):
    """
        Abstract base class to contain composers, djs, producers, conductors,
        remixers, artists, and other collaborators 
    """

    __metaclass__ = ABCMeta

    def __init__(self, collab):
        if collab:
            self.id = collab[0]['id']
            self.name = collab[0]['name']

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
