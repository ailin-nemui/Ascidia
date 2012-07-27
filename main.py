
import xml.dom
import xml.dom.minidom
import math
from collections import defaultdict
from collections import namedtuple
import random

CHAR_H_RATIO = 2.0

Line = namedtuple("Line","a b z stroke w stype")
Rectangle = namedtuple("Rectangle","a b z stroke w stype fill")
Ellipse = namedtuple("Ellipse", "a b z stroke w stype fill")
Arc = namedtuple("Arc","a b z start end stroke w stype fill")
Text = namedtuple("Text","pos z text colour size")
QuadCurve = namedtuple("QuadCurve","a b c z stroke w stype")

STROKE_SOLID = object()
STROKE_DASHED = object()

M_NONE = 0
M_OCCUPIED = (1<<0)
M_BOX_START_S = (1<<1)
M_BOX_AFTER_S = (1<<2)
M_BOX_START_E = (1<<3)
M_BOX_AFTER_E = (1<<4)
M_LINE_START_E = (1<<5)
M_DASH_START_E = (1<<6)
M_LINE_AFTER_E = (1<<7)
M_DASH_AFTER_E = (1<<8)
M_LINE_START_S = (1<<9)
M_DASH_START_S = (1<<10)
M_LINE_AFTER_S = (1<<11)
M_DASH_AFTER_S = (1<<12)
M_LINE_START_SE = (1<<13)
M_DASH_START_SE = (1<<14)
M_LINE_AFTER_SE = (1<<15)
M_DASH_AFTER_SE = (1<<16)
M_LINE_START_SW = (1<<17)
M_DASH_START_SW = (1<<18)
M_LINE_AFTER_SW = (1<<19)
M_DASH_AFTER_SW = (1<<20)

END_OF_INPUT = "\x00"


class SvgOutput(object):

	CHAR_W = 12.0
	CHAR_H = CHAR_W * CHAR_H_RATIO
	STROKE_W = 2.5
	FONT_SIZE = 16.0
	DASH_PATTERN = 8,8

	@staticmethod
	def output(items,stream):
		SvgOutput.INST._output(items,stream)
			
	def _output(self,items,stream):
		doc = xml.dom.minidom.getDOMImplementation().createDocument(None,"svg",None)
		root = doc.documentElement
		root.setAttribute("xmlns","http://www.w3.org/2000/svg")
		root.setAttribute("version","1.1")
		for item in sorted(items,key=lambda i: i.z):
			hname = "_do_%s" % type(item).__name__
			getattr(self,hname,lambda i,d,p: None)(item,doc,root)
		doc.writexml(stream,addindent="\t",newl="\n")
			
	def _colour(self,colour):
		return colour if colour else "none"
	
	def _x(self,x):
		return str(int(x * SvgOutput.CHAR_W))
		
	def _y(self,y):
		return str(int(y * SvgOutput.CHAR_H))
		
	def _w(self,w):
		return str(float(w * SvgOutput.STROKE_W))
			
	def _style_attrs(self,item,el):
		if hasattr(item,"stroke"):
			el.setAttribute("stroke",self._colour(item.stroke))
		if hasattr(item,"w"):
			el.setAttribute("stroke-width",self._w(item.w))
		if hasattr(item,"stype"):
			if item.stype == STROKE_DASHED:
				el.setAttribute("stroke-dasharray",",".join(
						map(str,SvgOutput.DASH_PATTERN)))
		if hasattr(item,"fill"):
			el.setAttribute("fill",self._colour(item.fill))
			
	def _do_Line(self,line,doc,parent):
		el = doc.createElement("line")
		el.setAttribute("x1",self._x(line.a[0]))
		el.setAttribute("y1",self._y(line.a[1]))
		el.setAttribute("x2",self._x(line.b[0]))
		el.setAttribute("y2",self._y(line.b[1]))
		self._style_attrs(line,el)
		parent.appendChild(el)
	
	def _do_Rectangle(self,rect,doc,parent):
		el = doc.createElement("rect")
		el.setAttribute("x",self._x(rect.a[0]))
		el.setAttribute("y",self._y(rect.a[1]))
		el.setAttribute("width",self._x(rect.b[0]-rect.a[0]))
		el.setAttribute("height",self._y(rect.b[1]-rect.a[1]))
		self._style_attrs(rect,el)
		parent.appendChild(el)
		
	def _do_Ellipse(self,ellipse,doc,parent):
		w = ellipse.b[0]-ellipse.a[0]
		h = ellipse.b[1]-ellipse.a[1]
		el = doc.createElement("ellipse")
		el.setAttribute("cx",self._x(ellipse.a[0]+w/2.0))
		el.setAttribute("cy",self._y(ellipse.a[1]+h/2.0))
		el.setAttribute("rx",self._x(w/2.0))
		el.setAttribute("ry",self._y(h/2.0))
		self._style_attrs(ellipse,el)
		parent.appendChild(el)
		
	def _do_Arc(self,arc,doc,parent):
		rx = (arc.b[0]-arc.a[0])/2
		ry = (arc.b[1]-arc.a[1])/2
		cx,cy = arc.a[0]+rx, arc.a[1]+ry
		sx = cx+math.cos(arc.start)*rx
		sy = cy+math.sin(arc.start)*ry
		ex = cx+math.cos(arc.end)*rx
		ey = cy+math.sin(arc.end)*ry
		el = doc.createElement("path")
		el.setAttribute("d","M %s,%s A %s,%s 0 %d 1 %s,%s" % (
			self._x(sx),self._y(sy), self._x(rx),self._y(ry), 
			1, self._x(ex),self._y(ey)))
		self._style_attrs(arc,el)
		parent.appendChild(el)
		
	def _do_QuadCurve(self,curve,doc,parent):
		el = doc.createElement("path")
		el.setAttribute("d","M %s,%s Q %s,%s %s,%s" % (
			self._x(curve.a[0]),self._y(curve.a[1]), self._x(curve.c[0]),self._y(curve.c[1]),
			self._x(curve.b[0]),self._y(curve.b[1]) ))
		self._style_attrs(curve,el)
		el.setAttribute("fill","none")
		parent.appendChild(el)
		
	def _do_Text(self,text,doc,parent):
		el = doc.createElement("text")
		el.setAttribute("x",self._x(text.pos[0]))
		el.setAttribute("y",self._y(text.pos[1]+0.75))
		el.setAttribute("font-family","monospace")
		el.appendChild(doc.createTextNode(text.text))
		el.setAttribute("fill",self._colour(text.colour))
		el.setAttribute("font-size",str(int(text.size*SvgOutput.FONT_SIZE)))
		parent.appendChild(el)
		
	
