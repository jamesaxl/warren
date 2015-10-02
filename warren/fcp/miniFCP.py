import random
import socket
import sys
from threading import Event, Lock, Thread
import time
if __debug__:
    import traceback

# defaults
REQUIRED_FCP_VERSION = "2.0"
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

#exceptions
class FCPConnectionRefused(Exception):
    """cannot connect to given host/port"""

class FCPException(Exception):
    """fcp error"""

# synchronous fcp stuff (single thread)
class FCPIOConnection(object):
    """class for real i/o and format helpers"""

    def __init__(self, **fcpargs):
        host = fcpargs.get('fcphost', DEFAULT_FCP_HOST)
        port = fcpargs.get('fcpport', DEFAULT_FCP_PORT)
        timeout = fcpargs.get('fcptimeout', DEFAULT_FCP_TIMEOUT)
        self._logger = fcpargs.get('fcplogger', None)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.socket.settimeout(timeout)
        try:
            self.socket.connect((host, port))
        except Exception as e:
            raise FCPConnectionRefused("Failed to connect to %s:%s - %s" % (host, port, e))
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
                raise FCPException("FCP socket closed by node")
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
                raise FCPException("FCP socket closed by node")
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
                raise FCPException("FCP socket closed by node")
            remaining -= chunklen
        if (None != self._logger):
            self._logger.write("in: <"+str(n)+" Bytes of data skipped>")

    def close(self):
        if (None != self._logger):
            self._logger.write("init: closing connection")
        self.socket.close()

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
        for k, v in list(kw.items()):
            line = k + "=" + str(v)
            self._sendLine(line)
        if "DataLength" in kw or hasdata:
            self._sendLine("Data")
        else:
            self._sendLine("EndMessage")

    def _sendCommand(self, messagename, hasdata, kw):
        self._sendLine(messagename)
        for k, v in list(kw.items()):
            line = k + "=" + str(v)
            self._sendLine(line)
        if "DataLength" in kw or hasdata:
            self._sendLine("Data")
        else:
            self._sendLine("EndMessage")

    def _sendData(self, data):
        if (None != self._logger):
            self._logger.write("out: <"+str(len(data))+" Bytes of data>")
        self.socket.sendall(data)

class FCPConnection(FCPIOConnection):
    """class for low level fcp protocol i/o

        kwargs:
            fcpname: client name
            fcphost:
            fcpport:
            fcptimeout: tcp connection timeout
            fcplogger: FCPLogger instance to log fcp traffic, defaults: None
            fcpnoversion: if true the node version check is omitted
            fcprequirednodeversion: minimum node version
            fcprequiredextversion: minimum ext version
    """

    def __init__(self, **fcpargs):
        """c'tor leaves a ready to use connection (hello done)"""
        FCPIOConnection.__init__(self, **fcpargs)
        self._helo(**fcpargs)

    def _helo(self, **fcpargs):
        """perform the initial FCP protocol handshake"""
        self._sendMessage("ClientHello", Name=fcpargs.get('fcpname', _getUniqueId()), ExpectedVersion=REQUIRED_FCP_VERSION)
        msg = self.readEndMessage()
        if not msg.isMessageName("NodeHello"):
            raise FCPException("Node helo failed: %s" % (msg.getMessageName()))

        # check node version
        if not fcpargs.get('fcpnoversion', False):
            reqversion = fcpargs.get('fcprequirednodeversion', REQUIRED_NODE_VERSION)
            version = msg.getIntValue("Build")
            if version < reqversion:
                raise FCPException("Node to old. Found %d, but need %d" % (version, reqversion))
            reqextversion = fcpargs.get('fcprequiredextversion', REQUIRED_EXT_VERSION)
            extversion = msg.getIntValue("ExtBuild")
            if extversion < reqextversion:
                raise FCPException("Node-ext to old. Found %d, but need %d" % (extversion, reqextversion))

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

    def __init__(self, name, **cmdargs):
        self._name = name
        self._items = cmdargs
        if 'Identifier' not in self._items:
            self._items['Identifier'] = _getUniqueId()

    def getCommandName(self):
        return self._name

    def getItems(self):
        return self._items

    def setItem(self, name, value):
        self._items[name] = value

    def hasData(self):
        if "DataLength" in self._items:
            return True
        else:
            return False 

class FCPMessage(object):
    """class for node to client messages"""
    _items = {}
    _messagename = ""
    _endmarker = ""

    def __str__(self):
        parts = []
        parts.append(self._messagename)
        for k in self._items:
            parts.append(str("=".join([k, self._items[k]])))
        parts.append(self._endmarker)
        return "\n".join(parts) or "??"

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

