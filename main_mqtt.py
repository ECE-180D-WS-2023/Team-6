from singleton import Singleton
from camera import Camera
from player import Player
from level import Level
import settings as config
import pygame
import paho.mqtt.client as mqtt

topic = "team6"
HOST = 'localhost'
PORT = 1883

def on_connect(client, userdata, flags, rc):
    print("Connected: " + str(rc))
    client.subscribe(topic)
    client.subscribe("scores")

def on_publish(client, userdata, flags, rc):
    print("Posted Score to other player")
    pass

key_mapping = {"RIGHT": pygame.K_RIGHT, "LEFT": pygame.K_LEFT}

client = mqtt.Client()
client.connect(HOST, PORT, 60)
client.on_connect = on_connect
client.on_publish = on_publish


class Game(Singleton):
    """
    A class to represent the game.

    used to manage game updates, draw calls and user input events.
    Can be access via Singleton: Game.instance .
    (Check Singleton design pattern for more info)
    """

    # constructor called on new instance: Game()
    def __init__(self) -> None:

        # ============= Initialisation =============
        self.__alive = True
        # Window / Render
        self.window = pygame.display.set_mode(config.DISPLAY, config.FLAGS)
        self.clock = pygame.time.Clock()

        # Instances
        self.camera = Camera()
        self.lvl = Level()
        self.player = Player(
            config.HALF_XWIN - config.PLAYER_SIZE[0] / 2,  # X POS
            config.HALF_YWIN + config.HALF_YWIN / 2,  # Y POS
            *config.PLAYER_SIZE,  # SIZE
            config.PLAYER_COLOR  # COLOR
        )

        # User Interface
        self.score = 0
        self.score_txt = config.SMALL_FONT.render("0 m", 1, config.GRAY)
        self.score_pos = pygame.math.Vector2(10, 10)

        self.gameover_txt = config.LARGE_FONT.render("Game Over", 1, config.GRAY)
        self.gameover_rect = self.gameover_txt.get_rect(
            center=(config.HALF_XWIN, config.HALF_YWIN))

    def close(self):
        self.__alive = False

    def reset(self):
        self.camera.reset()
        self.lvl.reset()
        self.player.reset()

    def _event_loop(self):
        # ---------- User Events ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                if event.key == pygame.K_RETURN and self.player.dead:
                    self.reset()
            self.player.handle_event(event)

    def on_message(self, client, userdata, msg):
        cmd = msg.payload.decode()
        key = key_mapping[cmd]
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": key}))

    def _update_loop(self):
        # ----------- Update -----------
        self.player.update()
        self.lvl.update()

        if not self.player.dead:
            self.camera.update(self.player.rect)
            # Calculate score and update UI txt
            self.score = -self.camera.state.y // 50
            self.score_txt = config.SMALL_FONT.render(
                str(self.score) + " m", 1, config.GRAY)
            client.publish("scores", str(self.score))

    def _render_loop(self):
        # ----------- Display -----------
        self.window.fill(config.WHITE)
        self.lvl.draw(self.window)
        self.player.draw(self.window)

        # User Interface
        if self.player.dead:
            self.window.blit(self.gameover_txt, self.gameover_rect)  # gameover txt
        self.window.blit(self.score_txt, self.score_pos)  # score txt

        pygame.display.update()  # window update
        self.clock.tick(config.FPS)  # max loop/s

    def run(self):
        # ============= MAIN GAME LOOP =============
        while self.__alive:
            self._event_loop()
            self._update_loop()
            self._render_loop()         
        pygame.quit()


if __name__ == "__main__":
    # ============= PROGRAM STARTS HERE =============
    game = Game()
    client.loop_start()
    client.on_message = game.on_message
    game.run()