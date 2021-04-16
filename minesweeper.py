import random, os
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
		self.difficulty = 'Beginner'
		self.Xsize, self.Ysize = 10, 10
		self.flags, self.curTime = IntVar(), IntVar()
		self.loop, self.vals, self.mines, self.original_color = None, None, None, None
		self.colors = ['#2626F2', '#007B00', '#FF0000', '#00007B', '#7B0000', '#008080', '#0D1110', '#808080']

		# Images used. [Cannot be declared as a global variable (too early)]
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
		difficultyBar.add_command(label='Beginner', command=lambda: self.changeDifficulty('Beginner'))
		difficultyBar.add_command(label='Intermediate', command=lambda: self.changeDifficulty('Intermediate'))
		difficultyBar.add_command(label='Expert', command=lambda: self.changeDifficulty('Expert'))
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
		# Create the SUNKEN label frame to hold flag count, game button, & timer.
		topBarLF = LabelFrame(self.master, relief=SUNKEN, bg='#C0C0C0', bd=5)
		topBarLF.place(relx=0.025, rely=0.015625, relwidth=0.955, height=45)

		# Add the flag count label to the top bar.
		self.flagLabel = Label(topBarLF, textvariable=self.flags)
		self.flagLabel.place(relx=0.06, y=3, relwidth=0.2, height=30)

		# Add the game button to the top bar.
		self.gameButton = Button(topBarLF, image=self.smiley, relief=RAISED, bd=4, command=self.resetGame)
		self.gameButton.place(relx=0.425, y=1, relwidth=0.145, height=35)
		self.gameButton.image = self.smiley

		# Add a timer label to the top bar.
		self.timeLabel = Label(topBarLF, textvariable=self.curTime)
		self.timeLabel.place(relx=0.74, y=3, relwidth=0.2, height=30)
		self.original_color = self.gameButton.cget('background')
	#########################################################################

	################################# Mine Field ############################
	def createGrid(self):
		# Create a SUNKEN label frame to hold the cells.
		self.gridLF = LabelFrame(self.master, relief=SUNKEN, bg='#C9C9C9', bd=4)
		self.gridLF.place(relx=0.025, rely=0.171875, relwidth=0.952, relheight=0.79)
		self.gridButtons = [[0 for y in range(16)] for x in range(30)]

		# Place all of them onto the label frame.
		for x in range(30):
			for y in range(16):
				self.gridButtons[x][y] = Button(self.gridLF, relief=RAISED, bd=5)
				self.bindAll(self.gridButtons[x][y])
				if x < 10 and y < 10:
					self.gridButtons[x][y].place(x=x*23+0, y=y*23+0, width=23, height=23)
	#########################################################################
###########################################################################################