# asynchronous fcp stuff (thread save)

class FCPConnectionRunner(Thread):
    """class for send/recive FCP commands asynchronly"""

    def __init__(self, cb, **kwargs):
        Thread.__init__(self)
        self.setDaemon(True)
        self._fcp_conn = None
        self._fcpargs = kwargs
        self._cb = cb
        self._wLock = Lock()
        self._ev = Event()

    def start(self):
        Thread.start(self)
        self._ev.wait()

    def run(self):
        try:
            self._fcp_conn = FCPConnection(**self._fcpargs)
        except Exception as e:
            if __debug__:
                traceback.print_exc()
        finally:
            self._ev.set()

        while self._fcp_conn:
            msg = self._fcp_conn.readEndMessage()
            if msg.isMessageName('CloseConnectionDuplicateClientName'):
                self.close()
            if msg.isDataCarryingMessage():
                self._cb.onDataMessage(msg, self._fcp_conn)
            else:
                self._cb.onMessage(msg)

    def close(self):
        """close the connection. think kill -9 ;)"""
        try:
            self._fcp_conn.close();
        finally:
            self._fcp_conn = None

    def shutDown(self):
        """close the connection softly"""
        self._wLock.acquire();
        try:
            self._fcp_conn.close();
        finally:
            self._fcp_conn = None
            self._wLock.release();

    def sendCommand(self, msg, data=None):
        self._wLock.acquire();
        try:
            self._fcp_conn.sendCommand(msg, data)
        finally:
            self._wLock.release();

class FCPJob(Thread):
    """abstract class for asynchronous jobs, they may use more then one fcp command and/or interact with the node in a complex manner"""

    def __init__(self, identifier=None):
        Thread.__init__(self)
        self._lastError = None
        self._lastErrorMessage = None
        self._waitEvent = Event()
        self._ConnectionRunner = None
        self._JobRunner = None
        if not identifier:
            self._identifier = _getUniqueId()
        else:
            self._identifier = identifier

    def getJobIdentifier(self):
        return self._identifier

    def prepare(self):
        """overwrite this for job preparation, collect data/files etc pp"""
        pass

    def getFCPCommand(self):
        raise NotImplementedError()

    def onMessage(self, msg):
        print(self.__class__.__name__, "got a msg but did not deal with it:\n", str(msg))

    def runFCP(self):
        self.prepare()
        cmd, data = self.getFCPCommand()
        self._ConnectionRunner.sendCommand(cmd, data)

    def waitForDone(self):
        self._waitEvent.wait()

    def setError(self, e):
        self._lastError = e
        self._waitEvent.set()

    def setErrorMessage(self, msg):
        self._lastErrorMessage = msg
        self._waitEvent.set()

    def setSuccess(self):
        self._lastError = None
        self._lastErrorMessage = None
        self._waitEvent.set()

    def isSuccess(self):
        return ((not self._lastError) and (not self._lastErrorMessage))

    def makeFCPCommand(self, name, **kwargs):
        cmd = FCPCommand(name, **kwargs)
        cmd.setItem('Identifier', self.getJobIdentifier())
        return cmd

    def run(self):
        try:
            self.runFCP()
        except Exception as e:
            if __debug__:
                traceback.print_exc()
            self._ConnectionRunner = None
            self.setError(e)

class FCPJobRunner(object):
    """abstract class for execute jobs asynchronously"""

    def __init__(self):
        # map identifier -> job
        self._jobs = {}

    def _registerJob(self, id, job):
        self._jobs[id] = job

    def _unregisterJob(self, jobID):
        self._jobs.pop(jobID)

    def onMessage(self, msg):
        id = None
        try:
            id = msg.getValue('Identifier')
        except KeyError as ke:
            if msg.isMessageName(['TestDDAReply', 'TestDDAComplete']):
                id = msg.getValue('Directory')
            else:
                raise ke
        job = self._jobs.get(id)
        if job:
            job.onMessage(msg)
        else:
            self.onUnhandledMessage(msg)

    def runJob(self, job):
        """execute a job blocking. does not return until job is done"""
        self.startJob(job)
        job.waitForDone()
        self._unregisterJob(job.getJobIdentifier())

    def startJob(self, job):
        """queue a job for execution and return imadently"""
        cr = self.getConnectionRunner(job.getJobIdentifier())
        job._JobRunner = self
        job._ConnectionRunner = cr
        self._registerJob(job.getJobIdentifier(), job)
        job.start()

class FCPSession(FCPJobRunner):
    """class for managing/running FCPJobs"""

    def start(self):
        pass

    def stop(self):
        pass