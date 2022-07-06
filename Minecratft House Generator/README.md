# Minecraft House Generator

## Overview
The aim of this project was to procedurally build a village in Minecraft using python and the mcpi API.
My contribution for this project was to build a random procedural house generator with python. (Houses module)
OOP was used for this team project. All the objects inherit from a Cuboid parent class in the helper module.

---

## Features
- The house generator is able to handle random sizes for house width/lenght.
- Internal rooms are recursively divided until a minimum size from a specified random range is reached. 
- When placing int walls, the code checks for doors and windows in the way. 
    - If one is found, another position is randomly selected from a list of possible options. 
    - If no positions are available, the room division stops. 
- All internal rooms are connected with a door. 
- When placing a door, the code checks for intersecting walls, if one is found the door is placed +- 1 block either side.
- All external walls have a window or a front door, while internal walls only have doors.
- Houses are randomly selected to be single or double storey. 
    - If a house is double storey a stair is added.

---
## Random Generator Preview
- Here is an example of the main.py file running to produce three random houses.

![](images/random_build.gif)

---
## Internal Wall Division
- Here is an example of the internal room division adding internal walls, doors and windows.

![](images/internal_divisions.gif)

---