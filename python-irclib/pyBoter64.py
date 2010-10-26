#! /usr/bin/env python
#*.*coding:utf-8*.*
#
# Example program using ircbot.py.
#
# Joel Rosdahl <joel@rosdahl.net>

#       pyboter64.py written in python2.8
#       version 2.64
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
PDO_FLAG = True
try:
    from ircbot import SingleServerIRCBot
except:
    print "python-ircbot Not found."
try:
    from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
except:
    print "python-irclib Not found."
try:
    from httplib import HTTPConnection
except:
    print "python-httplib Not found."
try:
    import pdo
except:
    PDO_FLAG = False
    print "python-pdo Not found."
    
try:
    from BeautifulSoup import BeautifulSoup
except:
    print "python-beautifulsoup Not found"
    
from datetime import date, datetime
from time import time, asctime, localtime, strftime, sleep
from random import shuffle
from string import lowercase
from urllib import urlencode, urlopen
from sys import argv, exc_info
from traceback import format_exc
#import irclib


#~ VARIABLES
VERSION = '2.64'
DEBUG = 1
#~ if PDO_FLAG == True:
    #~ DB = pdo.connect("Module=MySQLdb;User=pyboter;Passwd=pyboter1.0;DB=pyboter;host=localhost")
    
class TestBot(SingleServerIRCBot):
    def __init__(self, channel, varNickname, varPassword, varServer, varPort=6667):
        SingleServerIRCBot.__init__(self, [(varServer, varPort)], varNickname, varNickname)
        self.channel = channel
        self.NickName = varNickname
        self.password = varPassword
        self.flood = {}
        self.previousNick = ''
        self.details = {
            "status": 0,
            "select_nick": "SELECT `perm` FROM `users` WHERE `nick`='%s' AND `password`='%s' AND (%s) LIMIT 1",
            "insert_nick": "INSERT IGNORE INTO `users` (`nick`,`password`,`perm`) values('%s', '%s', '%s');",
            "delete_nick": "DELETE FROM `%s` WHERE `nick`='%s';",
            "update_nick": "UPDATE `users` SET `password`='%s' WHERE `nick`='%s';",
            "quote": "SELECT `texts` FROM `quotes` WHERE `type`='%.1s' ORDER BY RAND() LIMIT 1,1;",
            "owners": ["mephiston", "meph"],
            "owned": False
        }
        self.log=''
        
        
    def sql_on(self, varChat, varEvent):
        global conn
        details["status"]=1
        db=pdo.connect("Module=MySQLdb;User=pyboter;Passwd=pyboter1.0;DB=pyboter;host=localhost")
        varChat.privmsg( self.channel, "La conexión con SQL esta apagada.")
    
    def sql_off(self, varChat, varEvent):
        details["status"]=0
        try:
            db.close()
            varChat.privmsg( self.channel, "La conexión con SQL esta apagada.")
        except:
            return False
            
    def show_credits(self, varChat, varEvent):
        actual_time = asctime(localtime())
        ch_active = varEvent.target()
        varChat.privmsg( ch_active, "%s" % actual_time)
        varChat.privmsg( ch_active, "Este bot está enteramente creado en Python y PDO.")
        varChat.privmsg( ch_active, "Un experimento para demostrar el potencial de Python.")
        varChat.privmsg( ch_active, "Creado por Daniel Ripol (Mephiston).")
        varChat.privmsg( ch_active, "En fecha: 19 de Setiembre de 2010.")
        varChat.privmsg( ch_active, "Agradecimientos a: Choms, vgvgf, galrunch, y Dahrkael.")
        self.log+=ch_active+" "+strftime("(%Y-%m-%d %H:%M:%S) ",localtime(time()))+self.NickName+"Este bot está enteramente creado en Python y PDO. Un experimento para demostrar el potencial de Python. Creado por Daniel Ripol (Mephiston). En fecha: 19 de Setiembre de 2010. Agradecimientos a: Choms, vgvgf, galrunch, y Dahrkael.\n"
        
    def show_version(self, varChat, varEvent):
        dcc = self.dcc_listen()
        nick = nm_to_n(varEvent.source())
        varChat.ctcp("VERSION", nick, "pyBoter 2.64 Python IRC %s %d" % (
            ip_quad_to_numstr(dcc.localaddress),
            dcc.localport))
            
    def show_image(self, varChat, varEvent):
        ch_active = varEvent.target()
        varSentence="".join(varEvent.arguments()[0].split(":", 1)).split()
        if len(varSentence) <2:
            mens="Por favor, especifica sobre que quieres buscar imágenes. Ejemplo: !imagen Python"
            varChat.privmsg( ch_active, mens)
            self.log+=ch_active+" "+strftime("(%Y-%m-%d %H:%M:%S) ",localtime(time()))+self.NickName+mens+"\n"
        else:
            for imagen in varSentence[1:]:
                soup = BeautifulSoup((urlopen("http://www.flickr.com/badge_code_v2.gne?%s&tag=%s" % (urlencode({'count': 1, 'display': "popular", 'size': "m", "layout":"x", "source":"all_tag"}), imagen))).read())
                try:
                    soaped = soup.findAll("div",id="flickr_badge_image1")[0].findAll("img")[0]["src"].replace("_m.jpg",".jpg")
                except IndexError:
                    soaped = "Lo siento, no puedo encontrar fotos de %s, si quieres busca tí en Google: " % imagen
                    try:
                        soaped+=" http://images.google.es/images?um=1&q="+imagen+"&btnG"
                    except:
                        exc_type, exc_value, exc_traceback = exc_info()
                        formatted_lines = format_exc().splitlines()
                        print " ".join(formatted_lines)
                varChat.privmsg( ch_active, "%s" % soaped)
                self.log+=ch_active+" "+strftime("(%Y-%m-%d %H:%M:%S) ",localtime(time()))+self.NickName+soaped+"\n"
            
    def on_nicknameinuse(self, varChat, varEvent):
        varChat.nick(varChat.get_nickname() + "_")

    def on_welcome(self, varChat, varEvent):
        varChat.join(self.channel)
        if  self.password != False:
            varChat.privmsg( "NickServ", "IDENTIFY %s %s" % (self.NickName, self.password))
        mens='he llegado para serviros'
        varChat.privmsg( self.channel, mens)
        for chann in self.channel.split(','):
            self.log+=chann+" "+strftime("(%Y-%m-%d %H:%M:%S) ",localtime(time()))+self.NickName+mens+"\n"

    def on_privmsg(self, varChat, varEvent):
        self.do_command(varEvent, varEvent.arguments()[0])
        #~ varSentence="".join(varEvent.arguments()[0].split(":", 1)).split()

    def on_pubmsg(self, varChat, varEvent):
        a = varEvent.arguments()[0].split(":", 1)
        #if len(a) > 1 and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
            #self.do_command(varEvent, a[1].strip())
        self.do_command(varEvent, a[0].strip())
        return
        
    def show_status(self, varChat, varEvent):
        nick = nm_to_n(varEvent.source())
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
            
    def on_dccmsg(self, varChat, varEvent):
        varChat.privmsg("Has dicho: " + varEvent.arguments()[0])
        
    def say_hello(self, varChat, varEvent):
        varChat.privmsg( varEvent.target(), "Muy buenas!")
        self.log+=varEvent.target()+" "+strftime("(%Y-%m-%d %H:%M:%S)",localtime(time()))+self.NickName+"Muy buenas!\n"
        
    def to_end_year(self, varChat, varEvent):
        ch_active = varEvent.target()
        now = date.today()
        newyear = date(2010, 12, 31)
        cik = newyear - now
        restdays = cik.days
        mens="Faltan %s días para fin de año" % str(restdays)
        varChat.privmsg( ch_active, mens )
        self.log+=ch_active+" "+strftime("(%Y-%m-%d %H:%M:%S)",localtime(time()))+self.NickName+mens+"\n"
        
    def show_rodadora(self, varChat, varEvent):
        ch_active = varEvent.target()
        varChat.privmsg( ch_active, "."*6+"@")
        varChat.privmsg( ch_active, "."*12+"@")
        varChat.privmsg( ch_active, "."*18+"@")
        varChat.privmsg( ch_active, "."*24+"@")
        active_time = strftime("(%Y-%m-%d %H:%M:%S) ",localtime(time()))
        self.log+=active_time+self.NickName+"."*6+"@"+"\n"+active_time+self.NickName+"."*12+"@"+"\n"+active_time+self.NickName+"."*18+"@"+"\n"+active_time+self.NickName+"."*24+"@\n"

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
        ch_active = varEvent.target()
        varSentence="".join(varEvent.arguments()[0].split(":", 1)).split()
        varSay=nick+ ": "+" ".join(varSentence)

        timeline=ch_active+' '+strftime("(%Y-%m-%d %H:%M:%S) ",localtime(time()))+"".join(varSay)
        self.log+=timeline+"\n"
        print timeline
        #~ print len(varSentence)
        if varSentence[0][0] == '!':
            if self.flood.has_key(nick):
                sleep(1)
                self.flood[nick] = 0
            else:
                 self.flood[nick] = 1
            print self.flood
            if cmd == '!credits':
                self.show_credits(varChat, varEvent)
            if varSentence[0] == '!imagen':
                self.show_image(varChat, varEvent)
            #~ if 'mephiston' in varSentence:
                #~ varChat.privmsg( ch_active, 'Esta ausente, así que dudo que os conteste.')
            elif cmd == '!endyear':
                self.to_end_year(varChat, varEvent)
            elif cmd == '!rodadora':
                self.show_rodadora(varChat, varEvent)
            elif cmd == '!print':
                print self.log
                self.log=''
            else:
                varChat.notice(nick, "Not understood: " + cmd)
            

def main():
    import sys
    if len(sys.argv) not in [4,5]:
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
    if len(sys.argv) == 5:
        varPassword = sys.argv[4]
        bot = TestBot(channel, varNickname, varPassword, varServer, varPort)
    else:
        varPassword=False
        bot = TestBot(channel, varNickname, varPassword, varServer, varPort)
    bot.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Interrumpido por teclado"
