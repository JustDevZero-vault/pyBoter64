#! /usr/bin/env python
#*.*coding:utf-8*.*
#
# Example program using ircbot.py.
#
# Joel Rosdahl <joel@rosdahl.net>

#       pyboter64.py written in python2.8
#       version 1.1
#       Copyright 2010 Mephiston <meph.snake@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3.0 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, get a copy on http://www.gnu.org/licenses/gpl.txt

#   ---------------- Generic utilities ---------------- #
#   A usefull an fun bot for irc using python-irclib, and ircbot of Joel Rosdahl <joel@rosdahl.net> as base.

"""A example bot.

This is an example bot that uses the SingleServerIRCBot class from
ircbot.py.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.
It also responds to DCC CHAT invitations and echos data sent in such
sessions.

The known commands are:

    stats -- Prints some channel information.

    disconnect -- Disconnect the bot.  The bot will try to reconnect
                  after 60 seconds.

    die -- Let the bot cease to exist.

    dcc -- Let the bot invite you to a DCC CHAT connection.
"""
#import ircbot
from ircbot import SingleServerIRCBot
from datetime import date

#print dir(ircbot)
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
from random import shuffle
from string import lowercase
from httplib import HTTPConnection
#import irclib
#print dir(irclib)

class TestBot(SingleServerIRCBot):
    def __init__(self, channel, varNickname, varServer, varPort=6667):
        SingleServerIRCBot.__init__(self, [(varServer, varPort)], varNickname, varNickname)
        self.channel = channel

    def on_nicknameinuse(self, varChat, varEvent):
        varChat.nick(varChat.get_nickname() + "_")

    def on_welcome(self, varChat, varEvent):
        varChat.join(self.channel)

    def on_privmsg(self, varChat, varEvent):
        self.do_command(varEvent, varEvent.arguments()[0])

    def on_pubmsg(self, varChat, varEvent):
        a = varEvent.arguments()[0].split(":", 1)
        #if len(a) > 1 and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
            #self.do_command(varEvent, a[1].strip())
        self.do_command(varEvent, a[0].strip())
        return

    def on_dccmsg(self, varChat, varEvent):
        varChat.privmsg("Has dicho: " + varEvent.arguments()[0])

    def on_dccchat(self, varChat, varEvent):
        if len(varEvent.arguments()) != 2:
            return
        args = varEvent.arguments()[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                varPort = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, varPort)

    def do_command(self, varEvent, cmd):
        nick = nm_to_n(varEvent.source())
        varChat = self.connection
        varSay=(nick+ ": "+"".join(varEvent.arguments()[0].split(":", 1))).split()

        if cmd == "!desconecta":
            self.disconnect()
        elif cmd.lower() == "hola":
            print cmd
            varChat.privmsg( self.channel, "Muy buenas!")
        elif cmd == "!muere" and nick=="mephiston":
            listMuertes = ['Como no me he preocupado de nacer, no me preocupo de morir.',
            'Que triste, tan joven y muero por un comando.',
            'Dicen que la muerte solo llega una vez, pero ya llevo unas cuantas.',
            'Te arrepentiras de que no este... creeme.',
            'A mi puta casa me voy, nadie me quiere.',
            'La muerte llama, uno a uno, a todos los hombres y a las mujeres todas, sin olvidarse de ninguno, yo soy un bot, porque tengo que morir?',
            'La muerte es dulce, si tu no eres el caido, o es a manos de una bella.',
            'La muerte, es aqui donde la veis, el estallido orgasmico de la vida',
            'Miedo a la muerte? Uno no debe temerle a la muerte, si no a la vida.',
            'La muerte es un castigo para algunos, para otros un regalo, y para muchos un favor.'
            'Mi muerte es como una amarga piruleta, yo no la vivire, pero vosotros la recordareis']
            shuffle(listMuertes)
            varChat.privmsg( self.channel, "%s" % (listMuertes[0]))
            self.die()
        elif cmd == "!estado":
            for chname, chobj in self.channels.items():
                varChat.notice(nick, "--- Estadisticas del canal ---")
                varChat.notice(nick, "Channel: " + chname)
                users = chobj.users()
                users.sort()
                varChat.notice(nick, "Usuarios: " + ", ".join(users))
                opers = chobj.opers()
                opers.sort()
                varChat.notice(nick, "Operadores: " + ", ".join(opers))
                voiced = chobj.voiced()
                voiced.sort()
                varChat.notice(nick, "Voz: " + ", ".join(voiced))
        elif cmd == "!VERSION":
            dcc = self.dcc_listen()
            varChat.ctcp("VERSION", nick, "pyBoter64 Python IRC %s %d" % (
                ip_quad_to_numstr(dcc.localaddress),
                dcc.localport))
        elif cmd == "!rodadora":
            varChat.privmsg( self.channel, "."*6+"@")
            varChat.privmsg( self.channel, "."*12+"@")
            varChat.privmsg( self.channel, "."*18+"@")
            varChat.privmsg( self.channel, "."*24+"@")
        elif "!imagen" in varSay:
            if len(varSay) <3:
                varChat.privmsg( self.channel, "Por favor, especifica sobre que quieres buscar imágenes. Ejemplo: !imagen Python")
            else:
                imagen=varSay[2]
                varChat.privmsg( self.channel, "http://images.google.es/images?um=1&q=es&q="+imagen+"&btnG")
        elif cmd == "!año":
            now = date.today()
            newyear = date(2010, 12, 31)
            cik = newyear - now
            restdays = cik.days
            varChat.privmsg( self.channel, "Faltan "+str(restdays)+" días para fin de año")
        elif "!wiki" in varSay:
            if len(varSay) <3:
                varChat.privmsg( self.channel, " ¡Error! Debes especificar que quieres buscar Ejemplo: !wiki Linux")
            else:
                print varSay[2:]
                #imagen=varSay[2]
                busqueda=[]
                for x in varSay[2:]:
                    busqueda.append(x)
                    busqueda.append("+")
                final=len(busqueda)-1
                varChat.privmsg( self.channel, "http://es.wikipedia.org/w/index.php?title=Especial%3ABuscar&search="+"".join(busqueda[:final])+"&go=Ir")
        else:
            #varChat.notice(nick, "Comando no encontrado: " + "".join(varEvent.arguments()[0].split(":", 1)))
            print (nick+ ": "+"".join(varEvent.arguments()[0].split(":", 1)))

def main():
    import sys
    if len(sys.argv) != 4:
        print "Usage: testbot <server[:port]> <channel> <nickname>"
        sys.exit(1)

    varSystem = sys.argv[1].split(":", 1)
    varServer = varSystem[0]
    if len(varSystem) == 2:
        try:
            varPort = int(varSystem[1])
        except ValueError:
            print "Error: Puerto erroneo."
            sys.exit(1)
    else:
        varPort = 6667
    channel = sys.argv[2]
    varNickname = sys.argv[3]

    bot = TestBot(channel, varNickname, varServer, varPort)
    bot.start()

if __name__ == "__main__":
    main()
