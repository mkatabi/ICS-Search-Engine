from Tkinter import *
from index import InvertedIndex
import webbrowser

class SearchEngineGUI:
	def __init__(self, index):
		## Tkinter Set Up
		# master frame
		self.master = Tk()
		self.master.title("UCI ICS Search Engine")

		self.window_width = 800
		self.window_height = 500
		self.master.minsize(self.window_width, self.window_height)
		self.master.config(padx = 100, pady = 100)

		self.screen_width = self.master.winfo_screenwidth()
		self.screen_height = self.master.winfo_screenheight()

		self.x_coordinate = int((self.screen_width/2) - (self.window_width/2))
		self.y_coordinate = int((self.screen_height/2) - (self.window_height/2))

		self.master.geometry("{}x{}+{}+{}".format(self.window_width, self.window_height, self.x_coordinate, self.y_coordinate))

		# title label
		self.label = Label(self.master, text = "UCI ICS Search Engine", font = ("Georgia", 50))
		self.label.pack()

		# entry field
		self.entry = Entry(self.master, width = 30)
		self.entry.pack()

		# search button
		self.search_button = Button(self.master, text = "Search", command = self.search)
		self.search_button.pack()

		# Index Creation
		self.index = index

		self.master.mainloop()


	def search(self):
		query = self.entry.get()
		links = self.index.lookup_index(query)

		self.new_window = Toplevel(self.master)
		self.new_window.title("Results")

		for count, link in enumerate(links, 1):
			url, title, snippet = link
			title_label = Label(self.new_window, text = str(count) + ". " + title, wraplength = 1000, font=("Georgia", 15, 'bold'))
			result_label = Label(self.new_window, text = url, fg = "blue", wraplength = 1000)
			snippet_label = Label(self.new_window, text = "Snippet: " + snippet, pady = 10, wraplength = 1000)

			title_label.pack()
			result_label.pack()
			snippet_label.pack()

			result_label.bind("<Button-1>", self.open_url)


	def open_url(self, event):
		webbrowser.open_new("http://" + event.widget.cget("text"))

		