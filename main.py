import sys
from MpodController import *
from MpodGui import *

def GetMap(fname):
	f = None
	line = ""
	ch_map = {}
	try:
		f = open(fname, 'r')
	except FileNotFoundError:
		print("\tCouldn't open alias file:")
		print("\t" + fname)
		return None
	lines = iter(f.readlines())
	while True:
		try:
			line = next(lines)
		except StopIteration:
			break

		l = parse('{} {}', line)
		ch_map[l[0]] = l[1]

	return ch_map

def GetCrateGuis(args):
	i = -1
	flg = ""
	tmp = {}
	crate_guis = []
	while True:
		i += 1
		if not i < len(args):
			break
		print(args[i])

		if args[i][0:1] == "-":
			print("\tis flag")
			flg = args[i][1:]
			continue

		if(flg == ""):
			print("\tis ip")
			crate_guis += [MpodCrateGui(args[i], "", "-m +WIENER-CRATE-MIB", tmp)]
			tmp = {}
			continue

		if(flg == "f"):
			print("\tis file")
			tmp["f"] = GetMap(args[i])

		flg = ""

	return crate_guis

def main(args):
	print("Hello World")
	gui = MpodGui(GetCrateGuis(args))
	for crate_gui in gui.crate_guis:
		print("asdf")
		print(crate_gui.layout)
	while gui.Loop():
		continue

if __name__ == "__main__":
	args = sys.argv
	if args[0] is not None:
		args.pop(0)
	main(args)

