import sys
import os.path
import uuid
from glob import glob
from datetime import datetime
from datetime import timedelta

class HttpServer:
    def __init__(self):
        self.sessions={}
        self.types={}
        self.types['.pdf']='application/pdf'
        self.types['.jpg']='image/jpeg'
        self.types['.txt']='text/plain'
        self.types['.html']='text/html'
        self.types['.png']='image/png'
    def response(self,kode=404,message='Not Found',messagebody='',headers={}):
        tanggal = datetime.now().strftime('%c')
        resp=[]
        resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
        resp.append("Date: {}\r\n" . format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n" . format(len(messagebody)))
        for kk in headers:
            resp.append("{}:{}\r\n" . format(kk,headers[kk]))
        resp.append("\r\n")
        resp.append("{}" . format(messagebody))
        response_str=''
        for i in resp:  
            response_str="{}{}" . format(response_str,i)
        return response_str

    def proses(self,data):
        
        requests = data.split("\r\n")
        baris = requests[0]

        print baris
        j = baris.split(" ")
        try:
            method=j[0].upper().strip()
            if (method=='GET'):
                object_address = j[1].strip()
                return self.http_get(object_address)
            elif(method == 'OPTIONS'):
                return self.http_option()
            elif (method == "POST"):
                obj = j[1].strip()
                return self.http_post(requests[-1])
            elif (method == "HEAD"):
                obj = j[1].strip()
                return self.http_head(obj)
            else:
                return self.response(400,'Bad Request','',{})
        except IndexError:
            return self.response(400,'Bad Request','',{})
    
    def http_option (self):
        """
        HTTP/1.1 204 No Content
        Allow: OPTIONS, GET, HEAD, POST
        Cache-Control: max-age=604800
        Date: Thu, 13 Oct 2016 11:45:00 GMT
        Expires: Thu, 20 Oct 2016 11:45:00 GMT
        Server: EOS (lax004/2813)
        x-ec-custom-error: 1
        """
        tanggal = datetime.now().strftime('%c')
        resp=[]
        resp.append("HTTP/1.0 {} {}\r\n" . format(204,"No Content"))
        resp.append("Allow: OPTION, GET, HEAD, POST\r\n")
        resp.append("Cache-Control: max-age=604800")
        resp.append("Date: {}\r\n" . format(tanggal))
        resp.append("Expires: {}\r\n" . format((datetime.now()+ timedelta(days=7)).strftime('%c')))
        resp.append("Server: myserver/1.0\r\n")
        resp.append("\r\n")
        response_str=''
        for i in resp:  
            response_str="{}{}" . format(response_str,i)
        return response_str
    
    def http_head(self,object_address):
        files = glob('./*')
        thedir='.'
        if thedir+object_address not in files:
            return self.response(404,'Not Found','',{})
        fp = open(thedir+object_address,'r')
        isi = fp.read()
        fext = os.path.splitext(thedir+object_address)[1]
        content_type = self.types[fext]
        
        headers={}
        headers['Content-type']=content_type
        tanggal = datetime.now().strftime('%c')
        
        kode = 200
        message = 'OK'
        
        resp=[]
        resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
        resp.append("Date: {}\r\n" . format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n" . format(len(isi)))
        for kk in headers:
            resp.append("{}:{}\r\n" . format(kk,headers[kk]))
        resp.append("\r\n")
        resp.append("{}" . format(""))
        response_str=''
        for i in resp:  
            response_str="{}{}" . format(response_str,i)
        return response_str

    
    def http_get(self,object_address):
        files = glob('./*')
        thedir='.'
        if thedir+object_address not in files:
            return self.response(404,'Not Found','',{})
        fp = open(thedir+object_address,'r')
        isi = fp.read()
        
        fext = os.path.splitext(thedir+object_address)[1]
        content_type = self.types[fext]
        
        headers={}
        headers['Content-type']=content_type
        
        return self.response(200,'OK',isi,headers)
    
    def http_post(self, obj):
        print "content posted : "+ obj
        
                
#>>> import os.path
#>>> ext = os.path.splitext('/ak/52.png')

if __name__=="__main__":
    httpserver = HttpServer()
    d = httpserver.proses('GET testing.txt HTTP/1.0')
    print d
    d = httpserver.http_get('testing2.txt')
    print d
    d = httpserver.http_get('testing.txt')
    print d















