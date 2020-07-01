from datetime import date, datetime
import os, re, sys, argparse, urllib.parse, logging, requests

parser = argparse.ArgumentParser(
description="Script ini akan mengekstrak domain dari file yang Anda tentukan dan menambahkannya ke file final"
)
parser.add_argument('--file', action="store", default=None, dest='inputFile',
	help="Tentukan file untuk mengekstrak Domain")
parser.add_argument('--url', action="store", default=None, dest='url',
	help="Tentukan satu per satu halaman Web untuk mengekstrak Domain")
parser.add_argument('--target', action="store", default='all', dest='target',
	help="Tentukan domain target tingkat atas yang ingin kalian temukan dan ekstrak contoh. yahoo.com")
parser.add_argument('--verbose', action="store_true", default=False, dest='verbose',
	help="Enable slightly more verbose console output")
args = parser.parse_args()

if not len(sys.argv) > 1:
	parser.print_help()
	print()
	exit()

### Set the logger up
if not os.path.exists('logs'):
    os.makedirs('logs')
logfileName = "logs/newdomains.{}.log".format(args.target)
logging.basicConfig(filename=logfileName, filemode='a',
format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

outputFile = "final.{}.txt".format(args.target)

def extractDomains(args, inputFile, rawData):
	domains = []
	
	if not args.target:
		print("No target specified, defaulting to finding 'all' domains")
	
	for i in rawData:
		matches = re.findall(r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}', urllib.parse.unquote(urllib.parse.unquote(i)))
		if not args.target.lower() == 'all':
			for j in matches:
			
				if j.find(args.target.lower()) != -1:
					domains.append(j)
		else:
			for j in matches:
				if j.find('.com') != -1:
					domains.append(j)
				elif j.find('.net') != -1:
					domains.append(j)
				elif j.find('.org') != -1:
					domains.append(j)
				elif j.find('.tv') != -1:
					domains.append(j)
				elif j.find('.io') != -1:
					domains.append(j)
	print("File: {} has {} possible domains...".format(inputFile, len(rawData)))

	return domains


results = []

# If files are specified, check them
if args.inputFile:
	fileList = args.inputFile.split(',')
	for inputFile in fileList:
		try:
			with open(inputFile, 'r') as f:
				rawData = f.read().splitlines()
		except UnicodeDecodeError:
			with open(inputFile, 'r', encoding="ISO-8859-1") as f:
				rawData = f.read().splitlines()
				
		results += extractDomains(args, inputFile, rawData)
	
# If a URL is specified, pull that	
if args.url:
	headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"}
	rawData = requests.get(args.url, headers=headers)
	rawData = rawData.text.split('\n')
	results += extractDomains(args, args.url, rawData)
	
# sort and dedupe our results
finalDomains = sorted(set(results))

# read all the domains we already have. 
try:
	with open(outputFile, 'r') as out:
		oldDomains = out.read().splitlines()

# If no final file, create one	
except FileNotFoundError:
	print("Output file not found. Creating one...")
	
	with open(outputFile, 'w') as out:
		for i in finalDomains:
			out.write("{}\n".format(i))
			
	print("{} domains written to output file {}".format(len(finalDomains), outputFile))

# loop through fresh domains. If we don't already have it, add it to final file, notify us, log it.
else:
	newDomains = []
	with open(outputFile, 'a') as out:
		for i in finalDomains:
			if i not in oldDomains:
				newDomains.append(i)
				out.write("{}\n".format(i))
	
	if newDomains:			
		print("{} Domain baru telah ditemukan dan di simpan di {}".format(len(newDomains), outputFile))
		for i in newDomains:
			logger.info("Domain baru ditemukan: {}".format(i))
			
	else:
		print("Tidak ada domain baru.")
		