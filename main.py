from singleton import Singleton
from camera import Camera
from player import Player
from level import Level
import settings as config
import pygame
from pygame import mixer


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

    # Draw menu function
    def draw_menu(self):
        config.screen.blit(config.menu_background, (0, 0))

        title_text = config.LARGE_FONT.render("Doodle Jump 2.0", True, config.BLACK)
        config.screen.blit(title_text, (config.HALF_XWIN - 350, config.HALF_YWIN - 200))

        for text, position in config.menu_items:
            menu_text = config.menu_font.render(text, True, config.BLACK)
            config.screen.blit(menu_text, position)

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

        if not self.player.dead:
            self.camera.update(self.player.rect)
            # Calculate score and update UI txt
            self.score = -self.camera.state.y // 50
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
            self.window.blit(self.gameover_txt, self.gameover_rect)  # gameover txt
            self.window.blit(self.gameover2_txt, self.gameover2_rect)  # gameover txt
        
        self.window.blit(self.score_txt, self.score_pos)  # score txt

        if self.player.five_fingers:
            self.abilities_txt = config.SMALL_FONT.render(str(self.player.ability_frames_left), 1, config.RED)
        else:
            self.abilities_txt = config.SMALL_FONT.render(str(self.player.ability_frames_left), 1, config.WHITE)
            
        self.window.blit(self.abilities_txt, self.abilities_pos)

        pygame.display.update()  # window update
        self.clock.tick(config.FPS)  # max loop/s

    def run(self):
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
                            self.countdown()
                            self.run()
                            menu = False

if __name__ == "__main__":
    # ============= PROGRAM STARTS HERE =============
    game = Game()
    game.menu()
