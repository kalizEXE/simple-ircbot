import socket, sys, argparse
from time import gmtime, strftime, sleep
from multiprocessing import Process, Queue, JoinableQueue, Lock
from multiprocessing.sharedctypes import Array
from queue import Empty
import logging as log
from ctypes import c_char_p, Structure

log.basicConfig( level=log.DEBUG,
    format='[%(levelname)s] - %(threadName)-10s : %(message)s')

class Point(Structure):
	_fields_ = [('target', c_char_p), ('host', c_char_p)]

class Bot(object):
	"""docstring for Bot"""
	def __init__(self):
		super(Bot, self).__init__()
		self.nick = 'genove21'
		self.serverIrc = 'chat.oftc.net',6667
		self.channel = '#Genove23C_M_D'
		self.sockIRC = None
		self.exitcode = 'bye '+self.nick
		self.timecode = 'time '+self.nick
		self.userscode = 'users '+self.nick

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
			asnwer = self.sockIRC.recv(2048).decode('utf-8').strip('\n\r')
			log.debug(asnwer)

class Genove23(Bot):
	"""docstring for Genove23"""
	def __init__(self):
		super(Genove23, self).__init__()
		self.admin = None
		self.queue = JoinableQueue()
		self.exitQ = Queue()
		self.lock = Lock()
		self.target = Array(Point,[(str('').encode('utf-8'),str('').encode('utf-8'))],lock=self.lock)

	def exitbot(self):
		self.sendMsg('Ok ... f u ... bye!', self.channel)
		self.sockIRC.send(bytes('QUIT \n','utf-8'))
		self.exitQ.put(None)
		self.proc.join()

	def recvproc(self):
		def do_recv():
			asnwer = self.sockIRC.recv(2048).decode('utf-8')
			nstripAnswer = asnwer
			asnwer = asnwer.strip('\n\r')
			if asnwer.find('PING :') != -1: self.ping()
			elif asnwer.find('PRIVMSG') != -1:
				name = asnwer.split('!',1)[0][1:]
				msg = asnwer.split('PRIVMSG',1)[1].split(':',1)[1]
				log.debug(name)
				log.debug(msg)
				self.queue.put((name,msg))
			else:
				if asnwer.find('End of /NAMES list.')!= -1:
					lusers = nstripAnswer.split(':')[2].strip('\n\r').split(' ')
					log.debug(lusers)
				elif asnwer.find('End of /WHOIS list.')!= -1:
					data = nstripAnswer.split(':')
					data = [line.strip('\n\r') for line in data]
					data = data[7].split(' ')[3:]
					target = data[0]
					host = data[1]
					self.target[0].target = str(target).encode('utf-8')
					self.target[0].host = str(host).encode('utf-8')
					self.sendMsg(target+' tu host es '+host+' !!!',self.channel)
		while True:
			try:
				pill = self.exitQ.get_nowait()
				if pill == None:
					break
			except Empty:
				do_recv()
				sleep(.01)

	def newbot(self,admin,server=None,channel=None,nick=None):
		if server is not None : self.serverIrc = server
		if channel is not None : self.channel = channel
		if nick is not None : self.nick = nick
		self.admin = admin[0]
		self.connect()
		self.joinCh(self.channel)
		self.proc = Process(target=self.recvproc)
		self.proc.start()
		self.sendMsg('Buenas '+self.channel+'!!!',self.channel)
		self.loop()

	def loop(self):

		while True:
			try:
				asnwer = self.queue.get()
				name, msg = asnwer
				if len(name)<17:
					#ORDERS HERE ...
					if msg.find('Hola '+self.nick) != -1:
						self.sendMsg('Buenas '+name+'!',self.channel)
					if msg[:5].find('.tell') != -1:
						target = msg.split(' ',1)[1]
						if target.find(' ') != -1:
							msg = target.split(' ',1)[1]
							target = target.split(' ')[0]
						else:
							target = name
							msg = 'Error.... :('
						self.sendMsg(msg,target)
					if msg.find('.whois') != -1:
						target = msg.split(' ',1)[1]
						self.sockIRC.send(bytes('WHOIS '+target+' \n','utf-8'))
					if name.lower() == self.admin.lower() and msg.rstrip() == self.exitcode:
						self.queue.task_done()
						self.exitbot()
						break
					elif name.lower() == self.admin.lower() and msg.rstrip() == self.timecode:
						time_now=strftime("%H:%M:%S del %d-%m-%Y", gmtime())
						self.sendMsg('Son las '+time_now+' !!!',self.channel)
					elif name.lower() == self.admin.lower() and msg.rstrip() == self.userscode:
						self.sockIRC.send(bytes('NAMES '+self.channel+' \n','utf-8'))
				self.queue.task_done()
			except Empty:
				sleep(0.01)

if __name__ == '__main__':
	g = Genove23()
	parser = argparse.ArgumentParser(description="Manage Bot",add_help=True)
	add_parser = parser.add_argument("-a", type=str, nargs=1)
	args = parser.parse_args()
	g.newbot(args.a)
