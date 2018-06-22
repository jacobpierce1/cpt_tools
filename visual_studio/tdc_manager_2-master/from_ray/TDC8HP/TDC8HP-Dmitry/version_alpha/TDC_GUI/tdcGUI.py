#simple GUI for TDC manipulation
from Tkinter import *
import time

from multiprocessing import Process, Queue
from Queue import Empty

queue = Queue() 

class TDCpanel(Frame, object):
	
	def __init__(self):
		super(TDCpanel, self).__init__()   
		 
		self.initUI()
		
	def initUI(self):
		#Main frame
		self.master.title("TDC8HP Control Panel")
		self.pack(fill=BOTH, expand=True)
		
		#Button's frame
		self.frameBTN = Frame(self)
		self.frameBTN.pack(fill=X)
		
		self.startBTN = Button(self.frameBTN, text="Start", command=self.start, bg='green', fg='black')
		self.startBTN.pack(side=LEFT, fill=X, expand=TRUE)
		
		self.stopBTN = Button(self.frameBTN, text="Stop", command=self.stop, bg='red', fg='white')
		self.stopBTN.pack(side=RIGHT, fill=X, expand=TRUE)
		
		#Text's frame
		self.frameTXT = Frame(self)
		self.frameTXT.pack(fill=BOTH)

		self.scrollBar = Scrollbar(self.frameTXT)
		self.scrollBar.pack(side=RIGHT, fill=Y)
		
		self.outputTXT = Text(self.frameTXT,  wrap=WORD, yscrollcommand=self.scrollBar.set,)
		self.outputTXT.pack(side=LEFT, fill=BOTH, expand=TRUE)
		
		self.scrollBar.config(command=self.outputTXT.yview)
		#initText = "\
#Integer posuere erat a ante venenatis dapibus.\
#Posuere velit aliquet.\
#Aenean eu leo quam. Pellentesque ornare sem.\
#Lacinia quam venenatis vestibulum.\
#Nulla vitae elit libero, a pharetra augue.\
#Cum sociis natoque penatibus et magnis dis.\
#Parturient montes, nascetur ridiculus mus.\n"
		#self.outputTXT.insert(END, initText)
		
	def start(self):
		#self.startBTN.flash()
		self.startBTN.config(bg='gray')
		self.startBTN.config(state='disabled')
		#self.outputTXT.delete("1.0", END)
		
		self.slowProc = Process(target=slowFunc, args=(queue, ))
		self.slowProc.start()
		self.after(10, self.getValue)
	
	def stop(self):
		print("Stop TDC\n")
		quit()

	def getValue(self):
		if(self.slowProc.is_alive()):
			self.after(10, self.getValue)
			return
		else:
			try:
				self.outputTXT.insert(END, queue.get(0))
				self.outputTXT.insert(END, "\n")
				self.startBTN.config(state='normal')
				self.startBTN.config(bg='green')
			except Empty:
				self.outputTXT.insert(END, "Queue is empty.\n")
				

#slowFunc makes time consuming calculations.
#Thant's why it will be executed in a separate process
#The calculation time will be send to queue 
#and GUI will show the result in the text window 

def slowFunc(queue):
	start_time = time.time()
	sum=0
	for i in xrange(100000000):
		sum += i
	stop_time  = time.time()
	dt = stop_time - start_time
	queue.put(dt)
	
if __name__ == '__main__':
	
	root = Tk()
	root.geometry("350x150+100+300")
	app = TDCpanel()
	root.mainloop()  

