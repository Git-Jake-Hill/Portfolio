from helper import Cuboid, Enclosure, BaseStructure
from helper import Block
from mcpi import block
import random

class House(Cuboid):
    """A house object.
    
    Args:
        mc (object): pass in mcApi
        startingBlock (tuple): starting position for the house.
        endingBlock (tuple): ending position for the house.
        door_direction (char): "N", "E", "S", "W" - sets the front door to the wall facing that direction.
    
    """
    def __init__(self, mc, startingBlock, endingBlock, door_direction="W"):       
        super().__init__(mc, startingBlock, endingBlock)
        self.is_two_storey = bool(random.choice([True, False]))
        self.wall_height = 4
        self.roof_base_height = self.wall_height if not self.is_two_storey else (self.wall_height * 2)
        self.contents = [
            {
                'item': "floor",
                'content': Enclosure(mc, (startingBlock[0], startingBlock[1], startingBlock[2]), (endingBlock[0], startingBlock[1], endingBlock[2]), 5, ["floor"])
            },
            {
                'item': "firstLevel",
                'content': Level(mc, startingBlock, (endingBlock[0], startingBlock[1] + self.wall_height, endingBlock[2]), self.is_two_storey, door_direction)
            },
            {
                'item': "roof",
                'contnet': Roof(mc, self.roof_setout(self.startingBlock), self.roof_setout(self.endingBlock))
            }
        ]
        if self.is_two_storey: 
                self.contents.append(
                {
                'item': "secondLevel",
                'content': Level(mc, (startingBlock[0], startingBlock[1] + self.wall_height, startingBlock[2]), (endingBlock[0], startingBlock[1] + self.roof_base_height , endingBlock[2]), False) 
                }
                )
  
    def roof_setout(self, coord):
        print("Roof base height:", self.roof_base_height)
        return (coord[0], self.startingBlock[1] + self.roof_base_height + 1, coord[2])
             
class Level(Cuboid):
    """A level of a house.
    
    Args:
    
    
    """
    def __init__(self, mc, startingBlock, endingBlock, add_stair, door_direction=None):
        super().__init__(mc, startingBlock, endingBlock)
        global count
        count = 0
        self.add_stair = add_stair
        self.contents = [ 
            {
                'item': "ceiling",
                'content': Enclosure(mc, startingBlock, endingBlock, 5, ["ceiling"])
            },  
            {
                'item': "room",
                'content': Room(mc, startingBlock, endingBlock, self.add_stair, door_direction) 
            }
        ]
    
