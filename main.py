from singleton import Singleton
from camera import Camera
from player import Player
from level import Level
import settings as config
import pygame
from pygame import mixer
from connection import connection
import random


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
        mixer.init()
        mixer.music.load('Images/Space-Jazz.mp3')
        mixer.music.play()

        self.id = random.randint(1, 10000)
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
        self.initial_score = 0
        self.score = 0
        self.score_txt = config.SMALL_FONT.render("0 m", 1, config.WHITE)
        self.score_pos = pygame.math.Vector2(10, 10)

        self.gameover_txt = config.LARGE_FONT.render("Game Over", 1, config.WHITE)
        self.gameover_rect = self.gameover_txt.get_rect(
            center=(config.HALF_XWIN, config.HALF_YWIN))
        self.gameover2_txt = config.SMALL_FONT.render("Press Return to Restart", 1, config.WHITE)
        self.gameover2_rect = self.gameover_txt.get_rect(
            center=(config.HALF_XWIN + 100, config.HALF_YWIN + 100))
        
        self.abilities_txt = config.SMALL_FONT.render("3", 1, config.RED)
        self.abilities_pos = pygame.math.Vector2(config.HALF_XWIN * 2 - 70, 10)
        self.initial_ability_frames = 100

        self.is_multiplayer = False
        self.awaiting_partner = True
        self.partner_found = False
        self.sent_dead = False
        def handle_msg(client, data, msg):
            msg = msg.payload.decode('ascii')
            content = msg.split(',')
            if content[0] == str(self.id):
                return
            print(content)
            if content[1] == 'start_multiplayer' and self.awaiting_partner and self.is_multiplayer:
                self.awaiting_partner = False
                self.connection.publish('partner_found')
            if content[1] == 'partner_found':
                self.partner_found = True
            if content[1] == 'partner_died':
                self.awaiting_partner = False
                self.initial_score = int(content[2])
                self.initial_ability_frames = int(content[3])
        connect = connection(handle_msg, self.id)
        self.connection = connect

    # Draw menu function
    def draw_menu(self):
        config.screen.blit(config.menu_background, (0, 0))

        if self.is_multiplayer:
            title_text = config.LARGE_FONT.render("Partner Playing" if self.partner_found else "Awaiting Partner", True, config.BLACK)
        else:
            title_text = config.LARGE_FONT.render("Doodle Jump 2.0", True, config.BLACK)
            for text, position in config.menu_items:
                menu_text = config.menu_font.render(text, True, config.BLACK)
                config.screen.blit(menu_text, position)

        config.screen.blit(title_text, (config.HALF_XWIN - 350, config.HALF_YWIN - 200))
        pygame.display.flip()

    # Countdown function
    def countdown(self):
        for count in range(3, 0, -1):
            config.screen.blit(config.menu_background, (0, 0))
            countdown_text = config.countdown_font.render(str(count), True, config.BLACK)
            config.screen.blit(countdown_text, (config.HALF_XWIN - 50, config.HALF_YWIN - 50))
            pygame.display.flip()
            pygame.time.delay(1000)

    def close(self):
        self.__alive = False

    def reset(self):
        self.player.ability_frames_left = self.initial_ability_frames
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

    def _update_loop(self):
        # ----------- Update -----------
        self.player.update()
        self.lvl.update()
        if not self.player.dead and self.player.ability_frames_left < 100:
            self.player.ability_frames_left += 1/30

        if not self.player.dead:
            self.camera.update(self.player.rect)
            # Calculate score and update UI txt
            self.score = -(self.camera.state.y // 50) + self.initial_score
            self.score_txt = config.SMALL_FONT.render(
                str(self.score) + " m", 1, config.GRAY)

    def _render_loop(self):
        # ----------- Display -----------
        self.window.fill(config.WHITE)
        self.window.blit(config.backround, (-100, -100))  # Backround image
        self.lvl.draw(self.window)
        self.player.draw(self.window)

        # User Interface
        if self.player.dead:
            if self.is_multiplayer and not self.sent_dead:
                self.sent_dead = True
                self.connection.publish(f'partner_died,{self.score},{int(self.player.ability_frames_left)}')
            self.window.blit(self.gameover_txt, self.gameover_rect)  # gameover txt
            self.window.blit(self.gameover2_txt, self.gameover2_rect)  # gameover txt
        
        self.window.blit(self.score_txt, self.score_pos)  # score txt

        ability_txt = str(int(max(0, self.player.ability_frames_left)))
        if self.player.five_fingers:
            self.abilities_txt = config.SMALL_FONT.render(ability_txt, 1, config.RED)
        else:
            self.abilities_txt = config.SMALL_FONT.render(ability_txt, 1, config.WHITE)
            
        self.window.blit(self.abilities_txt, self.abilities_pos)

        pygame.display.update()  # window update
        self.clock.tick(config.FPS)  # max loop/s

    def run(self):
        self.player.ability_frames_left = self.initial_ability_frames
        # ============= MAIN GAME LOOP =============
        while self.__alive:
            self._event_loop()
            self._update_loop()
            self._render_loop()
        pygame.quit()

    # Menu init
    def menu(self):
        # Menu config
        menu = True
        while menu:
            self.draw_menu()
            if self.is_multiplayer and not self.awaiting_partner:
                self.countdown()
                self.run()
                menu = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu = False
                    pygame.quit()
                    quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    for text, position in config.menu_items:
                        text_width, text_height = config.menu_font.size(text)
                        text_x, text_y = position

                        if text_x <= mouse_pos[0] <= text_x + text_width and text_y <= mouse_pos[
                            1] <= text_y + text_height:
                            if text == 'Multiplayer':
                                self.is_multiplayer = True
                                self.awaiting_partner = True
                                self.connection.publish('start_multiplayer')
                            else:
                                self.countdown()
                                self.run()
                                menu = False

if __name__ == "__main__":
    # ============= PROGRAM STARTS HERE =============
    game = Game()
    game.menu()
