import json
import os
import socket
from tkinter.constants import FALSE
import requests
from urllib.request import urlopen
from requests.api import head, request
from requests.models import Response
from requests.structures import CaseInsensitiveDict
from datetime import datetime
import tkinter
from tkinter import Canvas, ttk
from tkinter.constants import ANCHOR
from tkinter.messagebox import showinfo
from tkinter import messagebox
from PIL import ImageTk,Image
import threading
import schedule
import sys

# ------ Assign const value -----

ConsoleWidth=70
buffer = 2048 #buffer send and recv data
ColorCode="#3d4546"
#Server IP and Port
ServerIP= socket.gethostbyname(socket.gethostname())
ServePort=64234

def FirstRunningServer():

    with open("AccountLive.json",'w') as out_file:
        out_file.write(json.dumps({"username":[],"pwd":[],"socket":[]},indent=3))
        out_file.close()

class GuiServer():
    
    def Run(self):
        self.clientwindow=tkinter.Tk()
        self.clientwindow.configure(bg = ColorCode)
        self.clientwindow.geometry("745x450")
        self.clientwindow.title("Currency Exchange Server")
        self.clientwindow.iconbitmap('logo.ico')
        self.Lb1 = tkinter.Listbox(self.clientwindow,width=ConsoleWidth,height=22)
        self.Lb1.config(background="black", foreground="white")
        self.Lb1.place(x=225,y=35)
        self.Lb2 = tkinter.Listbox(self.clientwindow,width=34,height=22)
        self.Lb2.config(background="white", foreground="black")
        self.Lb2.place(x=15,y=35)
        self.lable1=tkinter.Label(self.clientwindow,text="Current Online Users",width=20)
        self.lable1.config(fg="white", font=("",13,"bold"),bg = ColorCode,anchor="center")
        self.lable1.place(x=15,y=10)
        self.lable2=tkinter.Label(self.clientwindow,text="Current Activites",width=int(ConsoleWidth-20),)
        self.lable2.config(fg="white", font=("",13,"bold"),bg = ColorCode,anchor="center")
        self.lable2.place(x=226,y=10)
        self.IPlabel=tkinter.Label(self.clientwindow,text="Server ready on :")
        self.IPlabel.config(fg="white", font=("",13,"bold"),bg = ColorCode,anchor="center")
        self.IPlabel.place(x=450,y=400)
    
    def DisplayIP(self,msg):
        self.IPlabel=tkinter.Label(self.clientwindow,text=f"Server ready on : {msg}")
        self.IPlabel.config(fg="white", font=("",10,"underline"),bg = ColorCode,anchor="center")
        self.IPlabel.place(x=420,y=400)
    def Input1(self,mss):
        
        mss = '>>  ' +mss
        if(len(mss)>ConsoleWidth+10):
            while(mss!=""):
                displaymss=mss[:ConsoleWidth+10]
                self.Lb1.insert(tkinter.END, displaymss)
                mss=mss[ConsoleWidth+10:]
        else:
            self.Lb1.insert(tkinter.END, mss)
        self.Lb1.insert(tkinter.END,str(" "))    
        self.Lb1.place(x=225,y=35)
        self.Lb2.place(x=15,y=35)
        self.Lb1.yview(tkinter.END)
        

    def Input2(self,mss):
    
        self.Lb2.insert(tkinter.END, mss)
        self.Lb1.place(x=225,y=35)
        self.Lb2.place(x=15,y=35)
        self.Lb2.yview(tkinter.END) 
        self.Lb1.yview(tkinter.END)
       

    def AccountOnlineUpdate(self,url):
     
        f=open(url)
        data=json.load(f)
        self.Lb2.delete(0,tkinter.END)
        for i in data['username']:
            self.Input2(i)
        self.Input1(str(data))
        f.close()
       

    def on_closing(self):
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.clientwindow.destroy()
            FirstRunningServer()
            return True
        else:
            return False
       

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

def Save_data_to_Json(full_data,file_name="ExchangeCurrencyRate.json"): # save data to Json file

    # get time and date
    update_time, update_date=Get_time_and_day()
    full_data['update_time']=[update_date,update_time]

    # write data to json file
    with open(file_name,'w') as out_file:
        out_file.write(json.dumps(full_data,indent=2))
        out_file.close()

