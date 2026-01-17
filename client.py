from pygame import *
import socket
import json
from threading import Thread

# --- ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")

# --- ЗАВАНТАЖЕННЯ ФОНУ ---
background_img = image.load("./maksim.png").convert()
background_img = transform.scale(background_img, (WIDTH, HEIGHT))

# --- СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))  # ---- Підключення до сервера
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass

def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            if not data:
                game_state["winner"] = -1
                break
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)

# --- ГРА ---
game_over = False
winner = None
you_winner = None
my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()

while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    # --- ВІДЛІК ---
    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.blit(background_img, (0, 0))
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (5, 255, 100))
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue  # Не малюємо гру до завершення відліку

    # --- ПЕРЕМОГА / ПОРАЗКА ---
    elif "winner" in game_state and game_state["winner"] is not None:
        screen.blit(background_img, (0, 0))

        if you_winner is None:  # Встановлюємо лише один раз
            you_winner = (game_state["winner"] == my_id)

        text = "Ти переміг!" if you_winner else "Пощастить наступним разом!"
        win_text = font_win.render(text, True, (255, 215, 0))
        screen.blit(win_text, win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        restart_text = font_win.render('К - рестарт', True, (255, 215, 0))
        screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120)))

        display.update()
        continue  # Блокує гру після перемоги

    # --- ОСНОВНА ГРА ---
    else:
        screen.blit(background_img, (0, 0))
        if game_state:
            draw.rect(screen, (0, 255, 0), (20, game_state['paddles']['0'], 20, 100))
            draw.rect(screen, (255, 0, 255), (WIDTH - 40, game_state['paddles']['1'], 20, 100))
            draw.circle(screen, (255, 255, 255), (game_state['ball']['x'], game_state['ball']['y']), 10)
            score_text = font_main.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True, (255, 255, 255))
            screen.blit(score_text, (WIDTH // 2 - 25, 20))

            if game_state['sound_event']:
                if game_state['sound_event'] == 'wall_hit':
                    pass
                if game_state['sound_event'] == 'platform_hit':
                    pass
        else:
            wating_text = font_main.render(f"Очікування гравців...", True, (255, 255, 255))
            screen.blit(wating_text, (WIDTH // 2 - 25, 20))

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")
