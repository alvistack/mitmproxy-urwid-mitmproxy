#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Urwid escape sequences common to curses_display and raw_display
#    Copyright (C) 2004-2006  Ian Ward
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Urwid web site: http://excess.org/urwid/

"""
Terminal Escape Sequences for input and display
"""

import util
import os
import re

import encodings
utf8decode = lambda s: encodings.codecs.utf_8_decode(s)[0]

SO = "\x0e"
SI = "\x0f"

DEC_TAG = "0"
DEC_SPECIAL_CHARS = utf8decode("◆▒°±┘┐┌└┼⎺⎻─⎼⎽├┤┴┬│≤≥π≠£·")
ALT_DEC_SPECIAL_CHARS = u"`afgjklmnopqrstuvwxyz{|}~"

DEC_SPECIAL_CHARMAP = {}
assert len(DEC_SPECIAL_CHARS) == len(ALT_DEC_SPECIAL_CHARS), `DEC_SPECIAL_CHARS, ALT_DEC_SPECIAL_CHARS`
for c, alt in zip(DEC_SPECIAL_CHARS, ALT_DEC_SPECIAL_CHARS):
	DEC_SPECIAL_CHARMAP[ord(c)] = SO + alt + SI

SAFE_ASCII_DEC_SPECIAL_RE = re.compile(u"^[ -~%s]*$" % DEC_SPECIAL_CHARS)
DEC_SPECIAL_RE = re.compile(u"[%s]" % DEC_SPECIAL_CHARS)


###################
## Input sequences
###################

class MoreInputRequired(Exception):
	pass

def escape_modifier( digit ):
	mode = ord(digit) - ord("1")
	return "shift "*(mode&1) + "meta "*((mode&2)/2) + "ctrl "*((mode&4)/4)
	

input_sequences = [
	('[A','up'),('[B','down'),('[C','right'),('[D','left'),
	('[E','5'),('[F','end'),('[G','5'),('[H','home'),

	('[1~','home'),('[2~','insert'),('[3~','delete'),('[4~','end'),
	('[5~','page up'),('[6~','page down'),
	('[7~','home'),('[8~','end'),

	('[[A','f1'),('[[B','f2'),('[[C','f3'),('[[D','f4'),('[[E','f5'),
	
	('[11~','f1'),('[12~','f2'),('[13~','f3'),('[14~','f4'),
	('[15~','f5'),('[17~','f6'),('[18~','f7'),('[19~','f8'),
	('[20~','f9'),('[21~','f10'),('[23~','f11'),('[24~','f12'),
	('[25~','f13'),('[26~','f14'),('[28~','f15'),('[29~','f16'),
	('[31~','f17'),('[32~','f18'),('[33~','f19'),('[34~','f20'),

	('OA','up'),('OB','down'),('OC','right'),('OD','left'),
	('OH','home'),('OF','end'),
	('OP','f1'),('OQ','f2'),('OR','f3'),('OS','f4'),
	('Oo','/'),('Oj','*'),('Om','-'),('Ok','+'),

	('[Z','shift tab'),
] + [ 
	# modified cursor keys + home, end, 5 -- [#X and [1;#X forms
	(prefix+digit+letter, escape_modifier(digit) + key)
	for prefix in "[","[1;"
	for digit in "12345678"
	for letter,key in zip("ABCDEFGH",
		('up','down','right','left','5','end','5','home'))
] + [ 
	# modified F1-F4 keys -- O#X form
	("O"+digit+letter, escape_modifier(digit) + key)
	for digit in "12345678"
	for letter,key in zip("PQRS",('f1','f2','f3','f4'))
] + [ 
	# modified F1-F13 keys -- [XX;#~ form
	("["+str(num)+";"+digit+"~", escape_modifier(digit) + key)
	for digit in "12345678"
	for num,key in zip(
		(11,12,13,14,15,17,18,19,20,21,23,24,25,26,28,29,31,32,33,34),
		('f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11',
		'f12','f13','f14','f15','f16','f17','f18','f19','f20'))
] + [
	# mouse reporting (special handling done in KeyqueueTrie)
	('[M', 'mouse')
]