def Get_data_from_Json(file_name="ExchangeCurrencyRate.json"): # get data from save file
    
    #check if file exist or not
    if not os.path.isfile(file_name):
        Save_data_to_Json(full_data=Get_data_API(keys=Get_API_key()),file_name=file_name)

    # get data from file
    with open(file_name,'r') as file_in:
        response = json.load(file_in)
        file_in.close()

    return response

def Update_data_30min():
    while True:
        current_time,current_day=Get_time_and_day()
        filename=f"Data/{current_day['day']}_{current_day['month']}_{current_day['year']}.json"
        full_data=Get_data_from_Json(filename)
        Update_data(full_data=full_data)


def Update_data(full_data): #Check and update data 
    
    #assign and get date and time
    response=full_data
    last_update_time = full_data.get('update_time')
    current_time,current_day=Get_time_and_day()


    filename=f"Data/{current_day['day']}_{current_day['month']}_{current_day['year']}.json"


    #check if 30 minutes last or not
    if last_update_time[0].get('day')==current_day.get('day') and last_update_time[0].get('month')==current_day.get('month') and last_update_time[0].get('year')==current_day.get('year'):
        
        if last_update_time[1].get('hour')==current_time.get('hour'):
            
            if abs(int(last_update_time[1].get('minute')) - int(current_time.get('minute')))>=30:
                
                Save_data_to_Json(full_data=Get_data_API(keys=Get_API_key()),file_name=filename) 
                response=Get_data_from_Json(file_name=filename)
        else:

            Save_data_to_Json(full_data=Get_data_API(keys=Get_API_key()),file_name=filename) 
            response=Get_data_from_Json(file_name=filename)
    else:

        Save_data_to_Json(full_data=Get_data_API(keys=Get_API_key()),file_name=filename) 
        response=Get_data_from_Json(file_name=filename)
    
    return response

def Read_File(day):
    filename=f"Data/{day[0]}_{day[1]}_{day[2]}.json"
      #check if file exist or not
    if not os.path.isfile(filename):
        return None

    # get data from file
    try:
        with open(filename,'r') as file_in:
            response = json.load(file_in)
            file_in.close()
        return response
    except:
        return None

def Find_currency_file(full_data,GUI,currency_name=None):
    GUI.Input1(f"data_at_time: {full_data.get('update_time')}")
    update_time = f"{full_data.get('update_time')[0].get('day')}/{full_data.get('update_time')[0].get('month')}/{full_data.get('update_time')[0].get('year')} {full_data.get('update_time')[1].get('hour')}:{full_data.get('update_time')[1].get('minute')}:{full_data.get('update_time')[1].get('sec')}"
    
    #searching for currency name
    for object in full_data.get('results'):
        if(currency_name != None):
            if(object.get('currency')==currency_name):
                return object,update_time

    return None,update_time


