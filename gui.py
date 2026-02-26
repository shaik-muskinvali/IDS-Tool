import tkinter as tk

# Create window
window = tk.Tk()
window.title("My First App")
window.geometry("400x300")

# Create label
label = tk.Label(window, text="Welcome to My App")
label.pack(pady=20)

# Create button
def say_hello():
    label.config(text="Button Clicked!")

button = tk.Button(window, text="Click Me", command=say_hello)
button.pack()

# Run app
window.mainloop()