import miniFCP
import os

class FCPNode(object):


    def __init__(self, **fcpargs):
        self._fcpargs = fcpargs
        #hack: force fcp logging. useful at this early stage
        self._fcpargs['fcplogger'] = miniFCP.FCPLogger()
        self._defaultConnection = None

    def _getDefaultConnection(self):
        if not self._defaultConnection:
            self._defaultConnection = miniFCP.FCPConnection(**self._fcpargs)
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
        """transient direct insert"""
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
        """add a local file to global queue
           TestDDA is transparently done if the node request it,
           if the test fails it fallback to direct"""
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
        if kw.has_key('Mimetype'):
            cmd.setItem("Metadata.ContentType", kw['Mimetype'])
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
        """add data[] to global queue"""
        # TODO stream the data, data[] is ugly on big files.
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
        if kw.has_key('Mimetype'):
            cmd.setItem("Metadata.ContentType", kw['Mimetype'])
        cmd.setItem("RealTimeFlag", "true")
        #cmd.setItem("TargetFilename", "pastetebin")
        conn.sendCommand(cmd, data)

        while True:
            msg = conn.readEndMessage();
            if msg.isMessageName(['ProtocolError', 'PutSuccessful', 'PutFailed']):
                break

        return None