SvgOutput.INST = SvgOutput()


class PatternRejected(Exception): pass
class PatternStateError(Exception): pass
class NoSuchPosition(Exception): pass

class Pattern(object):
	
	gen = None
	is_finished = False
	curr = None
	
	def __init__(self):
		self.curr = None
		self.gen = self.matcher()
		self.gen.next()
		
	def matcher(self):
		yield
 		self.reject()
		
	def reject(self):
		raise PatternRejected()
		
	def occupied(self):
		return self.curr.meta & M_OCCUPIED
		
	def expect(self,chars,meta=M_OCCUPIED):
		if self.occupied() or not self.curr.char in chars:
			self.reject()
		else:
			return meta		

	def offset(self,x,y,pos=None):	
		if pos is None: pos = (self.curr.col,self.curr.row)
		return (pos[0]+x,pos[1]+y)

	def await_pos(self,pos):
		while (self.curr.col,self.curr.row) != pos:
			if self.curr.row > pos[1] or self.curr.char == END_OF_INPUT:
				raise NoSuchPosition(pos)
			yield M_NONE
			
	def test(self,currentchar):
		try:
			return self.gen.send(currentchar)
		except StopIteration:
			self.is_finished = True
			raise
		except NoSuchPosition as e:
			raise PatternRejected(e)
		
	def render(self):
		if not self.is_finished: 
			raise PatternStateError("Pattern not matched")
		return []
		

class LiteralPattern(Pattern):

	pos = None
	char = None
	
	def matcher(self):
		self.curr = yield
		self.pos = self.curr.col,self.curr.row
		self.char = self.curr.char
		if( not self.occupied() and not self.curr.char.isspace()
				and self.curr.char != END_OF_INPUT ):
			yield M_OCCUPIED
		else:
			self.reject()
		return
		
	def render(self):
		Pattern.render(self)
		return [ Text(self.pos,0,self.char,"brown",1) ]
		

class DiamondPattern(Pattern):

	tl = None
	br = None
	
	def matcher(self):
		self.curr = yield
		startj,starti = self.curr.row,self.curr.col
		rowcount = 0
		self.curr = yield self.expect("/")
		self.curr = yield self.expect("\\")
		while True:
			try:
				for meta in self.await_pos(self.offset(-(rowcount*2+2+1),1)):
					self.curr = yield meta
			except NoSuchPosition: break
			if self.curr.char != "/": break
			rowcount += 1
			self.curr = yield self.expect("/")
			for meta in self.await_pos(self.offset(rowcount*2,0)):
				self.curr = yield meta
			self.curr = yield self.expect("\\")
		for meta in self.await_pos((starti-rowcount,startj+rowcount+1)):
			self.curr = yield meta
		w = rowcount*2 + 2
		h = (rowcount+1) * 2
		while True:
			self.curr = yield self.expect("\\")
			for meta in self.await_pos(self.offset(rowcount*2,0)):
				self.curr = yield meta
			self.curr = yield self.expect("/")	
			if rowcount <= 0: break
			for meta in self.await_pos(self.offset(-(rowcount*2+2-1),1)):
				self.curr = yield meta
			rowcount -= 1
		self.tl = (starti-(w/2-1),startj)
		self.br = (starti+(w/2),startj+(h-1))		
		return
		
	def render(self):
		Pattern.render(self)
		w = self.br[0]-self.tl[0]+1
		h = self.br[1]-self.tl[1]+1
		return [		
			Line( (self.tl[0]+w/2.0, self.tl[1]),
				(self.br[0]+1.0, self.tl[1]+h/2.0), 1, "orange", 1, STROKE_SOLID),
			Line( (self.tl[0]+w/2.0, self.tl[1]),
				(self.tl[0], self.tl[1]+h/2.0), 1, "orange", 1, STROKE_SOLID),
			Line( (self.tl[0]+w/2.0, self.br[1]+1.0),
				(self.br[0]+1.0, self.tl[1]+h/2.0), 1, "orange", 1, STROKE_SOLID),
			Line( (self.tl[0]+w/2.0, self.br[1]+1.0),
				(self.tl[0], self.tl[1]+h/2.0), 1, "orange", 1, STROKE_SOLID) ]
				
		
