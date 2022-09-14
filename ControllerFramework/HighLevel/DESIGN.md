# High-level architecture
Ok, I have already rewritten high level several times and finally came to an idea and implementation that I like. I got an efficient, flexible and productive architecture.

## Main features
The main idea is that there is a so-called task manager. His task is to monitor the state of the robot, he knows everything: information from espiay, std and local highlevel information, such as, for example, the time since the start of the match. Having received all the information, the task manager processes it and makes decisions. I already wrote about the flexibility of the architecture, at the moment the architecture allows the task manager to do anything with the robot.

## Debugging
![image](https://user-images.githubusercontent.com/55328925/190237670-898f5a90-2b72-4ca0-ab34-ec5eea11b1fd.png)
Use webapi `http://localhost:8080/api/dev/tmgr`

## Going deeper