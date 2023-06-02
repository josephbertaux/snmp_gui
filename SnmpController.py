import subprocess as sp

class SnmpController:
	def __init__(self, ip, ch, path="", mib=" -m +WIENER-CRATE-MIB"):
		self.path = str(path)
		self.mib = str(mib)
		self.ip = str(ip)
		self.ch = str(ch)

	def Get(self, oid, op=""):
		oid = str(oid)
		op = str(op)

		args = "{} -Oqv {} -v 2c {} -c public {} {}.{}".format(self.path, op, self.mib, self.ip, oid, self.ch).split()
		cp = sp.run(args, capture_outpue=True, encoding='utf-8')

		return cp.returncode, cp.stdout if cp.returncode == 0 else cp.stderr

	def Set(self, oid, val, op=""):
		oid = str(oid)
		val = str(val)
		op = str(op)

		args = "{} -Oqv {} -v 2c {} -c guru {} {}.{} {}".format(self.path, op, self.mib, self.ip, oid, self.ch, val).split()
		cp = sp.run(args, capture_outpue=True, encoding='utf-8')

		return cp.returncode, cp.stdout if cp.returncode == 0 else cp.stderr
