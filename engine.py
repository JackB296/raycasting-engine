import pygame as pg
import sys
import math

pg.init()

class Player:
    def __init__(self, x, y, radius, color, direction):
        self.pos = pg.math.Vector2(x, y)
        self.direction = direction
        self.radius = radius
        self.color = color
        self.speed = 5

    def movement(self, keys, map, tile_size):
        #MOVE AND TURN PLAYER
            movement = False
            new_pos = self.pos.copy()

            if keys[pg.K_w]:
                new_pos += self.speed * pg.math.Vector2(math.cos(self.direction), math.sin(self.direction))
                movement = True
            if keys[pg.K_a]:
                self.direction -= math.pi / 36
            if keys[pg.K_s]:
                new_pos -= self.speed * pg.math.Vector2(math.cos(self.direction), math.sin(self.direction))
                movement = True
            if keys[pg.K_d]:
                self.direction += math.pi / 36

            if movement:
                # CHECK FOR COLLISIONS WITH WALLS
                collision = False
                for y in range(len(map)):
                    for x in range(len(map[y])):
                        wall_rect = pg.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                        if map[y][x] == "#" and wall_rect.collidepoint(new_pos):
                            collision = True
                            break
                if not collision:
                    self.pos = new_pos


    def draw(self, cur_surface):
        pg.draw.circle(cur_surface, self.color, self.pos, self.radius)

class Map:
    def __init__(self, map_data, tile_size, colors, player):
        self.map_data = map_data
        #MULTUPLY BY 2 SO OUR SCREEN IS THE width OF 2 MAPS
        self.width = len(self.map_data[0]) * tile_size * 2
        self.height = len(self.map_data) * tile_size
        self.surface = pg.Surface((self.width, self.height))
        self.tile_size = tile_size
        self.colors = colors
        self.player = player
        #HOW MANY RAYS TO RENDER
        self.ray_count = 150
        self.scale = (self.width / 2) / self.ray_count

    def render_map(self):
        """
        render a 2D map to visualize the player location and rays
        """
        for y, row in enumerate(self.map_data):
            for x, block in enumerate(row):
                color = self.colors[block]
                #MULTIPLY THE THE TILE SIZE BY THE LIST INDEX TO GET THE CORRECT POSITION
                rect = pg.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                pg.draw.rect(self.surface, color, rect)
                
    def raycast(self):
        """
        raycasting algorithm

        FOR FOV REFERENCE
        π / 6	30°
        π / 4	45°
        π / 3	60°
        π / 2	90°
        π	180°
        """
        
        fov = math.pi / 3
        
        #STARTING RAY ANGLE
        ray_angle = self.player.direction - (fov / 2)

        step_size = fov / self.ray_count

        #SET COLOR OF RAYS
        color = (255, 0, 0)

        for i in range(self.ray_count):
            
            #GET RAYS DIR AND POS
            dir_vector = pg.math.Vector2(math.cos(ray_angle), math.sin(ray_angle))
            start_pos = pg.math.Vector2(self.player.pos.x, self.player.pos.y)

            wall_hit = False
            wall_dist = None

            while not wall_hit:
                
                #GET MAP POSITION OF RAY
                map_x, map_y = int(start_pos.x // self.tile_size), int(start_pos.y // self.tile_size)

                # CHECK IF RAY HITS A WALL
                if self.map_data[map_y][map_x] == "#":
                    wall_hit = True

                    #GET DISTANCE FROM PLAYER TO RAY USING PYTHAGREOM THEOREM
                    wall_dist = (start_pos - self.player.pos).length()

                    #COMPUTE WALL HEIGHT BASED OFF DISTANCE FROM PLAYER
                    wall_height = 21000 / (wall_dist + 0.0001)

                    #COMPUTE WALL RECT POSITION BASED ON DISTANCE FROM PLAYER
                    wall_y = int(self.height / 2 - wall_height / 2)
                    wall_height = int(min(wall_height, self.height - wall_y))
                    wall_x = int(self.height + i * self.scale + 32)
                    wall_width = self.scale * 2

                    wall_rect = pg.Rect(wall_x, wall_y, wall_width, wall_height)

                    #CHANGE WALL COLOR BASED ON DISTANCE FROM PLAYER
                    wall_color =  255 / (1 + wall_dist * wall_dist * 0.0001)

                    pg.draw.rect(self.surface, (wall_color,wall_color,wall_color), wall_rect)

                start_pos += dir_vector * 2

            line_end = self.player.pos + dir_vector * wall_dist
            pg.draw.line(self.surface, color, self.player.pos, line_end)
            # MOVE TO THE NEXT RAY
            ray_angle += step_size

    def blit(self, screen):
        screen.blit(self.surface, (0, 0))


class Game:
    def __init__(self, screen, map, player, FPS, clock):
        self.screen = screen
        self.map = map
        self.player = player
        self.FPS = FPS
        self.clock = clock

    def run(self):
    
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            keys = pg.key.get_pressed()

            self.map.surface.fill((0,0,0))

            #RESET 3D
            pg.draw.rect(self.map.surface, (100, 100, 100), (int(self.map.width/2), 0, 
                                                             int(self.map.width/2), int(self.map.height/2)))
            pg.draw.rect(self.map.surface, (200, 200, 200), (int(self.map.width/2), int(self.map.height/2), 
                                                             int(self.map.width/2), int(self.map.height/2)))

            self.map.render_map()

            #HANDLE OUR MOVEMENT AND PASS IN OUR KEYS, MAP DATA, AND TILE SIZE
            self.player.movement(keys, self.map.map_data, self.map.tile_size)

            #RESET SCREEN
            self.screen.fill((0,0,0))

            self.player.draw(self.map.surface)
            self.map.raycast()
            self.map.blit(self.screen)

            #SHOW FPS
            fps = str(int(self.clock.get_fps()))
            font = pg.font.SysFont('Monospace Regular', 30)
            fps_surface = font.render(fps, False, (255, 255, 255))
            self.screen.blit(fps_surface, (0, 0))

            #UPDATE DISPLAY
            pg.display.flip()

            #TICK BY THE FPS
            self.clock.tick(self.FPS)

def main():
    clock = pg.time.Clock()

    FPS = 30

    map_data = [
    "#################",
    "#..........#....#",
    "#.......#.......#",
    "#....#..........#",
    "#.........#.....#",
    "#......####.....#",
    "#....#....#.....#",
    "#....#....#.....#",
    "#....#....#.....#",
    "#....#....#.....#",
    "#....######.....#",
    "#..#....####....#",
    "#.......####....#",
    "#..#........#...#",
    "#........#......#",
    "#################"
    ]

    #COLORS FOR OUR MAP
    colors = {
        "#": (100, 100, 100),
        ".": (255, 255, 255),
    }

    tile_size = 32

    player = Player(100, 100, tile_size // 2, (255, 0, 0), math.pi / 2)

    map = Map(map_data, tile_size, colors, player)

    screen = pg.display.set_mode((map.width, map.height))

    game = Game(screen, map, player, FPS, clock)

    game.run()

main()