class DbCylinderPattern(Pattern):

	tl = None
	br = None
	
	def matcher(self):
		w,h = 0,0
		self.curr = yield
		self.tl = (self.curr.col,self.curr.row)
		self.curr = yield self.expect(".")
		self.curr = yield self.expect("-")
		while self.curr.char != ".":
			self.curr = yield self.expect("-")
		w = self.curr.col-self.tl[0]+1
		self.curr = yield self.expect(".")
		for meta in self.await_pos(self.offset(-w,1)):
			self.curr = yield meta
		self.curr = yield self.expect("'")
		for n in range(w-2):
			self.curr = yield self.expect("-")
		self.curr = yield self.expect("'")
		for meta in self.await_pos(self.offset(-w,1)):
			self.curr = yield meta
		while True:	
			self.curr = yield self.expect("|")
			for meta in self.await_pos(self.offset(w-2,0)):
				self.curr = yield meta
			self.curr = yield self.expect("|")
			for meta in self.await_pos(self.offset(-w,1)):
				self.curr = yield meta
			if self.curr.char == "'": break
		self.curr = yield self.expect("'")
		for n in range(w-2):
			self.curr = yield self.expect("-")
		self.br = (self.curr.col,self.curr.row)
		self.curr = yield self.expect("'")
		return
		
	def render(self):
		Pattern.render(self)
		return [
			Ellipse((self.tl[0]+0.5,self.tl[1]+0.5),
				(self.br[0]+0.5,self.tl[1]+1.0+0.5),
				1,"purple",1,STROKE_SOLID,None),
			Line((self.tl[0]+0.5,self.tl[1]+1.0),
				(self.tl[0]+0.5,self.br[1]), 1,"purple",1,STROKE_SOLID),
			Line((self.br[0]+0.5,self.tl[1]+1.0),
				(self.br[0]+0.5,self.br[1]), 1,"purple",1,STROKE_SOLID),
			Arc((self.tl[0]+0.5,self.br[1]-1.0+0.5),
				(self.br[0]+0.5,self.br[1]+0.5),
				1, 0.0, math.pi, "purple",1,STROKE_SOLID,None)	]
				

class BoxPattern(Pattern):
	
	tl = None
	br = None
	
	def matcher(self):
		w,h = 0,0
		self.curr = yield
		self.tl = (self.curr.col,self.curr.row)
		rowstart = self.curr.col,self.curr.row
		self.curr = yield self.expect("+",meta=M_OCCUPIED|M_BOX_START_S|M_BOX_START_E)
		self.curr = yield self.expect("-",meta=M_OCCUPIED|M_BOX_START_S)
		while self.curr.char != "+":
			self.curr = yield self.expect("-",meta=M_OCCUPIED|M_BOX_START_S)
		w = self.curr.col-self.tl[0]+1
		self.curr = yield self.expect("+",meta=M_OCCUPIED|M_BOX_START_S)
		self.curr = yield M_BOX_AFTER_E
		for meta in self.await_pos(self.offset(0,1,rowstart)): 
			self.curr = yield meta
		while True:
			rowstart = self.curr.col,self.curr.row
			self.curr = yield self.expect("|",meta=M_OCCUPIED|M_BOX_START_E)
			for meta in self.await_pos(self.offset(w-2,0)):
				self.curr = yield meta
			self.curr = yield self.expect("|",meta=M_OCCUPIED)
			self.curr = yield M_BOX_AFTER_E
			for meta in self.await_pos(self.offset(0,1,rowstart)):
				self.curr = yield meta
			if self.curr.char == "+": break
		rowstart = self.curr.col,self.curr.row
		self.curr = yield self.expect("+",meta=M_OCCUPIED|M_BOX_START_E)
		for n in range(w-2):
			self.curr = yield self.expect("-",meta=M_OCCUPIED)
		self.br = (self.curr.col,self.curr.row)
		self.curr = yield self.expect("+",meta=M_OCCUPIED)
		self.curr = yield M_BOX_AFTER_E
		try:
			for meta in self.await_pos(self.offset(0,1,rowstart)):
				self.curr = yield meta
			rowstart = self.curr.col,self.curr.row
			for n in range(w):
				if self.curr.char=="\n": break
				self.curr = yield M_BOX_AFTER_S
		except NoSuchPosition: pass
		return
		
	def render(self):
		Pattern.render(self)
		return [Rectangle((self.tl[0]+0.5,self.tl[1]+0.5),
			(self.br[0]+0.5,self.br[1]+0.5),1,"red",1,STROKE_SOLID,None)]
			
			
