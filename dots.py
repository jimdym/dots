#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dots.py
#  
#  Copyright 2022  <jimduba@duba.org>
#
#	If you use this program or pieces of it or if you find anything wrong
#  with it, please, let me know at the above email address.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  

import pygame
from pygame.locals import *
import sys


class Dot:
	# a dot is a point (x,y). a draw method needs a color to draw it
	def __init__ (self, x, y):
		self.x=x
		self.y=y
		self.radius = DOT_RADIUS
	# end Dot init function
		
	def draw(self, win, color):
		pygame.draw.circle(win, color, (self.x, self.y), self.radius)

	def __eq__(self, other):
		if not isinstance(other, Dot):
			return NotImplemented
		return self.x==other.x and self.y==other.y

	def __str__(self):
		return "%s, %s" %(str(self.x), str(self.y))

class Seg:
	# a line segment connects 2 dots
	def __init__(self, dot1, dot2):
		if dot1.x == dot2.x: # vertical
			if dot1.y < dot2.y:
				self.dot1 = dot1
				self.dot2 = dot2
			else:
				self.dot1 = dot2
				self.dot2 = dot1
		if dot1.y == dot2.y: # horozontal
			if dot1.x < dot2.x:
				self.dot1 = dot1
				self.dot2 = dot2
			else:
				self.dot1 = dot2
				self.dot2 = dot1
				
		self.width = SEG_WIDTH

	def draw(self, win, color):
		pygame.draw.line(win, color, (self.dot1.x, self.dot1.y), (self.dot2.x, self.dot2.y), self.width)

	def __eq__(self, other):
		# what does it mean for one segment to be equal to another. This implementation does not assume the order of dots
		if not isinstance(other, Seg):
			return NotImplemented
		return (self.dot1 == other.dot1 and self.dot2==other.dot2) or (self.dot1 == other.dot2 and self.dot2 == other.dot1)

	def __str__(self):
		#This isn't really necessary, but it's great for troubleshooting so leave it in
		return "%s, %s" %(str(self.dot1), str(self.dot2))

	def isVert(self):
		# when doing work with squares, it's convenient to know if a segment is vertical or horizontal
		if self.dot1.x == self.dot2.x:
			return True
		else:
			return False

	def isHoriz(self):
		# this is just because it's confusing to think about not vertical
		if self.dot1.y == self.dot2.y:
			return True
		else:
			return False

	def isHLess(self, other):
		# is this horozontal segment closer to the top than other
		if self.dot1.y < other.dot1.y:
			return True
		return False

	def isVLess(self, other):
		# is this vertical segment more left than other
		if self.dot1.x < other.dot1.x:
			return True
		return False

	def adjacent(self, other):
		# adjacent only means the segments have a dot in common
		if self.dot1 == other.dot1:
			return True
		if self.dot1 == other.dot2:
			return True
		if self.dot2 == other.dot1:
			return True
		if self.dot2 == other.dot2:
			return True
		return False

	def para(self, other):
		# they must both be horozontal or vertical and 1 unit apart
		if (self.isVert() and other.isVert()):
			if abs(self.dot1.x-other.dot1.x) == DOT_DIST:
				return True
			return False
		if self.isHoriz() and other.isHoriz():
			if abs(self.dot1.y-other.dot1.y) == DOT_DIST:
				return True
			return False
		return False

	def coLinear(self, other):
		# if segments are colinear, they can't be part of the same square
		if self.dot1.x==self.dot2.x==other.dot1.x==other.dot2.x:
			return True
		if self.dot1.y==self.dot2.y==other.dot1.y==other.dot2.y:
			return True
		return False
		
# end class Seg definition

class Square:
	#  square gets won by a color
	def __init__(self, seg1, seg2, seg3, seg4, color):
		self.color=color
		# squares need to be:top - t, right side - r, bottom - b, left side - l
		# no matter the order they come in, they get ordered. Testing for being a square needs to happen before this as well as segment ordering
		
		self.t = seg1 # top
		self.r = seg2 # right side
		self.b = seg3 # bottom
		self.l = seg4 # left side
		

	def draw(self, win):
		# I'm going to store squares so the first dot is the top left
		pygame.draw.rect(win,self.color,(self.t.dot1.x,self.t.dot1.y,DOT_DIST,DOT_DIST))

	def __eq__(self, other):
		# you have to determine if one square is equal to another
		if self.t == other.t and self.r==other.r and self.b==other.b and self.l==other.l:
			return True
		return False

# end class Square definition

