import random
import socket
import sys
import threading
import time

REQUIRED_NODE_BUILD = -1
REQUIRED_NODE_VERSION = 1373
REQUIRED_EXT_VERSION = 29

DEFAULT_FCP_HOST = "127.0.0.1"
DEFAULT_FCP_PORT = 9481
DEFAULT_FCP_TIMEOUT = 1800

# utils
def _getUniqueId():
    """Allocate a unique ID for a request"""
    timenum = int( time.time() * 1000000 )
    randnum = random.randint( 0, timenum )
    return "id" + str( timenum + randnum )

class FCPLogger(object):
    """log fcp traffic"""

    def __init__(self, filename=None):
        self.logfile = sys.stdout
    
    def write(self, line):
        self.logfile.write(line + '\n')

# asynchronous stuff (single thread)
class FCPIOConnection(object):
    """class for real i/o and format helpers"""

    def __init__(self, host, port, timeout, logger=None):
        self._logger = logger
        socket.setdefaulttimeout(timeout)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        #self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        print self.socket.gettimeout()
        print socket.getdefaulttimeout()
        try:
            self.socket.connect((host, port))
        except Exception, e:
            raise Exception("Failed to connect to %s:%s - %s" % (host, port, e))
        if (None != self._logger):
            self._logger.write("init: connected to %s:%s (timeout %d s)" % (host, port, timeout))

    def __del__(self):
        """object is getting cleaned up, so disconnect"""
        try:
            self.socket.close()
        except:
            pass

    def _readline(self):
        buf = []
        while True:
            c = self.socket.recv(1)
            if c:
                if c == '\n':
                    break
                buf.append(c)
            else:
                raise Exception("FCP socket closed by node")
        ln = "".join(buf)
        return ln

    def read(self, n):
        chunks = []
        remaining = n
        while remaining > 0:
            chunk = self.socket.recv(remaining)
            chunklen = len(chunk)
            if chunk:
                chunks.append(chunk)
            else:
                raise Exception("FCP socket closed by node")
            remaining -= chunklen
        buf = "".join(chunks)
        if (None != self._logger):
            self._logger.write("in: <"+str(len(buf))+" Bytes of data read>")
        return buf

    def skip(self, n):
        remaining = n
        while remaining > 0:
            chunk = self.socket.recv(remaining)
            chunklen = len(chunk)
            if not chunk:
                raise Exception("FCP socket closed by node")
            remaining -= chunklen
        if (None != self._logger):
            self._logger.write("in: <"+str(n)+" Bytes of data skipped>")

    def readEndMessage(self):
        #the first line is the message name
        messagename = self._readline()

        if (None != self._logger):
            self._logger.write("in: "+messagename)

        items = {}
        while True:
            line = self._readline()

            if (None != self._logger):
                self._logger.write("in: "+line)

            if (len(line.strip()) == 0):
                continue # an empty line, jump over

            if line in ['End', 'EndMessage', 'Data']:
                endmarker = line
                break

            # normal 'key=val' pairs left
            k, v = line.split("=", 1)
            items[k] = v

        return FCPMessage(messagename, items, endmarker)

    def _sendLine(self, line):
        if (None != self._logger):
            self._logger.write("out: "+line)
        self.socket.sendall(line+"\n")

    def _sendMessage(self, messagename, hasdata=False, **kw):
        self._sendLine(messagename)
        for k, v in kw.items():
            line = k + "=" + str(v)
            self._sendLine(line)
        if kw.has_key("DataLength") or hasdata:
            self._sendLine("Data")
        else:
            self._sendLine("EndMessage")

    def _sendCommand(self, messagename, hasdata, kw):
        self._sendLine(messagename)
        for k, v in kw.items():
            line = k + "=" + str(v)
            self._sendLine(line)
        if kw.has_key("DataLength") or hasdata:
            self._sendLine("Data")
        else:
            self._sendLine("EndMessage")

    def _sendData(self, data):
        if (None != self._logger):
            self._logger.write("out: <"+str(len(data))+" Bytes of data>")
        self.socket.sendall(data)

