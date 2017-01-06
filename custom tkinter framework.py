from tkinter import *
import inspect

"""
Written by Joseph (YC) Kim.

tkinter animation framework class and a coupl of demos of it being used.
The framework provides a data structure to hold values in,
as well as a canvas to draw in.
"""
class TkAnimationFramework():

    class undefined(Exception): pass

    """
    Define these functions to be used. 
    init is used to initialize the data structure.
    If the canvas is requried in init, it may be added as a third argument,
    and will be handled automatically.
    """
    def draw(self, canvas, data): raise self.undefined
    def timerFired(self, data): raise self.undefined
    def init(self, data): raise self.undefined #you can pass in an optional canvas arg

    """
    definining these functions are optional.
    Once defined, it each will automatically be bound to the root to their
    corrosponding bindings.
    """
    def mousePress(self, event, data): raise self.undefined #left click
    def keyPress(self, event, data): raise self.undefined #keyboard
    def motion(self, event, data): raise self.undefined #mouse movement
    def mouseHeld(self, event, data): raise self.undefined #left click held


    def redrawAllWrapper(self):
        if self.redrawall: self.canvas.delete(ALL)
        try:
            self.draw(self.canvas, self.data)
        except self.undefined:
            pass
        self.canvas.update()

    def genericWrapper(self, key, event, function, args):
        try:
            function(event, *args)
        except self.undefined:
            #if function doesn't work unbind it
            self.root.unbind(key)
        self.redrawAllWrapper()

    def timerFiredWrapper(self):
        try:
            self.timerFired(self.data)
            self.redrawAllWrapper()
            self.canvas.after(self.data.timerDelay, self.timerFiredWrapper)

        except self.undefined:
            pass

    def makeBinding(self, key, function, args):
        self.root.bind(key, lambda event: self.genericWrapper(key, event, function, args))

    def initWrapper(self):
        try:
            self.data.garbage = set() # use this for delta graphics
            if len(inspect.getargspec(self.init).args) == 3: 
                self.init(self.data, self.canvas)
            else:
                self.init(self.data)
        except self.undefined:
            pass

    def __init__(self, width = 500, height = 500, redrawall = True, mainloop = True):
        self.redrawall = redrawall

        class Struct(): pass
        self.data = Struct()
        self.data.__doc__ = "data structure to store values"

        self.width = self.data.width = width
        self.height = self.data.height = height
        self.timerDelay = self.data.timerDelay = 1

        self.root = Tk()
        self.canvas = Canvas(self.root, width = self.width, height = self.height)
        self.canvas.pack()

        self.initWrapper()

        #bindings; if any isn't used, automatically unbinds them.
        self.makeBinding("<Button-1>", self.mousePress, (self.data,))
        self.makeBinding("<Key>", self.keyPress, (self.data,))
        self.makeBinding("<Motion>", self.motion, (self.data,))
        self.makeBinding("<B1-Motion>", self.motion, (self.data,))

        self.redrawAllWrapper()
        self.timerFiredWrapper()

        if mainloop:
            self.root.mainloop()










"""
example of how this framework may be used. Notice how not all of the functions
are defined, and that's okay.
"""
import math

class trailingObject():
    def __init__(self, duration, canvas, trailingFunction, drawFunction):
        self.capacity = duration
        self.canvas = canvas
        self.q = []
        self.df = drawFunction
        self.tf = trailingFunction

    def draw(self, *args, **kwargs):
        [self.tf(item) for item in self.q]
        self.q.append(self.df(*args, **kwargs))
        if len(self.q) > self.capacity:
            self.canvas.delete(self.q.pop(0))


def colorAdjust(s, dr, dg, db):
    r = s[1:3]
    g = s[3:5]
    b = s[5:]
    r = str(hex(min(255,max(int(int(r,16) + dr),0))))[2:]
    g = str(hex(min(255,max(int(int(g,16) + dg),0))))[2:]
    b = str(hex(min(255,max(int(int(b,16) + db),0))))[2:]
    r = "0" + r if len(r) == 1 else r
    g = "0" + g if len(g) == 1 else g
    b = "0" + b if len(b) == 1 else b
    return "#" + r + g + b

