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
