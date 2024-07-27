# A bot to randomly generate music
#
#
# Author: Thomas Tang
# Date Created: 26/02/2019

import song
from randomList import randomList
import socialMedia
import jsonreader
import instrumentPicker
import filters
import random, math
import struct
import os, subprocess
import sys
import datetime
from requests_oauthlib import OAuth1
import time
from pydub import AudioSegment
from pydub.playback import play

import mingus.core.notes as notes
import mingus.core.keys as keys
from mingus.containers import Note, NoteContainer, Bar, Track
from mingus.containers.instrument import Instrument, Piano, Guitar
from mingus.midi import midi_file_out as MidiFileOut#, fluidsynth
import mingus.extra.lilypond as LilyPond

from midi2audio import FluidSynth
from PIL import Image, ImageDraw

import xml.etree.ElementTree as ET
import re
import shutil

##Constants
svgtag = "{http://www.w3.org/2000/svg}"
linktag="{http://www.w3.org/1999/xlink}"
svglen = len(svgtag)
linklen = len(linktag)


tempos = [60.0, 75.0, 90.0, 100.0, 120.0, 150.0, 180.0, 200.0, 240.0]
measures = [.25, .5, 1, 2, 4]
durations = [1, 2, 4, 8, 16]
signatures = [(2, 2), (3, 2), (2,4), (3, 4), (4, 4), (5, 4), (6, 4), (3, 8), (5, 8), (7, 8), (9, 8), (11,8), (12, 8), (13, 8), (15, 16)]  

##read in config file
if(len(sys.argv) > 1):
	cfg = jsonreader.Reader(sys.argv[1])
else:
	print("Please provide a configuration file")
	sys.exit(1)

###FACEBOOK STUFF
fb = cfg["upload"]["facebook"]
socialMedia.FB_TOKEN  = fb["token"]

###TWITTER STUFF
tw = cfg["upload"]["twitter"]
CK = tw["consumer_key"]
CSK = tw["consumer_secret_key"]
AT = tw["access_token"]
ATS = tw["access_token_secret"]
socialMedia.TW_OAUTH = OAuth1(CK,
	client_secret=CSK,
	resource_owner_key=AT,
	resource_owner_secret=ATS)

##SONG PARAMS
sp = cfg["song_params"]
SAMPLE_RATE = sp["sample_rate"]
IDEAL_VOLUME = sp["target_volume"]
INSTRUMENT = sp["instrument"]
TEMPO = sp["tempo"]
KEY = sp["key"]
SEED = sp["seed"]


##FILES

out = cfg["outfiles"]
inf = cfg["infiles"]
FILE_HOME = out["home"]
if(not os.path.exists(FILE_HOME)):
		os.mkdir(FILE_HOME)
OUTMP4 = FILE_HOME + out["outmp4"]
OUTWAV = FILE_HOME + out["outwav"]
OUTMP3 = FILE_HOME + out["outmp3"]
OUTMP3T = FILE_HOME + out["outmp3_temp"]
OUTMID = FILE_HOME + out["outmid"]
VIDPIC = FILE_HOME + out["outpng"]
OUTSVG = FILE_HOME + out["outsvg"]
LOGPATH = out["outlog"]
FRAMEPATH = FILE_HOME + out["frame_folder"]
FRAMELENGTHTXT = FILE_HOME + out["frame_data_file"]
SOUNDFONT_PATH = inf["soundfont_folder"]

#ARCHIVE
acv = cfg["archive"]
ARCHIVE_FILES = acv["archive"]
ARCHIVE_LOCATION = acv["location"]

#FUN STUFF
tr = cfg["fun_stuff"]
AUDIO_REPLACE = tr["audio_replace"]
AUDIO_REPLACE_FILE = tr["replace_with"]


def main():
	global seed
	melody = song.Song()
	remove_files(force = True)
	
	if(INSTRUMENT is None):
		ip = instrumentPicker.InstrumentPicker(SOUNDFONT_PATH)
		melody.instrument = ip.Pick()
	else:
		melody.instrument = INSTRUMENT
	if(TEMPO is None):
		tl = randomList()
		tl.add(tempos, recursive = True)
		melody.tempo = tl.pickNormal()
	else:
		melody.tempo = TEMPO
	if(KEY is None):
		melody.key = random.choice(keys.major_keys)
	else:
		melody.key = KEY
		
	
	if(SEED is None):
		seed = random.randrange(sys.maxsize)
		print("Seed was: " + str(seed))
	else:
		seed = SEED
		print("Seed supplied: " + str(SEED))
	
	random.seed(seed)
	
	print(melody.tempo)
	print(melody.instrument)
	print (melody.key)
	
	melody.notes = write_song(melody)
	create_sheet(melody)
	create_frames(melody)

	exportToWav(melody)
	
	message = 'Instrument: ' + melody.instrument + ' \nTempo: ' + str(melody.tempo) + '\nPlayed in the key of ' + melody.key + '.'
	print(message)
	
	wavToMp4()
	upload_song(melody)
	if(ARCHIVE_FILES):
		archive_files(FILE_HOME, ARCHIVE_LOCATION)
	remove_files()
	
	#Finally, we exit
	return


