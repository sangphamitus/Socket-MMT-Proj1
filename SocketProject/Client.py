from datetime import datetime
import socket
import os
from urllib.request import DataHandler
import msvcrt
# ----- Assign const value ----

buffer=2048
client_Port=64234

# ------ Client  ----
def Create_Connection(): #Create connection

    # input Server IP
    server_IP=input('Input IP:')
    print(f'Connecting to Server IP: {server_IP}')
    
    #create socket
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        sock.connect((server_IP,client_Port))
    except:
        return None,(None,None)
        
    return sock,(server_IP,client_Port)

def Print_object(object): # print and dict
    
    print(f"Currency: {object[0]}")
    print(f"Buy Cash: {object[1]}")
    print(f"Buy transfer: {object[2]}")
    print(f"Sell: {object[3]}")

def Specific_Currency(client_sock):  # recev one dict and print
    
    # assign list contain data

    try:
        #recv data from sever
        # data_recv.append(client_sock.recv(buffer).decode('utf-8'))
        # data_recv.append(client_sock.recv(buffer).decode('utf-8'))
        # data_recv.append(client_sock.recv(buffer).decode('utf-8'))
        # data_recv.append(client_sock.recv(buffer).decode('utf-8'))
        data_recv =client_sock.recv(buffer).decode('utf-8')
        data_recv=str(data_recv).split(',')

        #print data
        Print_object(data_recv)
    
    except OSError:
        print("Server disconnected...")
        client_sock.close()
    
def Update_data(update_time): #Check and update data 
    
    #assign and get date and time
    now = datetime.now()
    date=datetime.today()
   
    if update_time==0:
        return True
    update_time=str(update_time).split(' ')
    
    #check if 30 minutes last or not
    if str(date.day) == update_time[0].split('/')[0] and str(date.month) == update_time[0].split('/')[1] and str(date.year)==update_time[0].split('/')[2]:
        
        if str(now.hour)==update_time[1].split(':')[0]:
            
            if abs(int(update_time[1].split(':')[1]) - int(now.minute))>=30:
                
                return True
        else:

            return True
    else:

        return True 
    
    return False

def Client_communicate(client_sock,server_addr): #Client communicate with server

    if Client_login(client_sock,server_addr)== False:
        return False
    List_Request=[]
    update_time=0
    last_update_time=0
    pos_request=0
    while True:
        msg=""
        print(List_Request)
        # adding up (may be discard)
        if pos_request==len(List_Request)-1:
            pos_request=0
            last_update_time=update_time
        if (Update_data(last_update_time)== True):
            if pos_request<len(List_Request):
                msg=List_Request[pos_request]
                pos_request=pos_request+1
        
        if msvcrt.kbhit() or msg=="":
        #--------------------     
          
        # get input command
            msg= input('Input: ')
        msg=msg.upper()

        try:
            client_sock.sendto(str.encode(msg),server_addr)
            #command Quit
            if msg =='QUIT':
                #quit loop
                break

            else:
                #get update time
                update_time=client_sock.recv(buffer).decode('utf-8')

                print(f'{update_time}')

                if msg!='ALL':
                    if msg == 'CLEAR':
                        List_Request=[]
                    #get confirm that server haves data or not
                    confirm =client_sock.recv(buffer).decode('utf-8')

                    if confirm == "true":
                        #have data
                        if 'ALL' in List_Request:
                            List_Request=[]
                        if msg not in List_Request:
                            List_Request.append(msg)
                        Specific_Currency(client_sock)
                    else:
                        #not have data
                        print("N/A")
                else:
                    List_Request =['ALL']
                    #get number of currency 
                    number = client_sock.recv(buffer)
                    number = number.decode('utf-8')
                    number =int(number)
                    

                    #receive all data of currency
                    no=0
                    while no<number:
                        data= client_sock.recv(buffer).decode('utf-8')
                        data=str(data).split(',')
                        while data[0]!='':
                            Print_object(data)
                            data=data[4:]
                            no=no+1
                        no=no+1
        except:
            print("Server disconnected..")
            break
    client_sock.close()
    return True

def Client_login(client_sock,server_addr):

    while True:
        
        #input username, pwd and status
        username=input('username: ')
        pwd = input('password: ')
        status_login= input('Login Status: ')
        msg=status_login+','+username+','+pwd
        #send info to server
        try:
            client_sock.sendto(msg.encode('utf-8'),server_addr)
            resp = client_sock.recv(buffer).decode('utf-8')

            print(resp)

            if resp == 'Login success' :
                os.system("Title "+username)
                return True
                
        except:
            print("Server disconnected..")
            client_sock.close()
            return False
            
        # client_sock.sendto(status_login.encode('utf-8'),server_addr)
        
        # client_sock.sendto(username.encode('utf-8'),server_addr)
  
        # client_sock.sendto(pwd.encode('utf-8'),server_addr)
      
        # recv resp from server
        


def main():
    os.system("Title "+"Client")
    sock,server_addr=Create_Connection()
    if sock== None:
        print("can't connect to server")
    else:
        Client_communicate(sock,server_addr)

if __name__=='__main__':
    main()

