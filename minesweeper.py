import random
from tkinter import *

# Author: Declan Sheehan
# Date: November 1st, 2020

# Difficulties:
# Easy:    10 MINES (10x10)
# Medium:  40 MINES (16x16)
# Hard:    99 MINES (30x16)

class minesweeper(Frame):
	def __init__(self):
		super().__init__()
		self.init_var()
		self.mainFrame()
		self.createTopBar()
		self.createGrid()
		self.setupGame(self.difficulty)
		self.updateTime()

	def init_var(self):
		# Game variables.
		self.GAME_STATE = 0
		self.difficulty = 'easy'
		self.Xsize, self.Ysize = 10, 10
		self.flags, self.curTime = IntVar(), IntVar()
		self.loop, self.vals, self.mines, self.original_color = None, None, None, None
		self.colors = ['#2626F2', '#007B00', '#FF0000', '#00007B', '#7B0000', '#008080', '#0D1110', '#808080']

		# Images used.
		self.smiley = PhotoImage(file='./images/smiley.png')
		self.frowny = PhotoImage(file='./images/frowny.png')
		self.coolface = PhotoImage(file='./images/cool.png')
		self.o_face = PhotoImage(file='./images/o-face.png')
		self.flag = PhotoImage(file='./images/flag.png').subsample(2, 2)
		self.mine = PhotoImage(file='./images/mine.png').subsample(13, 13)

######################################## Interface ########################################
	################################# Main Frame ############################
	def mainFrame(self):
		# Create main label frame raised to display like the original minesweeper.
		self.LF = LabelFrame(self.master, relief=RAISED, bg='#C5C3C4')
		self.LF.pack(expand=True, fill=BOTH)

		# Create menu & submenus.
		bar = Menu(self.master)
		difficultyBar = Menu(bar, tearoff=0)
		helpBar = Menu(bar, tearoff=0)

		# Game options:
		difficultyBar.add_command(label='New         F2', command=lambda: self.forceReset(Button(self.master)))
		difficultyBar.add_command(label='Beginner', command=lambda: self.changeDifficulty('easy'))
		difficultyBar.add_command(label='Intermediate', command=lambda: self.changeDifficulty('medium'))
		difficultyBar.add_command(label='Expert', command=lambda: self.changeDifficulty('hard'))
		difficultyBar.add_command(label='Exit', command=self.quitGame)

		# Help bar for aesthetics.
		helpBar.add_command(label='Contents               F1')
		helpBar.add_command(label='Search for Help on...')
		helpBar.add_command(label='Using Help')
		helpBar.add_command(label='About Minesweeper...')

		# Add menus to frame & bind the F2 key.
		bar.add_cascade(label='Game', menu=difficultyBar)
		bar.add_cascade(label='Help', menu=helpBar)
		self.master.bind('<F2>', self.forceReset)
		self.master.config(menu=bar)
	#########################################################################
	################################## Top Bar ##############################
	def createTopBar(self):
		topBarLF = LabelFrame(self.master, relief=SUNKEN, bg='#C0C0C0', bd=5)
		topBarLF.place(relx=0.025, rely=0.015625, relwidth=0.955, height=45)

		self.flagLabel = Label(topBarLF, textvariable=self.flags)
		self.flagLabel.place(relx=0.06, y=3, relwidth=0.2, height=30)

		self.gameButton = Button(topBarLF, image=self.smiley, relief=RAISED, bd=4, command=self.resetGame)
		self.gameButton.place(relx=0.425, y=1, relwidth=0.14, height=35)
		self.gameButton.image = self.smiley

		self.timeLabel = Label(topBarLF, textvariable=self.curTime)
		self.timeLabel.place(relx=0.74, y=3, relwidth=0.2, height=30)
		self.original_color = self.gameButton.cget('background')
	#########################################################################

	################################# Mine Field ############################
	def createGrid(self):
		self.gridLF = LabelFrame(self.master, relief=SUNKEN, bg='#C9C9C9', bd=4)
		self.gridLF.place(relx=0.025, rely=0.171875, relwidth=0.952, relheight=0.79)

		self.gridButtons = [[0 for y in range(16)] for x in range(30)]

		for x in range(30):
			for y in range(16):
				self.gridButtons[x][y] = Button(self.gridLF, relief=RAISED, bd=5)
				self.gridButtons[x][y].bind('<Button-3>', self.leftClick)
				self.gridButtons[x][y].bind('<ButtonPress-1>', self.onPress)
				self.gridButtons[x][y].bind('<ButtonRelease-1>', self.onRelease)
				if x < 10 and y < 10:
					self.gridButtons[x][y].place(x=x*23+0, y=y*23+0, width=23, height=23)
	#########################################################################