class LineSqCornerPattern(Pattern):

	pos = None
	ends = None
	
	def matcher(self):
		self.curr = yield
		if self.occupied(): self.reject()
		self.pos = self.curr.col,self.curr.row
		self.ends = []
		for m,dm,x,y in [
				(M_LINE_AFTER_E, M_DASH_AFTER_E, -1,0),
				(M_LINE_AFTER_S, M_DASH_AFTER_S, 0,-1),
				(M_LINE_AFTER_SE,M_DASH_AFTER_SE,-1,-1),
				(M_LINE_AFTER_SW,M_DASH_AFTER_SW,1,-1) ]:
			if self.curr.meta & m: 
				self.ends.append((x,y,bool(self.curr.meta & dm)))			
		self.curr = yield self.expect("+")
		for m,dm,x,y in [
				(M_LINE_START_E, M_DASH_START_E, 1,0),
				(M_LINE_START_SW,M_DASH_START_SW,-1,1),
				(M_LINE_START_S, M_DASH_START_S, 0,1),
				(M_LINE_START_SE,M_DASH_START_SE,1,1) ]:
			try:
				for meta in self.await_pos(self.offset(x,y,self.pos)):
					self.curr = yield meta
				if self.curr.meta & m:
					self.ends.append((x,y,bool(self.curr.meta & dm)))	
			except NoSuchPosition: pass
		if len(self.ends) < 2: self.reject()			
		return 
		
	def render(self):
		Pattern.render(self)
		centre = self.pos[0]+0.5,self.pos[1]+0.5
		retval = []
		for x,y,dsh in self.ends:
			retval.append( Line(centre,(centre[0]+x*0.5,centre[1]+y*0.5),
					1,"pink",1,STROKE_DASHED if dsh else STROKE_SOLID) )
		return retval


class LineRdCornerPattern(Pattern):
	
	pos = None
	ends = None
	
	def matcher(self):
		self.curr = yield
		
		if self.occupied(): self.reject()
		
		self.pos = self.curr.col,self.curr.row
		
		up,down = False,False
		if self.curr.char == ".": 
			down = True
		elif self.curr.char == "'": 
			up = True
		elif self.curr.char == ":": 
			up,down = True,True
		else: self.reject()
		
		self.ends = []
		for m,dm,x,y in [ 
				(M_LINE_AFTER_E, M_DASH_AFTER_E, -1, 0),
				(M_LINE_AFTER_SW,M_DASH_AFTER_SW, 1,-1),
				(M_LINE_AFTER_S, M_DASH_AFTER_S,  0,-1),
				(M_LINE_AFTER_SE,M_DASH_AFTER_SE,-1,-1) ]:		
			if y < 0 and not up: continue
			if self.curr.meta & m: self.ends.append((x,y,self.curr.meta & dm))
			
		self.curr = yield M_OCCUPIED
		
		for m,dm,x,y in [
				(M_LINE_START_E, M_DASH_START_E,  1, 0),
				(M_LINE_START_SW,M_DASH_START_SW,-1, 1),
				(M_LINE_START_S, M_DASH_START_S,  0, 1),
				(M_LINE_START_SE,M_DASH_START_SE, 1, 1), ]:
			try:
				if y > 0 and not down: continue
				for meta in self.await_pos(self.offset(x,y,self.pos)):
					self.curr = yield meta
				if self.curr.meta & m: self.ends.append((x,y,self.curr.meta & dm))
			except NoSuchPosition: pass
		
		if len(self.ends) < 2: self.reject()
		return 
		
	def render(self):
		Pattern.render(self)
		centre = self.pos[0]+0.5,self.pos[1]+0.5
		retval = []
		rest = self.ends[:]
		while len(rest)>0:
			end = rest[0]
			rest = rest[1:]
			for oth in rest:
				a = centre[0]+end[0]*0.5, centre[1]+end[1]*0.5
				b = centre[0]+oth[0]*0.5, centre[1]+oth[1]*0.5
				retval.append( QuadCurve(a,b,centre,1,"pink",1,
					STROKE_DASHED if end[2] and oth[2] else STROKE_SOLID) )		
		return retval


