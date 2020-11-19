import argparse
import glob
import json
import logging
import os
import re
import requests
import subprocess
import sys
import time
import tkinter as tk 
import tkinter.ttk as ttk
from concurrent import futures

thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)

class PrepareCalculations():
	
	def __init__(self):
		self.export_button_flag = False
		self.main_window()

	def main_window(self):
		
		self.root = tk.Tk()
		self.root.attributes('-type', 'dialog')
		self.root.title("GAMESS Input Builder - by tetsuo420")
		self.root.config(background='#2c302c')

		scrollbar = tk.Scrollbar(self.root)
		self.textbox = tk.Text(self.root, height=40, width=120, bg='black')
		self.textbox.tag_config("yellow", background="black", foreground="yellow")
		self.textbox.tag_config("green", background="black", foreground="green")
		self.textbox.tag_config("orange", background="black", foreground="orange")
		self.textbox.tag_config("red", background="black", foreground="red2")
		self.textbox.tag_config("finish", background="black", foreground="lime green")
		self.textbox.tag_config("result", background="black", foreground="sky blue")
		self.textbox.tag_config("total", background="black", foreground="CadetBlue1")
		self.textbox.tag_config("white", background="black", foreground="white")

		self.inp_filelist = [file for file in os.listdir() if file.endswith('.inp')]

		self.file_name = tk.Text(self.root, height=1, width=50, bg='black') 
		self.file_name.grid(column=4, row=0, pady=10) 
		self.file_name.tag_config("total", background="black", foreground="CadetBlue1")
		self.file_name.tag_config("white", background="black", foreground="white")


		# self.temp_text = tk.StringVar()
		# self.temp_text_label = tk.Label(self.root, textvariable=self.temp_text, width=17)
		# self.temp_text_label.config(background="#033e4d")		
		# self.temp_text_label.grid(row=2, column = 1, sticky=tk.W, padx=50, pady=5)

		for y in range(10):
			tk.Grid.rowconfigure(self.root, y, weight=1)
			tk.Grid.columnconfigure(self.root, y, weight=1)

		scrollbar.grid(row=1, column=10, sticky=tk.N+tk.S)
		scrollbar.config(background="#2c302c")
		self.textbox.grid(row=1, column=0, columnspan=10)
		scrollbar.config(command=self.textbox.yview)
		self.textbox.config(yscrollcommand=scrollbar.set)
		
		self.read_button = tk.Button(self.root, text ='Read Folder', command=self.read_molecules, width=10, height=2, cursor='heart')
		self.read_button.config(background="#2c302c", foreground="white")
		self.read_button.grid(row=2, column=4, padx=10, pady=10)


		style1 = ttk.Style()
		style1.configure("Mine.TCheckbutton", background="#033e4d", indicatorrelief="groove")
		style1.theme_settings("default", 
	   	{"TCheckbutton": {
		   	"configure": {"padding": 5},
			  	"map": {
					"background": [("active", "#033e4d"),("!disabled", "#033e4d")],
					"fieldbackground": [("!disabled", "#5C5C5C")],
				   	"foreground": [("focus", "lightgray"),("!disabled", "lightgray")], "indicatorcolor": [('selected','green2'),('pressed','CadetBlue2'),('!disabled', 'red')]					
			  }
		  }
	   })

		def check_flag1():
			button2 = tk.Button(self.root, text="Export", command=self.save_file, width=10, height=2)
			button2.config( background="#2c302c", foreground="white")
			
			if self.export_button_flag == True:
				button2.grid(row=2, column=6)
			else:
				try:
					button2.remove()
				except AttributeError:
					pass
			
			self.root.after(500, check_flag1)
			
		self.root.after(1000, check_flag1)
		self.root.mainloop()

	def read_molecules(self):

		self.read_button.destroy()
		self.next_button = tk.Button(self.root, text ='>', command=self.next_molecule, width=2, height=1)
		self.prev_button = tk.Button(self.root, text ='<', command=self.prev_molecule, width=2, height=1)
		self.next_button.configure(background="#2c302c", foreground="white")
		self.prev_button.configure(background="#2c302c", foreground="white")
		self.prev_button.grid(row=0, column=3, padx=1, stick=tk.E ,pady=10)
		self.next_button.grid(row=0, column=5, padx=1, stick=tk.W, pady=10)

		file_list = [file for file in os.listdir() if file.endswith(".pdb") or file.endswith(".log")]

		if len(file_list) == 0:
			self.textbox.insert(tk.END,f"\n   E   |  No '.pdb' or '.log' files found on current folder '{os.getcwd()}'.", "red")

		self.files_dict = {}

		for file_name in file_list:
			if file_name.endswith('.pdb'):
				subprocess.call([f"obabel -i pdb {file_name} -O {file_name[:-4]}.inp"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=dict(os.environ, PATH="/usr/bin"))
				with open(f"{file_name[:-4]}.inp", "r") as f:
					text = f.read()
				
				self.files_dict[file_name] = text
				os.remove(f"{file_name[:-4]}.inp")
			
			elif file_name.endswith('.log'):
				subprocess.call([f"obabel -i log {file_name} -O {file_name[:-4]}.inp"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=dict(os.environ, PATH="/usr/bin"))
				with open(f"{file_name[:-4]}.inp", "r") as f:
					text = f.read()
				
				self.files_dict[file_name] = text
				os.remove(f"{file_name[:-4]}.inp")

			self.current_file = list(self.files_dict.keys())[0]


		self.current_index = 0
		self.molec_list_len = len(list(self.files_dict.keys()))
		self.textbox.insert(tk.END,f"{self.files_dict[self.current_file]}", "white")
		self.file_name.insert(tk.END, f"{self.current_file} - ({self.current_index+1}/{self.molec_list_len})", "white")

		self.add_calculation_preset = tk.Button(self.root, text="Add calculation", width=10, height=2, command=self.calc_window)
		self.add_calculation_preset.config(background="#2c302c", foreground="white")
		self.add_calculation_preset.grid(row=2, column=4, padx=10, pady=10)

	def next_molecule(self):
		
		self.textbox.delete(1.0,tk.END)
		self.file_name.delete(1.0,tk.END)

		self.current_index = self.current_index + 1

		if self.current_index > self.molec_list_len-1:
			self.current_index = 0

		new_molecule = list(self.files_dict.keys())[self.current_index]
		self.current_file = new_molecule
		new_text = self.files_dict[new_molecule]

		self.file_name.insert(tk.END, f"{new_molecule} - ({self.current_index+1}/{self.molec_list_len})", "white")
		self.textbox.insert(tk.END,f"{new_text}", "white")

		if self.calc_dict[self.calc_choosen]['flag'] == 1:
			self.export_button_flag = True
		else:
			self.export_button_flag = False


	def prev_molecule(self):
		
		self.textbox.delete(1.0,tk.END)
		self.file_name.delete(1.0,tk.END)

		self.current_index = self.current_index - 1
		
		if self.current_index < 0:
			self.current_index = self.molec_list_len-1

		new_molecule = list(self.files_dict.keys())[self.current_index]
		self.current_file = new_molecule

		new_text = self.files_dict[new_molecule]

		self.file_name.insert(tk.END, f"{new_molecule} - ({self.current_index+1}/{self.molec_list_len})", "white")
		self.textbox.insert(tk.END,f"{new_text}", "white")

		if self.calc_dict[self.calc_choosen]['flag'] == 1:
			self.export_button_flag = True
		else:
			self.export_button_flag = False


	def calc_window(self):
		self.calc_window = tk.Toplevel(self.root)
		self.calc_window.attributes('-type', 'dialog')
		self.calc_window.config(background='#2c302c')
		self.calc_window.wm_geometry("500x150")

		for y in range(10):
			tk.Grid.rowconfigure(self.calc_window, y, weight=1)
			tk.Grid.columnconfigure(self.calc_window, y, weight=1)

		tk.Label(self.calc_window, text="Choose which molecule to open with 3D viewer:", foreground="white", background="#2c302c").grid(row = 2, column = 4)
		
		self.tkvar = tk.StringVar(self.calc_window)
		self.tkvar.set('Choose a preset')

		def change_dropdown(*args):
			self.tkvar.get()

		with open("/home/tetsuo420/Documents/.scripts/prepare_gamess/calc_methods.json", "r") as f1:
			file = f1.read()
		self.calc_dict = json.loads(file)

		popupMenu = tk.OptionMenu(self.calc_window, self.tkvar, *self.calc_dict)
		popupMenu.config(width=20, relief='raised', background="#2c302c", foreground="white")
		popupMenu.grid(row = 4, column = 4)

		self.tkvar.trace('w', change_dropdown)

		button = tk.Button(self.calc_window, text="Choose", command=self.get_calc)
		button.config( background="#2c302c", foreground="white")
		button.grid(row=5, column=4)

		self.calc_window.mainloop()

	def get_calc(self):
		self.calc_choosen = self.tkvar.get()
		self.calc_window.destroy()

		text_to_edit = self.files_dict[self.current_file]

		new_text = text_to_edit[:36]+f"{self.calc_dict[self.calc_choosen]['string']}"+text_to_edit[36:]
		new_text = new_text[:-2]
		self.files_dict[self.current_file] = new_text
		
		self.textbox.delete(1.0,tk.END)
		self.textbox.insert(tk.END, self.files_dict[self.current_file], "white")

		self.export_button_flag = True
		self.calc_dict[self.calc_choosen]['flag'] = 1

	def save_file(self):
		with open(f"{self.current_file[:-4]}.inp", "w+") as f:
			f.write(self.files_dict[self.current_file])

		self.textbox.delete(1.0,tk.END)
		self.textbox.insert(tk.END, f"	  i  | Input file '{self.current_file[:-4]}.inp' created in '{os.getcwd()}' ", "finish")
		
		def open_folder():
			os.system(f"caja {os.getcwd()}/")

		button3 = tk.Button(self.root, text="Open export folder", command=open_folder, width=15, height=2)
		button3.config( background="#2c302c", foreground="white")
		button3.grid(row=2, column=7)

st = PrepareCalculations()
