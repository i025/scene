from sceneact import *

scene = Scene('Room')
room = Asset('Room shell')

# Warm, narrow floorboards establish the direction and color of the room.
floor_colors = [(0.48, 0.32, 0.19), (0.53, 0.36, 0.22), (0.57, 0.39, 0.24), (0.50, 0.33, 0.20), (0.55, 0.37, 0.23)]
board_width = 0.24
for i in range(42):
    x = -5.04 + i * board_width
    room.include('Floorboard_%02d' % i, box(size=(board_width - 0.004, 10.0, 0.09), center=(x, 0, -0.045), color=floor_colors[i % len(floor_colors)]))

wall_color = (0.79, 0.83, 0.79)
trim_color = (0.25, 0.17, 0.11)
room.include('Back wall', box(size=(10.2, 0.12, 3.8), center=(0, 3.7, 1.9), color=wall_color))
room.include('Right wall', box(size=(0.12, 10.0, 3.8), center=(5.05, -1.3, 1.9), color=wall_color))
room.include('Back baseboard', box(size=(10.0, 0.08, 0.22), center=(0, 3.60, 0.11), color=trim_color))
room.include('Right baseboard', box(size=(0.08, 7.2, 0.22), center=(4.95, 0.05, 0.11), color=trim_color))
scene.include('Room', room)
realize(scene)

set_view((4.5, -7.5, 3.65), (0.0, 0.45, 1.05), lens=36)
area_emitter((0.0, -2.8, 5.5), power=1000, size=5.0, target=(0, 0.7, 0.4))
area_emitter((-3.5, 0.0, 3.8), power=500, size=4.0, target=(0, 1.5, 0.8))