import threading
import PySimpleGUI as sg
from MpodController import *

class MpodChannelGui():
	def __init__(self, ch, alias, ip, path="", mib="-m +WIENER-CRATE-MIB"):
		self.ip = str(ip)
		self.ch = str(ch)
		self.controller = MpodController(ip, path, mib)
		self.dict = {}
		self.dict['label_text'] = sg.Text("{:^8}".format(ch if alias == "" else alias), size=(8,1))
		self.dict['status_text'] = sg.Text("", size=(9,1))

		#self.layout = [sg.Frame("", [val for key, val in self.dict.items()])]
		self.layout = [val for key, val in self.dict.items()]

class MpodCrateGui():
	def __init__(self, ip, path="", mib="-m +WIENER-CRATE-MIB", ch_map={}):
		self.ip = str(ip)
		self.controller = MpodCrateController(ip, path, mib)
		self.ch_map = ch_map
		
		self.dict = {}
		self.layout = []
		for m in self.controller.channels:
			tmp = []
			for ch in m:
				self.dict[ch] = MpodChannelGui(ch, ch if ch not in ch_map else ch_map[ch], ip, path, mib)
				tmp += [self.dict[ch].layout]
			self.layout += [sg.Frame('', tmp)]

		self.controller.Init()

class MpodGui():
	def __init__(self, crate_guis):
		self.crate_guis = crate_guis
		self.layout = [crate_gui.layout for crate_gui in self.crate_guis]
		self.window = sg.Window('Mpod Control Gui', [self.layout])

	def Loop(self):
		event, values = self.window.read()

		if event == sg.WIN_CLOSED:
			try:
				self.window.close()
				return False
			except ValueError:
				return False