class ArrowheadPattern(Pattern):

	pos = None
	tobox = False
	dashed = False
	chars = None
	linemeta = None
	boxmeta = None
	dashmeta = None
	flipped = False
	xdir = None
	ydir = None
	
	def matcher(self):
		self.curr = yield
		self.pos = self.curr.col,self.curr.row
		if self.occupied() or not self.curr.char in self.chars: self.reject()
		if self.flipped:
			if self.curr.meta & self.boxmeta: self.tobox = True
		else:
			if not self.curr.meta & self.linemeta: self.reject()
		self.curr = yield M_OCCUPIED
		try:
			for meta in self.await_pos(self.offset(self.xdir-1,self.ydir)):
				self.curr = yield meta
			if self.flipped:
				if not self.curr.meta & self.linemeta: self.reject()
			else:
				if self.curr.meta & self.boxmeta: self.tobox = True	
		except NoSuchPosition:
			if self.flipped: raise
		return
		
	def render(self):
		flip = -1 if self.flipped else 1
		centre = (self.pos[0]+0.5,self.pos[1]+0.5)
		spos = (centre[0]-0.5*self.xdir*flip,centre[1]-0.5*self.ydir*flip)
		apos2 = (centre[0]+(0.5+0.5*self.tobox)*self.xdir*flip,centre[1]+(0.5+0.5*self.tobox)*self.ydir*flip)
		apos1 = (apos2[0]-0.8*self.xdir*flip-0.5*self.ydir*flip,apos2[1]-0.8*self.ydir*flip/CHAR_H_RATIO-0.5*self.xdir*flip/CHAR_H_RATIO)
		apos3 = (apos2[0]-0.8*self.xdir*flip+0.5*self.ydir*flip,apos2[1]-0.8*self.ydir*flip/CHAR_H_RATIO+0.5*self.xdir*flip/CHAR_H_RATIO)
		return [
			Line(apos1,apos2,1,"darkred",1,STROKE_SOLID),
			Line(apos3,apos2,1,"darkred",1,STROKE_SOLID),
			Line(spos,apos2,1,"darkred",1,STROKE_DASHED if self.dashed else STROKE_SOLID) ]
		

class LArrowheadPattern(ArrowheadPattern):

	chars = "<"
	linemeta = M_LINE_START_E
	boxmeta = M_BOX_AFTER_E
	dashmeta = M_DASH_START_E
	xdir = 1
	ydir = 0
	flipped = True
	
		
class RArrowheadPattern(ArrowheadPattern):
	
	chars = ">"
	linemeta = M_LINE_AFTER_E
	boxmeta = M_BOX_START_E
	dashmeta = M_DASH_AFTER_E
	xdir = 1
	ydir = 0
	flipped = False
	

class DArrowheadPattern(ArrowheadPattern):

	chars = "Vv"
	linemeta = M_LINE_AFTER_S
	boxmeta = M_BOX_START_S
	dashmeta = M_DASH_AFTER_S
	xdir = 0
	ydir = 1
	flipped = False
	# TODO: disallow word context


class UArrowheadPattern(ArrowheadPattern):
	
	chars = "^"
	linemeta = M_LINE_START_S
	boxmeta = M_BOX_AFTER_S
	dashmeta = M_DASH_START_S
	xdir = 0
	ydir = 1
	flipped = True

	
class CrowsFeetPattern(Pattern):

	pos = None
	xdir = 0
	ydir = 0
	chars = None
	startmeta = None
	endmeta = None
	flipped = True
	dashed = False

	def matcher(self):
		self.curr = yield
		self.pos = self.curr.col,self.curr.row
		if( self.occupied() or not self.curr.char in self.chars
				or not self.curr.meta & self.startmeta ): 
			self.reject()
		if not self.flipped and self.curr.meta & self.dashmeta: 
			self.dashed = True
		self.curr = yield M_OCCUPIED
		for meta in self.await_pos(self.offset(self.xdir-1,self.ydir)):
			self.curr = yield meta
		if not self.curr.meta & self.endmeta: self.reject()
		if self.flipped and self.curr.meta & self.dashmeta:
			self.dashed = True
		return
		
	def render(self):
		
		flip = -1 if self.flipped else 1
		centre = ( self.pos[0]+0.5, self.pos[1]+0.5 )
		spos = ( centre[0]-self.xdir*0.5*flip, centre[1]-self.ydir*0.5*flip )
		fpos1 = ( centre[0]+self.xdir*1.0*flip - 0.6*(not self.xdir),
					centre[1]+self.ydir*1.0*flip - 0.6*(not self.ydir)/CHAR_H_RATIO )
		fpos2 = ( centre[0]+self.xdir*1.0*flip, centre[1]+self.ydir*1.0*flip )
		fpos3 = ( centre[0]+self.xdir*1.0*flip + 0.6*(not self.xdir), 
					centre[1]+self.ydir*1.0*flip + 0.6*(not self.ydir)/CHAR_H_RATIO )
		fpos0 = ( fpos2[0]-self.xdir*1.0*flip, fpos2[1]-self.ydir*1.0*flip/CHAR_H_RATIO )
		return [ 
			Line(fpos0,fpos1,1,"gray",1,STROKE_SOLID),
			Line(fpos0,fpos2,1,"gray",1,STROKE_SOLID),
			Line(fpos0,fpos3,1,"gray",1,STROKE_SOLID),
			Line(spos,fpos0,1,"gray",1,STROKE_DASHED if self.dashed else STROKE_SOLID) ]

	
