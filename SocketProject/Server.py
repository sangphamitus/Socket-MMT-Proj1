import json
import os
import socket
import requests
from urllib.request import urlopen
from requests.api import head, request
from requests.models import Response
from requests.structures import CaseInsensitiveDict
from datetime import datetime
import threading
import multiprocessing

from Client import Client_login
# ------ Assign const value -----

buffer = 2048 #buffer send and recv data

#Server IP and Port
ServerIP= '127.0.0.1'
ServePort=64234

# ------ Get data from api ------
def Get_time_and_day(): #get current time and date to dict
    
    #get current time and date
    now = datetime.now()
    date=datetime.today()

    # make dist of time and date
    current_time ={}
    current_date={}

    # assign value to time dict
    current_time['hour']=now.hour
    current_time['minute']=now.minute
    current_time['sec']=now.second

    # assign value to date dict
    current_date['day']=date.day
    current_date['month']=date.month
    current_date['year']=date.year

    return current_time ,current_date

def Get_API_key(): # get api key 
    
    # assign url get keys
    keys_url="https://vapi.vnappmob.com/api/request_api_key?scope=exchange_rate"
    
    #get key from url 
    response =urlopen(keys_url)
    data =json.loads(response.read())
    keys=data.get('results')
    
    return keys

def Get_data_API(keys): # use keys to get api's data

    # assign url of vcb
    url= "https://vapi.vnappmob.com/api/v2/exchange_rate/vcb"
    
    # make header of request message
    headers = CaseInsensitiveDict()
    headers["Accept"] ="application/json"
    headers["Authorization"]= "Bearer "+keys

    # get response data
    resp =requests.get(url,headers=headers)
    full_data = json.loads(resp.content)
    
    return full_data

def Save_data_to_Json(full_data,file_name="SocketProject\ExchangeCurrencyRate.json"): # save data to Json file

    # get time and date
    update_time, update_date=Get_time_and_day()
    full_data['update_time']=[update_date,update_time]

    # write data to json file
    with open(file_name,'w') as out_file:
        out_file.write(json.dumps(full_data,indent=2))
        out_file.close()

def Get_data_from_Json(file_name="SocketProject\ExchangeCurrencyRate.json"): # get data from save file
    
    #check if file exist or not
    if not os.path.isfile(file_name):
        Save_data_to_Json(full_data=Get_data_API(keys=Get_API_key()))

    # get data from file
    with open(file_name,'r') as file_in:
        response = json.load(file_in)
        file_in.close()

    return response

def Update_data(full_data): #Check and update data 
    
    #assign and get date and time
    response=full_data
    last_update_time = full_data.get('update_time')
    current_time,current_day=Get_time_and_day()
    
    #check if 30 minutes last or not
    if last_update_time[0].get('day')==current_day.get('day') and last_update_time[0].get('month')==current_day.get('month') and last_update_time[0].get('year')==current_day.get('year'):
        
        if last_update_time[1].get('hour')==current_time.get('hour'):
            
            if abs(int(last_update_time[1].get('minute')) - int(current_time.get('minute')))>=30:
                
                Save_data_to_Json(full_data=Get_data_API(keys=Get_API_key())) 
                response=Get_data_from_Json()
        else:

            Save_data_to_Json(full_data=Get_data_API(keys=Get_API_key())) 
            response=Get_data_from_Json()
    else:

        Save_data_to_Json(full_data=Get_data_API(keys=Get_API_key())) 
        response=Get_data_from_Json()  
    
    return response
    
def Find_currency(full_data,currency_name=None): #find currency in data

    full_data=Update_data(full_data)
    #get latest update time
    print(f"data_at_time: {full_data.get('update_time')}")
    update_time = f"{full_data.get('update_time')[0].get('day')}/{full_data.get('update_time')[0].get('month')}/{full_data.get('update_time')[0].get('year')} {full_data.get('update_time')[1].get('hour')}:{full_data.get('update_time')[1].get('minute')}:{full_data.get('update_time')[1].get('sec')}"
    
    #searching for currency name
    for object in full_data.get('results'):
        if(currency_name != None):
            if(object.get('currency')==currency_name):
                return object,update_time

    return None,update_time


