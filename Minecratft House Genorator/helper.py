from mcpi import block
import statistics
import villageSettings as vs
from math import sqrt

#CLASSES
class Cuboid:
    """Superclass for all objects that occupy a three dimensional (cuboid) space.
    
    Args:
        startingBlock (tuple): First tuples representing x,y,z coordinates for the cuboid.
        endingBlock (tuple): Second tuple representing x,y,z coordinates for the cuboid.
    
    Attributes:
        startingBlock (tuple): First tuples representing x,y,z coordinates for the cuboid.
        endingBlock (tuple): Second tuple representing x,y,z coordinates for the cuboid.
        contents (dictionary): Dictionary containing other objects representing three dimensional space.
        
    """
    
    def __init__(self, mc, startingBlock, endingBlock, parentCuboidBlocksMatrix={}, rotateCuboid=0):
        self.startingBlock = startingBlock
        self.endingBlock = endingBlock
        self.parentCuboidBlocksMatrix = parentCuboidBlocksMatrix
        self.cuboidBlocksMatrix = {}
        self.cuboidSurfaceMatrix = {}
        self.mc = mc
        self.contents = []
                
    #SET
    def setCuboidBlocksMatrix(self):
        """Generates 3D matrix of all blocks within a cuboid.
        Ordered by Ym then x thenz.
        Each block represented by tuple (x, y, z, blockID)
        
        """
        # print("Starting get block matrix...")
        
        (x0, y0, z0) = self.startingBlock
        (x1, y1, z1) = self.endingBlock
        
        cuboidBlocks = {}
        
        if not self.parentCuboidBlocksMatrix:
            print(f"Calling MC API - getBlocks, pulling {abs(x0-x1) * abs(y0-y1) * abs(z0-z1)} blocks")
            blockIds = list(self.mc.getBlocks(x0, y0, z0, x1, y1, z1))
            for y in range(y1, y0-1, -1):
                y_square = {}
                for x in range(x1, x0-1, -1):
                    x_row = {}
                    for z in range(z1, z0-1, -1):
                        x_row[z] = Block(self.mc, x, y, z, blockIds.pop())
                    y_square[x] = x_row
                cuboidBlocks[y] = y_square
        else:
            # print("USING PARENT BLOCKS")
            #Loop through parent matrix and take just blocks within the child cuboid.
            for y in range(y1, y0-1, -1):
                y_square = {}
                for x in range(x1, x0-1, -1):
                    x_row = {}
                    for z in range(z1, z0-1, -1):
                        x_row[z] = self.parentCuboidBlocksMatrix[y][x][z]
                    y_square[x] = x_row
                cuboidBlocks[y] = y_square
                        
        # print("Finished get block matrix...")    
        
        self.cuboidBlocksMatrix = cuboidBlocks
    
    def setSurfaceBlocks(self):
        """Construct a 2d matrix ordered by X, Z containing coordinates of block on surface of the Cuboid.

        """
        if not self.cuboidBlocksMatrix:
            self.setCuboidBlocksMatrix()
                    
        cuboidMaxY = max(self.startingBlock[1], self.endingBlock[1])
        
        surfaceBlocks = {}
        
        cuboidMinX, cuboidMinY, cuboidMinZ, cuboidMaxX, cuboidMaxY, cuboidMaxZ = self.getCuboidMinMaxXYZ()
                
        for x in range(cuboidMinX, cuboidMaxX):
            x_row = {}
            for z in range(cuboidMinZ, cuboidMaxZ):
                y = cuboidMaxY
                while y > cuboidMinY and not isGroundBlock(self.cuboidBlocksMatrix[y][x][z].element):
                    y -=1
                surfaceBlock = self.cuboidBlocksMatrix[y][x][z]
                x_row[z] = surfaceBlock
            surfaceBlocks[x] = x_row
            
        self.cuboidSurfaceMatrix = surfaceBlocks
    
    def setZonePerimeterVisualisation(self, interval=5):
        """Sets beacons to define the zone's parllpd in content.
        
        Essentially builds cube/prllpd edges.

        """
        self.contents.append(
            {
                'item': 'Zone Perimeter',
                'content': Enclosure(self.mc, self.startingBlock, self.endingBlock, 138, ['ceiling', 'floor', 'backWall', 'frontWall', 'rightWall', 'leftWall'], interval)
            }
        )
    
    def setSurfaceBlock(self, x, z, newY, newId):
        """Update the surface block with new y value and id.

        Args:
            x (int): Integer of x CoOrdinate for which we are changing the surface block.
            z (int): Integer of z CoOrdinate for which we are changing the surface block.
            newY (int): Integer of new y CoOrdinate for the surface block that is being changed.
            newId (int): New ID integer for the new surface block.

        """
        if not self.cuboidSurfaceMatrix:
            self.setSurfaceBlocks()
        #Loop through surface blocks and replace
        self.cuboidSurfaceMatrix[x][z] = Block(self.mc, x, newY, z, newId, build=True)

    def setOrientation(self, orientationBlock):
        """Set the orientation of the cuboid.
        
        Set the orientation of the cuboid by orienting the front block closest to the orientationBlock.

        Args:
            orientationBlock (Block): The block to which the front block should be closest to.
            
        Return:
            (dictionary): Dictionary containing startingBlock and endingBlock coordinates as key value pairs.
        """
        cuboidRadius = self.getCuboidRadius()
        orientationList = [
            {
                'startingBlock': [self.startingBlock[0], self.startingBlock[1], self.startingBlock[2]],
                'endingBlock': [self.endingBlock[0], self.endingBlock[1], self.endingBlock[2]],
                'frontBlock': [self.endingBlock[0], self.endingBlock[1] - cuboidRadius, self.endingBlock[2] - cuboidRadius]
            },
            #sWAP Z AXIS
            {
                'startingBlock': [self.startingBlock[0], self.startingBlock[1], self.endingBlock[2]],
                'endingBlock': [self.endingBlock[0], self.endingBlock[1], self.startingBlock[2]],
                'frontBlock': [self.endingBlock[0], self.endingBlock[1] - cuboidRadius, self.startingBlock[2] - cuboidRadius]
            },
            #sWAP X AND Z AXIS
            {
                'startingBlock': [self.endingBlock[0], self.startingBlock[1], self.endingBlock[2]],
                'endingBlock': [self.startingBlock[0], self.endingBlock[1], self.startingBlock[2]],
                'frontBlock': [self.startingBlock[0], self.endingBlock[1] - cuboidRadius, self.startingBlock[2] - cuboidRadius]
            },
            #SWAP X AXIS
            {
                'startingBlock': [self.endingBlock[0], self.startingBlock[1], self.startingBlock[2]],
                'endingBlock': [self.startingBlock[0], self.endingBlock[1], self.endingBlock[2]],
                'frontBlock': [self.startingBlock[0], self.endingBlock[1] - cuboidRadius, self.endingBlock[2] - cuboidRadius]
            },
        ]
        
        correctOrientation = {
            'startingBlock': [self.startingBlock[0], self.startingBlock[1], self.startingBlock[2]],
            'endingBlock': [self.endingBlock[0], self.endingBlock[1], self.endingBlock[2]],
            'frontBlock': [self.endingBlock[0], self.endingBlock[1] - cuboidRadius, self.endingBlock[2] - cuboidRadius]
        }
        
        startingDistance = get2DDistance(correctOrientation['frontBlock'], orientationBlock)
        
        for item in orientationList:
            iteratingDistance = get2DDistance(item['frontBlock'], orientationBlock)
            if iteratingDistance < startingDistance:
                startingDistance = iteratingDistance
                correctOrientation = item
        
        self.startingBlock = correctOrientation['startingBlock']
        self.endingBlock = correctOrientation['endingBlock']
        
        return correctOrientation     
        
              
    #GET
    def getBorder(self, border):
        """Get a border of a parallelepiped. 
        
        floor, roof, backWall, leftWall, rightWall, frontWall. On X,Y,Z plane.
        
        Args:
            border (string): Name representing the border that is wanted.
        
        Return:
            (list) list containing coordinates of start and endblock of the dimensional border.
        """
        if border == 'floor':
            NewEndingBlock = (self.endingBlock[0], self.startingBlock[1], self.endingBlock[2])
            return [self.startingBlock, NewEndingBlock]
        elif border == 'backWall':
            NewEndingBlock = (self.endingBlock[0], self.endingBlock[1], self.startingBlock[2])
            return [self.startingBlock, NewEndingBlock]
        elif border == 'rightWall':
            NewEndingBlock = (self.startingBlock[0], self.endingBlock[1], self.endingBlock[2])
            return [self.startingBlock, NewEndingBlock]
        elif border == 'ceiling':
            newStartingBlock = (self.startingBlock[0], self.endingBlock[1], self.startingBlock[2])
            return [newStartingBlock, self.endingBlock]
        elif border == 'leftWall':
            newStartingBlock = (self.endingBlock[0], self.startingBlock[1], self.startingBlock[2])
            return [newStartingBlock, self.endingBlock]
        elif border == 'frontWall':
            newStartingBlock = (self.startingBlock[0], self.startingBlock[1], self.endingBlock[2])
            return [newStartingBlock, self.endingBlock]

    def getBlockFromCuboidBlocksMatrix(self, x, y, z):
        """Retrieve blocks from cuboidBlocks object by x, y, z.

        Args:
            x (int): X CoOrdinate Integer.
            y (int): Y CoOrdinate Integer.
            z (int): Z CoOrdinate Integer. 

        Returns:
            block: Block at specified coordinates.
        """
        if not self.cuboidBlocksMatrix:
            self.setCuboidBlocksMatrix()
        return self.cuboidBlocksMatrix[y, x, z]

    def getBlockFromCuboidSurfaceBlocksMatrix(self, x, z):
        """Get a block from the Cuboid's surface blocks matrix.

        Args:
            x (int): X CoOrdinate Integer.
            z (int): Z CoOrdinate Integer. 
            
        Returns:
            block: Surface Block at specified coordinates.
        """
        if not self.cuboidSurfaceMatrix:
            self.setSurfaceBlocks()
        return self.cuboidSurfaceMatrix[x][z]
    
    def getCuboidMinMaxXYZ(self):
        """Return list of min and max of a cuboid.
                
        Return:
            Return minx, miny, minz, maxx, maxy, maxz
        """ 
        return getMinMax(self.startingBlock, self.endingBlock)

    def get2DCentreBlock(self):
        """Get the block in the middle of the x and z axis.
        
        
        
        """
        pass

    def getCuboidSurfaceAltitudeStd(self):
        """Calculate the surface standard deviation of a cuboid.
        
        #Get all y values of surface blocks.
        #Calculate Std of these values.
                
        Return:
            (float):    Standard Deviation of the cuboid surface block altitude.        
        """
        self.setSurfaceBlocks()
        cuboidSurfaceBlocks = list(getNestedDictValues(self.cuboidSurfaceMatrix))
        cuboidSurfaceAltitudeList = [x.y for x in cuboidSurfaceBlocks]
        
        surfaceAltitudeStd = statistics.stdev(cuboidSurfaceAltitudeList)
        
        self.surfaceAltitudeStd = surfaceAltitudeStd
        
        return surfaceAltitudeStd
        
    def getCuboidCenterBlock(self):
        """Get the block at the center of the cuboid on surface.
        
        Return:
            (Block): The block within the cuboid matrix at the centrepoint   
        """
        
        cuboidMinX, cuboidMinY, cuboidMinZ, cuboidMaxX, cuboidMaxY, cuboidMaxZ = self.getCuboidMinMaxXYZ()
        
        xDelta = cuboidMaxX - cuboidMinX
        zDelta = cuboidMaxZ - cuboidMinZ
        
        return self.getBlockFromCuboidSurfaceBlocksMatrix(cuboidMinX + (xDelta / 2), cuboidMinZ + (zDelta / 2) )
        
    def getCuboidRadius(self):
        """Get the x/z radius of the cuboid.

        """
        
        cuboidMinX, cuboidMinY, cuboidMinZ, cuboidMaxX, cuboidMaxY, cuboidMaxZ = self.getCuboidMinMaxXYZ()
        
        return (cuboidMaxX - cuboidMinX) / 2
    
            
    #OTHER METHODS
    def clearCuboid(self):
        """Clear the space attributed to the cuboid with AIR.

        """
        self.mc.setBlocks(self.startingBlock[0], self.startingBlock[1], self.startingBlock[2], self.endingBlock[0], self.endingBlock[1], self.endingBlock[2], 0)

    def setFrontBlock(self):
        """Set the block at the front of the cuboid.
        
        #The front block is the block with halfway between starting and ending z and y blocks and equal to ending block x.
        
        Returns:
            (list): List of x, y, z coordinate integers.
        
        """
        
        cuboidRadius = self.getCuboidRadius()
                
        self.frontBlockCoOrdinates = [self.endingBlock[0], self.endingBlock[1] - cuboidRadius, self.endingblock[2] - cuboidRadius]
        
        return self.frontBlockCoOrdinates
        

    def containsWaterOrTownCenter(self, townCenterCoords):
        """Returns yes if surface blocks contain water.
        
        Return:
            (bool): true if water false otherwise.
        """
        if not self.cuboidSurfaceMatrix:
            self.setSurfaceBlocks()
        
        cuboidSurfaceBlocks = list(getNestedDictValues(self.cuboidSurfaceMatrix))

        # need to grab block direcly ABOVE surface block to check if it is water
        blocksAboveSurfaceBlocks = []
        for surfaceBlock in cuboidSurfaceBlocks:
            x = surfaceBlock.x
            y = surfaceBlock.y
            z = surfaceBlock.z

            if abs(x - townCenterCoords[0]) <= vs.TOWN_CENTER_RADIUS and abs(z - townCenterCoords[2]) <= vs.TOWN_CENTER_RADIUS:
                print(f"Plot at {x} ~ {z} contains the townCenter at {townCenterCoords}, ignoring plot")
                return True

            try:
                blockAbove = self.cuboidBlocksMatrix[y+1][x][z]
                blocksAboveSurfaceBlocks.append(blockAbove)
            except:
                print("Checking block which was above the zone ceiling")
                

        cuboidElementIdList = [x.element for x in blocksAboveSurfaceBlocks]
        
        waterBlockIds = [
            block.WATER.id,
            block.WATER_FLOWING.id,
            block.WATER_STATIONARY.id
        ]
        
        return any(item in waterBlockIds for item in cuboidElementIdList)