class KeyqueueTrie(object):
	def __init__( self, sequences ):
		self.data = {}
		for s, result in sequences:
			assert type(result) != type({})
			self.add(self.data, s, result)
	
	def add(self, root, s, result):
		assert type(root) == type({}), "trie conflict detected"
		assert len(s) > 0, "trie conflict detected"
		
		if root.has_key(ord(s[0])):
			return self.add(root[ord(s[0])], s[1:], result)
		if len(s)>1:
			d = {}
			root[ord(s[0])] = d
			return self.add(d, s[1:], result)
		root[ord(s)] = result
	
	def get(self, keys, more_available):
		return self.get_recurse(self.data, keys, more_available)
	
	def get_recurse(self, root, keys, more_available):
		if type(root) != type({}):
			if root == "mouse":
				return self.read_mouse_info(keys, 
					more_available)
			return (root, keys)
		if not keys:
			# get more keys
			if more_available:
				raise MoreInputRequired()
			return None
		if not root.has_key(keys[0]):
			return None
		return self.get_recurse(root[keys[0]], keys[1:], more_available)
	
	def read_mouse_info(self, keys, more_available):
		if len(keys) < 3:
			if more_available:
				raise MoreInputRequired()
			return None
		
		b = keys[0] - 32
		x, y = keys[1] - 33, keys[2] - 33  # start from 0
		
		prefix = ""
		if b & 4:	prefix = prefix + "shift "
		if b & 8:	prefix = prefix + "meta "
		if b & 16:	prefix = prefix + "ctrl "

		# 0->1, 1->2, 2->3, 64->4, 65->5
		button = ((b&64)/64*3) + (b & 3) + 1

		if b & 3 == 3:	
			action = "release"
			button = 0
		elif b & MOUSE_RELEASE_FLAG:
			action = "release"
		elif b & MOUSE_DRAG_FLAG:
			action = "drag"
		else:
			action = "press"

		return ( (prefix + "mouse " + action, button, x, y), keys[3:] )


# This is added to button value to signal mouse release by curses_display
# and raw_display when we know which button was released.  NON-STANDARD 
MOUSE_RELEASE_FLAG = 2048  

# xterm adds this to the button value to signal a mouse drag event
MOUSE_DRAG_FLAG = 32


#################################################
# Build the input trie from input_sequences list
input_trie = KeyqueueTrie(input_sequences)
#################################################

_keyconv = {
	-1:None,
	8:'backspace',
	9:'tab',
	10:'enter',
	127:'backspace',
	# curses-only keycodes follow..  (XXX: are these used anymore?)
	258:'down',
	259:'up',
	260:'left',
	261:'right',
	262:'home',
	263:'backspace',
	265:'f1', 266:'f2', 267:'f3', 268:'f4',
	269:'f5', 270:'f6', 271:'f7', 272:'f8',
	273:'f9', 274:'f10', 275:'f11', 276:'f12',
	277:'shift f1', 278:'shift f2', 279:'shift f3', 280:'shift f4',
	281:'shift f5', 282:'shift f6', 283:'shift f7', 284:'shift f8',
	285:'shift f9', 286:'shift f10', 287:'shift f11', 288:'shift f12',
	330:'delete',
	331:'insert',
	338:'page down',
	339:'page up',
	343:'enter',    # on numpad
	350:'5',        # on numpad
	360:'end',
}



def process_keyqueue(codes, more_available):
	"""
	codes -- list of key codes
	more_available -- if True then raise MoreInputRequired when in the 
		middle of a character sequence (escape/utf8/wide) and caller 
		will attempt to send more key codes on the next call.
	
	returns (list of input, list of remaining key codes).
	"""
	code = codes[0]
	if code >= 32 and code <= 126:
		key = chr(code)
		return [key], codes[1:]
	if _keyconv.has_key(code):
		return [_keyconv[code]], codes[1:]
	if code >0 and code <27:
		return ["ctrl %s" % chr(ord('a')+code-1)], codes[1:]
	if code >27 and code <32:
		return ["ctrl %s" % chr(ord('A')+code-1)], codes[1:]
	
	em = util.get_encoding_mode()
	
	if (em == 'wide' and code < 256 and  
		util.within_double_byte(chr(code),0,0)):
		if not codes[1:]:
			if more_available:
				raise MoreInputRequired()
		if codes[1:] and codes[1] < 256:
			db = chr(code)+chr(codes[1])
			if util.within_double_byte(db, 0, 1):
				return [db], codes[2:]
	if em == 'utf8' and code>127 and code<256:
		if code & 0xe0 == 0xc0: # 2-byte form
			need_more = 1
		elif code & 0xf0 == 0xe0: # 3-byte form
			need_more = 2
		elif code & 0xf8 == 0xf0: # 4-byte form
			need_more = 3
		else:
			return ["<%d>"%code], codes[1:]

		for i in range(need_more):
			if len(codes)-1 <= i:
				if more_available:
					raise MoreInputRequired()
				else:
					return ["<%d>"%code], codes[1:]
			k = codes[i+1]
			if k>256 or k&0xc0 != 0x80:
				return ["<%d>"%code], codes[1:]
		
		s = "".join([chr(c)for c in codes[:need_more+1]])
		try:
			return [s.decode("utf-8")], codes[need_more+1:]
		except UnicodeDecodeError:
			return ["<%d>"%code], codes[1:]
		
	if code >127 and code <256:
		key = chr(code)
		return [key], codes[1:]
	if code != 27:
		return ["<%d>"%code], codes[1:]

	result = input_trie.get(codes[1:], more_available)
	
	if result is not None:
		result, remaining_codes = result
		return [result], remaining_codes

	if codes[1:]:
		# Meta keys -- ESC+Key form
		run, remaining_codes = process_keyqueue(codes[1:], 
			more_available)
		if run[0] == "esc" or run[0].find("meta ") >= 0:
			return ['esc']+run, remaining_codes
		return ['meta '+run[0]]+run[1:], remaining_codes
		
	return ['esc'], codes[1:]