# ----- Account -------
class Account():
  
    
    def __init__(self):
        self.url_file="SocketProject\Account.json"
        self.url_online_file="SocketProject\AccountLive.json"
        self.user=None
        self.pwd=None

    def SetUser(self,user): #recv login element
        self.user=user

    def SetPwd(self,pwd):
        self.pwd=pwd

    def Read_json_file(self,file_name): #read json file
        
        #create file when it not exist
        if not os.path.isfile(file_name):
            with open(file_name,'w') as out_file:
                if file_name == self.url_file:
                    out_file.write(json.dumps({"username":[],"pwd":[]},indent=2))
                    out_file.close()
                else:
                    out_file.write(json.dumps({"username":[],"pwd":[],"socket":[]},indent=3))
                    out_file.close()
        
        #read file
        try:
            with open(file_name,'r') as in_file:
                data =json.load(in_file)
                in_file.close()
        except:
            with open(file_name,'w') as out_file:
                if file_name == self.url_file:
                    out_file.write(json.dumps({"username":[],"pwd":[]},indent=2))
                    out_file.close()
                else:
                    out_file.write(json.dumps({"username":[],"pwd":[],"socket":[]},indent=3))
                    out_file.close()
            with open(file_name,'r') as in_file:
                data =json.load(in_file)
                in_file.close()
        return data

    def Register(self,All_account): #Register account
        
        try:

            #get position of account in list
            pos = All_account.get('username').index(self.user)

        except:

            #if not in list , add it
            All_account.get('username').append(self.user)
            All_account.get('pwd').append(self.pwd)

            #rewrite to file
            with open(self.url_file,'w') as out_file:
                out_file.write(json.dumps(All_account,indent=2))
                out_file.close()
            
            #Res success
            return True
        
        #Res failed
        return False
    
    def LogIn(self,All_Account): #login account (return 1 for success. 0:account not exist, 2:already onl)

        pos =None
        try:
            pos=All_Account.get('username').index(self.user)
        except:

            return 0 # account not exist
        
        if self.pwd ==All_Account.get('pwd')[pos]:

            #check if already onl yet
            Account_live = self.Read_json_file(self.url_online_file) 
            
            try :
                pos =Account_live.get('username').index(self.user)
            
            except:
                
                return 1 # login success
            
            return 2 #already onl
        
        else:

            return 0 #wrong password 

    def LogOut(self,client_sock,client_IP): #log out
        
        #get online data
        current_online=self.Read_json_file(self.url_online_file)

        try:
            pos=current_online.get('socket').index(str(client_IP[0])+str(client_IP[1]))
            current_online.get('username').remove(current_online.get('username')[pos])
            current_online.get('pwd').remove(current_online.get('pwd')[pos])
            current_online.get('socket').remove(str(client_IP[0])+str(client_IP[1]))
            with open(self.url_online_file,'w') as out_file:
                out_file.write(json.dumps(current_online,indent=3))
                out_file.close()
            
        except OSError as err:
            print(err)
        
    def LogIn_Success(self,client_sock,client_IP):
        
        #get file online account data
        current_online =self.Read_json_file(self.url_online_file)

        current_online.get('username').append(self.user)
        current_online.get('pwd').append(self.pwd)
        current_online.get('socket').append(str(client_IP[0])+str(client_IP[1]))
        #rewrite opened account file
        with open(self.url_online_file,'w') as out_file:
            out_file.write(json.dumps(current_online,indent=3))
            out_file.close()
    
    def Client_Login(self,client_sock,client_IP):
        while True :
            #get status login
            msg =client_sock.recv(buffer).decode('utf-8')
            msg = str(msg).split(',')
            # Status_login = client_sock.recv(buffer).decode('utf-8')
            # print(Status_login)
            
            # # recv login information
            # self.user=client_sock.recv(buffer).decode('utf-8')
            # self.pwd=client_sock.recv(buffer).decode('utf-8')
            Status_login = msg[0]
            self.user=msg[1]
            self.pwd=msg[2]
            All_account=self.Read_json_file(self.url_file)

            if Status_login == 'Res':

                if self.Register(All_account) == True:

                    self.LogIn_Success(client_sock,client_IP)
                    client_sock.sendall('Login success'.encode('utf-8'))
                    break
                else:
                    client_sock.sendall('Username already have'.encode('utf-8'))

            else:   

                if Status_login == 'Log':

                    Account_status= self.LogIn(All_account)

                    if Account_status == 1:
                        self.LogIn_Success(client_sock,client_IP)
                        client_sock.sendall('Login success'.encode('utf-8'))
                        break

                    if Account_status == 0:
                        client_sock.sendall('Wrong password or username'.encode('utf-8'))

                    if Account_status == 2:
                        client_sock.sendall('Account current online'.encode('utf-8'))
                
