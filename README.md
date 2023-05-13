# Eurobot 2023 develop REPO
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