class LCrowsFeetPattern(CrowsFeetPattern):

	xdir = 1
	ydir = 0
	chars = ">"
	flipped = True
	startmeta = M_BOX_AFTER_E
	endmeta = M_LINE_START_E
	dashmeta = M_DASH_START_E


class RCrowsFeetPattern(CrowsFeetPattern):
	
	xdir = 1
	ydir = 0
	chars = "<"
	flipped = False
	startmeta = M_LINE_AFTER_E
	endmeta = M_BOX_START_E
	dashmeta = M_DASH_AFTER_E
	
	
class UCrowsFeetPattern(CrowsFeetPattern):

	xdir = 0
	ydir = 1
	chars = "Vv"
	flipped = True
	startmeta = M_BOX_AFTER_S
	endmeta = M_LINE_START_S
	dashmeta = M_DASH_START_S
	
	
class DCrowsFeetPattern(CrowsFeetPattern):

	xdir = 0
	ydir = 1
	chars = "^"
	flipped = False
	startmeta = M_LINE_AFTER_S
	endmeta = M_BOX_START_S
	dashmeta = M_DASH_AFTER_S


class LinePattern(Pattern):

	xdir = 0	
	ydir = 0
	startchars = None
	midchars = None
	startpos = None
	endpos = None
	startmeta = None
	endmeta = None
	stroketype = None
	
	def matcher(self):
		self.curr = yield
		pos = self.curr.col,self.curr.row
		self.startpos = pos
		for i,startchar in enumerate(self.startchars):
			pos = self.curr.col,self.curr.row
			self.curr = yield self.expect(startchar,
				meta=M_OCCUPIED|(self.startmeta if i==0 else 0))
		try:
			breaknow = False
			while not breaknow:
				for i,midchar in enumerate(self.midchars):
					for meta in self.await_pos(self.offset(self.xdir-1,self.ydir)):
						self.curr = yield meta
					if( self.curr.char != midchar or self.occupied() 
							or self.curr.char == END_OF_INPUT ): 
						if i==0: 
							breaknow = True
							break
						else:
							self.reject()
					pos = self.curr.col,self.curr.row
					self.curr = yield self.expect(midchar,meta=M_OCCUPIED)
			self.endpos = pos
			yield self.endmeta
		except NoSuchPosition:
			self.endpos = pos
		return
		
	def render(self):
		Pattern.render(self)
		return [ Line((self.startpos[0]+0.5+self.xdir*-0.5,self.startpos[1]+0.5+self.ydir*-0.5),
				(self.endpos[0]+0.5+self.xdir*0.5,self.endpos[1]+0.5+self.ydir*0.5),1,"blue",1,self.stroketype) ]
		


class UpDiagLinePattern(LinePattern):
	
	xdir = -1
	ydir = 1
	startchars = ["/"]
	midchars = startchars
	startmeta = M_LINE_START_SW
	endmeta = M_LINE_AFTER_SW
	stroketype = STROKE_SOLID


class UpDiagDashedLinePattern(LinePattern):
	
	xdir = -1
	ydir = 1
	startchars = [","]
	midchars = startchars
	startmeta = M_LINE_START_SW | M_DASH_START_SW
	endmeta = M_LINE_AFTER_SW | M_DASH_AFTER_SW
	stroketype = STROKE_DASHED
	
		
class DownDiagLinePattern(LinePattern):

	xdir = 1
	ydir = 1
	startchars = ["\\"]
	midchars = startchars
	startmeta = M_LINE_START_SE
	endmeta = M_LINE_AFTER_SE
	stroketype = STROKE_SOLID
	
		
class DownDiagDashedLinePattern(LinePattern):
	
	xdir = 1
	ydir = 1
	startchars = ["`"]
	midchars = startchars
	startmeta = M_LINE_START_SE | M_DASH_START_SE
	endmeta = M_LINE_AFTER_SE | M_DASH_AFTER_SE
	stroketype = STROKE_DASHED
	
		
class VertLinePattern(LinePattern):

	xdir = 0
	ydir = 1
	startchars = ["|"]
	midchars = startchars
	startmeta = M_LINE_START_S
	endmeta = M_LINE_AFTER_S
	stroketype = STROKE_SOLID
	
	
class VertDashedLinePattern(LinePattern):

	xdir = 0
	ydir = 1
	startchars = [";"]
	midchars = startchars
	startmeta = M_LINE_START_S | M_DASH_START_S
	endmeta = M_LINE_AFTER_S | M_DASH_AFTER_S
	stroketype = STROKE_DASHED
	
	
class HorizLinePattern(LinePattern):

	xdir = 1
	ydir = 0
	startchars = ["-"]
	midchars = startchars
	startmeta = M_LINE_START_E
	endmeta = M_LINE_AFTER_E
	stroketype = STROKE_SOLID


