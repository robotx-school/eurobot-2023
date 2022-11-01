import tkinter as tk

window = tk.Tk()
window.title("coord")
window.geometry("300x200")
window.resizable(width=False, height=False)
canvas = tk.Canvas(window, width=500, height=500, bg='white')
canvas.pack()

pos = [[0 for j in range(30)] for i in range(20)]

robot1_pos = (10, 10)
robot2_pos = (100, 100)


def click(a):
    global robot1_pos, robot2_pos
    canvas.create_rectangle(0, 0, 300, 200, fill='white', width=1)
    x, y = robot1_pos
    if a.keycode == 37 and x > 0: x -= 10
    if a.keycode == 39 and x < 290: x += 10
    if a.keycode == 38 and y > 0: y -= 10
    if a.keycode == 40 and y < 190: y += 10
    robot1_pos = (x, y)
    canvas.create_rectangle(x-10, y-10, x + 10, y + 10, fill='green')
    x, y = robot2_pos
    if a.keycode == 65 and x > 0: x -= 10
    if a.keycode == 68 and x < 290: x += 10
    if a.keycode == 87 and y > 0: y -= 10
    if a.keycode == 83 and y < 190: y += 10
    robot2_pos = (x, y)
    canvas.create_rectangle(x - 10, y - 10, x + 10, y + 10, fill='blue')


window.bind("<KeyPress>", click)
window.mainloop()
