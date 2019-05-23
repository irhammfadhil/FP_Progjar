import sys
import os
import json
import uuid
from Queue import *

class Chat:
    def __init__(self):
        self.sessions = {}
        self.users = {}
        self.groups = {}
        self.users['messi'] = { 'nama': 'Lionel Messi', 'negara': 'Argentina', 'password': 'surabaya', 'incoming' : {}, 'outgoing': {} }
        self.users['henderson'] = { 'nama': 'Jordan Henderson', 'negara': 'Inggris', 'password': 'surabaya', 'incoming': {}, 'outgoing': {} }
        self.users['lineker'] = { 'nama': 'Gary Lineker', 'negara': 'Inggris', 'password': 'surabaya','incoming': {}, 'outgoing':{}}
        self.users['darke'] = { 'nama': 'Darke Foster', 'negara': 'Canada', 'password': 'prototype', 'incoming' : {}, 'outgoing': {} }
        
    def proses(self, data, connection):
        j = data.split(" ")
        try:
            command = j[0].strip()
            if (command == 'auth'):
                username = j[1].strip()
                password = j[2].strip()
                print "Authenticating {}" . format(username)
                return self.autentikasi_user(username,password)
            elif (command == 'send'):
                sessionid = j[1].strip()
                usernameto = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = "{} {}" .format(message, w)
                usernamefrom = self.sessions[sessionid]['username']
                print "send message from {} to {}" . format(usernamefrom, usernameto)
                return self.send_message(sessionid, usernamefrom, usernameto, message)
            elif (command == 'inbox'):
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                print "inbox {}" . format(sessionid)
                return self.get_inbox(username)
            elif (command == 'logout'):
                sessionid = j[1].strip()
                if (sessionid in self.sessions):
                    del self.sessions[sessionid]
                return {'status' : 'OK'}
            elif (command == 'create_group'):
                group = j[1].strip()
                sessionid = j[2].strip()
                print "creating group {}..." . format(group)
                return self.create_group(group, sessionid)
            elif (command == 'join_group'):
                group = j[1].strip()
                sessionid = j[2].strip()
                print "{} is joining {}..." . format(self.sessions[sessionid]['username'], group)
                return self.join_group(group, sessionid)
            elif (command == 'send_group'):
                group = j[1].strip()
                sessionid = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = "{} {}" .format(message, w)
                print "{} is sending message to group : {}" . format(self.sessions[sessionid]['username'], group)
                return self.send_group(group, sessionid, message)
            elif (command == 'inbox_group'):
                group = j[1].strip()
                sessionid = j[2].strip()
                print "inbox_group {}" . format(group)
                return self.inbox_group(group, sessionid)
            elif (command == 'leave_group'):
                group = j[1].strip()
                sessionid = j[2].strip()
                print "{} is leaving {}..." . format(self.sessions[sessionid]['username'],group)
                return self.leave_group(group, sessionid)
            elif (command == 'sendfile'):
				sessionid = j[1].strip()
				usernameto = j[2].strip()
				filename = j[3].strip()
				usernamefrom = self.sessions[sessionid]['username']
				print "sending file from {} to {}" . format(usernamefrom, usernameto)
				return self.sendfile(sessionid, usernamefrom, usernameto, filename, connection)
            elif (command == 'recvfile'):
				sessionid = j[1].strip()
				filename = j[2].strip()
				usernamefrom = self.sessions[sessionid]['username']
				print "{} is downloading {}" . format(usernamefrom, filename)
				return self.recvfile(sessionid, filename, connection)
            elif (command == 'sendfile_group'):
				group = j[1].strip()
				sessionid = j[2].strip()
				filename = j[3].strip()
				usernamefrom = self.sessions[sessionid]['username']
				print "sending file from {} to {}" . format(usernamefrom, group)
				return self.sendfile_group(sessionid, usernamefrom, group, filename, connection)
            elif (command == 'recvfile_group'):
				group = j[1].strip()
				sessionid = j[2].strip()
				filename = j[3].strip()
				usernamefrom = self.sessions[sessionid]['username']
				print "{} is downloading file from {}" . format(usernamefrom, group)
				return self.recvfile_group(sessionid, group, filename, connection)
            else:
                return {'status' : 'ERROR', 'message' : '**Protocol Tidak Benar'}
        except IndexError:
            return {'status' : 'ERROR', 'message' : '--Protocol Tidak Benar'}
    
    def autentikasi_user(self, username, password):
        if(username not in self.users):
            return {'status' : 'ERROR', 'message' : 'User Tidak Ada'}
        if(self.users[username]['password'] != password):
            return {'status' : 'ERROR', 'message' : 'Password Salah'}
        tokenid = str(uuid.uuid4())
        self.sessions[tokenid] = { 'username' : username, 'userdetail' : self.users[username]}
        return {'status' : 'OK', 'tokenid' : tokenid}
    
    def get_user(self, username):
        if(username not in self.users):
            return False
        return self.users[username]
    
    def send_message(self, sessionid, username_from, username_dest, message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_dest)
        
        if (s_fr == False or s_to == False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
        message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = s_to['incoming']
        try:
            outqueue_sender[username_from].put(message)
        except KeyError:
            outqueue_sender[username_from] = Queue()
            outqueue_sender[username_from].put(message)
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from] = Queue()
            inqueue_receiver[username_from].put(message)
        return {'status': 'OK', 'message': 'Message Sent'}

    def get_inbox(self, username):
        s_fr = self.get_user(username)
        incoming = s_fr['incoming']
        msgs = {}
        for users in incoming:
            msgs[users] = []
            while not incoming[users].empty():
                msgs[users].append(s_fr['incoming'][users].get_nowait())
        return {'status': 'OK', 'messages': msgs}
    
    def create_group(self, group_name, sessionid):
        if group_name in self.groups:
            return {'status': 'ERROR', 'message': 'Group sudah ada'}
        self.groups[group_name] = {'group_name':group_name, 'log':[], 'users':[]}
        creator = self.sessions[sessionid]['username']
        self.groups[group_name]['users'].append(creator)
        return {'status':'OK', 'message': self.groups[group_name]}

    def join_group(self, group_name, sessionid):
        if group_name not in self.groups:
            return {'status': 'ERROR', 'message': 'Group tidak ada'}
        username = self.sessions[sessionid]['username']
        if username in self.groups[group_name]['users']:
            return {'status': 'ERROR', 'message': 'Kamu sudah ada di grup'}
        self.groups[group_name]['users'].append(username)
        return {'status':'OK', 'message': 'Group joined successfully'}
    
    def send_group(self, group_name, sessionid, message):
        if group_name not in self.groups:
            return {'status': 'ERROR', 'message': 'Group tidak ada'}
        username = self.sessions[sessionid]['username']
        if username not in self.groups[group_name]['users']:
            return {'status': 'ERROR', 'message': 'Kamu tidak bergabung di grup'}
        self.groups[group_name]['log'].append({'from':username, 'message':message})
        return {'status':'OK', 'message': 'Message sent'}
    
    def inbox_group(self, group_name, sessionid):
        if group_name not in self.groups:
            return {'status': 'ERROR', 'message': 'Group tidak ada'}
        username = self.sessions[sessionid]['username']
        if username not in self.groups[group_name]['users']:
            return {'status': 'ERROR', 'message': 'Kamu tidak bergabung di grup'}
        return {'status':'OK', 'messages':self.groups[group_name]['log']}
    
    def leave_group(self, group_name, sessionid):
        if group_name not in self.groups:
            return {'status': 'ERROR', 'message': 'Group tidak ada'}
        username = self.sessions[sessionid]['username']
        if username not in self.groups[group_name]['users']:
            return {'status': 'ERROR', 'message': 'Kamu tidak bergabung di grup'}
        self.groups[group_name]['users'].remove(username)
        return {'status':'OK', 'message':'You left the group'}
    
    def sendfile(self, sessionid, username_from, username_dest, filename, connection):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)

		if (s_fr==False or s_to==False):
			return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

		try:
			if not os.path.exists(username_dest):
				os.makedirs(username_dest)
			with open(os.path.join(username_dest, filename), 'wb') as file:
				while True:
					data = connection.recv(1024)
					print data
					if(data[-4:] == 'DONE'):
						data = data[:-4]
						file.write(data)
						break
					file.write(data)
				file.close()
		except IOError:
			raise

		message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': 'sent/received {}' . format(filename) }
		outqueue_sender = s_fr['outgoing']
		inqueue_receiver = s_to['incoming']
		try:
			outqueue_sender[username_from].put(message)
		except KeyError:
			outqueue_sender[username_from]=Queue()
			outqueue_sender[username_from].put(message)
		try:
			inqueue_receiver[username_from].put(message)
		except KeyError:
			inqueue_receiver[username_from]=Queue()
			inqueue_receiver[username_from].put(message)

		return {'status': 'OK', 'message': 'File sent'}

    def recvfile(self, sessionid, filename, connection):
		username = self.sessions[sessionid]['username']
		print "{} is downloading {}" . format(username, filename)

		try:
			file = open(os.path.join(username, filename), 'rb')
		except IOError:
			return {'status': 'Err', 'message': 'File not found'}
			
		result = connection.sendall("OK")
		while True:
			data = file.read(1024)
			if not data:
				result = connection.sendall("DONE")
				break
			connection.sendall(data)
		file.close()
		return
    
    def sendfile_group(self, sessionid, username_from, group_name, filename, connection):
		if group_name not in self.groups:
			return {'status': 'ERROR', 'message': 'Group tidak ada'}
		if username_from not in self.groups[group_name]['users']:
			return {'status': 'ERROR', 'message': 'Kamu tidak bergabung di grup'}

		try:
			if not os.path.exists(group_name):
				os.makedirs(group_name)
			with open(os.path.join(group_name, filename), 'wb') as file:
				while True:
					data = connection.recv(1024)
					print data
					if(data[-4:] == 'DONE'):
						data = data[:-4]
						file.write(data)
						break
					file.write(data)
				file.close()
		except IOError:
			raise

		return {'status': 'OK', 'message': 'File sent'}

    def recvfile_group(self, sessionid, group_name, filename, connection):
        if group_name not in self.groups:
			return {'status': 'ERROR', 'message': 'Group tidak ada'}
        username = self.sessions[sessionid]['username']
        if username not in self.groups[group_name]['users']:
			return {'status': 'ERROR', 'message': 'Kamu tidak bergabung di grup'}
		
        print "{} is downloading {}" . format(username, filename)

        try:
			file = open(os.path.join(os.getcwd(), group_name, filename), 'rb')
        except IOError:
			return {'status': 'Err', 'message': 'File not found'}
			
        result = connection.sendall("OK")
        while True:
			data = file.read(1024)
			if not data:
				result = connection.sendall("DONE")
				break
			connection.sendall(data)
        file.close()
        return

if __name__=="__main__":
    j = Chat()
    sesi = j.proses("auth messi surabaya")
    print sesi
    #sesi = j.autentikasi_user('messi','surabaya')
    #print sesi
    tokenid = sesi['tokenid']
    print j.proses("send {} henderson hello gimana kabarnya son " . format(tokenid))
    #print j.send_message(tokenid,'messi','henderson','hello son')
    #print j.send_message(tokenid,'henderson','messi','hello si')
    #print j.send_message(tokenid,'lineker','messi','hello si dari lineker')
    
    print j.get_inbox('messi')
    