#######################################   Methods   #######################################
	# Sets up the game by placing 10, 40, or 99 mines randomly on the lattice, then marking
	# the other cells either 0 (no adjacent mine) to 8 (8 adjacent mines) in an array of
	# arrays; in which the sub-array's index is the # of neighbors. Ex: (2, 4) in vals[X]
	# means (2, 4) has X neighboring mine(s).
	def setupGame(self, difficulty):
		count, self.mines, self.vals = 0, [], [[], [], [], [], [], [], [], [], []]
		if difficulty == 'Beginner':
			self.flags.set(10)
			while count < 10:
				mine = (random.randint(0, 9), random.randint(0, 9))
				if mine not in self.mines:
					self.mines.append(mine)
					count += 1
		elif difficulty == 'Intermediate':
			self.flags.set(40)
			while count < 40:
				mine = (random.randint(0, 15), random.randint(0, 15))
				if mine not in self.mines:
					self.mines.append(mine)
					count += 1
		elif difficulty == 'Expert':
			self.flags.set(99)
			while count < 99:
				mine = (random.randint(0, 29), random.randint(0, 15))
				if mine not in self.mines:
					self.mines.append(mine)
					count += 1

		for x in range(self.Xsize):
			for y in range(self.Ysize):
				if (x, y) not in self.mines:
					val = self.neighborCount(x, y)
					self.vals[val].append((x, y))

	# Counts the number of neighbors given a cell's position.
	def neighborCount(self, X, Y):
		value = 0
		for nx, ny in [(-1, -1), (-1, 0), (-1, 1),
					   ( 0, -1),          ( 0, 1),
					   ( 1, -1), ( 1, 0), ( 1, 1)]:
			if (X+nx, Y+ny) in self.mines:
				value += 1
		return value

	# On left click: find the cell's position, and check if it is a mine or a
	# a number. Then either lose the game, or discover neighboring cells.
	def onClick(self, event):
		for x in range(self.Xsize):
			for y in range(self.Ysize):
				if self.gridButtons[x][y] == event.widget:
					if self.gridButtons[x][y]['image'] == 'pyimage6':
						pass
					elif (x, y) in self.mines:
						self.gridButtons[x][y].config(bg='#FF0000')
						self.gameLose()
					else:
						self.discoverNeighbors(x, y, event.widget)

	# On right click: toggle a image of a flag on the cell if the cell has not
	# been clicked, and if there are greater than 0 flags available.
	def rightClick(self, event):
		if event.widget['bd'] != 1:
			if event.widget['image'] == '' and self.flags.get() > 0:
				event.widget.config(image=self.flag)
				event.widget.image = self.flag
				self.flags.set(self.flags.get() - 1)
			elif event.widget['image'] == 'pyimage6':
				event.widget.config(image='')
				self.flags.set(self.flags.get() + 1)

	# On left-button press: set the game button's image to an O-face.
	def onPress(self, event):
		self.gameButton.config(image=self.o_face)
		self.gameButton.image = self.o_face

	# On left-button release: revert the image to the smiley. Executes the
	# left-click function IFF the mouse curser is still on the button.
	def onRelease(self, event):
		self.gameButton.config(image=self.smiley)
		self.gameButton.image = self.smiley
		if event.x >= 0 and event.y >= 0 and event.x <= 22 and event.y <= 22:
			self.onClick(event)

	# Recursive flood-fill algorithm: discovers all non-number cells 
	# left, right, top, and bottom, and all numbered cells on each corner
	def discoverNeighbors(self, X, Y, cell):
		self.unbindAll(cell)
		if cell['bd'] != 1 and (X, Y) in self.vals[0]:
			if cell['image'] == 'pyimage6':
				self.bindAll(cell)
				self.gameButton.config(image=self.smiley)
			else:
				cell.config(bd=1)
				if X < self.Xsize - 1:
					self.discoverNeighbors(X+1, Y, self.gridButtons[X+1][Y])
				if X > 0:
					self.discoverNeighbors(X-1, Y, self.gridButtons[X-1][Y])
				if Y < self.Ysize - 1:
					self.discoverNeighbors(X, Y+1, self.gridButtons[X][Y+1])
				if Y > 0:
					self.discoverNeighbors(X, Y-1, self.gridButtons[X][Y-1])
				if X < self.Xsize - 1 and Y < self.Ysize - 1:
					self.discoverNeighbors(X+1, Y+1, self.gridButtons[X+1][Y+1])
				if X > 0 and Y > 0:
					self.discoverNeighbors(X-1, Y-1, self.gridButtons[X-1][Y-1])
				if X < self.Xsize - 1 and Y > 0:
					self.discoverNeighbors(X+1, Y-1, self.gridButtons[X+1][Y-1])
				if X > 0 and Y < self.Ysize - 1:
					self.discoverNeighbors(X-1, Y+1, self.gridButtons[X-1][Y+1])
		elif cell['bd'] != 1 and (X, Y) not in self.mines:
			if cell['image'] == 'pyimage6':
				self.bindAll(cell)
			else:
				for level in range(len(self.vals)):
					if (X, Y) in self.vals[level]:
						cell.config(text=str(level), bd=1, fg=self.colors[level-1], font=('Courier', 15, 'bold'), image='')
		self.checkForWin()

	# If the user clicks on a mine, the game is lost: all cells are unbound
	# the game buttons image turns into a frowny face, and the timer stops.
	def gameLose(self):
		for x in range(self.Xsize):
			for y in range(self.Ysize):
				self.unbindAll(self.gridButtons[x][y])
				if (x, y) in self.mines:
					self.gridButtons[x][y].config(image=self.mine)
					self.gridButtons[x][y].image = self.mine
		self.gameButton.config(image=self.frowny)
		self.master.after_cancel(self.loop)
		self.gameButton.image = self.frowny
		self.GAME_STATE = 1

	# Counts for the number of discovered cells to determine a win:
	# If the # of discovered cells equals X * Y - |Mines|.
	# Example: 30 * 16 - 99 = 381 possible discoverable cells for expert.
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
					self.unbindAll(self.gridButtons[x][y])
			self.gameButton.config(image=self.coolface)
			self.master.after_cancel(self.loop)
			self.gameButton.image = self.coolface
			self.GAME_STATE = 2
			self.saveScore()

	# Resets the game given the game-state:
	# Gamestate 0 -> No loss, no win.
	# Gamestate 1 -> Game lost.
	# Gamestate 2 -> Game won.
	def resetGame(self):
		if self.GAME_STATE == 0:
			return
		elif self.GAME_STATE == 1 or self.GAME_STATE == 2:
			self.setupGame(self.difficulty)
			for x in range(self.Xsize):
				for y in range(self.Ysize):
					self.gridButtons[x][y].config(relief=RAISED, bd=5, text='', image='', bg=self.original_color)
					self.bindAll(self.gridButtons[x][y])
			self.gameButton.config(image=self.smiley)
			self.gameButton.image = self.smiley
			self.master.after_cancel(self.loop)
			self.curTime.set(0)
			self.updateTime()
			self.GAME_STATE = 0

	# Force reset the game event. (Bound to F2)
	def forceReset(self, event):
		self.GAME_STATE = 1
		self.resetGame()

	# Swaps the difficulty of the game.
	# Resizes window, replaces cells, changes difficulty variable,
	# sets up the game, and forces a reset.
	def changeDifficulty(self, difficulty):
		if self.difficulty == difficulty:
			return
		if difficulty == 'Beginner':
			self.master.geometry('250x300')
			self.replaceCells(10, 10)
		elif difficulty == 'Intermediate':
			self.master.geometry('394x475')
			self.replaceCells(16, 16)
		elif difficulty == 'Expert':
			self.master.geometry('732x475')
			self.replaceCells(30, 16)
		self.difficulty = difficulty
		self.setupGame(self.difficulty)
		self.forceReset(Button(self.master))

	# A method to remove the current cells off the gui (place_forget()),
	# removes the key-binding, and replaces and rebinds them given a new
	# number of cells.
	def replaceCells(self, new_x, new_y):
		for x in range(self.Xsize):
			for y in range(self.Ysize):
				self.gridButtons[x][y].place_forget()
				self.unbindAll(self.gridButtons[x][y])
		self.Xsize, self.Ysize = new_x, new_y
		for x in range(self.Xsize):
			for y in range(self.Ysize):
				self.gridButtons[x][y].place(x=x*23+0, y=y*23+0, width=23, height=23)
				self.bindAll(self.gridButtons[x][y])

	# Simple method to add 3 different binds to a cell.
	def bindAll(self, cell):
		cell.bind('<Button-3>', self.rightClick)
		cell.bind('<ButtonPress-1>', self.onPress)
		cell.bind('<ButtonRelease-1>', self.onRelease)

	# Simple method to remove 3 different binds to a cell.
	def unbindAll(self, cell):
		cell.unbind('<Button-3>')
		cell.unbind('<ButtonPress-1>')
		cell.unbind('<ButtonRelease-1>')

	# Quits the game (menu bar function).
	def quitGame(self):
		self.master.destroy()

	def saveScore(self):
		fd = None
		if not os.path.isfile('./Scoreboard.txt'):
			fd = open('./Scoreboard.txt', 'a+')
			fd.write('DIFFICULTY     -   SCORE\n')
		else:
			fd = open('./Scoreboard.txt', 'a+')
		if self.difficulty == 'Beginner':
			fd.write(self.difficulty + '       -   ' + str(self.curTime.get()) + '\n')
		elif self.difficulty == 'Intermediate':
			fd.write(self.difficulty + '   -   ' + str(self.curTime.get()) + '\n')
		elif self.difficulty == 'Expert':
			fd.write(self.difficulty + '         -   ' + str(self.curTime.get()) + '\n')
		fd.close()

	# Updates the time every 1 second, and stops at 999 seconds.
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
