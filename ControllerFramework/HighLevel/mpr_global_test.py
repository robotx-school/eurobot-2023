# Communicate between main loop and process
from multiprocessing import Process, Value

def loop():
    print(1)

p = Process(target=lambda: loop())
p.run()
while True:
    print(p)