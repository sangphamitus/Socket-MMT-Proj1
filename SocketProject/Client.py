import tkinter
from tkinter import *
from tkinter.font import Font, families
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter.constants import ANCHOR
from tkinter.messagebox import askokcancel, showinfo
from tkinter import messagebox
from tkinter import Tk, Canvas, Frame, BOTH
import socket
import os
from urllib.request import DataHandler
import msvcrt
from datetime import datetime
import threading
from Server import Update_data
import sys
import time

# ----- Assign const value ----

buffer=2048
client_Port=64234

# ------ Client  ----

def RunThread(clientwindow,client_sock,server_addr):
    
    while True:
        time.sleep(1)
        try:
            client_sock.sendto(str("-").encode('utf-8'),server_addr)
        except:
            messagebox.askokcancel("QUIT","Cannot connect to server")  
            clientwindow.destroy()
            sys.exit()
        
            

def ClientGUI(IPServer,client_sock,server_addr):
    
    # tạo console
    clientwindow=tkinter.Tk()
    #clientwindow.configure(bg = "#FFF5E7")
    clientwindow.geometry("1050x600")
    clientwindow.iconbitmap('logo.ico')
    clientwindow.title("Currency Exchange")
    checkConnect=threading.Thread(target=RunThread,args=(clientwindow,client_sock,server_addr,))
    checkConnect.setDaemon(True)
    checkConnect.start()
    canvas= Canvas( clientwindow,width=1050 , height=600)
    img = ImageTk.PhotoImage(Image.open("main.jpg"))
    canvas.create_image(525,300,image=img)
    canvas.place(x=0,y=0)
    
    def on_closing():
        #khi bấm nút thoát 
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            clientwindow.destroy()
          
    def LogOutPopUp():
       # tạo pop up để hỏi logout
        Popup=tkinter.Toplevel(clientwindow)
        Popup.wm_title("log out")
        Popup.geometry("250x100")
        Popup.grab_set()
        tkinter.Label(Popup,text="Log out? ").place(x=50,y=20)
        tkinter.Button(Popup,text="Yes",command=lambda:logOut(Popup),width=10).place(x=30,y=50)
        tkinter.Button(Popup,text="No",command=Popup.destroy,width=10).place(x=130,y=50)
   
    clientwindow.protocol("WM_DELETE_WINDOW",on_closing)
    
    def logOUTfunc(IPServer,client_sock,server_addr):
        client_sock.sendto(str.encode('QUIT'),server_addr)
        client_sock.close()
        
        try:

            clientwindow.destroy()
            #inputServerIP()
        except:
            messagebox.askokcancel("QUIT","Cannot connect to server")  
            clientwindow.destroy()
            
        finally:
            os._exit(0)
            

    def logOut(Popup):
        Popup.destroy()
        logOUTfunc(IPServer,client_sock,server_addr)
        
    
   # tạo option input
    options= ["USD","EUR","HKD","AUD","CAD","CHF", "CNY","DKK", "GBP","INR","JPY","KRW","KWD","MYR", "NOK","RUB","SAR","SEK","SGD","THB"]
    
    #tạo frame chọn option menu
    variable = tkinter.StringVar(clientwindow)
    variable.set(options[0])
    
    w = tkinter.OptionMenu(clientwindow,variable,*options)
    w.config(width=17,bg = "#5a5865", fg = '#dff0ee',font=("",13,"bold"))
    
    # hiện chữ Currency Exchange
    #k=tkinter.Label(clientwindow,text= "Currency Exchange", fg = 'blue')
  #  k.config(font=("Courier", 20))
   # k.place(x=300,y=10)

    w.place(x=240,y=100)

  
    InputDay=tkinter.Entry(clientwindow)
    InputDay.config(width=12,font=("",20,""))
    InputDay.place(x=773,y=100)
    # tạo các nút 
    tkinter.Button(clientwindow,text="LOG OUT",command=LogOutPopUp,bg = "white", fg = 'black',borderwidth=0).place(x=50,y=20)
    #tkinter.Button(clientwindow,text="INPUT",command=lambda:print(f"{variable.get()}")).place(x=530,y=52 )
    tkinter.Button(clientwindow,text="INPUT",command=lambda:InputMsg(),width=18,bg = "#006cbe", fg = 'white',padx=10).place(x=375,y=150 )
    tkinter.Button(clientwindow,text="CLEAR LIST",command=lambda:ClearList(),width=18,bg = "#006cbe", fg = 'white',padx=10).place(x=525,y=150)
   # white_frame = tkinter.Frame(clientwindow, width = 900, height = 500, bg = 'white')
   # white_frame.place(x=0,y=100)
    columns =('currency','buy_cash','buy_transfer','sell','day')
    tree= ttk.Treeview(clientwindow,columns=columns,show='headings')
    
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background = "#006cbe", rowheight = 25, fieldbackground = "#121F50",font=("Alatsi",13,""),foreground='white')
    style.map("Treeview", background = [('selected', "#006cbe")],foreground=[('selected',"#ffffff")])
    
    tree.column('#0', width = 0, stretch =tkinter.NO)
    tree.column('currency',anchor='c')
    tree.column('buy_cash',anchor='c')
    tree.column('buy_transfer',anchor='c')
    tree.column('sell',anchor='c')
    tree.column('day',anchor='c')
    
    tree.heading("0", text = "", anchor = 'c')
    tree.heading('currency', text= 'Currency',anchor='c')
    tree.heading('buy_cash', text='Buy cash',anchor='c')
    tree.heading('buy_transfer',text='Buy transfer',anchor='c')
    tree.heading('sell',text='Sell',anchor='c')
    tree.heading('day',text='Day',anchor='c')

    # tạo màu cho mấy dòng lẻ và chẵn
    tree.tag_configure('odd', background = '#006cbe')
    tree.tag_configure('even', background = '#121F50')
    tree.tag_configure('word',foreground='white')

    recev=[]
    contact=[]
    def ClearList():
        recev.clear()
        contact.clear()
        for item in tree.get_children():
            tree.delete(item)

    def InputMsg():
        msg =variable.get()
        day=InputDay.get()
        if (len(day)==0):
            currntday =datetime.today()
            day=f"{currntday.day}/{currntday.month}/{currntday.year}"
        print(f'{variable.get()},{day}')
        msg=f'{variable.get()},{day}'
