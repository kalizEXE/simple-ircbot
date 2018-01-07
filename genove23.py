import socket, sys

class Bot(object):
	def __init__(self):
		super(Bot, self).__init__()
		self.nick = 'genove23'
		self.serverIrc = 'chat.oftc.net',6667
		self.channel = '#Genove23C_M_D'
		self.sockIRC = None

	def connect(self):
		self.sockIRC = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sockIRC.connect(self.serverIrc)
		self.sockIRC.send(bytes('USER '+self.nick+' '+self.nick+' '+\
								self.nick+' '+self.nick+'\n','utf-8'))
		self.sockIRC.send(bytes('NICK '+self.nick+'\n','utf-8'))

	def sendMsg(self,msg,target):
		self.sockIRC.send(bytes('PRIVMSG '+target+' :'+msg+'\n','utf-8'))

	def ping(self):
		self.sockIRC.send(bytes('PONG :pingis\n', 'utf-8'))

	def joinCh(self,channel):
		self.sockIRC.send(bytes('JOIN '+channel+'\n','utf-8'))
		asnwer = ''
		while asnwer.find('End of /NAMES list') == -1:
			asnwer = self.sockIRC.recv(2048).decode('utf-8')
			asnwer = asnwer.strip('\n\r')
			print(asnwer)

class Genove23(Bot):
	def __init__(self):
		super(Genove23, self).__init__()
		self.admin = None

	def newbot(self,admin,server=None,channel=None,nick=None):
		if server is not None : self.serverIrc = server
		if channel is not None : self.channel = channel
		if nick is not None : self.nick = nick
		self.exitcode = 'bye '+self.nick
		self.admin = admin
		self.connect()
		self.joinCh(self.channel)
		self.sendMsg('Buenas '+self.channel+'!!!',self.channel)
		self.loop()

	def loop(self):

		while True:
			asnwer = self.sockIRC.recv(2048).decode('utf-8')
			asnwer = asnwer.strip('\n\r')
			if asnwer.find('PING :') != -1: self.ping()
			elif asnwer.find('PRIVMSG') != -1:
				name = asnwer.split('!',1)[0][1:]
				msg = asnwer.split('PRIVMSG',1)[1].split(':',1)[1]
				if len(name)<17:
					if name.lower() == self.admin.lower() and msg.rstrip() == self.exitcode:
						self.sendMsg('Ok ... f u ... bye!', self.channel)
						self.sockIRC.send(bytes('QUIT \n','utf-8'))
						break


		
if __name__ == '__main__':
	g = Genove23()
	g.newbot(sys.argv[1])