def idSeg(t,dots, segs):
	# we have a mouse click and the coordinates, now find the best fit segment and add it to the list of segments
	# t is a list containing the mouse click
	x = t[0]
	y = t[1]
	# 2 out of bounds dots
	dot1 = Dot(0,0)
	dot2 = Dot(HEIGHT,WIDTH)
	d1 = HEIGHT
	d2 = WIDTH
	for d in dots:
		# dt is the distance from the cursor to the current dot under consideration
		dt = ((x -d.x)**2 + (y-d.y)**2)**.5
		if (d1 > d2) and (d1 > dt):
			d1 = dt
			dot1=d
		elif (d2 > d1) and (d2 > dt):
			d2 = dt
			dot2=d
		elif (d2 == d1) and (d2 > dt):
			d2 = dt
			dot2=d
	# now is that segment already taken:
	t = Seg(dot1, dot2)
	for s in segs:
		if s == t:
			print("\a") # ring the bell
			return False
	# all good append a new segment to the list
	segs.append(t)
	return True
		
# end definition for idSeg

def findSquare(segs,player):
	# there's a new segment at the end of segs, we want to find if it can form a new square (or two) with any of the other segments in the list
	# this function will return 0 (no squares), 1, or 2
	squares=[]
	if len(segs) < 4:
		return 0
	s = segs[-1] # easier for me to think of this way
	i=0
	clist=[] #list of segments that might form a square. if there are 4 or more, there may be a square
	
	while i < len(segs)-1:
		# look at each segment in the list to see 0if it could possibly form a square with s
		aList=False
		if s.adjacent(segs[i]) and aList==False: # must be adjacent
			if s.coLinear(segs[i])==False:
				clist.append(segs[i])
				aList=True
		if s.para(segs[i]) and aList==False: # or parallel and one unit away
			clist.append(segs[i])
			aList=True
		i+=1
	# clist could have up to 6 segments at this point
	sCount=0
	if len(clist) < 3:
		return sCount # can't be a square
	# clist contains the candidate segments that might form a square with s. go through the combinations of s and the segments in clist to see of they are a square.
	# clist can be = 3, 4, 5, or 6 and we want to take them 3 at a time, pair them with s and call is square
	a=0
	while a<len(clist)-2:
		b=a+1
		while b<len(clist)-1:
			c=b+1
			while c<len(clist):
				if b>a and c>b:
					plist=[]
					plist.append(clist[a])
					plist.append(clist[b])
					plist.append(clist[c])
					plist.append(s)
					
					nlist=isSquare(plist)
					if nlist:
						# The segments are sorted by isSquare so plist should be good
						sq=Square(nlist[0],nlist[1],nlist[2], nlist[3], player)
						sCount+=1
						squares.append(sq)
				c+=1
			b+=1
		a+=1
	return squares

# end findSquare function


def isSquare(clist):
	# takes the list of candidate segments and figures out if it's a square. sorts the incoming clist into the order for a square
	if len(clist) != 4:
		return False
	segs=[]
	for s in clist:
		segs.append(s) # work on a copy
	#
	# t,r,b,l top, right bottom left must exist to be a square. this also sorts the segs.
	#
	i=0
	ti=5
	ri=5
	bi=5
	li=5
	
	j=0
	while j < len(segs):
		pseg=True # should only put a segment in one place
		if pseg and segs[j].isHoriz() and ti == 5 and bi == 5:
			ti = j
			pseg=False
		if pseg and segs[j].isHoriz() and ti != 5:
			# this is the 2nd horozontal
			if segs[ti].isHLess(segs[j]):
				bi = j
				pseg=False
			else:
				bi=ti
				ti=j
				pseg=False
		if pseg and segs[j].isVert and ri ==5 and li == 5: # vertical
			ri = j
			pseg=False
		if pseg and segs[j].isVert() and ri != 5:
			if segs[ri].isVLess(segs[j])==False:
				li=j
				pseg=False
			else:
				li=ri
				ri=j
				pseg=False
		j+=1
		
	if ti==5 or ri==5 or bi==5 or li==5:
		return False
	#now check that the segments are contiguous
	if segs[ti].dot2==segs[ri].dot1 and segs[ri].dot2==segs[bi].dot2 and segs[bi].dot1==segs[li].dot2 and segs[li].dot1==segs[ti].dot1:
		# at this point modify passed in list?
		clist=[]
		clist.append(segs[ti])
		clist.append(segs[ri])
		clist.append(segs[bi])
		clist.append(segs[li])
		return clist
	clist=[]
	return clist
# end isSquare function