class Block:
    """The base block object.
    
    #Must observe law of gravity. If floating on air then build grass patch below.

    Args:
        mc (_type_): _description_
        x (int): _description_
        y (int): _description_
        z (int): _description_
        element (int): block id number
        trfrm (int, optional): _description_. Defaults to 0.
    """
    
    def __init__(self, mc, x, y, z, element, trfrm=0, build=False):
        self.x = x
        if y > 256 or y < 0:
            print("Y BLOCK HIGHER THAN THE CEILING")
        self.y = y
        self.z = z
        self.mc = mc
        self.element = element
        self.trfrm = trfrm
        if build:
            self.buildBlock()
        # self.terraform() TODO turn on for ground level only.
         
    # def terraform(self):
    #     """Terraforms if necessary.
        
    #     #Check to see law of gravity is okay.
    #     #Check to see if slope is okay.
        
        
    #     """
    #     if self.mc.getBlock(self.x, self.y-1, self.z) == 0:
    #         Block(self.mc, self.x, self.y-1, self.z, 2, self.trfrm + 1, true)
            
    #     if self.trfrm != 0:
    #         BaseStructure(self.mc, [self.x - self.trfrm, self.y, self.z - self.trfrm], [self.x + self.trfrm, self.y, self.z + self.trfrm], 2)
                    
    def buildBlock(self):
        """Builds the actual block.
        
        #If a terraform block then build 'platform' else just single block
        
        """
        elementID = self.element if self.trfrm == 0 else 2
        self.setBlockNat(self.x, self.y, self.z, elementID)
        
    def setBlockNat(self, x, y, z, elementID):
        """Native setblock function.
        
        #Checks if there is anything before placing.

        Args:
            x (_type_): _description_
            y (_type_): _description_
            z (_type_): _description_
            elementID (_type_): _description_
        """
        self.mc.setBlock(x, y, z, elementID)

