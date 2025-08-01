import socket
import random
import json

def load_leaderboard():
    try:
        with open("leaderboard.json", "r") as f:
            leaderboard = json.load(f)
    except FileNotFoundError:
        leaderboard = {}
    return leaderboard


def save_leaderboard(leaderboard):
    with open("leaderboard.json", "w") as f:
        json.dump(leaderboard, f)


def generate_number(difficulty):
    if difficulty == 'easy':
        return random.randint(1, 50)
    elif difficulty == 'medium':
        return random.randint(1, 100)
    elif difficulty == 'hard':
        return random.randint(1, 500)
    else:
        return None


def update_leaderboard(leaderboard, name, score):
    if name in leaderboard:
        if score < leaderboard[name]:
            leaderboard[name] = score
    else:
        leaderboard[name] = score


def handle_client(conn):
    SERVER_PASSWORD = "letmein123"
    conn.send("Welcome to the Number Guessing Game!\n".encode())
    conn.send("Enter password to play: ".encode())
    password = conn.recv(1024).decode().strip()

    if password != SERVER_PASSWORD:
        conn.send("Incorrect password. Connection closing.\n".encode())
        conn.close()
        return
    
    conn.send("Password accepted.\n".encode())

    conn.send("Do you want a bot to play the game? (yes/no): ".encode())
    response = conn.recv(1024)
    if not response:
        conn.close()
        return
    bot_play = response.decode().strip().lower() == 'yes'

    if bot_play:
        name = "Bot"
    else:
        conn.send("Enter your name: ".encode())
        name = conn.recv(1024).decode().strip()

    conn.send("Choose difficulty: Easy, Medium, Hard: ".encode())
    difficulty = conn.recv(1024).decode().strip().lower()

    number_to_guess = generate_number(difficulty)
    if number_to_guess is None:
        conn.send("Invalid difficulty!\n".encode())
        conn.close()
        return

    if difficulty == 'easy':
        min_guess, max_guess = 1, 50
    elif difficulty == 'medium':
        min_guess, max_guess = 1, 100
    elif difficulty == 'hard':
        min_guess, max_guess = 1, 500


    tries = 0

    try:
        while True:
            if bot_play:
                guess = random.randint(min_guess, max_guess)
                conn.send(f"Bot guesses: {guess}\n".encode())
            else:
                conn.send("Enter your guess: ".encode())
                guess_input = conn.recv(1024).decode().strip()
                if not guess_input.isdigit():
                    conn.send("Please enter a valid number!\n".encode())
                    continue
                guess = int(guess_input)

            tries += 1

            if guess == number_to_guess:
                conn.send(f"Congratulations! You've guessed the number in {tries} tries!\n".encode())
                if tries <= 5:
                    rating = "Excellent"
                elif tries <= 20:
                    rating = "Very Good"
                else:
                    rating = "Good/Fair"
                conn.send(f"Performance Rating: {rating}\n".encode())
                break
            elif guess < number_to_guess:
                response = "Try higher!"
                if bot_play:
                    min_guess = guess + 1
            else:
                response = "Try lower!"
                if bot_play:
                    max_guess = guess - 1
            if not bot_play:
                conn.send(f"{response}\n".encode())


    except (ConnectionResetError, ConnectionAbortedError):
        print("Client disconnected unexpectedly.")

    conn.send(f"The correct number was: {number_to_guess}\n".encode())

    leaderboard = load_leaderboard()
    update_leaderboard(leaderboard, name, tries)
    save_leaderboard(leaderboard)

    conn.close()


def main():
    HOST = '127.0.0.1'
    PORT = 8888

    leaderboard = load_leaderboard()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        print(f"Server started, listening on {PORT}")

        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            handle_client(conn)

if __name__ == "__main__":
    main()