#-------------------------------------------------------------        
        try:
            client_sock.sendto(str.encode(msg),server_addr)
            Update_time ="None"
            update_time=client_sock.recv(buffer).decode('utf-8')
            print(f'{update_time}')
            confirm =client_sock.recv(buffer).decode('utf-8')            
            if confirm == "true":
                try:
                    data_recv =client_sock.recv(buffer).decode('utf-8')
                    object=str(data_recv).split(',')
                    for item in tree.get_children():
                        tree.delete(item)
                    if variable.get() not in contact:
                        contact.append(variable.get())
                        recev.append((f'{object[0]} ',f'{object[1]}',f'{object[2]}',f'{object[3]}',f'{update_time}'))
                    else:
                        recev[contact.index(variable.get())] = (f'{object[0]} ',f'{object[1]}',f'{object[2]}',f'{object[3]}',f'{update_time}')

                except OSError:
                    messagebox.askokcancel("QUIT","Cannot connect to server") 
                    print("Server disconnected...")
                    client_sock.close()
                    clientwindow.destroy()
                    inputServerIP()
            else:
                messagebox.showinfo(title="Data Error",message="\tSorry! We don't have this data\n")
        except:
            messagebox.askokcancel("QUIT","Cannot connect to server") 
            print("Server disconnected...")
            client_sock.close()
            clientwindow.destroy()
            inputServerIP()
#--------------------------------------------------------------
        # for item in tree.get_children():
        #     tree.delete(item)
        # if variable.get() not in contact:
        #     contact.append(variable.get())
        #     recev.append((f'{variable.get()} ',f'0',f'0',f'0'))
        # else:
        #     recev[contact.index(variable.get())] = (f'{variable.get()} ',f'9',f'9',f'9')
        if update_time != "None" and update_time!="":
            idx=0
            for cont in recev:
                if idx %2 == 0:
                    tree.insert('',index='end',value=cont,tags=('even','word'))
                else:                
                    tree.insert('',index='end',value=cont,tags=('odd','word'))
                idx=idx+1
    
    
    def item_selected(event):

        for selected_item in tree.selection():
            item =tree.item(selected_item)
            record = item['values']

            showinfo(title='Information', message=','.join(record))

    
    
    #tree.bind('<<TreeviewSelect>>', item_selected)
    tree.place(x=20,y=190,height=400)

    clientwindow.mainloop()