def is_intstring(s):
	try:
		int(s)
		return True
	except ValueError:
		return False
		

#Remove files if they exist
def remove_files(force = False):
	print("Removing files...")
	rm = cfg["remove_files"].dict
	out = cfg["outfiles"]
	for f in rm:
		if(rm[f] or force):
			path = FILE_HOME + out[f]
			if os.path.isfile(path):
				print("Removing file: " + path)
				os.remove(path)  # remove the file
			elif os.path.isdir(path):
				print("Removing directory: " + path)
				shutil.rmtree(path)  # remove dir and all contains	
			
def write_song(melody):
	unl = keys.get_notes(melody.key)
	note_list = randomList()
	note_list.setDefaultWeight(100)
	note_list.add(unl, recursive=True)
	note_list.add(None, (random.gauss(25, 10)))
	print(note_list.normalisedWeights())
	print(note_list.list)
	
	wds = randomList()
	td = melody.tempo - 120.0
	#scaling for these is kinda wonky but whatever
	full = 0
	half = 0
	quarter = 0
	eighth = 0
	sixteenth = 0
	if(td < 0):
		#half notes - more often (180) for faster tempos, less often (90) for slower tempos
		half = max(0, random.gauss(120.0 + (td/ 2), 60))
		#full notes - 1.25x as often for faster tempos, half as often for slower tempos
		full = max(0, random.gauss((120.0 + (td/2))/2, 60))
		#sixteenth notes - less often (90) for faster tempos, more often (180) for slower tempos
		sixteenth = max(0, random.gauss((120.0 - td), 60))
	else:
		half = max(0, random.gauss(120.0 + (td/2), 60))
		full = max(0, random.gauss((120.0 + (td/2))*1.25, 60))
		sixteenth = max(0, random.gauss((120.0 - (td/4)), 60))
	
	#quarter notes - 120 median always
	quarter = max(0, random.gauss(120, 60))
	#eighth notes - 120 median always
	eighth = max(0, random.gauss(120, 60))
	
	wds.add(1, full)
	wds.add(2, half)
	wds.add(4, quarter)
	wds.add(8, eighth)
	wds.add(16, sixteenth)
	
	melody.weights = wds.normalisedWeights()
	sig = random.choice(signatures)
	print(sig)
	
	t = Track()
	i = 0
	numBars = melody.length

	while(i < numBars):
		b = Bar(melody.key, sig)
		while(b.current_beat != b.length):
			duration = wds.pickWeighted()
			n = note_list.pickWeighted()
			while(n == None and (duration <= 2 or duration > 8 or b.current_beat == 0 or melody.raw_song[-1][0] == None)):
				n = note_list.pickWeighted()
			if(b.place_notes(n, duration)):
				melody.raw_song.append((n, duration))				
		t.add_bar(b)
		i = i + 1	
	return t
	
	
def exportToWav(melody):
	MidiFileOut.write_Track(OUTMID, melody.notes, melody.tempo)
	sf=SOUNDFONT_PATH + melody.instrument + ".sf2"
	fs = FluidSynth(sf)
	fs.midi_to_audio(OUTMID, OUTWAV)
		
def wavToMp4():
	print("Converting to mp3...")
	#convert to mp3
	song = AudioSegment.from_wav(OUTWAV)
	song.export(OUTMP3, format="mp3")

	#remove .mp4 files
	if os.path.exists(OUTMP4):
		os.remove(OUTMP4)
	
	normalise_volume()
	if(AUDIO_REPLACE):
		audiofile = AUDIO_REPLACE_FILE
	else:
		audiofile = OUTMP3

	print("Converting to mp4...")
	#finally, convert it to video
	with open(os.devnull, 'w') as shutup:
		subprocess.call(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', FRAMELENGTHTXT, '-i', audiofile,  
		'-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
		'-c:a', 'aac', '-shortest', '-f', 'mp4', OUTMP4], 
		stdout=shutup, stderr=shutup)
	if os.path.exists(FRAMELENGTHTXT) and cfg["remove_files"].dict["frame_data_file"]:
		os.remove(FRAMELENGTHTXT)
	

def normalise_volume():
	print("Normalising volume...")
	with open(os.devnull, 'w') as shutup:
		subprocess.call(['ffmpeg', '-y', '-i', OUTMP3, '-filter:a', 'loudnorm', OUTMP3T], stdout=shutup, stderr=shutup)
		subprocess.call(['mv', OUTMP3T, OUTMP3])
	p1 = subprocess.Popen(['ffmpeg', '-i', OUTMP3, '-filter:a', 'volumedetect', '-f', 'null', '/dev/null'], stderr=subprocess.PIPE)
	p2 = subprocess.Popen(['grep', '-o', 'mean_volume: .*$'], stdin=p1.stderr, stdout=subprocess.PIPE, text = True)
	p1.stderr.close()
	mv = float(p2.communicate()[0][13:-3])
	dv = IDEAL_VOLUME
	delta = dv - mv
	arg = "volume=" + str(delta) + "dB"
	with open(os.devnull, 'w') as shutup:
		subprocess.call(['ffmpeg', '-y', '-i', OUTMP3, '-filter:a', arg, OUTMP3T], stdout=shutup, stderr=shutup)
		subprocess.call(['mv', OUTMP3T, OUTMP3])
	

