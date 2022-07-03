import spidev, time
import RPi.GPIO as GPIO
import sqlite3
from tkinter import *
import threading
import tkinter.ttk

stop_bool = False
ret ="first"
def fsr():
   global stop_bool
   global ret
   conn = sqlite3.connect('test.db')
   c= conn.cursor()
   c.execute("select num from record order by rowid desc limit 1")
   var = c.fetchall()
   x = var[0][0]
   tmp = str((x+1))
   print(tmp)

   GPIO.setwarnings(False)
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(18, GPIO.OUT)

   spi = spidev.SpiDev()
   spi.open(0, 0)
   spi.max_speed_hz=1000000

   # MCP3008 read fsr402 pressure
   def analog_read(channel):
      r = spi.xfer2([1, (8 + channel) << 4, 0])
      adc_out = ((r[1]&3) << 8) + r[2]
      return adc_out

   while True:
     if stop_bool == True:
        break
     global countA
     countA += 1
     #i=0
     reading1 = analog_read(0)
     reading2 = analog_read(1)
     reading3 = analog_read(2)
     voltage1 = reading1 * 3.3 / 1024
     voltage2 = reading2 * 3.3 / 1024
     voltage3 = reading3 * 3.3 / 1024
     print("읽은 값1은 %d\t압력은 %f V" % (reading1, voltage1))
     print("읽은 값2은 %d\t압력은 %f V" % (reading2, voltage2))
     print("읽은 값3은 %d\t압력은 %f V" % (reading3, voltage3))
     print(countA)
     time.sleep(1)

     if reading1 >= 800 and reading2 >= 800 and reading3 >= 900:
        GPIO.output(18, True)
        global countY
        countY += 1
        ret = "Y"
     elif reading2 >= 800 and reading3 >= 900:
          global countR
          countR += 1
          ret="R"
     elif reading1 >= 800 and reading2 >= 800:
          global countL
          countL += 1
          ret="L"
     elif reading1 >= 800 and reading3 >= 900:
          global countB
          countB += 1
          ret="B"
     else:
          GPIO.output(18, False)
          global countS
          countS += 1
          ret="Stand"

   c.execute("insert into record values (?, DATETIME('now','+9 hours'),?,?,?,?,?,?)",
             (tmp, countA, countY, countL, countR, countB, countS))
   conn.commit()
   conn.close()
   exit()

