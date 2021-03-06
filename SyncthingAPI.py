# -*- coding: utf-8 -*-

import json
import requests
import types
import urllib
from functools import lru_cache

import logging
logger = logging.getLogger("PySel.SyncthingAPI")

# the following url was used to build API
# https://www.digitalocean.com/community/tutorials/how-to-use-web-apis-in-python-3

class SyncthingAPI:
    def __init__(self):
        self.api_token = None
        self.api_url_base = 'http://localhost:8384/rest/'
        self.headerSelectStart = '//* Selective sync (generated by pyselective) *//'
        self.headerSelectFinish = '//* ignore all except selected *//'
        self._ignoreSelectiveList = []

    def _getRequest(self, suff):
        api_url = self.api_url_base + suff
        response = requests.get(api_url, headers = {'X-API-Key': self.api_token})

        if isinstance(response, types.GeneratorType):
            raise ImportError('It seems you use \"yieldfrom.request\" instead of \"requests\"')

        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        elif response.status_code == 403:
            raise requests.RequestException('Forbidden, api token could be wrong')
        elif response.status_code == 404:
            logger.warning("No object in the index: {0}".format(suff))
        else:
            raise requests.RequestException('Wrong status code: '+ str(response.status_code) + " (" + suff + ")")

    def _postRequest(self, suff, d):
        api_url = self.api_url_base + suff
        requests.post(api_url, headers = {'X-API-Key': self.api_token}, json = d)

    def _refineBrowseFolderRequest(self, d, rv = None):
        # to avoid copying
        if rv is None:
            rv = []
        # refine dict with list to list of dicts
        for key in d:
            if isinstance(d[key], dict):
                rv.append({ 'name' : key, 'isfolder': True, 'content': [] })
                self._refineBrowseFolderRequest(d[key], rv[-1]['content'])
            else:
                rv.append({ 'name' : key, 'isfolder': False})
        return rv

    def getFolderIter(self):
        return self._getRequest('stats/folder').keys()
    
    def getFoldersDict(self):
        dicts = self._getRequest('stats/folder')
        cfgd = self._getRequest('system/config')
        for k in dicts.keys():
            for f in cfgd['folders']:
                if f['id'] == k:
                    dicts[k]['label'] = f['label']
                    dicts[k]['path'] = f['path']
        return dicts

    def getIgnoreList(self, fid):
        rv = self._getRequest('db/ignores?folder={0}'.format(fid))['ignore']
        if rv is None:
            return []
        return rv
    
    def getIgnoreSelective(self, fid):
        l = self.getIgnoreList(fid)
        if l.count(self.headerSelectStart) == 0 or \
                l.count(self.headerSelectFinish) == 0:
            return []
        indstart = l.index(self.headerSelectStart)
        indend = l.index(self.headerSelectFinish)
        return l[indstart+1:indend]
    
    def setIgnoreSelective(self, fid, il):
        l = self.getIgnoreList(fid)
        indstart = l.index(self.headerSelectStart)
        indend = l.index(self.headerSelectFinish)

        if len(il) > 1 and il[-1].strip() == '':
            il[-1] = '\n'
        else:
            il.append('\n')

        sendlist = l[:indstart+1] + il + l[indend:]
        self._postRequest('db/ignores?folder={0}'.format(fid), {'ignore': sendlist})

    def browseFolder(self, fid):
        d = self._getRequest('db/browse?folder={0}'.format(fid))
        self._ignoreSelectiveList = self.getIgnoreSelective(fid)
        return self._refineBrowseFolderRequest(d)

    def browseFolderPartial(self, fid, path='', lev=0):
        if path == '':
            d = self._getRequest('db/browse?folder={0}&levels={1}'.format(fid, lev))
        else:
            d = self._getRequest('db/browse?folder={0}&prefix={1}&levels={2}'.format(fid, path, lev))
        self._ignoreSelectiveList = self.getIgnoreSelective(fid) # TODO caching
        return self._refineBrowseFolderRequest(d)

    @lru_cache(maxsize=100)
    def getFileInfoExtended(self, fid, fn):
        'fn: file name with path relative to the parent folder'
        rv = self._getRequest('db/file?folder={0}&file={1}'.format(fid, urllib.parse.quote(fn)))
        if (rv['local']['type'] == 'DIRECTORY' or rv['local']['type'] == 1):
            if ("!/" + fn) in self._ignoreSelectiveList:
                rv['local']['ignore'] = False
            if ("/" + fn + "/**") in self._ignoreSelectiveList:
                rv['local']['partial'] = True
            else:
                rv['local']['partial'] = False
        return rv

    def getVersion(self):
        logger.debug("Try read syncthing version...")
        rv = self._getRequest('svc/report')['version']
        logger.debug("Ok: {0}".format(rv))
        return rv