def upload_song(melody):
	print("uploading song...")
	message = 'Instrument: ' + melody.instrument + ' \nTempo: ' + str(melody.tempo) + '\nPlayed in the key of ' + melody.key + '.'
	print("Facebook:")
	if(fb["upload"]):
		postid = socialMedia.upload_to_facebook(OUTMP4, message)
		print("Post succeeded, posting followup comment...")
		comment = ("Approximate note weighting:\nWhole notes: " + pc(melody.weights[0][1]) + "\nHalf notes: " 
		+  pc(melody.weights[1][1]) + "\nQuarter notes: " + pc(melody.weights[2][1]) +
		"\nEighth notes: " + pc(melody.weights[3][1]) + "\nSixteenth notes: "+ pc(melody.weights[4][1]))
		print(comment)
		socialMedia.fb_comment(postid, comment)
	else:
		print("Facebook upload skipped.")
	print("Twitter:")
	if(tw["upload"]):
		socialMedia.upload_to_twitter(OUTMP4, message)
	else:
		print("Twitter upload skipped")
	
	t = time.strftime("%d-%m-%y %H:%M")
	log = open(LOGPATH, "a+")
	log.write("------------------------------------------\n")
	log.write(t + ". Seed: " + str(seed) + ".\n")
	log.write("Message:\n" + message + "\n")
	
def create_sheet(melody):
	sheet = LilyPond.from_Track(melody.notes)
	sheet = LilyPond.to_png(sheet, VIDPIC)
	im = Image.open(VIDPIC)
	im = im.crop((0, 0, 834, 500))
	im.save(VIDPIC)
	
def create_frames(melody):
	sheet = LilyPond.from_Track(melody.notes)
	LilyPond.to_svg(sheet, OUTSVG)
	tree = ET.parse(OUTSVG)
	root = tree.getroot()
	i = 0
	notelist = []
	linkreg = re.compile(r'(\d\d*):(\d\d*):(\d\d*)')
	coordreg = re.compile(r'(\d[\d\.]*), (\d[\d\.]*)') 
	for child in root:
		if(child.tag[svglen:] == "a" and len(list(child)) == 1):
			ctag = child[0].tag[svglen:]
			if(ctag == "path" or (ctag == "g" and child[0][0].tag[svglen:] == "path")):
				link = child.get(linktag + "href")
				r = linkreg.search(link)
				coordstr = child[0].get("transform")[10:26]
				r2 = coordreg.search(coordstr)
				notelist.append((int(r.group(1)), int(r.group(2)), (float(r2.group(1)), float(r2.group(2)))))
	notelist.sort()
	
	if(melody.key == "G" or melody.key == "F"):
		#If the Key is F or G the above reads the key signature as an extra note, we remove that here
		notelist = notelist[1:]
	if os.path.exists(FRAMELENGTHTXT):
		os.remove(FRAMELENGTHTXT)
	f = open(FRAMELENGTHTXT, "a+")
	if(not os.path.exists(FRAMEPATH)):
		os.mkdir(FRAMEPATH)
	index = 0
	for n in notelist:
		frame = Image.open(VIDPIC)
		draw = ImageDraw.Draw(frame)
		oldx = n[2][0]
		oldy = n[2][1]
		newx = conv_x(oldx)
		newy = conv_y(oldy)
		row = int(int(newy)/85 + 1)
		draw.line([newx - 1, row * 85 - 10, newx - 1, row * 85 - 50], fill = (255, 0, 0), width = 2)
		fn = FRAMEPATH + "frame" + str(index) + ".png"
		frame.save(fn)
		f.write("file \'" + fn + "\'\nduration " + str((1/melody.raw_song[index][1] * 4)/(melody.tempo / 60.0)) + "\n")
		index = index + 1
	f.write("file \'" + FRAMEPATH + "frame" + str(len(notelist) - 1) + ".png\'\nduration 2\nfile \'" +FRAMEPATH + "frame" + str(len(notelist) - 1) + ".png\'")
	f.close()
	
def pf(val):
    print("{0:.15f}".format(val))
	
def pc(val):
	return ("{0:.2f}%".format(val*100))
	
def conv_y(oldy):
	return (oldy*1181.0/169.0094)

def conv_x(oldx):
	return (oldx*834.0/119.5016)
	
def archive_files(fromlocation, tolocation):
	print("Archiving files...")
	if(not os.path.exists(tolocation)):
		os.mkdir(tolocation)
	t = time.strftime("-%H%M-%d%m%y")
	filename = tolocation + "/archive" + t +".zip"
	print(filename)
	with open(os.devnull, 'w') as shutup:
		p1 = subprocess.Popen(['zip', '-r', filename, "."], stdout = shutup, cwd = fromlocation)
		p1.wait()
	
	
if(__name__ == '__main__'):
	main()