def loginGUI(IPServer,client_sock,server_addr):
    loginwindow=tkinter.Tk()
    loginwindow.geometry("500x160")
    loginwindow.iconbitmap('logo.ico')
    loginwindow.title("Login Input")
    canvas= Canvas( loginwindow,width=500, height=160)
    img = ImageTk.PhotoImage(Image.open("Login.jpg"))
    canvas.create_image(250,80,image=img)
    canvas.place(x=0,y=0)
    def on_closing():
        #khi bấm nút thoát 
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                msg="QUIT"
                client_sock.sendto(msg.encode('utf-8'),server_addr)
                client_sock.close()
                loginwindow.destroy()
            except OSError:
                print("Server disconnected..")
                messagebox.askokcancel("QUIT","Cannot connect to server") 
                client_sock.close()
                loginwindow.destroy()
           

    loginwindow.protocol("WM_DELETE_WINDOW",on_closing)
    # label nếu login thâts bại 
    loginFail=tkinter.Label(loginwindow,fg="red",text="Please input Username and Password")


    # bấm nút login 
    def getLoginInfo(UserInput,PassInput,posInput):    
        
        # kiểm tra input username và password
        if len(UserInput.get()) !=0 and len(PassInput.get()) !=0:
                if (loginFail.winfo_exists()):
                    loginFail.destroy()
                # print(f"Username: {UserInput.get()}")
                # print(f"Password: {PassInput.get()}")
                # print(f"Pos: {posInput}") 
 #-------------------------------------------------------------------               
                msg=posInput+','+UserInput.get()+','+PassInput.get()
                # print(msg)
                # print(client_sock)
                try:
         
                    client_sock.sendto(msg.encode('utf-8'),server_addr)
                    resp = client_sock.recv(buffer).decode('utf-8')
                    print(resp)
                    if resp == 'Login success' :
                        os.system("Title "+UserInput.get())
                        tkinter.Label(loginwindow,fg="green",text=f"{posInput} success").grid(row=3,column=1)
                        loginwindow.destroy()
                        ClientGUI(IPServer,client_sock,server_addr)
                    else:
                        if(resp==""):
                            messagebox.askokcancel("QUIT","Cannot connect to server") 
                            client_sock.close()
                            loginwindow.destroy()
                            inputServerIP()
                        else :
                            messagebox.askokcancel("LoginErr",resp) 
                        #loginFail.grid(row=3,column=1,padx=(0,100))
                except OSError:
                    print("Server disconnected..")
                    messagebox.askokcancel("QUIT","Cannot connect to server") 
                    client_sock.close()
                    loginwindow.destroy()
                    inputServerIP()
                
#-------------------------------------------------------------------
                # tkinter.Label(loginwindow,fg="green",text=f"{posInput} success").grid(row=3,column=1)
                # loginwindow.destroy()
                # ClientGUI(IPServer)
        else:   
            #đăng nhập thât bại 
            loginFail.config(bg="#121F50",fg="white",font=("",8,"bold"))
            loginFail.place(x=150,y=100 )
    if IPServer =="":
        return False
    
     # tạo nơi nhập user và pass
    UserInput=tkinter.Entry(loginwindow,width=40)
    UserInput.config(bg="#121F50",insertbackground='white',font=("",12,""),fg="white")
    UserInput.place(x=120,y=13)
    PassInput=tkinter.Entry(loginwindow,width=40)
    PassInput.config(bg="#121F50",insertbackground='white',font=("",12,""),fg="white")
    PassInput.config(show="*")
    PassInput.place(x=120,y=45)

    # hiện label 
    lanle=tkinter.Label(text=f"{IPServer}")
    lanle.config(bg="#121F50",fg="white",font=("",8,"bold"))
    lanle.place(x=205,y=81)
    # hiện nút login và đăng kí
    tkinter.Button(text="Login",command=lambda : getLoginInfo(UserInput,PassInput,"Log"),bg = "#006cbe", fg = 'white',width=14,padx=33).place(x=90,y=120)
    tkinter.Button(text="Register",command= lambda: getLoginInfo(UserInput,PassInput,"Res"), bg = "#006cbe", fg = 'white',width=14,padx=33).place(x=260,y=120)
    loginwindow.mainloop()

def inputServerIP():
     # cửa sổ nhập IP

    #  Tạo console có kích cỡ
    window= tkinter.Tk()
    window.geometry("450x100")

    # cấu hình nền bg cho console
    window.configure(bg = "#e1dcfd")
    window.iconbitmap('logo.ico')
    # title của console
    window.title("Input IP Server")
    IPServer=""
    def show_entry_fields():
        if(len(ipInp.get())!= 0):
            print(f"IP Server {ipInp.get()}")
            IPServer =ipInp.get()
            
#-----------------------------------------------
            print(f'Connecting to Server IP: {IPServer}')
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                sock.connect((IPServer,client_Port))
                window.destroy()
               
                
                loginGUI(IPServer,sock,(IPServer,client_Port))
            except:
                messagebox.askokcancel("QUIT","Cannot connect to server")  
                window.destroy() 
#---------------------------------------


    #tạo label Input IP có màu bg tại vị trí (0,0) padding y padding x 
    canvas= Canvas(window,width=450, height=100)
    img = ImageTk.PhotoImage(Image.open("inputIP.jpg"))
    canvas.create_image(225,50,image=img)
    canvas.place(x=0,y=0)
    #tkinter.Label(window,text="Input IP: ",bg = "#e1dcfd").grid(row=0,column=0,pady=(20,20),padx=(20,20))

    # tạo khung để ghi
    ipInp =tkinter.Entry(window,width=35,fg='white' ,font=("",12))
    ipInp.config(bg="#121F50",insertbackground='white')
    ipInp.place(x=105,y=21)

    # tạo nút
    tkinter.Button(window,text="Input ", command=show_entry_fields, bg = "#006cbe", fg = 'white',width=12).place(x=200,y=60)
    window.mainloop()


def main():
    
    inputServerIP()

if __name__=='__main__':
    main()