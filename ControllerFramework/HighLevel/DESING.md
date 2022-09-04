# Application design
We have a high prvilaged wrapper(task manager). Task Manager controll all processes in HighLevel(watchdog, status changes). All high-level splitted into micro-services.
Micro-services are divided into 2 groups: passive and active. Active is service that works all time in another thread(and communicate with taskmanager via special global dictionary). Passive micro-service works only when you need. </br>
All micro-services is a class(object). </br>
### List of micro-services: 
#### Active
1. WebUI
2. SensorsReader(read buttons and another sensors data from robot)
3. SocketCommunication(communicate between robot and base camera) # Not implemented now
#### Passive
1. Robot(main class of robot, used for moving)
2. Interpreter(process route step)
3. Logger(integrated into TaslManager, but created by another class)

## TaskManager overview
`mainloop` method - after all high-level classes inited this method starts in main thread. This is a infinity loop that checks all robot sensors and process their output and then makes a decision what to do.

### TaskManager API return codes
If process manager return code is < 0, so it is error </br>
1: Process started </br>
100: Process killed </br>
-10: Error, Can't start process, error in process class</br>
-90: Error, Cant't start process, this process type already running(not implemented)</br>
-100: Error, no such process to kill

### TaskManager API share data
Share data `self.share_dict` is a global dict that shared for all processes. This dict is a solution of communication between processes(for example taskmanager and socket service).
#### ShareDict keys:
Global execution status variables(`execution_status` key):</br>
1. 0 - no route executing now
2. 1 - route execution starting request
3. 2 - route execution is going
4. 3 - route execution stop request