# ------ TCP server -------
class TCPSERVER(Account):

    # assign IP and Port 
    def __init__(self,IP,Port):
        self.IP=IP
        self.Port=Port
        self.sock=None
        super().__init__()
    #Print to screen
    def Print_to_Screen(self,msg):

        #get time and date
        current_time= datetime.now().strftime('%d-%m %H:%M:%S')
        print(f'[{current_time}] - recv: {msg}')

    def Send_currency_data(self,client_sock,object): # send currency data
    
        resp =f"{object.get('currency')},{object.get('buy_cash')},{object.get('buy_transfer')},{object.get('sell')},"
        # resp=f"{object.get('currency')} \0"
        # self.Print_to_Screen(resp)
        # client_sock.sendall(resp.encode('utf-8'))
        # resp=f"{object.get('buy_cash')} \0"
        # self.Print_to_Screen(resp)
        # client_sock.sendall(resp.encode('utf-8'))
        # resp=f"{object.get('buy_transfer')} \0"
        # self.Print_to_Screen(resp)
        # client_sock.sendall(resp.encode('utf-8'))
        # resp=f"{object.get('sell')} \0"
        # self.Print_to_Screen(resp)
        # client_sock.sendall(resp.encode('utf-8'))
        self.Print_to_Screen(resp)
        client_sock.sendall(resp.encode('utf-8'))

    def Config_server(self): # config server socket

        # creating socket TCP
        self.Print_to_Screen('Creating socket....')
        self.sock= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.Print_to_Screen('Socket created')

        #binding socket
        self.sock.bind((self.IP,self.Port))

        self.Print_to_Screen('Finished Config_server')

    def Wait_for_Client(self): # Client listen
        
        # listen and accept connection
        self.sock.listen(1)
        client_sock,client_IP = self.sock.accept()

        self.Print_to_Screen(f'Accepted connection from {client_IP}')
        self.Handle_client(client_sock,client_IP)

    def Handle_client(self,client_sock,client_IP): #handle Client
          # get data from json file
        
        self.Client_Login(client_sock,client_IP)

        full_data=Get_data_from_Json()
        try:
            # receive request from client
            data_enc =client_sock.recv(buffer)
            while data_enc:
                
                #get cmd from Client
                client_msg = data_enc.decode('utf-8')
                if client_msg =='Quit':
                    break
                else:

                    if client_msg!='All':

                        #find currency 
                        object,update_time =Find_currency(full_data,client_msg)

                        #send time update
                        client_sock.sendall(update_time.encode('utf-8'))

                        #send if server have that data or not 
                        if object != None:
                            client_sock.sendall(str('true').encode('utf-8'))
                            self.Send_currency_data(client_sock=client_sock,object=object)
                        else:
                            client_sock.sendall(str('false').encode('utf-8'))

                    else:
                        
                        # find currency 
                        object,update_time =Find_currency(full_data)

                        # send time update
                        client_sock.sendall(update_time.encode('utf-8'))

                        #get number of currency and send to client
                        number= len(full_data.get('results'))
                        client_sock.sendall(str(number).encode('utf-8'))
                        print(number)

                        #send all data to client
                        for no in full_data.get('results'):
                            self.Send_currency_data(client_sock=client_sock,object=no)

                #receive data from client
                data_enc =client_sock.recv(buffer)

        except OSError as err:
            self.Print_to_Screen(err)
        
        finally:
            
            #close connection
            self.Print_to_Screen(f'Closing client socket for {client_IP}')
            self.LogOut(client_sock,client_IP)
            client_sock.close()
            self.Print_to_Screen(f'Closed {client_IP}')
            

    def shutdown_server(self):
        
        #shutdown server
        self.Print_to_Screen('Server shutting down...')
        self.sock.close()

# ----- TCP multi client -----
class TCPSERVERMULTICLIENT(TCPSERVER):

    def __init__(self,IP,Port):
        super().__init__(IP,Port)

    def wait_for_client(self):

        try:
            #listen for client connection
            self.Print_to_Screen('Listening for connection')
            self.sock.listen(10)

            while True:

                #accept connection
                client_sock,client_IP = self.sock.accept()
                self.Print_to_Screen(f'Accepted connection from {client_IP}')

                #threading client
                client_thread=threading.Thread(target=self.Handle_client,args=(client_sock,client_IP))
                client_thread.start()
                
                # client_thread=multiprocessing.Process(target=self.Wait_for_Client)
                # client_thread.start()
                
        except KeyboardInterrupt:

            self.shutdown_server()
        finally:

            self.shutdown_server()

# ----- main -----

def main():
    os.system("Title "+"Server")
    tcp_server_multi_client=TCPSERVERMULTICLIENT(ServerIP,ServePort)
    tcp_server_multi_client.Config_server()
    tcp_server_multi_client.wait_for_client()

if __name__=='__main__':
    main()