class HorizDashedLinePattern(LinePattern):
	
	xdir = 1
	ydir = 0
	startchars = ["-"," ","-"," "]
	midchars = ["-"," "]
	startmeta = M_LINE_START_E | M_DASH_START_E
	endmeta = M_LINE_AFTER_E | M_DASH_AFTER_E
	stroketype = STROKE_DASHED


class TinyCirclePattern(Pattern):

	pos = None
	
	def matcher(self):
		self.curr = yield
		if self.curr.char.isalpha(): self.reject()
		self.curr = yield M_NONE
		self.pos = self.curr.col,self.curr.row
		self.curr = yield self.expect("O")
		if self.curr.char.isalpha(): self.reject()
		return
		
	def render(self):
		Pattern.render(self)
		return [ Ellipse((self.pos[0]+0.5-0.4,self.pos[1]+0.5-0.4/CHAR_H_RATIO), 
				(self.pos[0]+0.5+0.4,self.pos[1]+0.5+0.4/CHAR_H_RATIO), 1, 
				"magenta", 1, STROKE_SOLID, None) ]
				
				
class SmallCirclePattern(Pattern):
	
	left = None
	right = None
	y = None
	
	def matcher(self):
		self.curr = yield
		self.left = self.curr.col
		self.y = self.curr.row
		self.curr = yield self.expect("(")
		for n in range(3):
			if self.curr.char == ")": break
			self.curr = yield M_NONE
		else:
			self.reject()
		self.right = self.curr.col
		self.curr = yield self.expect(")")
		return
		
	def render(self):
		Pattern.render(self)
		d = self.right-self.left
		return [ Ellipse((self.left+0.5,self.y+0.5-d/2.0/CHAR_H_RATIO),
				(self.right+0.5,self.y+0.5+d/2.0/CHAR_H_RATIO), 1, "green",
				1,STROKE_SOLID,None) ]


class JumpPattern(Pattern):

	pos = None
	hdash = False
	vdash = False
	char = None

	def matcher(self):
		self.curr = yield
		ndash,edash,sdash,wdash = [False]*4
		if( self.curr.char != self.char or self.occupied() 
				or not self.curr.meta & M_LINE_AFTER_E 
				or not self.curr.meta & M_LINE_AFTER_S ):
			self.reject()
		if self.curr.meta & M_DASH_AFTER_E: wdash = True
		if self.curr.meta & M_DASH_AFTER_S: ndash = True
		self.pos = self.curr.col,self.curr.row
		self.curr = yield M_OCCUPIED
		for meta in self.await_pos(self.offset(1,0,self.pos)):
			self.curr = yield meta
		if not self.curr.meta & M_LINE_START_E: self.reject()
		if self.curr.meta & M_DASH_START_E: edash = True
		for meta in self.await_pos(self.offset(0,1,self.pos)):
			self.curr = yield meta
		if not self.curr.meta & M_LINE_START_S: self.reject()
		if self.curr.meta & M_DASH_START_S: sdash = True
		self.hdash = edash and wdash
		self.vdash = ndash and sdash 
		return
		
		
class LJumpPattern(JumpPattern):

	char = "("
		
	def render(self):
		return [ 
			Line((self.pos[0],self.pos[1]+0.5),(self.pos[0]+1.0,self.pos[1]+0.5),
				1,"cyan",1,STROKE_DASHED if self.hdash else STROKE_SOLID),
			Arc((self.pos[0]+0.5-0.6,self.pos[1]),(self.pos[0]+0.5+0.6,self.pos[1]+1.0),
				1,math.pi*0.5,math.pi*1.5,"cyan",1,STROKE_DASHED if self.vdash else STROKE_SOLID, None), ]
	
	
class RJumpPattern(JumpPattern):

	char = ")"
	
	def render(self):
		return [
			Line((self.pos[0],self.pos[1]+0.5),(self.pos[0]+1.0,self.pos[1]+0.5),
				1,"cyan",1,STROKE_DASHED if self.hdash else STROKE_SOLID),
			Arc((self.pos[0]+0.5-0.6,self.pos[1]),(self.pos[0]+0.5+0.6,self.pos[1]+1.0),
				1,math.pi*-0.5,math.pi*0.5,"cyan",1,STROKE_DASHED if self.vdash else STROKE_SOLID,None), ]
	
	
class UJumpPattern(JumpPattern):

	char = "^"
	
	def render(self):
		return [
			Line((self.pos[0]+0.5,self.pos[1]),(self.pos[0]+0.5,self.pos[1]+1.0),
				1,"cyan",1,STROKE_DASHED if self.vdash else STROKE_SOLID),
			Arc((self.pos[0],self.pos[1]+0.5-0.4),(self.pos[0]+1.0,self.pos[1]+0.5+0.4),
				1,math.pi,math.pi*2,"cyan",1,STROKE_DASHED if self.hdash else STROKE_SOLID,None), ]

		
