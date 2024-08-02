import pygame
import random
import os
import sys

def log_error(message):
    print(f"FEL: {message}", file=sys.stderr)

try:
    pygame.init()
    print("Pygame initialiserat framgångsrikt.")

    # Skärmstorlek
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Ninja Leopard")
    print("Fönster skapat framgångsrikt.")

    # Få den absoluta sökvägen till skriptets katalog
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Skriptkatalog: {script_dir}")

    # Funktion för att ladda och skala bilder från assets-mappen
    def load_image(name, scale_width=None, scale_height=None):
        try:
            full_path = os.path.join(script_dir, "assets", name)
            print(f"Försöker ladda bild: {full_path}")
            image = pygame.image.load(full_path).convert_alpha()
            if scale_width and scale_height:
                image = pygame.transform.scale(image, (scale_width, scale_height))
            return image
        except pygame.error as e:
            log_error(f"Kunde inte ladda bilden '{name}': {e}")
            return None

    leopard_size_x = 110
    leopard_size_y = 55
    # Ladda och skala bilder
    images = {
        "background": load_image("level_1.png", SCREEN_WIDTH, SCREEN_HEIGHT),
        "leopard_standing": load_image("leopard_standing_4_legs.png", leopard_size_x, leopard_size_y),
        "leopard_running": load_image("running_leopard.png", leopard_size_x, leopard_size_y),
        "leopard_shooting": load_image("leopard_standing_hind_legs.png", leopard_size_x, leopard_size_y),
        "leopard_jumping": load_image("leopard_jumping.png", leopard_size_x, leopard_size_y),
        "leopard_flipping": load_image("leopard_flipping.png", leopard_size_x, leopard_size_y),
        "thunder": load_image("thunder_blue.png", 50, 50),
        "bomb": load_image("bomb.png", 30, 30)
    }

    monster_images = []
    for i in range(1, 4):
        monster_image = load_image(f"monster_{i}.png", 100, 100)
        if monster_image:
            monster_images.append(monster_image)
        else:
            log_error(f"Kunde inte ladda monster_{i}.png")

    if not monster_images:
        log_error("Inga monsterbilder kunde laddas. Avslutar.")
        pygame.quit()
        sys.exit(1)

    print("Alla bilder laddade framgångsrikt.")

    # Spelarklass
    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = images["leopard_standing"]
            self.original_image = self.image
            self.rect = self.image.get_rect()
            self.rect.x = 50
            self.rect.y = SCREEN_HEIGHT - self.rect.height - 10
            self.speed = 5
            self.jump_speed = -15
            self.gravity = 0.8
            self.vertical_speed = 0
            self.is_jumping = False
            self.is_running = False
            self.is_shooting = False
            self.lives = 10
            self.facing_right = True

        def update(self):
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
                if self.facing_right:
                    self.image = pygame.transform.flip(self.original_image, True, False)
                    self.facing_right = False
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
                if not self.facing_right:
                    self.image = pygame.transform.flip(self.original_image, True, False)
                    self.facing_right = True
            
            if keys[pygame.K_h]:
                self.is_running = True
                self.speed = 8
                self.original_image = images["leopard_running"]
            else:
                self.is_running = False
                self.speed = 5
                self.original_image = images["leopard_standing"]

            if keys[pygame.K_UP] and not self.is_jumping:
                self.is_jumping = True
                self.vertical_speed = self.jump_speed
                self.original_image = images["leopard_jumping"]

            if self.is_jumping:
                self.rect.y += self.vertical_speed
                self.vertical_speed += self.gravity
                if self.vertical_speed > 0:
                    self.original_image = images["leopard_flipping"]
                if self.rect.bottom >= SCREEN_HEIGHT - 10:
                    self.rect.bottom = SCREEN_HEIGHT - 10
                    self.is_jumping = False
                    self.vertical_speed = 0

            if keys[pygame.K_x]:
                self.is_shooting = True
                self.original_image = images["leopard_shooting"]
            else:
                self.is_shooting = False

            if not self.facing_right:
                self.image = pygame.transform.flip(self.original_image, True, False)
            else:
                self.image = self.original_image

            self.rect.clamp_ip(screen.get_rect())

            print(f"Spelarens liv: {self.lives}")  # Log spelarens liv

    # Monsterklass
    class Monster(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = random.choice(monster_images)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.lives = 3
            self.bomb_timer = 0

        def update(self):
            self.bomb_timer += 1
            if self.bomb_timer >= 90:  # Skjut en bomb var 1.5 sekund
                self.bomb_timer = 0
                return Bomb(self.rect.right, self.rect.centery, direction="left")
            return None

    # Bombklass
    class Bomb(pygame.sprite.Sprite):
        def __init__(self, x, y, direction="right"):
            super().__init__()
            self.image = images["bomb"]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.speed = 5
            self.direction = direction

        def update(self):
            if self.direction == "right":
                self.rect.x += self.speed
                if self.rect.left > SCREEN_WIDTH:
                    self.kill()
            else:
                self.rect.x -= self.speed
                if self.rect.right < 0:
                    self.kill()

    # Blixtklass
    class Thunder(pygame.sprite.Sprite):
        def __init__(self, x, y, direction="right"):
            super().__init__()
            self.image = images["thunder"]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.speed = 10
            self.direction = direction

        def update(self):
            if self.direction == "right":
                self.rect.x += self.speed
                if self.rect.left > SCREEN_WIDTH:
                    self.kill()
            else:
                self.rect.x -= self.speed
                if self.rect.right < 0:
                    self.kill()

    # Skapa spelgrupper
    all_sprites = pygame.sprite.Group()
    monsters = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    thunders = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    # Placera monster i kokosnötter
    coconut_positions = [
        {"x": 1524, "y": 817},
        {"x": 261, "y": 279},
        {"x": 127, "y": 911}
    ]

    for pos in coconut_positions:
        monster = Monster(pos["x"], pos["y"])
        all_sprites.add(monster)
        monsters.add(monster)

    # Spelloopen
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    direction = "right" if player.facing_right else "left"
                    thunder = Thunder(player.rect.right, player.rect.centery, direction)
                    all_sprites.add(thunder)
                    thunders.add(thunder)
                elif event.key == pygame.K_ESCAPE:
                    running = False

        all_sprites.update()

        # Hantera kollisioner
        for monster in monsters:
            new_bomb = monster.update()
            if new_bomb:
                all_sprites.add(new_bomb)
                bombs.add(new_bomb)

        monster_hits = pygame.sprite.spritecollide(player, monsters, False)
        for monster in monster_hits:
            player.lives -= 1
            if player.lives <= 0:
                print("Du förlorade alla liv! Återställ spelarens liv för att fortsätta spela.")
                player.lives = 10  # Återställ spelarens liv
                pygame.time.delay(1000)  # Vänta en sekund

        bomb_hits = pygame.sprite.spritecollide(player, bombs, True)
        for bomb in bomb_hits:
            player.lives -= 1
            if player.lives <= 0:
                print("Du förlorade alla liv! Återställ spelarens liv för att fortsätta spela.")
                player.lives = 10  # Återställ spelarens liv
                pygame.time.delay(1000)  # Vänta en sekund

        thunder_hits = pygame.sprite.groupcollide(thunders, monsters, True, False)
        for thunder, hit_monsters in thunder_hits.items():
            for monster in hit_monsters:
                monster.lives -= 1
                if monster.lives <= 0:
                    monster.kill()

        # Rita allt
        screen.blit(images["background"], (0, 0))
        all_sprites.draw(screen)
        
        # Visa spelarens liv
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
        screen.blit(lives_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

except Exception as e:
    log_error(f"Ett oväntat fel inträffade: {e}")
    import traceback
    traceback.print_exc()

finally:
    pygame.quit()
    print("Spelet har avslutats.")
