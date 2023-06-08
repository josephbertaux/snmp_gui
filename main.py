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
		return ch_map

	lines = iter(f.readlines())
	while True:
		try:
			line = next(lines)
		except StopIteration:
			break

		l = parse("{} {}\n", line)
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

		if args[i][0:1] == "-":
			flg = args[i][1:]
			continue

		if(flg == ""):
			crate_guis += [MpodCrateGui(args[i], args[i] if "a" not in tmp else tmp["a"], {} if "f" not in tmp else tmp["f"], "", "-m +WIENER-CRATE-MIB")]
			tmp = {}
			continue

		if(flg == "f"):
			tmp["f"] = GetMap(args[i])

		if(flg == "a"):
			tmp["a"] = args[i]

		flg = ""

	return crate_guis

def main(args):
	crate_guis = GetCrateGuis(args)
	if crate_guis == []:
		print("No ips specified in argument lists")
		print("Exiting")
		return

	gui = MpodGui(crate_guis)
	while gui.Loop():
		continue

if __name__ == "__main__":
	args = sys.argv
	if args[0] is not None:
		args.pop(0)
	main(args)