class Enclosure(Cuboid):
    """An enclosure. List containing strings of either: floor, backWall, rightWall, ceiling, leftWall, frontWall. All optional.
    
     Args:
        mc (object): Minecraft object.
        startingBlock (tuple): First tuples representing x,y,z coordinates for the cuboid.
        endingBlock (tuple): Second tuple representing x,y,z coordinates for the cuboid.
        elementId (int): Id for which element makes the structure.
        structureList (list): list of components to be included. Floor, roof etc.
        
    
    """  
    
    def __init__(self, mc, startingBlock, endingBlock, elementId, structureList, interval=1):
        super().__init__(mc, startingBlock, endingBlock)
        self.elementId = elementId
        self.interval = interval
        self.contents = [ { 'item': x, 'content': BaseStructure(self.mc, self.getBorder(x)[0], self.getBorder(x)[1], self.elementId, interval)} for x in structureList]

class BaseStructure(Cuboid):
    """A two dimensional set of blocks. Wall, roof, path, anything.
    
     Args:
        element (int): Integer ID for the element type.
    """
    
    def __init__(self, mc, startingBlock, endingBlock, element, interval=1):
        super().__init__(mc, startingBlock, endingBlock)
        self.element = element
        self.startingBlock = startingBlock
        self.endingBlock = endingBlock
        self.interval = interval
        self.coOrdinateMatrix = self.generateCuboidCoOrdinateMatrix()
        self.contents = [ { 'item': 'block', 'content': Block(mc, i[0], i[1], i[2], self.element, build=True) } for i in self.coOrdinateMatrix]
        
    def generateCuboidCoOrdinateMatrix(self):
        returnList = []
        xOne = int(self.startingBlock[0])
        xTwo = int(self.endingBlock[0] + 1)
        yOne = int(self.startingBlock[1])
        yTwo = int(self.endingBlock[1] + 1)
        zOne = int(self.startingBlock[2])
        zTwo = int(self.endingBlock[2] + 1)
        xIncrement = (-1 * self.interval) if (xOne > xTwo) else (1 * self.interval)
        yIncrement = (-1 * self.interval) if (yOne > yTwo) else (1 * self.interval)
        zIncrement = (-1 * self.interval) if (zOne > zTwo) else (1 * self.interval)
        for x in range(xOne, xTwo, xIncrement):
            for y in range(yOne, yTwo):
                for z in range(zOne, zTwo, zIncrement):
                    returnList.append([x, y, z])
                    
        return returnList


