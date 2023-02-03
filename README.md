# Eurobot 2023 develop branch
### About branches
`main` - Stable, pending to test || tested on real robot(status can be checked from merge pull request description)</br>
`develop` - Legacy code for now </br>
`micro_serviced` - Current rolling development
### Content:
[Controller Framework(Communication between Arduino & RPi)](/ControllerFramework) </br>
[Gui for simple routes creating](/PathMaker)
### About PathMaker
PathMaker requires external libraries that you can find in ControllerFramework. </br>
`geometry.py` - Vector math </br>
`robot.py` - Robot declaration(on high-level) </br>
`spilib.py` - SPI communication between Arduino and RPi