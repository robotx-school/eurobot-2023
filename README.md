# Eurobot 2023 develop REPO
## Repo archived
THis robot got third place in Russia final. Now this repo is closed.

### About branches
`master` is now default branch for develop. All code pushed directed in this branch.
`main` - Stable, pending to test || tested on real robot(status can be checked from merge pull request description)</br>
`develop` - Legacy code for now </br>
`micro_serviced` - Current rolling development
### Content:
[Controller Framework(Communication between Arduino & RPi)](/ControllerFramework) </br>
[Gui for simple routes creating](/PathMaker) </br>
[WebCalculator](https://ret7020.github.io/EurobotCalculator/)
### About PathMaker
PathMaker requires external libraries that you can find in ControllerFramework. </br>
`geometry.py` - Vector math </br>
`robot.py` - Robot declaration(on high-level) </br>
`spilib.py` - SPI communication between Arduino and RPi

### Servo
0 deg to 25 deg

### Fast local net discover
* Xiaomi ips range: *0.0.0.0/24*
* delo fake router ips range: *0.0.0.0/24*

```bash
nmap -sn 192.168.1.11/24
```

### MATCH TO DO CHECKLIST 
- [] Robot position: Edge of start board; Forward gripper direction to CherryTrashBox
- [] Robot servos enabled before starting high-level
- [] Robot high-level started then disable servo; put cherries in gripper; enable servo
- [] Lidar servo works; changing self angle
- [] Robot web api works
- [] Robot high-level started in screen session
- [] Check robot route with correct side(71.blue.json or 71.green.json)
- [] ChecrryTrashBox web api works and showing 00 at start