#HELPER FUNCTIONS
def isGroundBlock(blockId):
    """If block is a solid ground block then returns true else false.

    Args:
        blockId (int): THe integer ID of the block.
        
    Returns:
        (bool): True if solid block else false.
    """
    groundBlockIds = [
        block.STONE.id,
        block.GRASS.id,
        block.DIRT.id,
        block.COBBLESTONE.id,
        block.SAND.id,
        block.GRAVEL.id,
        block.SANDSTONE.id,
        block.ICE.id,
        block.SNOW_BLOCK.id,
        block.CLAY.id,
        block.COAL_ORE.id,
        block.IRON_ORE.id,
    ]
    
    if blockId == 0:
        return False
    elif blockId in groundBlockIds:
        return True
    else:
        return False

def isWaterBlock(blockId):
    """Id block is a water block of any type then returns true else false.

    Args:
        blockID (int): The block id.
        
    Return:
        (bool): True if water id else false.
    """
    waterBlockIds = [
        block.WATER.id,
        block.WATER_FLOWING.id,
        block.WATER_STATIONARY.id
    ]
    
    if blockId == 0:
        return False
    elif blockId in waterBlockIds:
        return True
    else:
        return False

def getMinMax(startingBlock, endingBlock):
    """Return list of min and max of a cuboid.
    
    Args:
        startingBlock (tuple): x,y,z tuple representing coordinates of first block.
        endingBlock (tyuple): x,y,z tuple representing coordinates of ending block.
        
    Return:
        Return minx, miny, minz, maxx, maxy, maxz
    """ 
    cuboidMinX = min(startingBlock[0], endingBlock[0])
    cuboidMinY = min(startingBlock[1], endingBlock[1])
    cuboidMinZ = min(startingBlock[2], endingBlock[2])
    
    cuboidMaxX = max(startingBlock[0], endingBlock[0])
    cuboidMaxY = max(startingBlock[1], endingBlock[1])
    cuboidMaxZ = max(startingBlock[2], endingBlock[2])
    
    return cuboidMinX, cuboidMinY, cuboidMinZ, cuboidMaxX, cuboidMaxY, cuboidMaxZ

def get2DDistance(startingBlockCoordinates, endingBlockCoOrdinates):
    """Get the xz distance between two blocks.

    Args:
        startingBlock (list): _description_
        endingBlock (list): _description_
    """
    
    x1, y1, z1 = startingBlockCoordinates
    x2, y2, z2 = endingBlockCoOrdinates
    
    distance = sqrt(abs(x2 - x1) ** 2 + abs(z2 - z1) ** 2)
    
    return distance

def getNestedDictValues(d):
    for v in d.values():
        if isinstance(v, dict):
            yield from getNestedDictValues(v)
        else:
            yield v