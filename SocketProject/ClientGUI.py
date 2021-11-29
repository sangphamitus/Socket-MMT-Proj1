import tkinter
from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter.constants import ANCHOR
from tkinter.messagebox import showinfo
from tkinter import messagebox
from tkinter import Tk, Canvas, Frame, BOTH

def ClientGUI(IPServer):

    # tạo console
    clientwindow=tkinter.Tk()
    #clientwindow.configure(bg = "#FFF5E7")
    clientwindow.geometry("900x550")
    clientwindow.title("Currency Exchange")
    bg = PhotoImage(file = "currency exchange.png")

    label1 = Label( clientwindow, image = bg)
    label1.place(x = 0, y = 0)
    
    frame1 = Frame(clientwindow)
    frame1.pack(pady = 20 )
  

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
    

    def logOut(Popup):

        # tắt pop up và bật login gui 
        Popup.destroy()
        clientwindow.destroy()
        loginGUI(IPServer)
    
    # tạo option input
    options= ["USD","EUR","HKD","AUD","CAD","CHF", "CNY","DKK", "GBP","INR","JPY","KRW","KWD","MYR", "NOK","RUB","SAR","SEK","SGD","THB"]
    
    #tạo frame chọn option menu
    variable = tkinter.StringVar(clientwindow)
    variable.set(options[0])
    left_frame = tkinter.Frame(clientwindow, width = 805, height = 130, bg = '#DDC488')
    left_frame.place(x=20,y=0)
    w = tkinter.OptionMenu(clientwindow,variable,*options)
    w.config(width=10,bg = "#5a5865", fg = '#dff0ee')
    
    # hiện chữ Currency Exchange
    k=tkinter.Label(clientwindow,text= "Currency Exchange", fg = 'blue')
    k.config(font=("Courier", 20))
    k.place(x=300,y=10)
    k2=tkinter.Label(clientwindow,text= "Currency")
    k2.config(font=("Courier", 15))
    k2.place(x=300,y=52)
    w.place(x=420,y=50)

    # tạo các nút 
    tkinter.Button(clientwindow,text="LOG OUT",command=LogOutPopUp,bg = "white", fg = 'red').place(x=50,y=20)
    #tkinter.Button(clientwindow,text="INPUT",command=lambda:print(f"{variable.get()}")).place(x=530,y=52 )
    tkinter.Button(clientwindow,text="INPUT",command=lambda:InputMsg(),width=18).place(x=300,y=90 )
    tkinter.Button(clientwindow,text="CLEAR LIST",command=lambda:ClearList(),width=18).place(x=440,y=90 )
   # white_frame = tkinter.Frame(clientwindow, width = 900, height = 500, bg = 'white')
   # white_frame.place(x=0,y=100)

    # tạo các trêe view để xem các kết quả trả về
    columns =('currency','buy_cash','buy_transfer','sell')
    tree= ttk.Treeview(clientwindow,columns=columns,show='headings')
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background = "white", foreground = "black", rowheight = 25, fieldbackground = "white")
    style.map("Treeview", background = [('selected', 'blue')])
    
    tree.column('#0', width = 0, stretch =tkinter.NO)
    tree.column('currency',anchor='c')
    tree.column('buy_cash',anchor='c')
    tree.column('buy_transfer',anchor='c')
    tree.column('sell',anchor='c')
    
    tree.heading("0", text = "", anchor = 'c')
    tree.heading('currency', text= 'Currency',anchor='c')
    tree.heading('buy_cash', text='Buy cash',anchor='c')
    tree.heading('buy_transfer',text='Buy transfer',anchor='c')
    tree.heading('sell',text='Sell',anchor='c')

    # tạo màu cho mấy dòng lẻ và chẵn
    tree.tag_configure('odd', background = '#CCCCFF')
    tree.tag_configure('even', background = 'white')


    recev=[]
    contact=[]

    # xóa danh sách xem kết quả 
    def ClearList():
        recev.clear()
        contact.clear()
        for item in tree.get_children():
            tree.delete(item)


    # thêm msg vào danh sách kết quả
    def InputMsg():
        print(f'{variable.get()} ')
        for item in tree.get_children():
            tree.delete(item)
        if variable.get() not in contact:
            contact.append(variable.get())
            recev.append((f'{variable.get()} ',f'0',f'0',f'0'))
        else:
            recev[contact.index(variable.get())] = (f'{variable.get()} ',f'9',f'9',f'9')
        
        # hiện màu cho dòng
        idx=0
        for cont in recev:
            if idx %2 == 0:
                tree.insert('',index='end',value=cont,tags=('even',))
            else:                
                tree.insert('',index='end',value=cont,tags=('odd',))
            idx=idx+1
    
    def item_selected(event):

        for selected_item in tree.selection():
            item =tree.item(selected_item)
            record = item['values']

            showinfo(title='Information', message=','.join(record))

    
    
    #tree.bind('<<TreeviewSelect>>', item_selected)

    # chỗ hiện tree view
    tree.place(x=20,y=130,height=400)

    clientwindow.mainloop()