def displayScore(squares):
	redScore=0
	greenScore=0
	for sq in squares:
		if sq.color==RED:
			redScore+=1
		if sq.color==GREEN:
			greenScore+=1
	print(redPlayer + " score is " + str(redScore))
	print(greenPlayer + " score is " + str(greenScore))

	return redScore+greenScore

# end displayScore

def main(args):
	
	run = True
	clock = pygame.time.Clock()
	WIN.fill(BLACK)
	player = RED # red goes first
	numSq = (WIDTH/DOT_DIST - 1) **2

	print("number of squares = " + str(numSq))
	
	dots=[]
	segs=[]
	squares=[]
	
	# initialize all the dots. Rows and colums are separate because it may not be a square all the time. DOT_DIST is space between dots
	for x in range(0, WIDTH, DOT_DIST):
		for y in range(0, HEIGHT, DOT_DIST):
			d=Dot(int(x+OFFSET),int(y+OFFSET))
			dots.append(d)
	
	while run: # runs continuously and checks for input each pass
		
		clock.tick(60) # frame rate 60 frames per second
		WIN.fill(BLACK)
		# The board chages color to reflect whose turn it is
		# squares remain the color of the player who completed them
		for sq in squares:
			sq.draw(WIN)
		for seg in segs:
			seg.draw(WIN, player)
		for dot in dots:
			dot.draw(WIN, player)

		playerMoved = False 
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				break
			mousePress = []
			if event.type == pygame.MOUSEBUTTONDOWN:
				mousePress = pygame.mouse.get_pressed()
				if mousePress[0]: # left mouse press and we need coordinates
					if idSeg(pygame.mouse.get_pos(), dots,segs):
						# new segment is at the end of segs so
						newSquares=[]
						newSquares=findSquare(segs,player)
						if newSquares: # it has to return one or more squares
							for s in newSquares:
								squares.append(s)
							playerMoved = False # gets another turn
							totScore=displayScore(squares)
							if totScore==numSq:
								run=False
						else:
							playerMoved=True
						# now search segs t see if it's a new square or 2 new squares
					
		pygame.display.update()
		# and it's the next players turn
		if playerMoved == True:
			if player == RED:
				player = GREEN
			else:
				player = RED
		playerMoved=False
		
	# end main event loop
	# display something about final scores
	WIN.fill(BLACK)
	# The board chages color to reflect whose turn it is
	# squares remain the color of the player who completed them
	for sq in squares:
		sq.draw(WIN)
	for seg in segs:
		seg.draw(WIN, player)
	for dot in dots:
		dot.draw(WIN, player)
	pygame.display.update()
	endGame()
	
	pygame.quit()
	
	return 0

# end main function

def printRules():
	print("This is the game of DOTS. When the DOTS are red, it's the red")
	print("players turn, When the DOTS are green, it's the green players turn")
	print('\n')
	print("When it's your turn, use the mouse to click between two dots, if")
	print("you don't form a square, the line segment will light up and it will")
	print("switch to the other players turn. If you form a square, the square")
	print("will light up with your color (and it will stay that way) and you")
	print("get another turn.")
	print('\n')
	print("You can choose the board size: 1 will be very small, 2 a bit bigger,")
	print("3 bigger, etc .. . Then you'll be asked for names to match the ")
	print("colors.")

# end printRules

def boardSize(MAXBS):
	while True:
		try:
			bs=int(input('Enter the board size (3, 4, ... 15)'))
		except:
			print("No, idiot. Needs to be a number. An integer 3 to 15")
			continue
		else:
			if bs<3 or bs>MAXBS:
				print("Nope, try again.")
				continue
			else:
				return bs
			
# end boardSize

def getRedName():
	rn=input('Enter the name associated with the red player: ')
	return rn

def getGreenName():
	gn=input('Enter the name associated with the green player: ')
	return gn

#end getting of the names

def endGame():
	input("Take a good look at the board and press enter ")

MAXBS = 15 # largest board size
WHITE = (255, 255, 255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255) # not very visible against black
BLACK = (0, 0, 0)
#WIDTH, HEIGHT = 400,400
DOT_DIST = 50 # distance between dots should evenly divide into width/height
DOT_RADIUS = 5
OFFSET = 10 # center dots better in window
SEG_WIDTH = 4 # width of line segments

# before starting pygame print instructions and get player names.
printRules()
bs = boardSize(MAXBS)
WIDTH = (bs+1)*50
HEIGHT= WIDTH
redPlayer=getRedName()
greenPlayer= getGreenName()

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DOTS")

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