def colorShift(data):
    freq = 3
    data.cr += 0.05
    red = math.sin(freq*data.cr + 0)*127 + 128
    green = math.sin(freq*data.cr + 2)*127 + 128
    blue = math.sin(freq*data.cr + 4)*127 + 128
    data.colorcount = (int(red) << 16) + (int(green) << 8) + int(blue)
    dat = hex(data.colorcount)[2:]
    full = "#" + "0"*(6-len(dat)) + dat
    data.rainbow =  full
    pass

def create_ball(trailamount, canvas, dx, drawfunc):
    return trailingObject(trailamount, canvas, lambda item: canvas.itemconfig(item, fill = colorAdjust(canvas.itemcget(item, "fill"), +dx,+dx,+dx)),
                                   drawfunc)
class thing(TkAnimationFramework):

    def draw(self, canvas, data):
        x0,y0,x1,y1 = data.ballx-data.r, data.bally-data.r, data.ballx+data.r, data.bally+data.r
        if data.mode == "rainbow":
            data.ball.draw(x0,y0,x1,y1,  fill = data.rainbow, width = 0) 
 
        else:
            if data.mode == "black": color = "#000000"
            elif data.mode == "red": color = "#ff0000"
            elif data.mode == "green": color = "#00ff00"
            elif data.mode == "blue": color = "#0000ff"
            data.ball.draw(x0,y0,x1,y1, fill = color, width = 0)

    def timerFired(self, data):
        if data.mode == "rainbow": colorShift(data)
        data.ballvy += data.gravity
        data.bally += data.ballvy
        data.ballx += data.ballvx

        if data.ballx + data.r >= data.width:
            data.ballx = data.width - data.r
            data.ballvx *= -1
        elif data.ballx - data.r <= 0:
            data.ballx = data.r
            data.ballvx *= -1

        if data.bally + data.r >= data.height:
            if data.down:
                data.down = False
                data.ballvy = 0
                data.bally = data.height - data.r
            else:
                data.ballvy *= -1
                data.bally = data.height - data.r
                data.ballvy += 2

        if data.bally - data.r <= 0:
            data.ballvy *= -1

    def keyPress(self, event, data):
        if event.keysym == "Up":
            data.ballvy = -20
        if event.keysym == "Right":
            data.ballvx += 1
        if event.keysym == "Left":
            data.ballvx -= 1
        if event.keysym == "Down":
            data.ballvy = 20
            data.down = True
        if event.keysym == "minus":
            data.r -= 5
        if event.keysym == "equal":
            data.r += 5
        if event.keysym == "space":
            data.mode = data.modes[(data.modes.index(data.mode)+1)%len(data.modes)]

    def init(self, data, canvas):
        data.ballx = 100
        data.bally = 300
        data.r = 50

        data.ballvx = 0
        data.ballvy = 0
        data.gravity = 1
        data.down = False
        cap = 15
        dx = 250/cap
        data.ball = create_ball(cap, canvas, dx, canvas.create_oval)

        data.modes = ["black", "red", "blue", "green", "rainbow"]
        data.mode = data.modes[0]
        data.cr = 0
        data.rainbow = "#123456"

        canvas.create_text(data.width//2, data.height//2, text = """
            TRAILING BALL DEMO
            ARROW KEYS TO MOVE
            SPACE TO CHANGE COLORS
            """, justify = "center")

    def __init__(self):
        super().__init__(500,500, redrawall = False)

"""
Another example. Shows how simple it can be to use this framework.
"""

class asdf(TkAnimationFramework):
    def drawcircle(self, canvas,cx, cy, r, n = 0, color = "black"):
        canvas.create_oval(cx-r,cy-r,cx+r,cy+r, fill = color, width = 0)
        ncolor = "black" if color == "white" else "white"
        if n > 0: self.drawcircle(canvas, cx + r/(2*math.sqrt(2)), cy + r/(2*math.sqrt(2)), r//2, n-1, ncolor)
    def draw(self, canvas, data):
        self.drawcircle(canvas, data.width//2, data.height//2, 100,4)
        
# thing()
asdf(400,400)