def loginGUI(IPServer):

    # tạo cửa sổ console login có kích thước và title
    loginwindow=tkinter.Tk()
    loginwindow.geometry("500x160")
    loginwindow.title("Login Input")

    # label nếu login thâts bại 
    loginFail=tkinter.Label(loginwindow,fg="red",text="Please input Username and Password")


    # bấm nút login 
    def getLoginInfo(UserInput,PassInput,posInput):    
        
        # kiểm tra input username và password
        if len(UserInput.get()) !=0 and len(PassInput.get()) !=0:
                if (loginFail.winfo_exists()):
                    loginFail.destroy()
                print(f"Username: {UserInput.get()}")
                print(f"Password: {PassInput.get()}")
                print(f"Pos: {posInput}") 

                # đăng nhập thành công
                tkinter.Label(loginwindow,fg="green",text=f"{posInput} success").grid(row=3,column=1)

                #Đóng console 
                loginwindow.destroy()

                # mở GUi client
                ClientGUI(IPServer)
        else:   

            #đăng nhập thât bại 
            loginFail.grid(row=3,column=1,padx=(0,100))
    if IPServer =="":
        return False
    
    # hiện pasword và username 
    tkinter.Label(text="Username").grid(row=0,column=0,ipadx=10)
    tkinter.Label(text="Password").grid(row=1,column=0)

    # tạo nơi nhập user và pass
    UserInput=tkinter.Entry(loginwindow,width=50)
    UserInput.grid(row=0,column=1,padx=(10,100),pady=(10,5))
    PassInput=tkinter.Entry(loginwindow,width=50)
    PassInput.config(show="*")
    PassInput.grid(row=1,column=1,padx=(10,100))

    # hiện label 
    tkinter.Label(text=f"IP Server: {IPServer}").grid(row=2,column=1,padx=(0,100))
   
    # hiện nút login và đăng kí
    tkinter.Button(text="Login",command=lambda : getLoginInfo(UserInput,PassInput,"Log"), bg = "#5a5865", fg = '#dff0ee',width=14,padx=30).place(x=80,y=120)
    tkinter.Button(text="Register",command= lambda: getLoginInfo(UserInput,PassInput,"Reg"), bg = "#5a5865", fg = '#dff0ee',width=14,padx=30).place(x=240,y=120)
    loginwindow.mainloop()

def inputServerIP():
    # cửa sổ nhập IP

    #  Tạo console có kích cỡ
    window= tkinter.Tk()
    window.geometry("450x100")

    # cấu hình nền bg cho console
    window.configure(bg = "#e1dcfd")

    # title của console
    window.title("Input IP Server")
    IPServer=""

    # sau khi bấm nút
    def show_entry_fields():

        # kiểm tra xem ô entry có rỗng hay k 
        if(len(ipInp.get())!= 0):

            # nếu không rỗng, lấy thông tin server
            print(f"IP Server {ipInp.get()}")
            IPServer =ipInp.get()

            # đóng console
            window.destroy()

            # mở GUI login
            loginGUI(IPServer)

    #tạo label Input IP có màu bg tại vị trí (0,0) padding y padding x 
    tkinter.Label(window,text="Input IP: ",bg = "#e1dcfd").grid(row=0,column=0,pady=(20,20),padx=(20,20))

    # tạo khung để ghi
    ipInp =tkinter.Entry(window,width=50)
    ipInp.grid(row=0,column=1)

    # tạo nút
    tkinter.Button(window,text="Input ", command=show_entry_fields,padx=20, bg = "#5a5865", fg = '#dff0ee',width=14).grid(row=2,column=1,padx=(10,30))
    window.mainloop()

def main():
    inputServerIP()

if __name__=='__main__':
    main()