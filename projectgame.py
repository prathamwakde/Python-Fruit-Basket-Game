import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 998, 789
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fruit Catcher")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonts
def get_font(size):
    """Load and return a font."""
    try:
        return pygame.font.Font("font.ttf", size)
    except FileNotFoundError:
        print("Font file not found! Using default font.")
        return pygame.font.Font(None, size)

# Load assets
try:
    BG = pygame.transform.scale(pygame.image.load("background.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT))
    GAME_NAME_IMG = pygame.transform.scale(pygame.image.load("game_name.png"), (800, 150))
    BUTTON_IMG = pygame.transform.scale(pygame.image.load("button.png"), (300, 100))

    fruit_images = [
        pygame.transform.scale(pygame.image.load("apple.png"), (60, 60)),
        pygame.transform.scale(pygame.image.load("banana.png"), (60, 60)),
        pygame.transform.scale(pygame.image.load("orange.png"), (60, 60)),
        pygame.transform.scale(pygame.image.load("pineapple.png"), (60, 60)),
        pygame.transform.scale(pygame.image.load("mango.png"), (60, 60)),
        pygame.transform.scale(pygame.image.load("strawberrie.png"), (60, 60)),
    ]

    basket_img = pygame.transform.scale(pygame.image.load("basket.png"), (120, 60))
    heart_img = pygame.transform.scale(pygame.image.load("heart.png"), (40, 40))
except pygame.error as e:
    print(f"Error loading images: {e}")
    sys.exit()

# Load sounds
try:
    pygame.mixer.music.load("background_music.mp3")
    fruit_collect_sound = pygame.mixer.Sound("fruit_collect.wav")
    game_over_sound = pygame.mixer.Sound("game_over.mp3")
    game_win_sound = pygame.mixer.Sound("game_win.mp3")
except pygame.error as e:
    print(f"Error loading sounds: {e}")
    sys.exit()

# Constants
BASKET_SPEED = 20
FRUIT_SPEED = 5
SPAWN_INTERVAL = 30
MAX_MISSED_FRUITS = 3
WINNING_SCORE = 50

# Button class
class Button:
    def __init__(self, image, pos, text, font, base_color, hover_color):
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color

    def draw(self, screen):
        """Draw the button with dynamic text color."""
        screen.blit(self.image, self.rect)
        color = self.hover_color if self.is_hovered() else self.base_color
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_hovered(self):
        """Check if the button is hovered by the mouse."""
        return self.rect.collidepoint(pygame.mouse.get_pos())

# Toggle music
music_on = False

def toggle_music(state):
    """Toggle the background music on or off."""
    global music_on
    if state == "ON":
        pygame.mixer.music.play(-1)
        music_on = True
    elif state == "OFF":
        pygame.mixer.music.stop()
        music_on = False

# Play screen
def play():
    basket_x = (SCREEN_WIDTH - basket_img.get_width()) // 2
    basket_y = SCREEN_HEIGHT - basket_img.get_height() - 10
    fruits = []
    spawn_timer = 0
    score = 0
    missed_fruits = 0

    clock = pygame.time.Clock()

    while True:
        SCREEN.blit(BG, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and basket_x > 0:
            basket_x -= BASKET_SPEED
        if keys[pygame.K_RIGHT] and basket_x < SCREEN_WIDTH - basket_img.get_width():
            basket_x += BASKET_SPEED

        # Spawn fruits
        spawn_timer += 1
        if spawn_timer >= SPAWN_INTERVAL:
            fruit_x = random.randint(0, SCREEN_WIDTH - 60)
            fruit_img = random.choice(fruit_images)
            fruits.append([fruit_x, 0, fruit_img])
            spawn_timer = 0

        # Move and draw fruits
        for fruit in fruits[:]:
            fruit[1] += FRUIT_SPEED
            if basket_x < fruit[0] < basket_x + basket_img.get_width() and \
               basket_y < fruit[1] + 60 < basket_y + basket_img.get_height():
                fruits.remove(fruit)
                score += 1
                fruit_collect_sound.play()
            elif fruit[1] > SCREEN_HEIGHT:
                fruits.remove(fruit)
                missed_fruits += 1

        for fruit in fruits:
            SCREEN.blit(fruit[2], (fruit[0], fruit[1]))

        # Draw basket
        SCREEN.blit(basket_img, (basket_x, basket_y))

        # Draw score
        score_text = get_font(36).render(f"Score: {score}", True, BLACK)
        SCREEN.blit(score_text, (10, 10))

        # Draw lives
        for i in range(MAX_MISSED_FRUITS - missed_fruits):
            SCREEN.blit(heart_img, (SCREEN_WIDTH - (i + 1) * 50 - 10, 10))

        # Check for game over or win
        if missed_fruits >= MAX_MISSED_FRUITS:
            display_animated_text("game_over.gif", game_over_sound)
            break
        if score >= WINNING_SCORE:
            display_animated_text("game_win.gif", game_win_sound)
            break

        pygame.display.flip()
        clock.tick(30)

    main_menu()

# Display animated text
def display_animated_text(image_path, sound, delay=3000):
    try:
        img = pygame.image.load(image_path)
        img = pygame.transform.scale(img, (600, 150))
        sound.play()
    except pygame.error as e:
        print(f"Error loading image {image_path}: {e}")
        return

    alpha = 0
    x, y = (SCREEN_WIDTH - 600) // 2, (SCREEN_HEIGHT - 150) // 2
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()

    while pygame.time.get_ticks() - start_time < delay:
        SCREEN.blit(BG, (0, 0))
        img.set_alpha(alpha)
        SCREEN.blit(img, (x, y))
        alpha = min(alpha + 10, 255)
        pygame.display.flip()
        clock.tick(30)

# Options screen
def options():
    while True:
        SCREEN.blit(BG, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        back_button = Button(BUTTON_IMG, (SCREEN_WIDTH // 2, 560), "BACK", get_font(30), "Black", "Green")
        music_on_button = Button(BUTTON_IMG, (SCREEN_WIDTH // 2 - 200, 360), "MUSIC ON", get_font(30), "Black", "Green")
        music_off_button = Button(BUTTON_IMG, (SCREEN_WIDTH // 2 + 200, 360), "MUSIC OFF", get_font(30), "Black", "Green")

        for button in [back_button, music_on_button, music_off_button]:
            button.draw(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_hovered():
                    main_menu()
                if music_on_button.is_hovered():
                    toggle_music("ON")
                if music_off_button.is_hovered():
                    toggle_music("OFF")

        pygame.display.update()

# Main menu
def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        SCREEN.blit(GAME_NAME_IMG, (99, 50))

        play_button = Button(BUTTON_IMG, (SCREEN_WIDTH // 2, 250), "PLAY", get_font(30), "Black", "Green")
        options_button = Button(BUTTON_IMG, (SCREEN_WIDTH // 2, 350), "OPTIONS", get_font(30), "Black", "Green")
        quit_button = Button(BUTTON_IMG, (SCREEN_WIDTH // 2, 450), "QUIT", get_font(30), "Black", "Green")

        for button in [play_button, options_button, quit_button]:
            button.draw(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.is_hovered():
                    play()
                if options_button.is_hovered():
                    options()
                if quit_button.is_hovered():
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

# Start the game
main_menu()