class FCPConnection(FCPIOConnection):
    """class for low level fcp protocol i/o"""

    def __init__(self, host, port, timeout, name=None, logger=None, noversion=False):
        """c'tor leaves a ready to use connection (hello done)"""
        FCPIOConnection.__init__(self, host, port, timeout, logger)
        self._helo(name, noversion)

    def _helo(self, name, noversion):
        """perform the initial FCP protocol handshake"""
        if name == None:
            name = _getUniqueId()
        self._sendMessage("ClientHello", Name=name, ExpectedVersion="2.0")
        msg = self.readEndMessage()
        if not msg.isMessageName("NodeHello"):
            raise Exception("Node helo failed: %s" % (msg.getMessageName()))

        # check versions
        if not noversion:
            version = msg.getIntValue("Build")
            if version < REQUIRED_NODE_VERSION:
                if version == (REQUIRED_NODE_VERSION-1):
                    revision = msg.getValue("Revision")
                    if not revision == '@custom@':
                        revision = int(revision)
                        if revision < REQUIRED_NODE_BUILD:
                            raise Exception("Node to old. Found build %d, but need minimum build %d" % (revision, REQUIRED_NODE_BUILD))
                else:
                    raise Exception("Node to old. Found %d, but need %d" % (version, REQUIRED_NODE_VERSION))

            extversion = msg.getIntValue("ExtBuild")
            if extversion < REQUIRED_EXT_VERSION:
                raise Exception("Node-ext to old. Found %d, but need %d" % (extversion, REQUIRED_EXT_VERSION))

    def sendCommand(self, command, data=None):
        if data is None:
            hasdata = command.hasData()
        else:
            hasdata = True
        self._sendCommand(command.getCommandName(), hasdata, command.getItems())
        if data is not None:
            self._sendData(data)

    def write(self, data):
        self._sendData(data)

class FCPCommand(object):
    """class for client to node messages"""

    def __init__(self, name, identifier=None):
        self._name = name
        self._items = {}
        if None == identifier:
            self._items['Identifier'] = _getUniqueId()
        else:
            self._items['Identifier'] = identifier

    def getCommandName(self):
        return self._name

    def getItems(self):
        return self._items

    def setItem(self, name, value):
        self._items[name] = value

    def hasData(self):
        if self._items.has_key("DataLength"):
            return True
        else:
            return False 

class FCPMessage(object):
    """class for node to client messages"""
    _items = {}
    _messagename = ""
    _endmarker = ""

    def __init__(self, messagename, items, endmarker):
        self._messagename = messagename
        self._endmarker = endmarker
        self._items = items 

    def isMessageName(self, testname):
        if self._messagename in testname:
            return True
        else:
            return False

    def getMessageName(self):
        return self._messagename

    def getIntValue(self, name):
        return int(self._items[name])

    def getValue(self, name):
        return self._items[name]

    def isDataCarryingMessage(self):
        return self._endmarker == "DATA"

# asynchronous stuff (thread save)

class FCPConnectionRunner(threading.Thread):
    """class for send/recive FCP commands asynchronly"""

    _fcp_conn = None
    _cb = None

    def run(self):
        self._fcp_conn = FCPConnection()

        while true:
            msg = self._fcp_conn.readEndMessage()
            if msg.isDataCarryingMessage():
                self._cb.onDataMessage(msg)
            else:
                self._cb.onMessage(msg)

    def close(self):
        self._fcp_conn.close();

    def send(self, msg, data=None):
        self._fcp_conn.sendCommand(msg, data)

class FCPJob(object):
    """abstract class for asynchronous jobs, they may use more then one fcp command and/or interact with the node in a complex manner"""

class FCPSession(object):
    """class for managing/running FCPJobs on a single connection"""

    def start(self):
        pass

    def stop(self):
        pass