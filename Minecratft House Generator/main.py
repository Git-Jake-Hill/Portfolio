from Houses import House
from mcpi.minecraft import Minecraft
from mcpi import block
import random
from time import sleep

mc = Minecraft.create()
x, y, z = mc.player.getTilePos()

# clear a flat area
dist = 200
mc.setBlocks(x - dist, y, z - dist, x + dist, y + 30, z + dist, block.AIR.id)
mc.setBlocks(x - dist, y - 1, z -dist, x + dist, y - 1, z + dist, block.GRASS.id)

sleep(15)

# specific size house
house_width = 50
house_length = 50

start_house = (x, y - 1, z)
end_house = (x + house_width, y, z + house_length)

# new_house = House(mc, start_house, end_house)


offset_builings = -35
for i in range(5):
    
    # random size house
    random_width = random.randint(10, 25)
    random_depth = random.randint(10, 25)

    start_house = (x + (i*offset_builings), y - 1, z)
    end_house = (x + random_width + (i*offset_builings), y, z + random_depth)

    new_house = House(mc, start_house, end_house, "W")