import threading
import time
from parse import parse
import PySimpleGUI as sg

from MpodController import *

class MpodChannelGui():
	def TurnOn(self, v=""):
		if "v_set_text" in self.dict and v == "":
			v = self.dict["v_set_text"].get()
		if v != "":
			self.controller.SetVoltage(self.ch, v)
		self.controller.TurnOn(self.ch)

	def TurnOff(self):
		self.controller.TurnOff(self.ch)

	def Clear(self):
		self.controller.Clear(self.ch)

	def Reset(self):
		self.controller.Reset(self.ch)

	def SetVoltage(self, v):
		self.controller.SetVoltage(ch, v)

	def RefreshStatus(self, val=""):
		if val == "":
			self.dict["status_text"].update("Err", background_color="black")
			return

		vals = val.split()
		if vals[0] == "04":
			self.dict["status_text"].update("Trp", background_color="black")
			return

		if vals[0] == "00":
			self.dict["status_text"].update("Off", background_color="red")
			return

		if vals[0] != "80":
			self.dict["status_text"].update("Err", background_color="black")
			return

		self.dict["status_text"].update("On", background_color="green")
		if vals[1] is None or vals[1] == "01":
			return

		if vals[1] == "09":
			self.dict["status_text"].update("Rmp Down", background_color="orange")
			return

		if vals[1] == "11":
			self.dict["status_text"].update("Rmp Up", background_color="orange")
			return

		self.dict["status_text"].update(val)

	def __init__(self, ch, ip, alias="", path="", mib="-m +WIENER-CRATE-MIB"):
		self.ip = str(ip)
		self.ch = str(ch)
		self.controller = MpodController(ip, path, mib)
		self.dict = {}
		self.dict["label_text"] = sg.Text("{:^8}".format(ch if alias == "" else alias), size=(8,1))
		self.dict["status_text"] = sg.Text("", size=(9,1))
		self.dict["on_button"] = sg.Button(" On", size=(3,1), key=lambda: self.TurnOn())
		self.dict["off_button"] = sg.Button("Off", size=(3,1), key=lambda: self.TurnOff())
		self.dict["reset_button"] = sg.Button("Reset", size=(5,1), key=lambda: self.Reset())
		self.dict["clear_button"] = sg.Button("Clear", size=(5,1), key=lambda: self.Clear())

		self.layout = [sg.Frame("", [[val for key, val in self.dict.items()]])]
		#self.layout = [val for key, val in self.dict.items()]