###########################################################################################

#######################################   Methods   #######################################
	def setupGame(self, difficulty):
		count, self.mines, self.vals = 0, [], [[], [], [], [], [], [], [], [], []]
		if difficulty == 'easy':
			self.flags.set(10)
			while count < 10:
				mine = (random.randint(0, 9), random.randint(0, 9))
				if mine not in self.mines:
					self.mines.append(mine)
					count += 1
		elif difficulty == 'medium':
			self.flags.set(40)
			while count < 40:
				mine = (random.randint(0, 16), random.randint(0, 16))
				if mine not in self.mines:
					self.mines.append(mine)
					count += 1
		elif difficulty == 'hard':
			self.flags.set(99)
			while count < 99:
				mine = (random.randint(0, 30), random.randint(0, 16))
				if mine not in self.mines:
					self.mines.append(mine)
					count += 1

		for x in range(self.Xsize):
			for y in range(self.Ysize):
				if (x, y) not in self.mines:
					val = self.neighborCount(x, y)
					self.vals[val].append((x, y))

	def neighborCount(self, X, Y):
		value = 0
		for nx, ny in [(-1, -1), (-1, 0), (-1, 1),
					   ( 0, -1),          ( 0, 1),
					   ( 1, -1), ( 1, 0), ( 1, 1)]:
			if (X+nx, Y+ny) in self.mines:
				value += 1
		return value

	def onClick(self, event):
		for x in range(self.Xsize):
			for y in range(self.Ysize):
				if self.gridButtons[x][y] == event.widget:
					if (x, y) in self.mines:
						self.gridButtons[x][y].config(bg='#FF0000')
						self.gameLose()
					else:
						self.discoverNeighbors(x, y, event.widget)

	def leftClick(self, event):
		if event.widget['bd'] != 1:
			if event.widget['image'] == '' and self.flags.get() > 0:
				event.widget.config(image=self.flag)
				event.widget.image = self.flag
				self.flags.set(self.flags.get() - 1)
			elif event.widget['image'] == 'pyimage5':
				event.widget.config(image='')
				self.flags.set(self.flags.get() + 1)

	def onPress(self, event):
		self.gameButton.config(image=self.o_face)
		self.gameButton.image = self.o_face
		print(event.x, event.y)

	def onRelease(self, event):
		self.gameButton.config(image=self.smiley)
		self.gameButton.image = self.smiley
		print(event.x, event.y)
		if event.x >= 0 and event.y >= 0 and event.x <= 22 and event.y <= 22:
			self.onClick(event)

	# Recursive flood-fill algorithm.
	def discoverNeighbors(self, X, Y, cell):
		cell.unbind('<Button-3>')
		cell.unbind('<ButtonPress-1>')
		cell.unbind('<ButtonRelease-1>')
		if cell['bd'] != 1 and (X, Y) in self.vals[0]:
			if cell['image'] == 'pyimage5':
				cell.config(image='')
			cell.config(bd=1)
			if X < self.Xsize - 1:
				self.discoverNeighbors(X+1, Y, self.gridButtons[X+1][Y])
			if X > 0:
				self.discoverNeighbors(X-1, Y, self.gridButtons[X-1][Y])
			if Y < self.Ysize - 1:
				self.discoverNeighbors(X, Y+1, self.gridButtons[X][Y+1])
			if Y > 0:
				self.discoverNeighbors(X, Y-1, self.gridButtons[X][Y-1])
		elif cell['bd'] != 1 and (X, Y) not in self.mines:
			for level in range(len(self.vals)):
				if (X, Y) in self.vals[level]:
					cell.config(text=str(level), bd=1, fg=self.colors[level-1], font=('Courier', 15, 'bold'), image='')
		self.checkForWin()

	def gameLose(self):
		for x in range(self.Xsize):
			for y in range(self.Ysize):
				self.gridButtons[x][y].unbind('<Button-3>')
				self.gridButtons[x][y].unbind('<ButtonPress-1>')
				self.gridButtons[x][y].unbind('<ButtonRelease-1>')
				if (x, y) in self.mines:
					self.gridButtons[x][y].config(image=self.mine)
					self.gridButtons[x][y].image = self.mine
		self.gameButton.config(image=self.frowny)
		self.master.after_cancel(self.loop)
		self.gameButton.image = self.frowny
		self.GAME_STATE = 1

	def checkForWin(self):
		discovered_cells = 0
		for x in range(self.Xsize):
			for y in range(self.Ysize):
				if (x, y) not in self.mines:
					if self.gridButtons[x][y]['bd'] == 1:
						discovered_cells += 1
		if discovered_cells == self.Xsize * self.Ysize - len(self.mines):
			for x in range(self.Xsize):
				for y in range(self.Ysize):
					self.gridButtons[x][y].unbind('<Button-3>')
					self.gridButtons[x][y].unbind('<ButtonPress-1>')
					self.gridButtons[x][y].unbind('<ButtonRelease-1>')
			self.gameButton.config(image=self.coolface)
			self.master.after_cancel(self.loop)
			self.gameButton.image = self.coolface
			self.GAME_STATE = 2

	def resetGame(self):
		if self.GAME_STATE == 0:
			return
		elif self.GAME_STATE == 1 or self.GAME_STATE == 2:
			self.setupGame(self.difficulty)
			for x in range(self.Xsize):
				for y in range(self.Ysize):
					self.gridButtons[x][y].config(relief=RAISED, bd=5, text='', image='', bg=self.original_color)

					self.gridButtons[x][y].bind('<Button-3>', self.leftClick)
					self.gridButtons[x][y].bind('<ButtonPress-1>', self.onPress)
					self.gridButtons[x][y].bind('<ButtonRelease-1>', self.onRelease)
			self.gameButton.config(image=self.smiley)
			self.gameButton.image = self.smiley
			self.master.after_cancel(self.loop)
			self.curTime.set(0)
			self.updateTime()
			self.GAME_STATE = 0

	def forceReset(self, event):
		self.GAME_STATE = 1
		self.resetGame()

	def changeDifficulty(self, difficulty):
		if self.difficulty == difficulty:
			return
		if difficulty == 'easy':
			self.master.geometry('250x300')
			self.replaceCells(10, 10)
		elif difficulty == 'medium':
			self.master.geometry('394x475')
			self.replaceCells(16, 16)
		elif difficulty == 'hard':
			self.master.geometry('732x475')
			self.replaceCells(30, 16)
		self.difficulty = difficulty
		self.setupGame(self.difficulty)
		self.forceReset(Button(self.master))

	def replaceCells(self, new_x, new_y):
		for x in range(self.Xsize):
			for y in range(self.Ysize):
				self.gridButtons[x][y].place_forget()
				self.gridButtons[x][y].unbind('<Button-3>')
				self.gridButtons[x][y].unbind('<ButtonPress-1>', self.onPress)
				self.gridButtons[x][y].unbind('<ButtonRelease-1>', self.onRelease)
		self.Xsize, self.Ysize = new_x, new_y
		for x in range(self.Xsize):
			for y in range(self.Ysize):
				self.gridButtons[x][y].place(x=x*23+0, y=y*23+0, width=23, height=23)
				self.gridButtons[x][y].bind('<Button-3>', self.leftClick)
				self.gridButtons[x][y].bind('<ButtonPress-1>', self.onPress)
				self.gridButtons[x][y].bind('<ButtonRelease-1>', self.onRelease)

	def quitGame(self):
		self.master.destroy()

	def updateTime(self):
		if self.curTime.get() == 999:
			return
		self.curTime.set(self.curTime.get() + 1)
		self.loop = self.master.after(1000, self.updateTime)
###########################################################################################

def main():
	root = Tk()
	root.iconbitmap('./images/mine.ico')
	root.resizable(False, False)
	root.title('Minesweeper')
	root.geometry('250x320')
	ms = minesweeper()
	root.mainloop()

if __name__ == '__main__':
	main()
