## Black Jack Game - GUI Version
# Constants

import os
from pathlib import Path
from pygame.math import Vector2


display = 0 # select display (for second screen = 1)
window_size = (1200,600)

FPS = 30

script_path  = Path(os.path.dirname(os.path.abspath(__file__)))
images_path  = Path(script_path, "images")

textFont = 'Corbel'

# Colors
black                 = (0,0,0)
window_color          = (40,185,84)
buttonArea_color      = (233,244,122)
color_active          = (170,170,170)
color_inactive        = (120,120,120)
color_disabled        = (85,85,85)
color_resultsBox      = (255,255,204)
color_resultsBoxFont  = (204,204,0)