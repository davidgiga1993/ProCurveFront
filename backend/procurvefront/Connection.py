import re
import struct
import telnetlib
from telnetlib import DO, DONT, IAC, WILL, WONT


class Connection:
    ASNI_REGEX = re.compile(r'(\x1B\[[0-?]*[ -/]*[@-~])|\x1bE')

    def __init__(self, host: str, port: int, password: str):
        self._host = host
        self._port = port
        self._password = password

        self._tn = None

    def connect(self):
        """
        Connects to the switch via telnet using the given user name
        """
        self._tn = telnetlib.Telnet(self._host, port=self._port)

        def callback(socket, command, option):
            if command in (DO, WILL) and ord(option) == 31:  # Accept NAWS
                socket.sendall(IAC + command + option)
                return
            if command in (DO, DONT):
                socket.sendall(IAC + WONT + option)
                return
            if command in (WILL, WONT):
                socket.sendall(IAC + DONT + option)

        self._tn.set_option_negotiation_callback(callback)
        if self._password is not None:
            self._read_until('Password: ')
        self._send(self._password + '\n')
        self._read_until('# ')
        self._set_terminal_size()

    def get_config(self, running: bool):
        """
        Returns the complete switch configuration

        :param running: True if the running config should be returned, false to get the startup config
        :return: Config as string
        :rtype: str
        """
        if running:
            show = 'running-config'
        else:
            show = 'config'

        return self._send_cmd('show ' + show)

    def has_config_diff(self):
        """
        Checks if the running config is different from the startup config

        :return: True if different
        :rtype: bool
        """
        content = self._send_cmd('show running-config status')
        return 'is same as' not in content

    def _set_terminal_size(self):
        """
        Sends the terminal size so we don't get any interactive pagination
        """
        naws_command = struct.pack('!BBBHHBB',
                                   255, 250, 31,  # IAC SB NAWS
                                   427, 75,  # Width Height
                                   255, 240)  # IAC SE
        self._tn.get_socket().send(naws_command)

    def _send_cmd(self, command: str):
        """
        Sends the given command to the switch

        :param command: Command (without line feed)
        :return: Reply
        """
        command += '\n'
        self._send(command)
        content = self._read_until('# ')
        # Content contains the command send + \n\r
        # All other \r\n are duplicated resulting in \n\r\n\r
        content = content.replace('\r', '').replace('\n\n', '\n').replace(command, '')

        # Last line is the prompt
        content = '\n'.join(content.splitlines()[:-1])
        return content

    def _read_until(self, content: str):
        """
        Reads until the given text has been read

        :param content: Expected text
        :return: Raw ASCII content
        :rtypet: str
        """
        reply = self._tn.read_until(content.encode('ascii'))
        reply = Connection.ASNI_REGEX.sub('', reply.decode('ascii'))
        return reply

    def _send(self, content: str):
        """
        Sends the given content

        :param content: Content
        """
        self._tn.write(content.encode('ascii'))
