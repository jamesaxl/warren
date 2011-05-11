import miniFCP
import os

class FCPNode(object):

    _defaultConnection = None

    def __init__(self, name, host=miniFCP.DEFAULT_FCP_HOST, port=miniFCP.DEFAULT_FCP_PORT, to=miniFCP.DEFAULT_FCP_TIMEOUT, log=None, noversion=False):
        self.name = name
        self.host = host
        self.port = port
        self.to = to
        self.log = miniFCP.FCPLogger()
        self.noversion = noversion

    def _getDefaultConnection(self):
        if self._defaultConnection == None:
            self._defaultConnection = miniFCP.FCPConnection(self.host, self.port, self.to, self.name, self.log, self.noversion)
        return self._defaultConnection

    def setFCPLogger(self, log=None):
        self.log = log

    def getConfig(self, WithCurrent=False,WithExpertFlag=False):
        conn = self._getDefaultConnection()

        cmd = miniFCP.FCPCommand('GetConfig')
        cmd.setItem("WithCurrent", WithCurrent)
        cmd.setItem("WithExpertFlag", WithExpertFlag)

        conn.sendCommand(cmd)

        msg = conn.readEndMessage()
        return msg
    
    def ping(self, identifier=None):
        conn = self._getDefaultConnection()
        cmd = miniFCP.FCPCommand('Void', identifier)
        conn.sendCommand(cmd)
        # no reply

    def putDirect(self, uri, content, callback, **kw):
        conn = self._getDefaultConnection()
        cmd = miniFCP.FCPCommand("ClientPut")
        cmd.setItem('Verbosity', -1)
        cmd.setItem('URI', "CHK@")
        cmd.setItem('MaxRetries', 3)
        cmd.setItem('DontCompress', 'false')
        cmd.setItem('PriorityClass', '1')
        cmd.setItem('Global', 'false')
        cmd.setItem('Persistence', 'connection')
        cmd.setItem("UploadFrom", "direct")
        cmd.setItem("DataLength", str(len(content)))
        if kw.has_key('Mimetype'):
            cmd.setItem("Metadata.ContentType", kw['Mimetype'])
        cmd.setItem("RealTimeFlag", "true")
        cmd.setItem("TargetFilename", "pastetebin")
        conn.sendCommand(cmd, content)

        while True:
            msg = conn.readEndMessage();
            callback(msg.getMessageName(), msg)
            if msg.isMessageName(['ProtocolError', 'PutSuccessful', 'PutFailed']):
                break

        return None

    def putQueueFile(self, filename, uri, **kw):
        conn = self._getDefaultConnection()
        cmd = miniFCP.FCPCommand("ClientPut")
        cmd.setItem('Verbosity', -1)
        cmd.setItem('URI', "CHK@")
        cmd.setItem('MaxRetries', -1)
        cmd.setItem('DontCompress', 'false')
        cmd.setItem('PriorityClass', '1')
        cmd.setItem('Global', 'true')
        cmd.setItem('Persistence', 'forever')
        cmd.setItem("UploadFrom", "disk")
        cmd.setItem("Filename", filename)
        #cmd.setItem("Metadata.ContentType", "text/plain;  charset=utf-8")
        cmd.setItem("RealTimeFlag", "true")
        #cmd.setItem("TargetFilename", "pastetebin")
        conn.sendCommand(cmd)

        msg = conn.readEndMessage()
        if not msg.isMessageName('ProtocolError'):
            print "somthing else went wrong"
            return
        code = msg.getIntValue('Code')
        if code != 9:
            if code != 25:
                print "somthing else went wrong"
                return

            directory = os.path.split(filename)[0]
            isDDA = self._testDDAread(conn, directory)
        else:
            isDDA = False

        if isDDA:
            conn.sendCommand(cmd)
        else:
            f = open(filename, 'r')
            c = f.read()
            f.close()
            cmd.setItem("UploadFrom", "direct")
            cmd.setItem("DataLength", str(len(c)))
            conn.sendCommand(cmd, c)

        return None

    def _testDDAread(self, conn, dir):
        cmd = miniFCP.FCPCommand("TestDDARequest")
        cmd.setItem('Directory', dir)
        cmd.setItem('WantReadDirectory', 'true')
        cmd.setItem('WantWriteDirectory', 'false')

        conn.sendCommand(cmd)
        msg = conn.readEndMessage()
        if not msg.isMessageName('TestDDAReply'):
            print "somthing else went wrong"
            return False

        filename = msg.getValue('ReadFilename')

        if not os.path.exists(filename):
            print "file not found. no dda"
            return False

        f = open(filename, 'r')
        c = f.read()
        f.close()

        cmd = miniFCP.FCPCommand("TestDDAResponse")
        cmd.setItem('Directory', dir)
        cmd.setItem('ReadContent', c)
        conn.sendCommand(cmd)

        msg = conn.readEndMessage()
        if not msg.isMessageName('TestDDAComplete'):
            print "somthing else went wrong"
            return False

        return msg.getValue('ReadDirectoryAllowed') == 'true'

    def putQueueData(self, data, uri, **kw):
        conn = self._getDefaultConnection()
        cmd = miniFCP.FCPCommand("ClientPut")
        cmd.setItem('Verbosity', -1)
        cmd.setItem('URI', "CHK@")
        cmd.setItem('MaxRetries', -1)
        cmd.setItem('DontCompress', 'false')
        cmd.setItem('PriorityClass', '1')
        cmd.setItem('Global', 'true')
        cmd.setItem('Persistence', 'forever')
        cmd.setItem("UploadFrom", "direct")
        cmd.setItem("DataLength", str(len(data)))
        #cmd.setItem("Metadata.ContentType", "text/plain;  charset=utf-8")
        cmd.setItem("RealTimeFlag", "true")
        #cmd.setItem("TargetFilename", "pastetebin")
        conn.sendCommand(cmd, data)

        while True:
            msg = conn.readEndMessage();
            if msg.isMessageName(['ProtocolError', 'PutSuccessful', 'PutFailed']):
                break

        return None
