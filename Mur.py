import sys
import pygame

# ----------------------
# Константы
# ----------------------
WIDTH, HEIGHT = 960, 540
FPS = 60

# Физика
GRAVITY = 2000.0          # пикселей/сек^2
TERMINAL_VELOCITY = 2400  # максимальная скорость падения (px/s)
JUMP_VELOCITY = 900.0     # скорость прыжка вверх (px/s)
PLAYER_SPEED = 260.0      # горизонтальная скорость (px/s)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY = (255, 192, 203)
PLATFORM_COLOR = BLACK
PLAYER_COLOR = WHITE


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, w: int = 40, h: int = 40):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))

        # Реальные координаты и скорость с плавающей точкой
        self.pos = pygame.Vector2(self.rect.topleft)
        self.vel = pygame.Vector2(0.0, 0.0)
        self.on_ground = False
        # Для детекции фронта нажатия прыжка
        self._jump_prev = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        # Горизонтальное движение
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = PLAYER_SPEED
        else:
            self.vel.x = 0.0

        # Прыжок по фронту нажатия (SPACE)
        jump_down = keys[pygame.K_SPACE]
        if jump_down and not self._jump_prev:
            self.jump()
        self._jump_prev = jump_down

    def jump(self):
        # Прыгнуть можно только стоя на земле
        if self.on_ground:
            self.vel.y = -JUMP_VELOCITY
            self.on_ground = False

    def apply_gravity(self, dt: float):
        # v = v0 + g * dt, ограничиваем терминальной скоростью
        self.vel.y = min(self.vel.y + GRAVITY * dt, TERMINAL_VELOCITY)

    def move_and_collide(self, dt: float, platforms: list[pygame.Rect]):
        # Горизонтальное перемещение и столкновения
        self.pos.x += self.vel.x * dt
        self.rect.x = round(self.pos.x)

        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel.x > 0:  # движение вправо
                    self.rect.right = p.left
                elif self.vel.x < 0:  # движение влево
                    self.rect.left = p.right
                self.pos.x = float(self.rect.x)

        # Вертикальная ��асть: применяем гравитацию, движемся, обрабатываем коллизии
        self.apply_gravity(dt)
        self.pos.y += self.vel.y * dt
        self.rect.y = round(self.pos.y)

        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel.y > 0:  # падали вниз — упёрлись в верх платформы
                    self.rect.bottom = p.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:  # летели вверх — ударились головой
                    self.rect.top = p.bottom
                    self.vel.y = 0
                self.pos.y = float(self.rect.y)

        # Ограничение перемещения границами окна
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = float(self.rect.x)
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.pos.x = float(self.rect.x)

        if self.rect.top < 0:
            self.rect.top = 0
            self.vel.y = 0
            self.pos.y = float(self.rect.y)
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel.y = 0
            self.on_ground = True
            self.pos.y = float(self.rect.y)

    def update(self, dt: float, platforms: list[pygame.Rect]):
        self.handle_input()
        self.move_and_collide(dt, platforms)


def build_level() -> list[pygame.Rect]:
    # Несколько платформ + пол (добавлено >=5 платформ)
    ground = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)
    # Ступени и площадки
    p1 = pygame.Rect(80, HEIGHT - 140, 180, 20)
    p2 = pygame.Rect(300, HEIGHT - 220, 180, 20)
    p3 = pygame.Rect(540, HEIGHT - 300, 160, 20)
    p4 = pygame.Rect(760, HEIGHT - 220, 160, 20)
    p5 = pygame.Rect(880, HEIGHT - 140, 80, 20)
    p6 = pygame.Rect(360, HEIGHT - 120, 160, 20)
    return [ground, p1, p2, p3, p4, p5, p6]


def draw(screen: pygame.Surface, player: Player, platforms: list[pygame.Rect]):
    screen.fill(SKY)

    # Платформы
    for p in platforms:
        pygame.draw.rect(screen, PLATFORM_COLOR, p)

    # Игрок
    screen.blit(player.image, player.rect)

    # Немного отладочной информации
    font = pygame.font.SysFont("consolas", 18)
    info = (
        f"vx={player.vel.x:.1f} px/s  "
        f"vy={player.vel.y:.1f} px/s  "
        f"ground={player.on_ground}  "
        f"gravity={GRAVITY:.0f}"
    )
    text = font.render(info, True, WHITE)
    screen.blit(text, (10, 10))


def main():
    pygame.init()
    pygame.display.set_caption("Платформер: гравитация + прыжок (SPACE)")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    platforms = build_level()
    player = Player(60, HEIGHT - 300)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # в секундах

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
        player.update(dt, platforms)

        draw(screen, player, platforms)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
