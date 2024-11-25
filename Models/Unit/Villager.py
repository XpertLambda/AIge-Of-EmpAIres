from Models.Unit.Unit import Unit  
from Settings.setup import BUILDING_TIME_REDUCTION, RESOURCE_COLLECTION_RATE, RESOURCE_CAPACITY


from Models import Unit  # Import Unit for inheritance
from Models import Building  # Import Building class
from Models import GameMap  # Import GameMap class


class Villager(Unit):
    def __init__(self, acronym="V"):
        super().__init__(acronym)  # Initialize parent class (Unit)
        self.resources = 0  # Amount of resources the villager is currently carrying
        self.carry_capacity = 20  # Maximum resources a villager can carry
        self.resource_rate = 25 / 60  # Rate of resource collection (units per second)
        self.busy = False

    def isAvailable(self):
        """Check if the villager is available to perform tasks."""
        if self.busy:
            print(f"{self.acronym} is currently busy.")
            return False
        return True

    def collectResource(self, resource_tile, duration):
        """
        Collect resources from a resource tile for the given duration.
        :param resource_tile: Tile object representing the resource.
        :param duration: Time (in seconds) to spend collecting.
        """
        # Ensure this is a valid resource tile
        if not isinstance(self, Villager):
            raise TypeError("Only Villager instances can collect resources.")

        valid_resources = {'G': 'gold', 'W': 'wood', 'F': 'food'}

        # Check if the tile is a valid resource type
        if self.isAvailable() and resource_tile.terrain_type in valid_resources.keys():
            self.busy = True
            print(f"{self.acronym} is moving to the resource tile at ({resource_tile.x}, {resource_tile.y}).")
            self.seDeplacer(resource_tile.x, resource_tile.y)  # Move to the resource location

            # Calculate total resources that can be collected
            total_collectable = min(self.resource_rate * duration, self.carry_capacity - self.resources)
            self.resources += total_collectable

            resource_type = valid_resources[resource_tile.terrain_type]
            print(f"{self.acronym}: Collected {total_collectable:.2f} units of {resource_type}. Total now: {self.resources:.2f}.")

            self.busy = False
            return
        print(f"{self.acronym} cannot collect resources from this tile. Terrain type: {resource_tile.terrain_type}.")

    def stockerRessources(self, building):
        """
        Store the collected resources in a resource drop point (e.g., town hall).
        :param building: Building object where resources will be stored.
        """
        if not isinstance(self, Villager):
            raise TypeError("Only Villager instances can store resources.")

        if self.isAvailable() and building.resourceDropPoint:
            print(f"{self.acronym} is moving to the drop-off building at ({building.x}, {building.y}).")
            self.seDeplacer(building.x, building.y)  # Move to the building

            self.busy = True
            print(f"{self.acronym} is storing {self.resources} resources in {building.acronym}.")
            building.addResources(self.resources)
            self.resources = 0  # Empty the villager's carrying capacity
            self.busy = False
            return
        print(f"{self.acronym} cannot store resources at this building.")

    def buildBatiment(self, building, x, y, game_map, num_villagers):
        """
        Construct a building at the specified location.
        :param building: Building object to be constructed.
        :param x: X-coordinate of the construction site.
        :param y: Y-coordinate of the construction site.
        :param game_map: GameMap object for placement.
        :param num_villagers: Number of villagers involved in construction.
        """
        if not isinstance(self, Villager):
            raise TypeError("Only Villager instances can build a building.")

        if self.isAvailable():
            print(f"{self.acronym}: Moving to location ({x}, {y}) to build {building.acronym}.")
            self.seDeplacer(x, y)  # Move to the build location

            # Verify the spot is empty
            if not game_map.can_place_building(game_map.grid, x, y, building):
                print(f"{self.acronym}: Location ({x}, {y}) is not empty. Cannot construct {building.acronym}.")
                return

            self.busy = True
            time_needed = self.buildTime(building, num_villagers)

            if self.resources >= building.woodCost:
                self.resources -= building.woodCost
                print(f"{self.acronym}: Building {building.acronym} at ({x}, {y}). This will take {time_needed:.2f} seconds.")
                game_map.place_building(x, y, building)  # Place the building on the map
                print(f"{self.acronym}: {building.acronym} constructed successfully. Remaining resources: {self.resources}.")
                self.busy = False
                return
            print(f"{self.acronym}: Not enough resources to start construction.")
            self.busy = False

    def buildTime(self, building, num_villagers):
        """
        Calculate the construction time for a building.
        :param building: Building object.
        :param num_villagers: Number of villagers involved in construction.
        :return: Time needed to construct the building.
        """
        if not isinstance(self, Villager):
            raise TypeError("Only Villager instances can calculate build time.")

        if num_villagers <= 0:
            return building.buildTime
        return max(10, (3 * building.buildTime) / (num_villagers + 2))