def Find_currency(full_data,GUI,currency_name=None): #find currency in data

    #
    #get latest update time
    GUI.Input1(f"data_at_time: {full_data.get('update_time')}")
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
        
        self.url_file="Account.json"
        self.url_online_file="AccountLive.json"
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

    def LogOut(self,client_sock,client_IP,GUI): #log out
        
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
            GUI.AccountOnlineUpdate(self.url_online_file)
        except OSError as err:
            GUI.Input1(err)
        
    def LogIn_Success(self,client_sock,client_IP,GUI):
        
        #get file online account data
        current_online =self.Read_json_file(self.url_online_file)
        GUI.AccountOnlineUpdate(self.url_online_file)
        current_online.get('username').append(self.user)
        current_online.get('pwd').append(self.pwd)
        current_online.get('socket').append(str(client_IP[0])+str(client_IP[1]))
        
        
        GUI.Input2(self.user)
        #rewrite opened account file
        with open(self.url_online_file,'w') as out_file:
            out_file.write(json.dumps(current_online,indent=3))
            out_file.close()
        
    
    def Client_Login(self,client_sock,client_IP,GUI):
        while True :
            #get status login
            msg =client_sock.recv(buffer).decode('utf-8')
            if(len(msg)!=0):
                if(msg=="QUIT"):
                    return False
                msg = str(msg).split(',')
                #print(msg)
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

                        self.LogIn_Success(client_sock,client_IP,GUI)
                        client_sock.sendall('Login success'.encode('utf-8'))
                        return True
                    else:
                        client_sock.sendall('Username already in'.encode('utf-8'))

                else:   

                    if Status_login == 'Log':

                        Account_status= self.LogIn(All_account)

                        if Account_status == 1:
                            self.LogIn_Success(client_sock,client_IP,GUI)
                            client_sock.sendall('Login success'.encode('utf-8'))
                            return True

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

    def Print_to_Screen(self,msg,GUI):

        #get time and date
        current_time= datetime.now().strftime('%d-%m %H:%M:%S')
        GUI.Input1(f'[{current_time}] :  {msg}')

    def Send_currency_data(self,client_sock,object,GUI): # send currency data
    
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
        self.Print_to_Screen(resp,GUI)
        client_sock.sendall(resp.encode('utf-8'))

    def Config_server(self,GUI): # config server socket

        # creating socket TCP
        self.Print_to_Screen('Creating socket....',GUI)
        
        self.sock= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.Print_to_Screen('Socket created',GUI)
        
        #binding socket
        self.sock.bind((self.IP,self.Port))

        self.Print_to_Screen('Finished Config_server',GUI)
        self.Print_to_Screen(f'Server ready on : {self.IP} , Port: {self.Port}',GUI)
        GUI.DisplayIP(f" {self.IP} ,Port: {self.Port}")
     

    def Wait_for_Client(self,GUI): # Client listen
        
        # listen and accept connection
        self.sock.listen(1)
        client_sock,client_IP = self.sock.accept()

        self.Print_to_Screen(f'Accepted connection from {client_IP}',GUI)
     
        self.Handle_client(client_sock,client_IP,GUI)

    def Handle_client(self,client_sock,client_IP,GUI): #handle Client
          # get data from json file
        
        if(self.Client_Login(client_sock,client_IP,GUI)==True):

            
            current_time,current_day=Get_time_and_day()


            filename=f"Data/{current_day['day']}_{current_day['month']}_{current_day['year']}.json"
            full_data=Get_data_from_Json(filename)
            try:
                # receive request from client
                

               
                while True:
                    data_enc =client_sock.recv(buffer)
                    #get cmd from Client
                    client_msg = data_enc.decode('utf-8')
                    
                    if('-' in client_msg):
                        continue
                    self.Print_to_Screen(f'Recv msg from {client_sock} : {client_msg} ',GUI)
                    if client_msg =='QUIT':
                        break
                    else:

                        if client_msg!='ALL':
                            
                            
                            all_msg=client_msg.split(',')
                            client_msg=all_msg[0]
                            day=all_msg[1].split('/')
                            currntday=datetime.today()
                            day[0]=int(day[0])
                            day[1]=int(day[1])
                            day[2]=int(day[2])
                            if(int(day[0])==int(currntday.day) and int(day[1])==int(currntday.month) and int(day[2])==int(currntday.year)):
                            
                           

                            #find currency 
                                object,update_time =Find_currency(full_data,GUI,client_msg)
                            else:
                                full_data_file=Read_File(day)
                                if(full_data_file!=None):
                                    object,update_time=Find_currency_file(full_data_file,GUI,client_msg)
                                else:
                                    update_time ="None"
                                    object=None
                            #send time update
                            client_sock.sendall(update_time.encode('utf-8'))

                            #send if server have that data or not 
                            if object != None:
                                client_sock.sendall(str('true').encode('utf-8'))
                                self.Send_currency_data(client_sock=client_sock,object=object,GUI=GUI)
                            else:
                                client_sock.sendall(str('false').encode('utf-8'))

                        else:
                            
                            # find currency 
                            object,update_time =Find_currency(full_data,GUI)

                            # send time update
                            client_sock.sendall(update_time.encode('utf-8'))

                            #get number of currency and send to client
                            number= len(full_data.get('results'))
                            client_sock.sendall(str(number).encode('utf-8'))
                            #print(number)

                            #send all data to client
                            for no in full_data.get('results'):
                                self.Send_currency_data(client_sock=client_sock,object=no,GUI=GUI)

                    #receive data from client
                    data_enc =client_sock.recv(buffer)

            except OSError as err:
                try:
                    self.Print_to_Screen(err,GUI)
                except:
                    self.Print_to_Screen(err,GUI)
            finally:
                
                #close connection
                try:
                    self.Print_to_Screen(f'Closing client socket for {client_IP}',GUI)
                
                    self.LogOut(client_sock,client_IP,GUI)
                    client_sock.close()
                    self.Print_to_Screen(f'Closed {client_IP}',GUI)
                except:
                    client_sock.close()
             
        else:
            #close connection
            self.Print_to_Screen(f'Closing client socket for {client_IP}',GUI)
            
            client_sock.close()
            self.Print_to_Screen(f'Closed {client_IP}',GUI)   
            

    def shutdown_server(self):
        
        #shutdown server
       
          
        FirstRunningServer()
        self.sock.close()
        os._exit(0)
       

