from pygame.font import SysFont
from pygame import init
import pygame

init()
# ==================================

# Window Settings
XWIN, YWIN = 1000, 800  # Resolution
HALF_XWIN, HALF_YWIN = XWIN / 2, YWIN / 2  # Center
DISPLAY = (XWIN, YWIN)
FLAGS = 0  # Fullscreen, resizeable...
FPS = 60  # Render frame rate

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BROWN = (165, 42, 42)
RED = (255, 0, 0)
ANDROID_GREEN = (164, 198, 57)
FOREST_GREEN = (87, 189, 68)

# Player
PLAYER_SIZE = (45, 45)
PLAYER_COLOR = (255, 255, 255)  # Transparent
PLAYER_MAX_SPEED = 17
PLAYER_JUMPFORCE = 17
PLAYER_BONUS_JUMPFORCE = 50
GRAVITY = .5

# Platforms
PLATFORM_COLOR = FOREST_GREEN
PLATFORM_COLOR_LIGHT = BROWN
PLATFORM_SIZE = (150, 10)
PLATFORM_DISTANCE_GAP = (50, 150)
MAX_PLATFORM_NUMBER = 15  # Chance is 1/n
BONUS_SPAWN_CHANCE = 5  # Chance is 1/n
BONUS_SIZE = (40, 20)
BREAKABLE_PLATFORM_CHANCE = 12

# Fonts
LARGE_FONT = SysFont("", 128)
SMALL_FONT = SysFont("arial", 24)

# Images
backround = pygame.image.load('Images/backround_2.jpg')
doodle = pygame.image.load('Images/doodle.png')
doodle = pygame.transform.scale(doodle, PLAYER_SIZE)
doodle_l = pygame.transform.flip(doodle, True, False)

spring = pygame.image.load('Images/spring.png')
spring = pygame.transform.scale(spring, BONUS_SIZE)

# Sounds
jump_sound = pygame.mixer.Sound("Images/jump_sound.mp3")
break_sound = pygame.mixer.Sound("Images/breaking_sound.mp3")
basic_sound = pygame.mixer.Sound("Images/basic_jumping.mp3")
death_sound = pygame.mixer.Sound("Images/death_sound.mp3")

# Music
mixer.init()
mixer.music.load('Images/Space-Jazz.mp3')
mixer.music.play()
