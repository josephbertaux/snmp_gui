import subprocess as sp

class MpodController:
	def __init__(self, ip, path="", mib="-m +WIENER-CRATE-MIB"):
		self.path = str(path)
		self.mib = str(mib)
		self.ip = str(ip)

		self.debug = True

		self.default_voltage = "100" # Default voltage to ramp to when turned on
		self.default_current = "0.0005" # Default current limit in amps
		self.default_risefall = "1" # Default ramp speeds

	def Walk(self, oid, op=""):
		oid = str(oid)
		op = str(op)

		args = "{}snmpwalk -Oq{} -v 2c {} -c public {} {}".format(self.path, op, self.mib, self.ip, oid).split()

		if(self.debug):
			print(args)
			return "", ""
		else:
			cp = sp.run(args, capture_outpue=True, encoding='utf-8')
			return cp.returncode, cp.stdout if cp.returncode == 0 else cp.stderr

	def Get(self, oid, ch, op=""):
		oid = str(oid)
		ch = str(ch)
		op = str(op)

		args = "{}snmpget -Oq{} -v 2c {} -c public {} {}.{}".format(self.path, op, self.mib, self.ip, oid, ch).split()

		if(self.debug):
			print(args)
			return "", ""
		else:
			cp = sp.run(args, capture_outpue=True, encoding='utf-8')
			return cp.returncode, cp.stdout if cp.returncode == 0 else cp.stderr

	def Set(self, oid, ch, flg, val, op=""):
		oid = str(oid)
		ch = str(ch)
		flg = str(flg)
		val = str(val)
		op = str(op)

		args = "{}snmpset -Oq{} -v 2c {} -c guru {} {}.{} {} {}".format(self.path, op, self.mib, self.ip, oid, ch, flg, val).split()

		if(self.debug):
			print(args)
			return "", ""
		else:
			cp = sp.run(args, capture_outpue=True, encoding='utf-8')
			return cp.returncode, cp.stdout if cp.returncode == 0 else cp.stderr

	def Init(self, ch):
		# Trip funcitonality
		#(64 is ramp down, 128 is emergency off, 192 is all off)
		self.Set("outputSupervisionBehavior", ch, "i", "64")

		# Time in ms for current to exceed the max for tripping to be enabled
		# (min 16)
		self.Set("outputTripTimeMaxCurrent", ch, "i", "16")

		# Voltage rise and fall rates in V/s
		self.Set("outputVoltageRiseRate", ch, "F", self.default_risefall)
		self.Set("outputVoltageFallRate", ch, "F", self.default_risefall)

		# Maximum current threshold in A
		self.Set("outputCurrent", ch, "F", self.default_current, "p 10.9")
		self.Set("outputSupervisionMaxCurrent", ch, "F", self.default_current, "p 10.9") # Not actually important

		# Voltage setting in V
		self.Set("outputVoltage", ch, "F", self.default_voltage)

	def TurnOn(self, ch):
		self.Set("outputSwitch", ch, "i", "1")

	def TurnOff(self, ch):
		self.Set("outputSwitch", ch, "i", "0")

	def Clear(self, ch):
		self.Set("outputSwitch", ch, "i", "10")

	def Reset(self, ch):
		self.Clear(ch)
		self.TurnOn(ch)

	def SetVoltage(self, ch, v):
		self.Set("outputVoltage", ch, "F", v)

class MpodCrateController(MpodController):
	def __init__(self, ip, path="", mib="-m +WIENER-CRATE-MIB"):
		super().__init__(ip, path, mib)
		self.num_channels = 16 # channels per module
		self.num_modules = 8 # number of modules
		self.channels = [["u{:d}".format(m * 100 + ch) for ch in range(0, self.num_channels)] for m in range(0, self.num_modules)]

	def Init(self):
		# disableKill
		self.Set("groupsSwitch", "64", "i", "4")
		for m in self.channels:
			for ch in m:
				super().Init(ch)

	def CrateOn(self):
		self.Set("groupsSwitch", "64", "i", "1")

	def CrateOff(self):
		self.Set("groupsSwitch", "64", "i", "0")

	def CrateClear(self):
		self.Set("groupsSwitch", "64", "i", "10")

	def CrateVoltage(self, v):
		for m in self.channels:
			for ch in m:
				self.Set("outputVoltage", ch, "F", v)

	def ModuleOn(self, m):
		for ch in self.channels[m]:
			self.Set("outputSwitch", ch, "i", "1")

	def ModuleOff(self, m):
		for ch in self.channels[m]:
			self.Set("outputSwitch", ch, "i", "0")

	def ModuleClear(self, m):
		for ch in self.channels[m]:
			self.Set("outputSwitch", ch, "i", "10")

	def ModuleVoltage(self, m, v):
		for ch in self.channels[m]:
			self.Set("outputVoltage", ch, "F", v)

	def ChannelOn(self, ch):
		self.Set("outputSwitch", ch, "i", "1")

	def ChannelOff(self, ch):
		self.Set("outputSwitch", ch, "i", "0")

	def ChannelClear(self, ch):
		self.Set("outputSwitch", ch, "i", "10")

	def ChannelVoltage(self, m, v):
		self.Set("outputVoltage", ch, "F", v)