PATTERNS = [
	DbCylinderPattern,
	DiamondPattern,
	BoxPattern,
	SmallCirclePattern,
	TinyCirclePattern,
	HorizDashedLinePattern,
	HorizLinePattern,
	VertLinePattern,
	VertDashedLinePattern,
	UpDiagLinePattern,
	UpDiagDashedLinePattern,
	DownDiagLinePattern,
	DownDiagDashedLinePattern,
	LineSqCornerPattern,
	LineRdCornerPattern,
	LJumpPattern,
	RJumpPattern,
	UJumpPattern,
	LArrowheadPattern,
	RArrowheadPattern,
	DArrowheadPattern,
	UArrowheadPattern,
	LCrowsFeetPattern,
	RCrowsFeetPattern,
	UCrowsFeetPattern,
	DCrowsFeetPattern,
	LiteralPattern
]


class MatchLookup(object):

	_matches = None
	_occupants = None
	_match_meta = None
	
	def __init__(self):
		self._matches = []
		self._occupants = defaultdict(list)
		self._match_meta = defaultdict(dict)

	def get_all_matches(self):
		return list(self._matches)
		
	def get_occupants_at(self,pos):
		return list(self._occupants[pos])
		
	def get_meta_for(self,match):
		return dict(self._match_meta[match])
		
	def add_match(self,match):
		self._matches.append(match)
		
	def add_meta(self,match,pos,meta):
		if meta & M_OCCUPIED:
			self._occupants[pos].append(match)
		self._match_meta[match][pos] = meta
		
	def remove_match(self,match):
		try: 
			self._matches.remove(match)
		except ValueError: pass
		for pos,meta in self._match_meta[match].items():
			if meta & M_OCCUPIED:
				try:
					self._occupants[pos].remove(match)
				except ValueError: pass
		del(self._match_meta[match])
		
	def remove_cooccupants(self,match):
		for pos,meta in self.get_meta_for(match).items():
			if meta & M_OCCUPIED:
				for m in self.get_occupants_at(pos):
					self.remove_match(m)
		
		
CurrentChar = namedtuple("CurrentChar","row col char meta")


if __name__ == "__main__":

	INPUT = """\
MiniOreos Oranges O O O test- - > -->--><- -     | .-            ^ ,       `    
+---+  +-<>  ---+ +-------+ .-----.  /`          '-'     .     .-',         :   | | |
| O |  |  +------+| +---+ | '-----' //``|    + + +--.   /|    /| ,          ; --)-(-^--
+---+--+ O| ***  || |(*)| |-| --- | ``//v   /|,; |   `|/ '---' |,           ;   | | |
/`  |O |  +------+| +---+ | | --- |  `/+-+   +   +----:----.   :     .- - - :   
    +--+   .--.   +-------+ '-----' /` | |  + +  |   /|`    ` /  ^   ;      ;
() (A)  `  '--' /`This is a test|  /+ `+-+  |`|`  '   :   .--'---+>  '- - - :
  (  )   ` |  | `/  --- ---+    | // ` ` -<-  +    `   ` / +--+  v'.--.    ,    
 v (   )  +'--'    +---+ --+--+-+ `   +/ +<--.      :   :->|  |<---|  |   :
   |      |   | |  ||-`-`     | |  ` //   `   `    /  | |  +--+    '--'   ;
 love  .--'   v v  +-----+  |   |   `/  <  .   '--' ^ ^     ^   +--+  +--+V
   |  / +--+  |            aV   Vote       |    ^   ; |     |   |  |>-|  |
   ^    |  |                                                    +--+  +--+
  +--+  +--+                                                   
-<|  |   V                                                          
  +--+   |                                                  """.replace("`","\\")
	
#	INPUT = """\
#      |   |   |       ;      ;      |      |
#     -^- -^ -( )- - - ^- - --^--- - ^- - +-^- - 
#      |   |   |       ;      ;      |      ;  """.replace("*","\\")

		
	complete_matches = []
	complete_meta = {}
	for pclass in PATTERNS:
		print pclass.__name__
		ongoing = MatchLookup()	
		for j,line in enumerate((INPUT+END_OF_INPUT).splitlines()):
			for i,char in enumerate(line+"\n"):	
				meta = complete_meta.get((j,i),M_NONE)
				newp = pclass()
				ongoing.add_match(newp)
				for match in ongoing.get_all_matches():
					if not match in ongoing.get_all_matches():
						continue
					try:
						matchmeta = match.test(CurrentChar(j,i,char,meta))
					except PatternRejected:
						ongoing.remove_match(match)
					except StopIteration:
						complete_matches.append(match)
						for p,m in ongoing.get_meta_for(match).items():
							complete_meta[p] = complete_meta.get(p,M_NONE) | m
						ongoing.remove_cooccupants(match)
						ongoing.remove_match(match)
					else:
						ongoing.add_meta(match,(j,i),matchmeta)
		
	renderitems = []				
	for m in complete_matches:
		renderitems.extend(m.render())
	with open("test2.svg","w") as f:
		SvgOutput.output(renderitems,f)
	
	
	
	