####################
## Output sequences
####################

ESC = "\x1b"

CURSOR_HOME = ESC+"[H"

APP_KEYPAD_MODE = ESC+"="
NUM_KEYPAD_MODE = ESC+">"

SWITCH_TO_ALTERNATE_BUFFER = ESC+"[?1049h"
RESTORE_NORMAL_BUFFER = ESC+"[?1049l"

#RESET_SCROLL_REGION = ESC+"[;r"
#RESET = ESC+"c"

REPORT_CURSOR_POSITION = ESC+"[6n"

INSERT_ON = ESC + "[4h"
INSERT_OFF = ESC + "[4l"

def set_cursor_position( x, y ):
	assert type(x) == type(0)
	assert type(y) == type(0)
	return ESC+"[%d;%dH" %(y+1, x+1)

def move_cursor_right(x):
	return ESC+"[%dC" % x

HIDE_CURSOR = ESC+"[?25l"
SHOW_CURSOR = ESC+"[?25h"

MOUSE_TRACKING_ON = ESC+"[?1000h"+ESC+"[?1002h"
MOUSE_TRACKING_OFF = ESC+"[?1002l"+ESC+"[?1000l"

DESIGNATE_G1_SPECIAL = ESC+")0"

_fg_attr = {
	'default':	"0;39",
	'black':	"0;30",
	'dark red':	"0;31",
	'dark green':	"0;32",
	'brown':	"0;33",
	'dark blue':	"0;34",
	'dark magenta':	"0;35",
	'dark cyan':	"0;36",
	'light gray':	"0;37",
	'dark gray':	"1;30",
	'light red':	"1;31",
	'light green':	"1;32",
	'yellow':	"1;33",
	'light blue':	"1;34",
	'light magenta':"1;35",
	'light cyan':	"1;36",
	'white':	"1;37",
}

_fg_attr_xterm = {
	'default':	"39",
	'black':	"30",
	'dark red':	"31",
	'dark green':	"32",
	'brown':	"33",
	'dark blue':	"34",
	'dark magenta':	"35",
	'dark cyan':	"36",
	'light gray':	"37",
	'dark gray':	"90",
	'light red':	"91",
	'light green':	"92",
	'yellow':	"93",
	'light blue':	"94",
	'light magenta':"95",
	'light cyan':	"96",
	'white':	"97",
}

###############################################
# Detect xterm and use non-bold bright colours
if os.environ.get('TERM',None) == 'xterm':
	_fg_attr = _fg_attr_xterm
###############################################


_bg_attr = {
	'default':	"49",
	'black':	"40",
	'dark red':	"41",
	'dark green':	"42",
	'brown':	"43",
	'dark blue':	"44",
	'dark magenta':	"45",
	'dark cyan':	"46",
	'light gray':	"47",
#	'dark gray':	"100",
#	'light red':	"101",
#	'light green':	"102",
#	'yellow':	"103",
#	'light blue':	"104",
#	'light magenta':"105",
#	'light cyan':	"106",
#	'white':	"107",
}

def set_attributes( fg, bg ):
	assert _fg_attr.has_key( fg )
	assert _bg_attr.has_key( bg )
	return ESC+"["+_fg_attr[fg]+";"+_bg_attr[bg]+"m"
	#if fg == 'light gray':
		# xterm workaround
	#return ESC+"[39m"+e
	#return e
