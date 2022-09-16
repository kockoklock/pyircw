import socket
from typing import Callable, Iterable, Tuple

class IRC_Client:
    """An irc client wrapper for socket communication with irc server"""
    def __init__(self, address: str, port: int):
        self.__address = address
        self.__port = port

    def connect(self):
        """Create a connection to the irc server"""
        address_pair = (self.__address, self.__port)
        self.__socket = socket.create_connection(address_pair)

    def pong(self, s: str):
        """Respond to the PING {s} message with PONG {s}"""
        s = f'PONG {s}\r\n'
        self.send(s)

    def privmsg(self, channel: str, message: str):
        """Send a private message to a channel"""
        s = f'PRIVMSG {channel} {message}\r\n'
        self.send(s)

    def nick(self, nickname: str):
        """Change nickname"""
        self.nickname = nickname
        s = f'NICK {nickname}\r\n'
        self.send(s)

    def user(self, username: str, mode: int, fullname: str):
        """Identify user to the server"""
        self.username = username 
        self.mode = mode
        self.fullname = fullname 
        s = f'USER {username} {mode} * :{fullname}'
        self.send(s)

    def join(self, channel):
        """Join a channel"""
        s = f'JOIN {channel}\r\n'
        self.send(s)

    def read(self):
        """Read messages from the server.
        Store them in self.messages"""
        buf = _read_buffer(self.__socket)
        if buf is None:
            self.messages = []
            return
        lines = buf.split('\r\n')[:-1]
        self.messages = _parse_irc_messages(lines)

    def send(self, s):
        """Send a message to the server"""
        self.__socket.send(s.encode('utf-8'))

BotFunction = Callable[['Bot', 'IRC_Message'], str | None]
class Bot(IRC_Client):
    """An irc bot.
    Calls functions in {on_privmsg} when a PRIVMSG is read.
    Calls functions in {functions} when a PRIVMSG is initiated with {bang}
    and the name of the function."""
    def __init__(self, address: str, port: int, channel: str, nickname: str,
                 username: str | None = None, mode: int = 0,
                 fullname: str | None = None, bang: str = '!',
                 functions: Iterable[Tuple[str, BotFunction]] | None = None,
                 on_privmsg: Iterable[BotFunction] | None = None):
        super().__init__(address, port)
        self.channel    = channel
        self.nickname   = nickname
        self.username   = nickname if username is None else username
        self.mode       = mode
        self.fullname   = nickname if fullname is None else fullname
        self.bang       = bang
        self.functions  = [] if functions is None else functions
        self.on_privmsg = [] if on_privmsg is None else on_privmsg

    def register(self):
        """Registers the bot to the client"""
        self.nick(self.nickname)
        self.user(self.username, self.mode, self.fullname)

    def __call_function(self, msg, respond_to):
        """Call functions in functions"""
        if msg.message[0] != self.bang:
            return
        for b, f in self.functions:
            if msg.message.split(' ')[0][1:] != b:
                return
            try:
                r = f(self, msg)
            except Exception as e:
                r = repr(e)
            if r is not None:
                self.privmsg(respond_to, r)

    def __call_on_privmsg(self, msg, respond_to):
        """Call functions in on_privmsg"""
        for f in self.on_privmsg:
            try:
                r = f(self, msg)
            except Exception as e:
                r = repr(e)
            if r is not None:
                self.privmsg(respond_to, r)

    def run(self):
        self.read()
        for msg in self.messages:
            print(msg)
            match msg.command:
                case 'PING':
                    self.pong(msg.middle)
                case '001':
                    self.join(self.channel)
                case 'PRIVMSG':
                    respond_to = msg.middle if msg.middle[0] == "#" \
                            else msg.nickname
                    self.__call_function(msg, respond_to)
                    self.__call_on_privmsg(msg, respond_to)



## Message class
class IRC_Message:
    def __init__(self, s):
        prefix = nickname = command = middle = trailing = message = None
        w = s.split(' ')
        if len(w) > 1:
            if w[0][0] == ':':
                prefix, command = w[:2]
            else:
                command = w[0]
        if prefix is not None and '!' in prefix:
            nickname = prefix.split('!')[0][1:]
        if command is not None and len(w) > w.index(command) + 1:
            middle = w[w.index(command)+1]
        if middle is not None and len(w) > w.index(middle) + 1:
            trailing = ' '.join(w[w.index(middle) + 1:])
        if trailing is not None:
            message = trailing[1:]

        self.prefix = prefix
        self.nickname = nickname
        self.command  = command
        self.middle   = middle
        self.trailing = trailing 
        self.message  = message 

    def __str__(self):
        s = ""
        for w in (self.prefix, self.command, self.middle, self.trailing):
            if w is not None:
                s += w + " "
        return s[:-1]

## Helper functions

def _read_buffer(sock):
    buf = sock.recv(1024)
    if len(buf) < 1:
        return None
    while buf[-1] != b'\n'[0]:
        buf += sock.recv(1024)
    return buf.decode('utf-8')

def _parse_irc_messages(messages):
    ret = []
    for m in messages:
        i = IRC_Message(m)
        ret.append(i) 
    return ret

