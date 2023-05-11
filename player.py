from math import copysign
from pygame.math import Vector2
from pygame.locals import KEYDOWN, KEYUP, K_LEFT, K_RIGHT, K_SPACE
from pygame.sprite import collide_rect
from pygame.event import Event
import mediapipe as mp
import cv2

from singleton import Singleton
from sprite import Sprite
from level import Level
import settings as config

# Return the sign of a number: getsign(-5)-> -1
getsign = lambda x: copysign(1, x)


class Player(Sprite, Singleton):
    """
    A class to represent the player.

    Manages player's input,physics (movement...).
    Can be access via Singleton: Player.instance.
    (Check Singleton design pattern for more info).
    """

    # (Overriding Sprite.__init__ constructor)
    def __init__(self, *args):
        # calling default Sprite constructor
        Sprite.__init__(self, *args)
        self.__startrect = self.rect.copy()
        self.__maxvelocity = Vector2(config.PLAYER_MAX_SPEED, 100)
        self.__startspeed = 5

        # velocity and jumpforce
        self._velocity = Vector2()
        self._input = 0
        self._jumpforce = config.PLAYER_JUMPFORCE
        self._bonus_jumpforce = config.PLAYER_BONUS_JUMPFORCE

        # gravity
        self.gravity = config.GRAVITY
        self.accel = .5
        self.deccel = .6
        self.space_pressed = False
        self.dead = False

        # mediapipe
        self.cap = cv2.VideoCapture(0)
        success, _ = self.cap.read()
        if not success:
            self.cap = None

        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands( model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5 )
        self.frame_num = 0
        self.five_fingers = False
        self.ability_frames_left = 100

        # image setup
        self._image = config.doodle

    def _fix_velocity(self) -> None:
        """ Set player's velocity between max/min.
        Should be called in Player.update().
        """
        self._velocity.y = min(self._velocity.y, self.__maxvelocity.y)
        self._velocity.y = round(max(self._velocity.y, -self.__maxvelocity.y), 2)
        self._velocity.x = min(self._velocity.x, self.__maxvelocity.x)
        self._velocity.x = round(max(self._velocity.x, -self.__maxvelocity.x), 2)

    def reset(self) -> None:
        " Called only when game restarts (after player death)."
        self._velocity = Vector2()
        self.rect = self.__startrect.copy()
        self.camera_rect = self.__startrect.copy()
        self.dead = False

    def handle_event(self, event: Event) -> None:
        """ Called in main loop foreach user input event.
        :param event pygame.Event: user input event
        """
        # Check if start moving
        if event.type == KEYDOWN:
            # Moves player only on x-axis (left/right)
            if event.key == K_LEFT:
                self._velocity.x = -self.__startspeed
                self._input = -1
                self._image = config.doodle_l
            elif event.key == K_RIGHT:
                self._velocity.x = self.__startspeed
                self._input = 1
                self._image = config.doodle
            elif event.key == K_SPACE:
                self.space_pressed = not self.space_pressed

        # Check if stop moving
        elif event.type == KEYUP:
            if (event.key == K_LEFT and self._input == -1) or (
                    event.key == K_RIGHT and self._input == 1):
                self._input = 0

    def jump(self, force: float = None) -> None:
        if not force: force = self._jumpforce
        self._velocity.y = -force

    def onCollide(self, obj: Sprite) -> None:
        self.rect.bottom = obj.rect.top
        self.jump()

    def collisions(self) -> None:
        """ Checks for collisions with level.
        Should be called in Player.update().
        """
        lvl = Level.instance
        if not lvl: return
        for platform in lvl.platforms:
            # check falling and colliding <=> isGrounded ?
            if self._velocity.y > .5:
                # check collisions with platform's spring bonus
                if platform.bonus and collide_rect(self, platform.bonus):
                    self.onCollide(platform.bonus)
                    self.jump(platform.bonus.force)
                    config.jump_sound.play()
                    self.ability_frames_left = min(100, self.ability_frames_left + 10)

                # check collisions with platform
                if collide_rect(self, platform):
                    self.onCollide(platform)
                    platform.onCollide()
                    config.basic_sound.play()

    def update(self) -> None:
        """ For position and velocity updates.
        Should be called each frame.
        """
        # Check if player out of screen: should be dead
        if self.camera_rect.y > config.YWIN * 2:
            if not self.dead:
                config.death_sound.play()
            self.dead = True
            return
        # Velocity update (apply gravity, input acceleration)
        self._velocity.y += self.gravity
        if self._input:  # accelerate
            self._velocity.x += self._input * self.accel
        elif self._velocity.x:  # deccelerate
            self._velocity.x -= getsign(self._velocity.x) * self.deccel
            self._velocity.x = round(self._velocity.x)
        self._fix_velocity()

        # Position Update (prevent x-axis to be out of screen)
        self.rect.x = (self.rect.x + self._velocity.x) % (config.XWIN - self.rect.width)
        self.rect.y += self._velocity.y

        self.collisions()


        self.frame_num += 1
        if (self.frame_num % 5 != 0):
            return
    
        if self.space_pressed and self.ability_frames_left > 0:
            self.gravity = config.GRAVITY / 4
            self.five_fingers = True
            self.ability_frames_left -= 3
            return
        else:
            self.gravity = config.GRAVITY
            self.five_fingers = False
        
        if self.cap is None:
            return
        success, image = self.cap.read()
        if not success:
            return
        
        # To improve performance, optionally mark the image as not writeable
        image = cv2.flip(image, 1)
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image)

        fingerCount = 0
        if results and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get hand index to check label (left or right)
                handIndex = results.multi_hand_landmarks.index(hand_landmarks)
                handLabel = results.multi_handedness[handIndex].classification[0].label

                # Set variable to keep landmarks positions (x and y)
                handLandmarks = []

                # Fill list with x and y positions of each landmark
                for landmarks in hand_landmarks.landmark:
                    handLandmarks.append([landmarks.x, landmarks.y])

                # Test conditions for each finger: Count is increased if finger is 
                #   considered raised.
                # Thumb: TIP x position must be greater or lower than IP x position, 
                #   deppeding on hand label.
                if handLabel == "Left" and handLandmarks[4][0] > handLandmarks[3][0]:
                    fingerCount = fingerCount+1
                elif handLabel == "Right" and handLandmarks[4][0] < handLandmarks[3][0]:
                    fingerCount = fingerCount+1

                # Other fingers: TIP y position must be lower than PIP y position, 
                #   as image origin is in the upper left corner.
                if handLandmarks[8][1] < handLandmarks[6][1]:       #Index finger
                    fingerCount = fingerCount+1
                if handLandmarks[12][1] < handLandmarks[10][1]:     #Middle finger
                    fingerCount = fingerCount+1
                if handLandmarks[16][1] < handLandmarks[14][1]:     #Ring finger
                    fingerCount = fingerCount+1
                if handLandmarks[20][1] < handLandmarks[18][1]:     #Pinky
                    fingerCount = fingerCount+1

        if fingerCount >= 5 and self.ability_frames_left > 0:
            self.gravity = config.GRAVITY / 4
            self.five_fingers = True
            self.ability_frames_left -= 3
        else:
            self.gravity = config.GRAVITY
            self.five_fingers = False