count = 0
class Room(Cuboid):
    """A room object.
    
    Args:
    
    """
    def __init__(self, mc, startingBlock, endingBlock, add_stair=False, door_direction=None):
        super().__init__(mc, startingBlock, endingBlock)
        global count
        count += 1
        self.ext_walls =["backWall", "leftWall", "rightWall", "frontWall"]
        self.int_walls = []
        self.min_room_size = random.randrange(5,8) # 6
        self.block_range = 0
        self.random_pos = 99
        self.bad_list= []
        self.door_direction = door_direction
        self.door_position = ()
        self.start_block_list = []
        self.end_block_list = []
        self.contents = []
        self.add_external_walls()
        self.contents.append(
            {
                'item': "room",
                'content': self.divide_room() 
            }
        )
        if add_stair:
            self.contents.append(
                    {
                    'item': "stair",
                    'content': stairs(self.mc, (startingBlock[0] + 1,startingBlock[1], startingBlock[2] + 1), endingBlock, "E")
                    }
                )
        if door_direction != None:
            print("***EXT DOOR HERE***")
            print("add door to", door_direction)
            self.external_door()

    def add_external_walls(self):
        """Adds external walls with a window for the current room.
        """        
        print("Wall divide function:")
        self.contents.append(
                    {
                    'item': "ext_walls",
                    'content': [ Wall(self.mc, self.getBorder(x)[0], self.getBorder(x)[1], 5, x) for x in self.ext_walls]
                    }
                )
        

    
    def divide_room(self, axis = None):
        """Divides a room into smaller rooms
        Args:
            axis (_type_): _description_
        Return:
            Returns a room or a list of two rooms
        """

        print("Rooms = ", count, "Room type:", type(self))
        print("\nDivide room:") 
        print("Room coords:", self.startingBlock, self.endingBlock)       
        roomMinX, roomMinY, roomMinZ, roomMaxX, roomMaxY, roomMaxZ = self.getCuboidMinMaxXYZ()
        room_x_dist = abs(roomMaxX - roomMinX)
        room_z_dist = abs(roomMaxZ - roomMinZ)
        print(" x size:", room_x_dist)
        print(" z size:", room_z_dist)

        # get axis if not set
        if axis == None:
            if room_x_dist >= room_z_dist:
                print("axis: x")
                axis = "x"
                room_length = room_x_dist
            else:
                print("axis: z")
                axis = "z"
                room_length = room_z_dist
        
        # block range
        self.block_range = room_length - (self.min_room_size * 2) + 1
        print("Room index range:", room_length, "-", (self.min_room_size * 2), "=", self.block_range)
        if self.block_range < 1:
            print("***Room too small to divide***")
            return

        if axis == "x":
            self.start_block_list = [(self.startingBlock[0] + self.min_room_size + x, self.startingBlock[1], self.startingBlock[2]) for x in range(self.block_range)]
            self.end_block_list = [(self.startingBlock[0] + self.min_room_size + x, self.endingBlock[1], self.endingBlock[2]) for x in range(self.block_range)]

        else:
            self.start_block_list = [(self.startingBlock[0], self.startingBlock[1], self.startingBlock[2] + self.min_room_size + x) for x in range(self.block_range)]
            self.end_block_list = [(self.endingBlock[0], self.endingBlock[1], self.startingBlock[2] + self.min_room_size + x) for x in range(self.block_range)]
            
        
        print(self.start_block_list)
        print(self.end_block_list)

        # get random pos
        good_value = False
        while not good_value:
            random_pos = random.randrange(0, self.block_range)
            
            wall_end = (self.end_block_list[random_pos][0], self.startingBlock[1], self.end_block_list[random_pos][2]) # needs to be the base of wall for y value
            if self.check_if_door(self.start_block_list[random_pos]) or self.check_if_door(wall_end):
                if random_pos not in self.bad_list:
                    self.bad_list.append(random_pos)
            else:
                good_value = True
                print("random wall pos index:", random_pos)

            if len(self.bad_list) == len(self.start_block_list):
                print("  Door in the way, cant divide room")
                return

        if axis == "x":
            # x room 1
            new_room_start = (self.startingBlock[0], self.startingBlock[1], self.start_block_list[random_pos][2])
            new_room_end = (self.end_block_list[random_pos][0], self.endingBlock[1], self.end_block_list[random_pos][2])
            room_a = Room(self.mc, new_room_start, new_room_end)
            # room 2
            new_room_start = (self.end_block_list[random_pos][0], self.startingBlock[1], self.start_block_list[random_pos][2])
            new_room_end = (self.endingBlock[0], self.endingBlock[1], self.end_block_list[random_pos][2])
            room_b = Room(self.mc, new_room_start, new_room_end)
        else:
            # z room 1
            new_room_start = (self.startingBlock[0], self.startingBlock[1], self.startingBlock[2])
            new_room_end = (self.end_block_list[random_pos][0], self.endingBlock[1], self.end_block_list[random_pos][2])
            room_a = Room(self.mc, new_room_start, new_room_end)
            # room 2
            new_room_start = (self.start_block_list[random_pos][0], self.startingBlock[1], self.start_block_list[random_pos][2])
            new_room_end = (self.endingBlock[0], self.endingBlock[1], self.endingBlock[2])
            room_b = Room(self.mc, new_room_start, new_room_end)
        

        int_wall = Wall(self.mc, self.start_block_list[random_pos], self.end_block_list[random_pos], 5, "int_wall")
        int_wall.add_door(axis)
        self.int_walls.append(int_wall)

        return [room_a, room_b]
    
    
    def check_if_door(self, postition):
        """Check for a door or window, if returns True, dont place a wall here.
        Args:
            postition (_type_): _description_
        Returns:
            boolean: True, False
        """  
        block_to_check = self.mc.getBlock(postition[0], postition[1] + 1, postition[2])
        found = False
        # print("\nChecking for door/window:", postition[0], postition[1] + 1, postition[2])
        if block.DOOR_WOOD.id == block_to_check or block.GLASS.id == block_to_check:
            found = True
            print("Found door/window, dont place wall:", found)
            print("At position:", postition[0], postition[1] + 1, postition[2])
        return found

    def external_door(self):
        if self.door_direction.upper() == "N":
            self.door_position = ((self.startingBlock[0] + self.endingBlock[0]) / 2, self.startingBlock[1] + 1, self.startingBlock[2])
            axis = "z"
        elif self.door_direction.upper() == "S":
            self.door_position = ((self.startingBlock[0] + self.endingBlock[0]) / 2, self.startingBlock[1] + 1, self.endingBlock[2])
            axis = "z"
        elif self.door_direction.upper() == "E":
            self.door_position = (self.endingBlock[0], self.startingBlock[1] + 1, (self.startingBlock[2] + self.endingBlock[2]) / 2)
            axis = "x"
        elif self.door_direction.upper() == "W":
            self.door_position = (self.startingBlock[0], self.startingBlock[1] + 1, (self.startingBlock[2] + self.endingBlock[2]) / 2)
            axis = "x"

        ext_door_pos = select_placement_position(self, self.door_position, axis)
        if ext_door_pos != None:
            Door(self.mc, ext_door_pos)

