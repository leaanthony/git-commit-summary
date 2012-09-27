#!/usr/bin/env python

import optparse, sys, os, datetime, dateutil.parser
from collections import defaultdict
import subprocess

parser = optparse.OptionParser("Usage: %prog [options]")

cmd = "git log"

def fatalError(msg):
	print "Fatal Error: " + msg
	sys.exit(-1)

parser.add_option("-d", "--dir", help="Set repository directory", action="store")

(opts, args) = parser.parse_args()

if opts.dir:
	try:
		os.chdir(opts.dir)
	except:
		fatalError("Directory '%s' is not valid" % opts.dir)

class commit:

	def __init__(self, hash=""):
		self.hash = hash
		self.author = ""
		self.date = ""
		self.notes = []

	def __repr__(self):
		result = "<commit "
		count = 0
		for v in vars(self).items():
			if count > 0:
				result += ", "
			if type(v[1]) == type(0):
				result += "%s=%s" % (v[0],v[1])
			else:
				result += "%s='%s'" % (v[0],v[1])
			count += 1
		result += ">"
		return result 


class commitlog:

	def __init__(self):
		self.logs = []

	def parse(self):
		this_commit = None
		p = subprocess.Popen(cmd.split(), shell=False, stdout=subprocess.PIPE)
		o,r = p.communicate()
		log = o.split("\n")
		if p.returncode != 0:
			sys.exit(p.returncode)

		for l in log:
			sl = l.strip()
			if sl.startswith("commit"):
				if this_commit != None:
					self.logs.append(this_commit)
				this_commit = commit( sl.split()[1] )
			elif sl.lower().startswith("author"):
				if this_commit == None:
					fatalError("Author with no commit?:\n\n" + sl)
				this_commit.author = " ".join(sl.split()[1:])
			elif sl.lower().startswith("date"):
				this_commit.date = dateutil.parser.parse(" ".join(sl.split()[1:]).strip())
			else:
				if len(sl) > 0:
					this_commit.notes.append(sl)


		if this_commit != None:
			self.logs.append(this_commit)

	def getByAuthor(self, logs=None):
		if logs == None: logs = self.logs
		result = defaultdict(list)
		for l in logs:
			result[l.author].append(l)
		return result


	def outputByAuthor(self):
		print "# Git log summary (" + str(datetime.datetime.today().strftime('%d %h %Y')) +")"
		by_author = self.getByAuthor()
		for k in by_author.keys():
			print "## Author: " + k
			for c in by_author[k]:
				print "  * %s: %s  " % (c.date.strftime('%d %h %Y'),c.notes[0])
				if len(c.notes) > 1:
					for n in c.notes[1:]:
						print " "*4 + n.strip()


c = commitlog()
c.parse()
c.outputByAuthor()

