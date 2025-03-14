#Importing Libraries
from tkinter import *
import sqlite3 


root = Tk()
root.title('Taskflow App')

#Create the connector
dataConnector = sqlite3.connect('userData.db')

root.mainloop()
