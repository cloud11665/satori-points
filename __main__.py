from koishi import Koishi
import logging
from pprint import pprint
import os
import getpass
from datetime import datetime, timedelta
import re

logging.basicConfig(
	level=logging.INFO,
	format="[%(asctime)s] %(levelname)s: %(message)s",
	datefmt="%H:%M:%S"
)

class Colors:
	BLACK = "\033[0;30m"
	RED = "\033[0;31m"
	GREEN = "\033[0;32m"
	BROWN = "\033[0;33m"
	BLUE = "\033[0;34m"
	PURPLE = "\033[0;35m"
	CYAN = "\033[0;36m"
	LIGHT_GRAY = "\033[0;37m"
	DARK_GRAY = "\033[1;30m"
	LIGHT_RED = "\033[1;31m"
	LIGHT_GREEN = "\033[1;32m"
	YELLOW = "\033[1;33m"
	LIGHT_BLUE = "\033[1;34m"
	LIGHT_PURPLE = "\033[1;35m"
	LIGHT_CYAN = "\033[1;36m"
	LIGHT_WHITE = "\033[1;37m"
	BOLD = "\033[1m"
	FAINT = "\033[2m"
	ITALIC = "\033[3m"
	UNDERLINE = "\033[4m"
	BLINK = "\033[5m"
	NEGATIVE = "\033[7m"
	CROSSED = "\033[9m"
	END = "\033[0m"
	# cancel SGR codes if we don't write to a terminal
	if not __import__("sys").stdout.isatty():
		for _ in dir():
			if isinstance(_, str) and _[0] != "_":
				locals()[_] = ""
	else:
		# set Windows console in VT mode
		if __import__("platform").system() == "Windows":
			kernel32 = __import__("ctypes").windll.kernel32
			kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
			del kernel32

login = input("login:\n> ")
print("\033[A"+" "*20+"\033[A")
pwd = getpass.getpass("password:\n> ")
print("\033[A"+" "*20+"\033[A")
acc = Koishi(login,pwd)
cid = int(input("contest id:\n> "))
print("\033[A"+" "*20+"\033[A")

points = 0

if not (selected := filter(lambda x:x.id==cid, acc.contests)):
	logging.error("Invalid contest id, exiting.")
	exit()

selected,= selected
results = selected.results

duemap = {}
pointmap = {}
problemmap = {x.code:x for x in selected.problems}
resultmap = {
	x.src:
		[*reversed([y for y in results if y.src==x.src])]
	for x in results}

for code in [*problemmap.keys()]:
	if problemmap[code].note in ("","(zadanie dodatkowe)", "(obie grupy)"):
		if any(map(lambda x:x.ok, resultmap.get(code,[]))):
			pointmap[code] = 1
		else:
			pointmap[code] = 0
		resultmap.pop(code,...)
		problemmap.pop(code,...)

for code in [*resultmap.keys()]:
	#due = re.match(r"^\(termin: (\d{1,2}|\.)+\)$", problemmap[code].note)
	try:
		due = problemmap[code].note
		due = due[due.rfind(" "):][:-1].strip()
	except:
		problemmap.pop(code)
		resultmap.pop(code)
		continue

	# problem due date
	due = datetime.strptime(due, r"%d.%m.%Y") \
	        .replace(hour=23, minute=59, second=59)

	for res in [*resultmap[code]]:
		if res.date > due + timedelta(days=7):
			if res.ok:
				pointmap[code] = 0
			resultmap[code].remove(res)

	resultmap[code] = [*filter(lambda x:x.ok, resultmap[code])]

	if resultmap[code] == []:
		if code not in pointmap:
			pointmap[code] = -1
		resultmap.pop(code)
		continue

	duemap[code] = due

for code in duemap:
	res = [*filter(lambda x:x.ok, resultmap[code])][0]
	due = duemap[code]
	off = res.date.timestamp() - due.timestamp()
	if off < 0:
		pointmap[code] = 1
	else:
		pointmap[code] = round(1-off/0x93A80, 3)

for x in sorted(pointmap.keys()):
	key = f"*{x[:-1]}" if x.endswith("*") else x
	val = pointmap[x]
	col = Colors.RED if val<0 else Colors.YELLOW if val==0 else Colors.GREEN
	val = f"{val}.000" if val//1 == val else val
	sep = " " if pointmap[x] < 0 else "  "
	print(f"{key.rjust(4)}:{sep}{col}{val}{Colors.END}")
print("-"*15)
print(f"suma: {sum(pointmap.values())}")
