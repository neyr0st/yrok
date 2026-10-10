import pygame
import time
import random
import psycopg as psycopg2 

# PostgreSQL 
DB_CONFIG = {
    "dbname": "snake_game",
    "user": "postgres",
    "password": "2008",  
    "host": "localhost",
    "port": "5432",
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def save_score(player_name, score):
    """Сохраняет результат игры в БД."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO scores (player_name, score) VALUES (%s, %s)",
            (player_name, score)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Ошибка сохранения в БД:", e)

def get_best_score():
    """Возвращает лучший результат из БД."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT player_name, score FROM scores ORDER BY score DESC LIMIT 1")
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row if row else ("—", 0)
    except Exception as e:
        print("Ошибка чтения из БД:", e)
        return ("—", 0)

#Pygame 
pygame.init()

white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

dis_width = 800
dis_height = 600
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Змейка от Skillbox')
clock = pygame.time.Clock()

snake_block = 10
snake_speed = 15

font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)


def Your_score(score):
    value = score_font.render("Ваш счёт: " + str(score), True, yellow)
    dis.blit(value, [0, 0])

def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, black, [x[0], x[1], snake_block, snake_block])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [dis_width / 6, dis_height / 3])


def ask_player_name():
    """Простое окно ввода имени через pygame."""
    name = ""
    input_active = True
    while input_active:
        dis.fill(blue)
        prompt = font_style.render("Введите имя и нажмите Enter:", True, white)
        dis.blit(prompt, [dis_width / 6, dis_height / 3])
        name_surf = score_font.render(name + "|", True, yellow)
        dis.blit(name_surf, [dis_width / 6, dis_height / 2])
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 20:
                    name += event.unicode
    return name.strip()


def gameLoop(player_name):
    game_over = False
    game_close = False

    x1 = dis_width / 2
    y1 = dis_height / 2
    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0

    score_saved = False

    while not game_over:

       
        while game_close == True:
            if not score_saved:
                save_score(player_name, Length_of_snake - 1)
                score_saved = True

            best_name, best_score = get_best_score()

            dis.fill(blue)
            message("Вы проиграли! Q — выход, C — заново", red)
            Your_score(Length_of_snake - 1)

            best_text = font_style.render(
                f"Лучший результат: {best_name} — {best_score}", True, white
            )
            dis.blit(best_text, [dis_width / 6, dis_height / 3 + 40])
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop(player_name)
                        return

        # --- обработка событий ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change
        dis.fill(blue)
        pygame.draw.rect(dis, green, [foodx, foody, snake_block, snake_block])

        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block, snake_List)
        Your_score(Length_of_snake - 1)
        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()


player_name = ask_player_name()
gameLoop(player_name)