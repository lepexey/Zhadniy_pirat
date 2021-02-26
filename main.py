import os
import sys

import pygame

pygame.init()
SCREEN_WIDTH = 800  # 16 * 50
SCREEN_HEIGHT = 600  # 12 * 50
size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Жадный пират")

FPS = 50


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Жадный пират", "", "",
                  "Правила игры",
                  "Управление:","", "","", "","", "","", "",
                  "Цель - собрать как можно больше монет",
                  "и дойти до финиша"]

    fon = pygame.transform.scale(load_image('starting_menu.png'), (800, 600))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    pic = pygame.transform.scale(load_image("keys.png"), (200, 170))
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        screen.blit(pic, (100, 240))

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def end_screen():
    intro_text = ["Жадный пират", "", "",
                  "Спасибо за прохождение",
                  "Это был только один уровень, в дальнейшем",
                  "я добавлю еще уровни и усложнение геймплея"]

    fon = pygame.transform.scale(load_image('starting_menu.png'), (800, 600))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'block': pygame.transform.scale(load_image("bl2.png"), (50, 50)),
    'flag': pygame.transform.scale(load_image("flag.png"), (60, 50)),
    'coin': pygame.transform.scale(load_image("coin.png"), (50, 50)),
    'player': pygame.transform.scale(load_image("player.png"), (40, 49)),
}
player_image = load_image('player.jpg')


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        global tiles_group, all_sprites
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y)


# Подключение фото для заднего фона
bg = pygame.transform.scale(load_image('back(0).png'), (800, 600))
tiles_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
player = None


# Класс, описывающий поведение главного игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = tile_images['player']

        self.right = True  # Изначально игрок смотрит вправо, поэтому эта переменная True
        self.rect = self.image.get_rect().move(
            50 * x, 50 * y)
        print(x, y)

        # Задаем вектор скорости игрока
        self.change_x = 0
        self.change_y = 0

    def update(self):
        self.calc_grav()

        # Передвигаем его на право/лево
        # change_x будет меняться позже при нажатии на стрелочки клавиатуры
        self.rect.x += self.change_x

        # Следим ударяем ли мы какой-то другой объект, платформы, например
        block_hit_list = pygame.sprite.spritecollide(self, tiles_group, False)
        # Перебираем все возможные объекты, с которыми могли бы столкнуться
        for block in block_hit_list:
            # Если мы идем направо,
            # устанавливает нашу правую сторону на левой стороне предмета, которого мы ударили
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # В противном случае, если мы движемся влево, то делаем наоборот
                self.rect.left = block.rect.right

        # Передвигаемся вверх/вниз
        self.rect.y += self.change_y

        # То же самое, вот только уже для вверх/вниз
        block_hit_list = pygame.sprite.spritecollide(self, tiles_group, False)
        for block in block_hit_list:
            # Устанавливаем нашу позицию на основе верхней / нижней части объекта, на который мы попали
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Останавливаем вертикальное движение
            self.change_y = 0

    def calc_grav(self):
        # Здесь мы вычисляем как быстро объект будет
        # падать на землю под действием гравитации
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .95

        # Если уже на земле, то ставим позицию Y как 0
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        self.rect.y += 10
        platform_hit_list = pygame.sprite.spritecollide(self, tiles_group, False)
        self.rect.y -= 10

        # Если все в порядке, прыгаем вверх
        if (len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT) and self.change_y == 0:
            self.change_y = -16

    # Передвижение игрока
    def go_left(self):
        # Сами функции будут вызваны позже из основного цикла
        self.change_x = -12  # Двигаем игрока по Х
        if self.right:  # Проверяем куда он смотрит и если что, то переворачиваем его
            self.flip()
            self.right = False

    def go_right(self):
        # то же самое, но вправо
        self.change_x = 12
        if not self.right:
            self.flip()
            self.right = True

    def stop(self):
        # вызываем этот метод, когда не нажимаем на клавиши
        self.change_x = 0

    def flip(self):
        # переворот игрока (зеркальное отражение)
        self.image = pygame.transform.flip(self.image, True, False)


coins_group = pygame.sprite.Group()
flag_group = pygame.sprite.Group()


class Flag(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        global coins_group
        super().__init__(flag_group)
        self.image = tile_images['flag']
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y)

    def update(self):
        block_hit_list = pygame.sprite.spritecollide(self, all_sprites, False)
        # Перебираем все возможные объекты, с которыми могли бы столкнуться
        for block in block_hit_list:
            block.kill()
            self.kill()
            end_screen()


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        global coins_group
        super().__init__(coins_group)
        self.image = tile_images['coin']
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y)

    def update(self):
        global money
        block_hit_list = pygame.sprite.spritecollide(self, all_sprites, False)
        if block_hit_list:
            self.kill()
            money += 1


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('block', x, y)
            elif level[y][x] == '!':
                Flag(x, y)
            elif level[y][x] == 'c':
                Coin(x, y)
            elif level[y][x] == 'x':
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - SCREEN_WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - SCREEN_HEIGHT // 2)


money = 0


def coin_load():
    global money
    with open("data/temp.txt", "rt") as t:
        money = int(t.readline().rstrip())


def coin_save():
    with open("data/temp.txt", "wt") as t:
        print(str(money), file=t)


def main():
    global player
    start_screen()
    player, level_x, level_y = generate_level(load_level('level1.txt'))

    all_sprites.add(player)
    coin_load()

    camera = Camera()
    running = True
    clock = pygame.time.Clock()
    while running:
        # Отслеживание действий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()
        all_sprites.update()
        tiles_group.update()

        # Если игрок приблизится к правой стороне, то дальше его не двигаем
        if player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH
        # Если игрок приблизится к левой стороне, то дальше его не двигаем
        if player.rect.left < 0:
            player.rect.left = 0

        screen.blit(bg, (0, 0))
        all_sprites.draw(screen)
        tiles_group.draw(screen)
        coins_group.draw(screen)
        flag_group.draw(screen)
        # изменяем ракурс камеры
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        for sprite in coins_group:
            camera.apply(sprite)
        for sprite in flag_group:
            camera.apply(sprite)
        coins_group.update()
        flag_group.update()

        font = pygame.font.Font(None, 40)
        text = font.render(f"{money}".rjust(5, "0"), True, (255, 215, 0))
        screen.blit(text, (707, 570))
        clock.tick(35)
        pygame.display.flip()
    coin_save()
    pygame.quit()


if __name__ == '__main__':
    main()