class Wall(Cuboid): 
    """A wall object.
    
    Args:
    
    """
    def __init__(self, mc, startingBlock, endingBlock, elementId, name):
        super().__init__(mc, startingBlock, endingBlock)
        self.name = name
        
        self.contents = [
            {
                'item': "soild_wall",
                'content': BaseStructure(mc, startingBlock, endingBlock, elementId)
            }
        ]
        
        self.add_window()

    def get_wall_midpoint(self):
        wall_start = self.startingBlock
        wall_end = self.endingBlock
        return ((wall_start[0] + wall_end[0]) // 2, wall_start[1] + 1, (wall_start[2] + wall_end[2]) // 2)

    def add_door(self, axis):
        start_position = self.get_wall_midpoint()
        # print("  Adding door:", start_position)
        position = select_placement_position(self, start_position, axis)
        if position == None:
            return

        self.contents.append(
            {
                'item': "door", 'content':Door(self.mc, position)
            }
        )

    def add_window(self):
        
        if self.name == "int_wall":
            return
        # print("  Adding window:", self.get_wall_midpoint())
        self.contents.append(
            {
                'item': "window", 'content':Window(self.mc, self.get_wall_midpoint())
            }
        )
    
class stairs(Cuboid):
    """A set of stairs object.

        Args:
            mc (_type_): _description_
            startingBlock (tuple): _description_
            endingBlock (tuple): _description_
            direction (char): Direction of stair
        """  
    def __init__(self, mc, startingBlock, endingBlock, direction):
        super().__init__(mc, startingBlock, endingBlock)
        self.startingBlock = startingBlock  # (x, y, z)
        self.x_pos = startingBlock[0]
        self.y_pos = startingBlock[1]
        self.z_pos = startingBlock[2]
        self.direction = direction
        
        self.contents = [
            {
                'item': "stair",
                'content': self.generate_stair(4, self.startingBlock)
            }
        ]

    def generate_stair(self, height, start_coord):
        if height == 0:
            return

        # cut floor above
        if height > 0:
            self.mc.setBlock(
                start_coord[0], self.y_pos + 4, start_coord[2], block.AIR)
        # set stair block
        self.mc.setBlock(
            start_coord[0], start_coord[1] + 1, start_coord[2], block.WOOD_PLANKS)

        if self.direction.upper() == "N":
            next_coord = start_coord[0], start_coord[1] + 1, start_coord[2] - 1
            self.generate_stair(height - 1, next_coord)

        elif self.direction.upper() == "S":
            next_coord = start_coord[0], start_coord[1] + 1, start_coord[2] + 1
            self.generate_stair(height - 1, next_coord)
            
        elif self.direction.upper() == "E":
            next_coord = start_coord[0] + 1, start_coord[1] + 1, start_coord[2]
            self.generate_stair(height - 1, next_coord)
            
        elif self.direction.upper() == "W":
            next_coord = start_coord[0] - 1, start_coord[1] + 1, start_coord[2]
            self.generate_stair(height - 1, next_coord)

class Door(Cuboid):
    """A door object two blocks high.
    
    Args:
        mc (_type_): _description_
        startingBlock (tuple): location of bottom panel
        endingBlock (tuple): location of top panel
    
    """
    def __init__(self, mc, startingBlock, endingBlock = None):    
        super().__init__(mc, startingBlock, endingBlock)
        self.endingBlock = (startingBlock[0], startingBlock[1] + 1, startingBlock[2])
        self.top_panel = block.DOOR_WOOD.withData(8)
        self.bottom_panel = block.DOOR_WOOD.withData(0) 
        self.contents = [
            {
                'item': "top_panel",
                'content': self.generate_door(self.endingBlock, self.top_panel)
            },
            {
                'item': "bottom_panel",
                'content': self.generate_door(self.startingBlock, self.bottom_panel)
            }
        ]
    
    def generate_door(self, postion, panel):
        """generates a door block
        Args:
            postion (x,y,z): postion for the door block to be placed
            panel (door panel): specifies top or bottom pannel of the door
        Returns:
            Block: return the current block that is placed
        """        
        current_block = self.mc.setBlock(postion[0], postion[1], postion[2], panel)
        return current_block

class Window(Cuboid):
    """A window object two blocks high.
    
    Args:
        mc (_type_): _description_
        startingBlock (tuple): location of bottom panel
        endingBlock (tuple): location of top panel
    
    """
    def __init__(self, mc, startingBlock, endingBlock = None):    
        super().__init__(mc, startingBlock, endingBlock)
        self.contents = [
            {
                'item': "window",
                'content': BaseStructure(mc, startingBlock, [startingBlock[0], startingBlock[1] + 1 , startingBlock[2]], 20)
            }
        ]

class Brick(Block):
    """Extends Block class to for stair direction on roof
    """    
    def __init__(self, mc, x, y, z, element, direction):
        super().__init__(mc, x, y, z, element)
        self.type = element
        self.dir = direction 

    def buildBlock(self):
        """Overriding for Brick class to not build on initialisation.
        """
        pass

class Roof(Cuboid):
    """Roof object
    Args:
        mc (_type_): _description_
        startingBlock (_type_): _description_
        endingBlock (_type_): _description_
    """    
    def __init__(self, mc, startingBlock, endingBlock): 
        super().__init__(mc, startingBlock, endingBlock)
        self.xSize = abs(startingBlock[0] - endingBlock[0]) + 1
        self.ySize = abs(startingBlock[1] - endingBlock[1]) + 1
        self.zSize = abs(startingBlock[2] - endingBlock[2]) + 1
        self.relative_points = []
        self.reverse = False
        self.bricks = {}
        self.is_timber = bool(random.choice([True, False]))
        self.gable = bool(random.choice([True, False]))
        self.generate_roof_blocks()
        self.contents = [
            {
                'item': "roof",
                'content': self.build_roof()
            }
        ]
    
    def generate_roof_blocks(self):
        """Generates either gable or sloped style roof.
        The build_roof function then cerates the actual blocks.
        """        
        rows = self.zSize
        cols = self.xSize
        height_val = 0
        height_step_max = 0

        if rows > cols:
            temp_rows = rows
            rows = cols
            cols = temp_rows
            self.reverse = True

        for i in range(rows):
            temp = []
            for j in range(cols):
                temp.append(str(i) + "," + str(j))
            self.relative_points.append(temp)

        if self.gable:
            print("visualise roof: Gable")
            row_mid = (rows // 2) - 1
            self.cap_roof_ends(self.startingBlock, self.endingBlock, row_mid)
            # gable style roof
            for first_num, row in enumerate(self.relative_points):
                for second_num, col in enumerate(row):
                    if first_num == row_mid + 1 and rows % 2 == 1:
                        direction = " X "
                        roof_block = block.WOOD_PLANKS if self.is_timber else block.COBBLESTONE
                    elif first_num <= row_mid:
                        direction = " ^ "
                        roof_block = block.STAIRS_WOOD.withData(2) if self.is_timber else block.STAIRS_COBBLESTONE.withData(2)
                    else:
                        direction = " v "
                        roof_block = block.STAIRS_WOOD.withData(3) if self.is_timber else block.STAIRS_COBBLESTONE.withData(3)
                    
                    print(direction, end= "")
                    self.bricks[self.relative_points[first_num][second_num]] = Brick(self.mc,
                        second_num, height_val, first_num, roof_block, direction)

                if first_num < row_mid:
                    height_val += 1
                elif first_num == row_mid: # and rows % 2 == 0
                    pass
                elif first_num == row_mid + 1 and rows % 2 == 1:
                    pass
                else:
                    height_val -= 1
                print()
        else:
            print("visualise roof: Sloped")
            if rows % 2 == 0:
                row_mid = (rows // 2) - 1
                west_count = rows // 2
            else:
                row_mid = rows // 2
                west_count = (rows // 2) + 1
            col_mid = cols // 2
            # west_count = rows // 2
            east_count = cols
            # sloped roof
            for first_num, row in enumerate(self.relative_points):
                for second_num, col in enumerate(row):
                    if second_num < west_count and first_num >= second_num:
                        direction = " < "
                        roof_block = block.STAIRS_WOOD.withData(0) if self.is_timber else block.STAIRS_COBBLESTONE.withData(0)

                    elif second_num - east_count >= -1 and first_num < second_num:
                        direction = " > "
                        roof_block = block.STAIRS_WOOD.withData(1) if self.is_timber else block.STAIRS_COBBLESTONE.withData(1)

                    elif first_num <= row_mid:
                        direction = " ^ "
                        roof_block = block.STAIRS_WOOD.withData(2) if self.is_timber else block.STAIRS_COBBLESTONE.withData(2)

                    else:
                        direction = " v "
                        roof_block = block.STAIRS_WOOD.withData(3) if self.is_timber else block.STAIRS_COBBLESTONE.withData(3)

                    print(direction, end= "")
                    if second_num + height_step_max >= cols:
                        height_val -= 1

                    # setout point nort-west corner
                    self.bricks[self.relative_points[first_num][second_num]] = Brick(self.mc,
                        second_num, height_val, first_num, roof_block, direction)

                    if height_val < height_step_max and second_num < col_mid:
                        height_val += 1
                print()
                if first_num == row_mid and rows % 2 == 1:
                    west_count -= 1
                elif first_num > row_mid:
                    west_count -= 1
                

                if first_num < row_mid:
                    east_count -= 1
                    height_step_max += 1

                elif first_num == row_mid and rows % 2 == 0:
                    pass
                else:
                    east_count += 1
                    height_step_max -= 1
    

    def build_roof(self):
        return_list = []
        if self.reverse:
            # print("reverse")
            # reverse output - transpose array to rotate roof direction
            rez = [[self.relative_points[j][i]
                    for j in range(len(self.relative_points))] for i in range(len(self.relative_points[0]))]

            for row in rez:
                for i in row:
                    
                    if self.bricks[i].type == block.WOOD_PLANKS or self.bricks[i].type == block.COBBLESTONE:
                        pass # skip WOOD_PLANKS or COBBLESTONE as it is not a stair block
                    else:
                        self.bricks[i].type.data = self.stair_dir(self.bricks[i].type.data)
                    
                    curr_block = self.mc.setBlock(self.startingBlock[0] + self.bricks[i].z, self.startingBlock[1] + self.bricks[i].y,
                                        self.startingBlock[2] + self.bricks[i].x, self.bricks[i].type)
                    return_list.append(curr_block)

        else:
            for first_num, row in enumerate(self.relative_points):
                for second_num, col in enumerate(row):
                    curr_block = self.mc.setBlock(self.startingBlock[0] + self.bricks[col].x, self.startingBlock[1] + self.bricks[col].y,
                                        self.startingBlock[2] + self.bricks[col].z, self.bricks[col].type)
                    return_list.append(curr_block)

        return return_list

    def stair_dir(self, val):
        """ change stair direction for reversing roof layout
        0 : Ascending East - facing west
        1 : Ascending West - facing east
        2 : Ascending South - facing north
        3 : Ascending North - facing south
        Args:
            val (int): current stair direction 0-3
        Returns:
            int: required int 0-3 for roof layout
        """        
        
        if type(val) == int:
            if val == 0:
                return 2
            if val == 1:
                return 3
            if val == 2:
                return 0
            if val == 3:
                return 1
        else:
            if val == " < ":
                return " ^ "
            if val == " > ":
                return " v "
            if val == " ^ ":
                return " < "
            if val == " v ":
                return " > "

    def cap_roof_ends(self, startingBlock, endingBlock, height):
        """fills in the gap at the ends of the gable roof.
        Args:
            startingBlock (tuple): _description_
            endingBlock (tuple): _description_
            height (int): height at midpoint of roof
        """        
        
        if height < 1:
            return
        
        if self.reverse:
            structure_list = ["backWall", "frontWall"]
            start = (startingBlock[0] + 1, startingBlock[1], startingBlock[2])
            end = (endingBlock[0] - 1, startingBlock[1], endingBlock[2])
            Enclosure(self.mc, start, end, 5, structure_list)
            start = (startingBlock[0] + 1, startingBlock[1] + 1, startingBlock[2])
            end = (endingBlock[0] - 1, startingBlock[1] + 1, endingBlock[2])
            
        else:
            structure_list = ["leftWall", "rightWall"]
            start = (startingBlock[0], startingBlock[1], startingBlock[2] + 1)
            end = (endingBlock[0], startingBlock[1], endingBlock[2] - 1)
            Enclosure(self.mc, start, end, 5, structure_list)
            start = (startingBlock[0], startingBlock[1] + 1, startingBlock[2] + 1)
            end = (endingBlock[0], startingBlock[1] + 1, endingBlock[2] - 1)
        
        self.cap_roof_ends(start, end, height -1)

# HELPER FUNCTIONS
def get_contents(object_name, item_name):
        for index, dict in enumerate(object_name.contents):
        # print(dict)
            for k,v in dict.items():
            # print("key:", k , "value:", v)
                if v == item_name:
                    # print("  ",item_name, object_name.contents[index]["content"].contents)
                    return object_name.contents[index]["content"]

def check_if_wall(self, postition, axis):
        """Check if block is not air.
        Args:
            postition (tuple): _description_
            axis (char): x or z orientaion
        Returns:
            boolean: True, False
        """  
        if axis == "x":
            block_to_check_neg = self.mc.getBlock(postition[0] - 1, postition[1] + 1, postition[2])
            block_to_check_pos = self.mc.getBlock(postition[0] + 1, postition[1] + 1, postition[2])
        elif axis == "z":
            block_to_check_neg = self.mc.getBlock(postition[0], postition[1] + 1, postition[2] - 1)
            block_to_check_pos = self.mc.getBlock(postition[0], postition[1] + 1, postition[2] + 1)

        print("\n    Checking for wall:", block_to_check_neg, block_to_check_pos)
        if block.AIR.id != block_to_check_neg or block.AIR.id != block_to_check_pos:
            print("Found wall in front of door:")
            return True
            
        return False

def select_placement_position(self, position, axis):
    """Check for internal wall either side before placing door.

    Args:
        position (_type_): _description_
        axis (_type_): _description_

    Returns:
        None if no good position to place door, or position to place.
    """    
    if axis == "x":
        if check_if_wall(self, position, axis):
            new_position = (position[0], position[1], position[2] + 1)
            if check_if_wall(self, new_position, axis):
                last_position = (position[0], position[1], position[2] - 1)
                if check_if_wall(self, last_position, axis):
                    print("Could not place door due to wall!:", position)
                    return None
                else:
                    position = last_position
            else:
                position = new_position
        else:
            position = position

    elif axis == "z":
        if check_if_wall(self, position, axis):
            new_position = (position[0] + 1, position[1], position[2])
            if check_if_wall(self, new_position, axis):
                last_position = (position[0] - 1, position[1], position[2])
                if check_if_wall(self, last_position, axis):
                    print("Could not place door due to wall!:", position)
                    return None
                else:
                    position = last_position
            else:
                position = new_position
        else:
            position = position
    
    return position
