import tkinter as tk
import json
import re
import tkinter.filedialog
import tkinter.messagebox
import math

x, y = 0, 0
lx, ly = 0, 0

root = tk.Tk()
root.geometry("300x600")
root.resizable(0, 0)

root.title('PathMaker_lite')

output_default = {'blue': {'path': [], 'pos': [335, 1790]}, 'green': {'path': [], 'pos': [335, 210]}}
output = output_default.copy()
output = json.dumps(output)
output = json.loads(output)

team = False

canvas = tk.Canvas(root, width=300, height=200)
canvas.pack(anchor = "nw", expand=True)

def click_team_btn():
    global team
    team = not team
    
    if team:
        team_btn.config(text="Команда: blue")
    else:
        team_btn.config(text="Команда: green")
    format_()

team_btn = tk.Button(root, text="Команда: green", command=click_team_btn)
team_btn.pack()

def V2_angle_V2(a : tuple = (0, 1), b : tuple = (1, 0)) -> float: 
    v = math.degrees(math.acos( (a[0]*b[0] + a[1]*b[1])/ (math.sqrt(a[0]**2 + a[1]**2) * math.sqrt(b[0]**2+ b[1]**2))))
    return v

def format_(from_text = True):
    global output
    global canvas
    global text
    global team
    canvas.delete("all")
    canvas.create_image((152, 102),image=python_image)

    if team:
        team_str = "blue"
    else:
        team_str = "green"

    if text.get(1.0, tk.END) == "" or text.get(1.0, tk.END) == "\n" or text.get(1.0, tk.END) == " ":
        output = output_default.copy()
        output = json.dumps(output)
        output = json.loads(output)
    elif from_text:
        output = json.loads(text.get(1.0, tk.END))

    output_str = json.dumps(output, indent = 2)


    
    canvas.create_oval(output["green"]["pos"][0]//10-5,output["green"]["pos"][1]//10-5,output["green"]["pos"][0]//10+5,output["green"]["pos"][1]//10+5,fill='green')
    canvas.create_oval(output["blue"]["pos"][0]//10-5,output["blue"]["pos"][1]//10-5,output["blue"]["pos"][0]//10+5,output["blue"]["pos"][1]//10+5,fill='blue')
    c_path = output[team_str]["pos"].copy()
    rot = 90
    for i in output[team_str]["path"]:
        if (isinstance(i[0], int) or isinstance(i[0], float)) and len(i) == 2:
            canvas.create_line(c_path[0]//10,
                               c_path[1]//10,
                               i[0]//10,
                               i[1]//10,
                               fill='green',
                               width=5,
                               arrow=tk.LAST)
            rot =  round(V2_angle_V2(((i[0] - c_path[0]), (i[1] - c_path[1]))) +180)+90
            c_path = [i[0], i[1]]
            
        elif (isinstance(i[0], int) or isinstance(i[0], float)) and len(i) == 3:
            if c_path[0] <= i[0] and c_path[1] <= i[1] and c_path != i:
                angle_plane = 3
            elif c_path[0] >= i[0] and c_path[1] <= i[1] and c_path != i:
                angle_plane = 4
            elif c_path[0] >= i[0] and c_path[1] >= i[1] and c_path != i:
                angle_plane = 1
            elif c_path[0] <= i[0] and c_path[1] >= i[1] and c_path != i:
                angle_plane = 2
            else:
                angle_plane = 0
                
            canvas.create_line(c_path[0]//10,
                               c_path[1]//10,
                               i[0]//10,
                               i[1]//10,
                               fill='purple', dash=(10,2),
                               width=3,
                               arrow=tk.LAST)
            canvas.create_line(c_path[0]//10,
                               c_path[1]//10,
                               c_path[0]//10,
                               i[1]//10,
                               fill='green',
                               width=5,
                               arrow=tk.LAST)
            canvas.create_line(c_path[0]//10,
                               i[1]//10,
                               i[0]//10,
                               i[1]//10,
                               fill='green',
                               width=5,
                               arrow=tk.LAST)

            if c_path[0] <= i[0] and c_path != i:
                rot = 180
            elif c_path[0] >= i[0] and c_path != i:
                rot = 0
            c_path = [i[0], i[1]]

            
        elif (isinstance(i[0], str)) and len(i) >= 2:
            if i[0] == "rotate" and (isinstance(i[1], int) or isinstance(i[1], float)):
                rot -= int(i[1])
                canvas.create_oval(c_path[0]//10-2,c_path[1]//10-2,c_path[0]//10+2,c_path[1]//10+2,fill='black')


                
            elif i[0] == "forward" and (isinstance(i[1], int) or isinstance(i[1], float)):
                c_path_ = c_path.copy()
                c_path[0] += round(math.cos(math.radians(rot+180))*i[1] / 5.71)
                c_path[1] += round(math.sin(math.radians(rot+180))*i[1] / 5.71)
                canvas.create_line(c_path_[0]//10,
                               c_path_[1]//10,
                               c_path[0]//10,
                               c_path[1]//10,
                               fill='blue',
                               width=5,
                               arrow=tk.LAST)
            elif i[0] == "back" and (isinstance(i[1], int) or isinstance(i[1], float)):
                c_path_ = c_path.copy()
                c_path[0] += round(math.cos(math.radians(rot))*i[1] / 5.71)
                c_path[1] += round(math.sin(math.radians(rot))*i[1] / 5.71)
                canvas.create_line(c_path_[0]//10,
                               c_path_[1]//10,
                               c_path[0]//10,
                               c_path[1]//10,
                               fill='red',
                               width=5,
                               arrow=tk.LAST)
        elif i[0] == "to90":
            rot = 90
            canvas.create_oval(c_path[0]//10-2,c_path[1]//10-2,c_path[0]//10+2,c_path[1]//10+2,fill='white')
                

        
        rot = rot%360
                
            
    print(f"format_ / rot (prog): {rot} / c_path: {c_path}")
    text.delete(1.0, tk.END)
    text.insert(1.0, output_str)
    

format_btn = tk.Button(root, text="Сохранение формата (Ctrl + B)", command=format_)
format_btn.pack()

v = tk.Scrollbar(root, orient='vertical')
v.pack(side="right", fill='y')

token_to_tag = {"~" : "red", "-" : "orange"}

def on_edit_text(event):
    for tag in text.tag_names():
        text.tag_remove(tag, 1.0, tk.END)
    
    s = text.get(1.0, tk.END)
    
    for i, line in enumerate(s.splitlines(), start=1):
        for match in re.finditer(r"\S", line):
            token_text = match.group(0).lower()
            start = match.start()
            end = match.end()
            
            if token_text in token_to_tag:
                text.tag_add(token_to_tag[token_text], f"{i}.0", f"{i}.100")

    text.edit_modified(0)



text = tk.Text(root, width=37, height=20, yscrollcommand=v.set)
text.pack(anchor = "nw", expand=True)
text.insert(1.0, json.dumps(output))
text.tag_config("red", foreground="red")
text.tag_config("orange", foreground="orange")

text.bind('<<Modified>>', on_edit_text)


def callback(event):
    global x
    global y
    global lx
    global ly
    lx, ly = event.x, event.y
    x, y = round(event.x*1000/152/2*3), round(event.y*1000/102/2*2)
    menu.post(event.x_root, event.y_root)

def text_callback(event):
    text_menu.post(event.x_root, event.y_root)

def go_to_point():
    global x
    global y
    global text
    global team
    global output
    if team:
        output["blue"]["path"].append([x, y])
    else:
        output["green"]["path"].append([x, y])
    format_(False)

def go_to_point_tr():
    global x
    global y
    global text
    global team
    global output
    if team:
        output["blue"]["path"].append([x, y, "tg"])
    else:
        output["green"]["path"].append([x, y, "tg"])
    format_(False)

def set_start_point():
    global x
    global y
    global text
    global team
    global output
    if team:
        output["blue"]["pos"] = []
        output["blue"]["pos"].append(x)
        output["blue"]["pos"].append(y)
    else:
        output["green"]["pos"] = []
        output["green"]["pos"].append(x)
        output["green"]["pos"].append(y)
    format_(False)

menu = tk.Menu(tearoff=0)
menu.add_command(label="Передвижение на точку (вектор p1p2) BETA!", command=go_to_point)
menu.add_command(label="Передвижение на точку (проекции вектора p1p2)", command=go_to_point_tr)
menu.add_command(label="Установить начальную позицию", command=set_start_point)

def to90():
    global team
    global output
    if team:
        output["blue"]["path"].append(["to90"])
    else:
        output["green"]["path"].append(["to90"])
    format_(False)

def back():
    global team
    global output
    if team:
        output["blue"]["path"].append(["back", -1])
    else:
        output["green"]["path"].append(["back", -1])
    format_(False)

def forward():
    global team
    global output
    if team:
        output["blue"]["path"].append(["forward", -1])
    else:
        output["green"]["path"].append(["forward", -1])
    format_(False)

def rotate():
    global team
    global output
    if team:
        output["blue"]["path"].append(["rotate", -1])
    else:
        output["green"]["path"].append(["rotate", -1])
    format_(False)

def servo():
    global team
    global output
    if team:
        output["blue"]["path"].append(["servo", ["~"], ["~"]])
    else:
        output["green"]["path"].append(["servo", ["~"], ["~"]])
    format_(False)

def delayf():
    global team
    global output
    if team:
        output["blue"]["path"].append(["delay", -1])
    else:
        output["green"]["path"].append(["delay", -1])
    format_(False)

def open_gripper():
    global team
    global output
    if team:
        output["blue"]["path"].append(["open_gripper"])
    else:
        output["green"]["path"].append(["open_gripper"])
    format_(False)

def close_gripper():
    global team
    global output
    if team:
        output["blue"]["path"].append(["close_gripper"])
    else:
        output["green"]["path"].append(["close_gripper"])
    format_(False)

def gripper_init():
    global team
    global output
    if team:
        output["blue"]["path"].append(["gripper_init"])
    else:
        output["green"]["path"].append(["gripper_init"])
    format_(False)

def gripper_grab_start():
    global team
    global output
    if team:
        output["blue"]["path"].append(["gripper_grab_start"])
    else:
        output["green"]["path"].append(["gripper_grab_start"])
    format_(False)

def update_prediction():
    global team
    global output
    if team:
        output["blue"]["path"].append(["update_prediction", "~"])
    else:
        output["green"]["path"].append(["update_prediction", "~"])
    format_(False)

text_menu = tk.Menu(tearoff=0)
text_menu.add_command(label="to90", command=to90)
text_menu.add_command(label="back", command=back)
text_menu.add_command(label="forward", command=forward)
text_menu.add_command(label="rotate", command=rotate)
text_menu.add_command(label="servo", command=servo)
text_menu.add_command(label="delay", command=delayf)
text_menu.add_command(label="open_gripper", command=open_gripper)
text_menu.add_command(label="close_gripper", command=close_gripper)
text_menu.add_command(label="gripper_init", command=gripper_init)
text_menu.add_command(label="gripper_grab_start", command=gripper_grab_start)
text_menu.add_command(label="update_prediction", command=update_prediction)


def save_file():
    global output
    filepath = tk.filedialog.asksaveasfilename(defaultextension="txt", filetypes = (("TXT File with path JSON", "*.txt"), ), initialfile="path.txt")
    if filepath != "":
        print(f"OUTPUT: {output}")
        with open(filepath, "w") as file:
            file.write(json.dumps(output, indent = 2))

def open_file():
    global output
    filepath = tk.filedialog.askopenfilename()
    if filepath != "":
        with open(filepath, "r") as file:
            text_from_file = file.read()
            output = json.loads(text_from_file)
    format_(False)

mainmenu = tk.Menu(root) 
root.config(menu=mainmenu)

def new_file():
    global output
    global output_default
    output = output_default.copy()
    output = json.dumps(output)
    output = json.loads(output)
    format_(False)

def help_():
    tk.messagebox.showinfo("Информация", \
"""PathMaker_lite - программа для создания path переменной роботов на базе spilib_lite (имеется частичная поддержка форков spilib для работы с JSON path).
Негарантирована корректная работа BETA-функционала!

Использование:
ПКМ по карте для выбора типа движения
ПКМ по рабочему полю для выбора типа разового задания

Выделение синтаксиса JSON path:
1. ~ или "~" красным, как поля для заполнения string или многомерных массивов. 
2. -1 жёлтым, как поля для заполнения integer


Eurobot 2023 | RobotX | Вт 16:00-20:00""")


mainmenu.add_command(label='Новый', command=new_file)
mainmenu.add_command(label='Открыть', command=open_file)
mainmenu.add_command(label='Сохранить', command=save_file)
mainmenu.add_command(label='Справка', command=help_)

python_image = tk.PhotoImage(file='plane.gif')
canvas.create_image(
    (152, 102),
    image=python_image
)
    
canvas.bind("<Button-3>", callback)
text.bind("<Button-3>", text_callback)


root.bind('<Control-b>', format_)

format_()
root.mainloop()