# ----- TCP multi client -----


class TCPSERVERMULTICLIENT(TCPSERVER,GuiServer):
     
    
    def __init__(self,IP,Port):
        TCPSERVER.__init__(self,IP,Port)
        self.gui=GuiServer()
        self.gui.Run()
        self.Config_server(self.gui)
        FirstRunningServer()
        

    def CloseProcess(self):
        if(self.gui.on_closing() == True):
            FirstRunningServer()
            self.shutdown_server()
            
        else:
            FirstRunningServer()
            self.shutdown_server()

    def CloseButton(self):
        FirstRunningServer()
        self.shutdown_server()
        self.gui.clientwindow.destroy()
       
          
    def wait_for_client(self):

    
        try:
            tkinter.Button(self.gui.clientwindow,text="Shutdown server ", command=self.CloseButton, bg = "#006cbe", fg = 'white',width=12).place(x=15,y=400)
            tkinter.Button(self.gui.clientwindow,text="Clear List command", command=lambda:self.gui.Lb1.delete(0,tkinter.END), bg = "#006cbe", fg = 'white',width=15).place(x=225,y=400)
            
            self.gui.clientwindow.protocol("WM_DELETE_WINDOW",lambda:self.CloseProcess())  
            #listen for client connection
            self.Print_to_Screen('Listening for connection',self.gui)
            self.sock.listen(10)

            while True:
                
                #accept connection
                try: 
                    client_sock,client_IP = self.sock.accept()
                    self.Print_to_Screen(f'Accepted connection from {client_IP}',self.gui)
                    
                    #threading client
                    client_thread=threading.Thread(target=self.Handle_client,args=(client_sock,client_IP,self.gui))
                    client_thread.start()
                except OSError as err:
                    self.gui.Input1(err)
                
                # client_thread=multiprocessing.Process(target=self.Wait_for_Client)
                # client_thread.start()
            
        except KeyboardInterrupt:
            
            FirstRunningServer()
            self.shutdown_server()
            
        finally:
            
            FirstRunningServer()
            self.shutdown_server()



    def RunGuiAndClient(self):
       

        try:
            Update_thread=threading.Thread(target=Update_data_30min)
            Update_thread.setDaemon(True)
            
            Connection_Theading= threading.Thread(target=self.wait_for_client)
            Connection_Theading.setDaemon(True)
            Update_thread.start() 
            Connection_Theading.start()
            
        except OSError as er:
            self.gui.Input1(er)
        self.gui.clientwindow.mainloop() 

# ----- main -----





def MainFunc():
    
    os.system("Title "+"Server")
    #FirstRunningServer()
    tcp_server_multi_client=TCPSERVERMULTICLIENT(ServerIP,ServePort)
    tcp_server_multi_client.Config_server(tcp_server_multi_client.gui)
    #tcp_server_multi_client.wait_for_client()
    
    tcp_server_multi_client.RunGuiAndClient()


if __name__=='__main__':
    MainFunc()