def tk():
   #start
   global ret
   
   root=Tk()
   root.title("system")
   root.geometry("500x400+300+300")

   def stop_record():
      global stop_bool
      print("stop")
      stop_bool=True

   #stop record
   recordStop_btn = Button(root, text="stop", command=stop_record)
   recordStop_btn.pack(pady="5")
   #canvas
   canvas = Canvas(root, width=300, height=200)
   canvas.pack()
   #back
   b=canvas.create_rectangle(50,50,250,120, fill='red')
   #left
   l=canvas.create_rectangle(50,120,150,240, fill='red')
   #right
   r=canvas.create_rectangle(150,120,250,240, fill='red')

   #update square
   def pr():
      global stop_bool
      global ret
      while True:
         if stop_bool == True:
            break
         print(ret)
         if ret=="Y":
            canvas.itemconfig(b,fill='green')
            canvas.itemconfig(l,fill='green')
            canvas.itemconfig(r,fill='green')
            statLB.config(text="good posture")
         elif ret=="L":
            canvas.itemconfig(b,fill='green')
            canvas.itemconfig(l,fill='red')
            canvas.itemconfig(r,fill='green')
            statLB.config(text="Your posture is tilted to the left. Or don't cross your legs.")
         elif ret=="R":
            canvas.itemconfig(b,fill='green')
            canvas.itemconfig(l,fill='green')
            canvas.itemconfig(r,fill='red')
            statLB.config(text="Your posture is tilted to the right. Or don't cross your legs.")
         elif ret=="B":
            canvas.itemconfig(b,fill='red')
            canvas.itemconfig(l,fill='green')
            canvas.itemconfig(r,fill='green')
            statLB.config(text="Your posture is tilted forward. Put your back on the chair")
         else: #stand&first
            canvas.itemconfig(b,fill='red')
            canvas.itemconfig(l,fill='red')
            canvas.itemconfig(r,fill='red')
            statLB.config(text="Are you standing? We can't detect your posture.")
         time.sleep(1)

   def new_window():
      global new
      new = Toplevel()
      new.geometry("800x600+300+300")
      new.title("show record")
      lbl = Label(new, text="before")
      lbl.pack()
      treeview_b = tkinter.ttk.Treeview(new, columns = ["one","two","three","four","five","six"], 
                                        displaycolumns=["one","two","three","four","five","six"])
      treeview_b.pack()

      treeview_b.column("#0", width=1)
      treeview_b.heading("#0", text="")

      treeview_b.column("#1",width=180)
      treeview_b.heading("one", text="date")

      treeview_b.column("#2",width=130)
      treeview_b.heading("two", text="sitting time(sec)")

      treeview_b.column("#3",width=120)
      treeview_b.heading("three", text="good(%)")

      treeview_b.column("#4",width=120)
      treeview_b.heading("four", text="to left(%)")

      treeview_b.column("#5",width=120)
      treeview_b.heading("five", text="to right(%)")

      treeview_b.column("#6",width=120)
      treeview_b.heading("six", text="to forward(%)")

      conn = sqlite3.connect('test.db')
      c= conn.cursor()
      c.execute("select * from record where num=(select num from record order by rowid desc limit 1)-1")
      var = c.fetchone()
      date = var[1]
      time = var[2]
      if var[3]==0:
          good = var[3]
      else:
          good = (int(var[3])/(int(var[2])-int(var[7])))*100
      if var[4]==0:
          left = var[4]
      else:
          left = (int(var[4])/(int(var[2])-int(var[7])))*100
      if var[5]==0:
          right = var[5]
      else:
          right = (int(var[5])/(int(var[2])-int(var[7])))*100
      if var[6]==0:
          forward = var[6]
      else:
          forward = (int(var[6])/(int(var[2])-int(var[7])))*100

      treelist=[(date,time,good,left,right,forward)]

      for i in range(len(treelist)):
         treeview_b.insert('','end',text=i,values=treelist[i])

      lbl2 = Label(new, text="recent")
      lbl2.pack()
      treeview_r = tkinter.ttk.Treeview(new, columns = ["one","two","three","four","five","six"],
                                        displaycolumns=["one","two","three","four","five","six"])
      treeview_r.pack()

      treeview_r.column("#0", width=1)
      treeview_r.heading("#0", text="")

      treeview_r.column("#1",width=180)
      treeview_r.heading("one", text="date")

      treeview_r.column("#2",width=130)
      treeview_r.heading("two", text="sitting time(sec)")

      treeview_r.column("#3",width=120)
      treeview_r.heading("three", text="good(%)")

      treeview_r.column("#4",width=120)
      treeview_r.heading("four", text="to lef(%)")

      treeview_r.column("#5",width=120)
      treeview_r.heading("five", text="to right(%)")

      treeview_r.column("#6",width=120)
      treeview_r.heading("six", text="to forward(%)")

      c.execute("select * from record where num=(select num from record order by rowid desc limit 1)")
      var = c.fetchone()
      date = var[1]
      time = var[2]
      if var[3]==0:
          good = var[3]
      else:
          good = (int(var[3])/(int(var[2])-int(var[7])))*100
      if var[4]==0:
          left = var[4]
      else:
          left = (int(var[4])/(int(var[2])-int(var[7])))*100
      if var[5]==0:
          right = var[5]
      else:
          right = (int(var[5])/(int(var[2])-int(var[7])))*100
      if var[6]==0:
          forward = var[6]
      else:
          forward = (int(var[6])/(int(var[2])-int(var[7])))*100

      treelist=[(date,time,good,left,right,forward)]

      for i in range(len(treelist)):
         treeview_r.insert('','end',text=i,values=treelist[i])

   testbut=Button(root, text="push!", command=threading.Thread(target=pr,daemon=True).start())
   testbut.pack(pady="10")
   testbut.pack_forget()
   #status label
   statLB = Label(root,text="status")
   statLB.pack()

   #show record
   record_btn = Button(root, text="show record", command=new_window)
   record_btn.pack(pady="5",side="bottom")

   #end
   root.mainloop()

if __name__ =='__main__':
   countA = 0
   countY = 0
   countL = 0
   countR = 0
   countB = 0
   countS = 0

   my_thread1 = threading.Thread(target=fsr)
   my_thread2 = threading.Thread(target=tk)
   my_thread1.daemon = True
   my_thread1.start()
   my_thread2.start()

