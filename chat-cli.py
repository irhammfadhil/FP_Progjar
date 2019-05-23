import socket
import os
import json
import datetime

TARGET_IP = "127.0.0.1"
TARGET_PORT = 8889


class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid=""
    def proses(self,cmdline):
	j=cmdline.split(" ")
	try:
	    command=j[0].strip()
	    if (command=='auth'):
		username=j[1].strip()
		password=j[2].strip()
		return self.login(username,password)
	    elif (command=='send'):
		usernameto = j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
		return self.sendmessage(usernameto,message)
            elif (command=='inbox'):
                return self.inbox()
            elif (command=='logout'):
                return self.logout()
            elif(command=='create_group'):
                group = j[1].strip()
                return self.create_group(group)
            elif(command=='join_group'):
                group = j[1].strip()
                return self.join_group(group)
            elif(command=='send_group'):
                group = j[1].strip()
                message=""
                for w in j[2:]:
                    message="{} {}" . format(message, w)
                return self.sendmessage_group(group, message)
            elif(command=='inbox_group'):
                group = j[1].strip()
                return self.inbox_group(group)
            elif(command=='leave_group'):
                group = j[1].strip()
                return self.leave_group(group)
            elif(command=='sendfile'):
                usernameto = j[1].strip()
                filename = j[2].strip()
                return self.sendfile(usernameto, filename)
            elif(command=='recvfile'):
                filename = j[1].strip()
                return self.recvfile(filename)
            elif(command=='sendfile_group'):
                group = j[1].strip()
                filename = j[2].strip()
                return self.sendfile_group(group, filename)
            elif(command=='recvfile_group'):
                group = j[1].strip()
                filename = j[2].strip()
                return self.recvfile_group(group, filename)
	    else:
		return "*Maaf, command tidak benar"
	except IndexError:
	    return "-Maaf, command tidak benar"
    def sendstring(self,string):
        try:
            self.sock.sendall(string)
            receivemsg = ""
            while True:
                data = self.sock.recv(10)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data)
                    if receivemsg[-4:]=="\r\n\r\n":
                        return json.loads(receivemsg)
        except:
            self.sock.close()
    def login(self,username,password):
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
    def logout(self):
        if(self.tokenid==""):
            return "Your're not logged in."
        string = "logout {} \r\n" . format(self.tokenid) 
        result = self.sendstring(string)
        if result['status']=='OK':
            #print self.tokenid
            self.tokenid = ""
            return "Successfully logged out."
        else:
            return "500 Internal server error."
        
    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
    def inbox(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])
    def sendfile(self,usernameto,filename):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendfile {} {} {} \r\n" . format(self.tokenid,usernameto,filename)
        #print os.path.join(os.getcwd(),filename)
        self.sock.sendall(string)
        
        try:
            with open(os.path.join(os.getcwd(),filename), 'rb') as file:
                while True:
                    bytes = file.read(1024)
                    if not bytes:
                        result = self.sendstring("DONE")
                        break
                    self.sock.sendall(bytes)
                file.close()
        except IOError:
            return "Error, file not found"
        
        if result['status']=='OK':
            return "file sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
    def recvfile(self, filename):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="recvfile {} {} \r\n" . format(self.tokenid,filename)
        self.sock.sendall(string)
        
        data = self.sock.recv(1024)
        
        if data[:2]=='OK':
            print data
            now = datetime.datetime.now()
            seconds = (now - datetime.datetime(2019, 1, 1)).total_seconds()
            file =  open(str(int(seconds)) + filename, 'wb')
            if(file):
                file.write(data[2:])
                while True:
                    data = self.sock.recv(1024)
                    if(data[-4:] == 'DONE'):
                        data = data[:-4]
                        file.write(data)
                        break
                    file.write(data)
                file.close()
            else:
                return "Error, something happened"
        else:
            return "Error, file not found"
    def create_group(self, group_name):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="create_group {} {} \r\n" .format(group_name, self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['message']))
        else:
            return "Error, {}" . format(result['message'])
    def join_group(self, group_name):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="join_group {} {} \r\n" .format(group_name, self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['message']))
        else:
            return "Error, {}" . format(result['message'])
    def sendmessage_group(self, group_name, message):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send_group {} {} {} \r\n" .format(group_name, self.tokenid, message)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['message']))
        else:
            return "Error, {}" . format(result['message'])
    def inbox_group(self, group_name):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox_group {} {} \r\n" .format(group_name, self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])
    def leave_group(self, group_name):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="leave_group {} {} \r\n" .format(group_name, self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['message']))
        else:
            return "Error, {}" . format(result['message'])
    def sendfile_group(self, group_name, filename):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendfile_group {} {} {} \r\n" . format(group_name,self.tokenid,filename)
        self.sock.sendall(string)
        
        try:
            with open(os.path.join(os.getcwd(),filename), 'rb') as file:
                while True:
                    bytes = file.read(1024)
                    if not bytes:
                        result = self.sendstring("DONE")
                        break
                    self.sock.sendall(bytes)
                file.close()
        except IOError:
            return "Error, file not found"
        
        if result['status']=='OK':
            return "file sent to {}" . format(group_name)
        else:
            return "Error, {}" . format(result['message'])
    def recvfile_group(self, group_name, filename):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="recvfile_group {} {} {} \r\n" . format(group_name,self.tokenid,filename)
        self.sock.sendall(string)
        
        data = self.sock.recv(1024)
        
        if data[:2]=='OK':
            print data
            now = datetime.datetime.now()
            seconds = (now - datetime.datetime(2019, 1, 1)).total_seconds()
            file =  open(str(int(seconds)) + filename, 'wb')
            if(file):
                file.write(data[2:])
                while True:
                    data = self.sock.recv(1024)
                    if(data[-4:] == 'DONE'):
                        data = data[:-4]
                        file.write(data)
                        break
                    file.write(data)
                file.close()
            else:
                return "Error, something happened"
        else:
            return "Error, file not found"

if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = raw_input("Command {}:" . format(cc.tokenid))
        if(cmdline == 'exit'):
            print "Exiting program"
            break
        print cc.proses(cmdline)

