from PyQt4.QtCore import QThread
import urllib.request, urllib.error, urllib.parse, zipfile
import os.path
from io import StringIO

def buildOpener(url, proxy=None):
    if len(url)>=4 and url[:4]=='http' and proxy and proxy.get('host','') != '':
        proxies = {'http':'%s:%s' % (proxy['host'],proxy['port']),
                   'https':'%s:%s' % (proxy['host'],proxy['port']),}
        p = urllib.request.ProxyHandler(proxies=proxies)
        opener = urllib.request.build_opener(p)
    else:
        opener = urllib.request.build_opener()
    return opener

def checkFileForInsert(mimeData, proxy=None):
    for format in mimeData.formats():
        if format == "text/uri-list":
            url = str(mimeData.urls()[0].toString()).encode('utf-8') # only use the first one
            opener = buildOpener(url, proxy)
            try:
                u = opener.open(url)
                for header in list(u.headers.items()):
                    if header[0] == 'content-type':
                        u.close()
                        return (url, header[1])
            except IOError as e:
                if e.errno == 21: #directory on linux
                    return (url,'directory')
                elif e.errno == 13 and os.path.isdir(url): #directory on windows
                    return (url,'directory')
                else:
                    return False
            except Exception as e:
                return False
    return False

class DirectoryInsert(QThread):

    def __init__(self, parent, url):
        QThread.__init__(self, parent)
        self.nodeManager = parent
        self.url = url

    def run(self):
        zipFileName, zipFile = self.zipDir(self.url)
        zipFile.seek(0)
        keyType = self.nodeManager.config['warren']['file_keytype']
        self.nodeManager.node.putQueueData(keyType, zipFile.read(), TargetFilename=zipFileName, Mimetype='application/zip', Priority=4)
        self.quit() # because we put everything on node's global queue, we are not interested in what happens after put()

    def zipDir(self, dirPath):
        tmpReq = urllib.request.Request(self.url)
        plainUrl = tmpReq.get_selector()
        parentDir, dirName = os.path.split(plainUrl)
        includeDirInZip = False

        def trimPath(path):
            archivePath = path.replace(parentDir, "", 1)
            if parentDir:
                archivePath = archivePath.replace(os.path.sep, "", 1)
            if not includeDirInZip:
                archivePath = archivePath.replace(dirName + os.path.sep, "", 1)
            return os.path.normcase(archivePath)

        ramFile = StringIO()

        zipFile = zipfile.ZipFile(ramFile, 'w', compression=zipfile.ZIP_DEFLATED)
        
        for (archiveDirPath, dirNames, fileNames) in os.walk(plainUrl):
            for fileName in fileNames:
                filePath = os.path.join(archiveDirPath, fileName)
                zipFile.write(filePath, os.path.join(dirName,trimPath(filePath)))

            if not fileNames and not dirNames: # empty folders
                zipInfo = zipfile.ZipInfo(os.path.join(dirName,trimPath(archiveDirPath) + "/"))
                zipInfo.external_attr = 0o777 << 16
                zipFile.writestr(zipInfo, "")

        return (dirName+'.zip', ramFile)

class FileInsert(QThread):

    def __init__(self, parent, url, mimeType, proxy=None):
        QThread.__init__(self, parent)
        self.nodeManager = parent
        self.url = url
        self.mimeType = mimeType
        self.proxy = proxy

    def run(self):
        keyType = self.nodeManager.config['warren']['file_keytype']
        tmpReq = urllib.request.Request(self.url)
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

