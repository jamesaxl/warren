from PyQt4.QtCore import QThread
import urllib2
import os.path

def buildOpener(url, proxy=None):
    if len(url)>=4 and url[:4]=='http' and proxy and proxy.get('host','') != '':
        proxies = {'http':'%s:%s' % (proxy['host'],proxy['port']),
                   'https':'%s:%s' % (proxy['host'],proxy['port']),}
        p = urllib2.ProxyHandler(proxies=proxies)
        opener = urllib2.build_opener(p)
    else:
        opener = urllib2.build_opener()
    return opener

def checkFileForInsert(mimeData, proxy=None):
    try:
        for format in mimeData.formats():
            if format == "text/uri-list":
                url = unicode(mimeData.urls()[0].toString()).encode('utf-8') # only use the first one
                opener = buildOpener(url, proxy)
                u = opener.open(url)
                for header in u.headers.items():
                    if header[0] == 'content-type':
                        u.close()
                        return (url, header[1])
        return False
    except: # TODO make this nicer
        return False

class FileInsert(QThread):

    def __init__(self, parent, url, mimeType, proxy=None):
        QThread.__init__(self, parent)
        self.nodeManager = parent
        self.url = url
        self.mimeType = mimeType
        self.proxy = proxy

    def run(self):
        keyType = self.nodeManager.config['warren']['file_keytype']
        tmpReq = urllib2.Request(self.url)
        if tmpReq.get_type() == 'file':
            plainUrl = tmpReq.get_selector()
            self.nodeManager.node.putQueueFile(keyType, plainUrl)
        else:
            opener = buildOpener(self.url, self.proxy)
            u = opener.open(self.url)
            filename = os.path.basename(self.url)
            data = u.read() # we have to make this streaming in the future (pyFreenet can't handle it atm)
            u.close()
            insert = self.nodeManager.node.putQueueData(keyType, data, TargetFilename=filename, Mimetype=self.mimeType)