class MpodCrateGui():
	def CrateOn(self):
		self.controller.CrateOn()

	def CrateOff(self):
		self.controller.CrateOff()

	def CrateClear(self):
		self.controller.CrateClear()

	def CrateInit(self):
		self.controller.Init()

	def ModuleOn(self, m):
		return lambda: self.controller.ModuleOn(m)

	def ModuleOff(self, m):
		return lambda: self.controller.ModuleOff(m)

	def ModuleClear(self, m):
		return lambda: self.controller.ModuleClear(m)

	def Refresh(self):
		return_code, output = self.controller.Walk("outputStatus")
		#if return_code == "":
		#	return

		#if int(return_code) != 0:
		#	print("Error: " + str(return_code))
		#	return

		#if output == "":
		#	return

		#debug block
		f = None
		try:
			f = open("snmpwalk_-Oq_.txt", "r")
		except FileNotFoundError:
			print("Could not open file")
			return
		output = f.read()
		#~debug block

		upper_params = [{"col":"black", "txt":"All Off"} for upper in self.uppers]
		lower_params = [{"col":"green", "txt":"All On "} for lower in self.lowers]
		output = output.split("\n")
		for line in output:
			if line == "":
				continue
			vals = parse("{}::{oid}.{ch} \"{val}\"", line)
			if vals is None:
				continue
			self.dict[vals["ch"]].RefreshStatus(vals["val"])

			m = int(int(parse("u{}", vals["ch"])[0]) / 100)
			upper_params[m] = self.RefreshUpper(upper_params[m], vals["val"])
			lower_params[m] = self.RefreshLower(lower_params[m], vals["val"])

		for m in range(0, len(self.uppers)):
			self.uppers[m].update(upper_params[m]["txt"], background_color=upper_params[m]["col"])
		for m in range(0, len(self.lowers)):
			self.lowers[m].update(lower_params[m]["txt"], background_color=lower_params[m]["col"])

	def RefreshUpper(self, m, val=""):
		if val == "":
			return m

		vals = val.split()

		if vals[0] == "80" and (vals[1] is None or (vals[1] != "09" and vals[1] != "11")):
			m["txt"] = "Any On "
			m["col"] = "green"
		if m["col"] == "green":
			return m

		if vals[0] == "80" and (vals[1] is not None and (vals[1] == "09" or vals[1] == "11")):
			m["txt"] = "Any On "
			m["col"] = "orange"
		if m["col"] == "orange":
			return m

		if vals[0] == "01":
			m["txt"] = "All Off"
			m["col"] = "red"
		if m["col"] == "red":
			return m

		if vals[0] == "04":
			m["txt"] = "All Off"
			m["col"] = "black"
		if m["col"] == "black":
			return m

		return m

	def RefreshLower(self, m, val):
		if val == "":
			return m

		vals = val.split()

		if vals[0] == "04":
			m["txt"] = "Any Off"
			m["col"] = "black"
		if m["col"] == "black":
			return m

		if vals[0] == "00":
			m["txt"] = "Any Off"
			m["col"] = "red"
		if m["col"] == "red":
			return m

		if vals[0] == "80" and (vals[1] is not None and (vals[1] == "09" or vals[1] == "11")):
			m["txt"] = "All On "
			m["col"] = "orange"
		if m["col"] == "orange":
			return m

		if vals[0] == "80" and (vals[1] is None or (vals[1] != "09" and vals[1] != "11")):
			m["txt"] = "All On "
			m["col"] = "green"
		if m["col"] == "green":
			return m

		return m

	def __init__(self, ip, alias="", ch_map={}, path="", mib="-m +WIENER-CRATE-MIB"):
		self.ip = str(ip)
		self.controller = MpodCrateController(ip, path, mib)
		self.alias = alias if alias != "" else self.ip
		self.ch_map = ch_map
		self.indicator_width = 6
		self.tab_width = self.indicator_width + 4
		self.refresh_wait = 15

		self.dict = {}
		self.tabs = {}
		self.uppers = []
		self.lowers = []
		self.layout = []
		self.layout += [sg.Button("Crate On", key=lambda: self.CrateOn())]
		self.layout += [sg.Button("Crate Off", key=lambda: self.CrateOff())]
		self.layout += [sg.Button("Crate Clear", key=lambda: self.CrateClear())]
		self.layout += [sg.Button("Crate Init", key=lambda: self.CrateInit())]
		self.layout = [self.layout]
		for m in self.controller.channels:
			s = int(int(parse("u{}", m[0])[0]) / 100)
			tmp = []
			tmp += [sg.Button("Module On", key=self.ModuleOn(s))]
			tmp += [sg.Button("Module Off", key=self.ModuleOff(s))]
			tmp += [sg.Button("Module Clear", key=self.ModuleClear(s))]
			tmp = [tmp]

			s = str(s)
			self.dict["upper_indicator{}".format(s)] = sg.Text("upper", size=(self.indicator_width, 1))
			self.uppers += [self.dict["upper_indicator{}".format(s)]]
			self.dict["lower_indicator{}".format(s)] = sg.Text("lower", size=(self.indicator_width, 1))
			self.lowers += [self.dict["lower_indicator{}".format(s)]]
			for ch in m:
				self.dict[ch] = MpodChannelGui(ch, self.ip, ch if ch not in self.ch_map else self.ch_map[ch], path, mib)
				tmp += [self.dict[ch].layout]

			self.tabs[s] = sg.Tab((s if s not in ch_map else ch_map[s]).center(self.tab_width), tmp)

		self.layout += [self.uppers]
		self.layout += [self.lowers]
		self.layout += [[sg.TabGroup([[val for key, val in self.tabs.items()]])]]

class MpodGui():
	def AllOn(self):
		for crate_gui in self.crate_guis:
			self.window.perform_long_operation(crate_gui.CrateOff, "Event")

	def AllOff(self):
		for crate_gui in self.crate_guis:
			self.window.perform_long_operation(crate_gui.CrateOff, "Event")

	def AllClear(self):
		for crate_gui in self.crate_guis:
			self.window.perform_long_operation(crate_gui.CrateClear, "Event")

	def AllInit(self):
		thrs = []
		for crate_gui in self.crate_guis:
			thrs += [threading.Thread(target=crate_gui.CrateInit)]
		for thr in thrs:
			thr.start()
		for thr in thrs:
			thr.join()
		print("Init done")

	def Refresh(self):
		t = time.time()
		thrs = []
		for crate_gui in self.crate_guis:
			thrs += [threading.Thread(target=crate_gui.Refresh)]
		for thr in thrs:
			thr.start()
		for thr in thrs:
			thr.join()
		t = self.refresh_wait - (time.time() - t)
		if(t > 0):
			time.sleep(t)

	def CallRefresh(self):
		self.window.perform_long_operation(self.Refresh, self.update_id)

	def __init__(self, crate_guis):
		self.update_id = "Update"
		self.refresh_wait = 15

		self.layout = []
		self.layout += [sg.Button("All On", key=lambda: self.AllOn())]
		self.layout += [sg.Button("All Off", key=lambda: self.AllOff())]
		self.layout += [sg.Button("All Clear", key=lambda: self.AllClear())]
		self.layout += [sg.Button("All Init", key=lambda: self.AllInit())]
		self.layout = [self.layout]

		self.crate_guis = crate_guis
		self.layout += [[sg.Frame(crate_gui.alias, crate_gui.layout) for crate_gui in self.crate_guis]]

		self.window = sg.Window("Mpod Control Gui", [[sg.Column(self.layout, scrollable=True, expand_x=True, expand_y=True)]], resizable=True, finalize=True)
		self.window.bind("<Configure>", "Configure")
		self.CallRefresh()

	def Loop(self):
		event, values = self.window.read()

		if event == sg.WIN_CLOSED:
			try:
				self.window.close()
				return False
			except:
				return False

		if callable(event):
			self.window.perform_long_operation(event, "Event")

		if event == self.update_id:
			self.CallRefresh()

		return True
