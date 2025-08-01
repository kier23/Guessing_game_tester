import socket

def main():
    HOST = '127.0.0.1'
    PORT = 8888

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        
        print(s.recv(1024).decode())

        
        print(s.recv(1024).decode(), end='')  
        password = input("> ")
        s.send(password.encode())

        
        response = s.recv(1024).decode()
        print(response)
        if "Incorrect password" in response:
            return  

        
        print(s.recv(1024).decode(), end='')
        bot_play = input("> ").lower()
        s.send(bot_play.encode())

        if bot_play != "yes":
            print(s.recv(1024).decode(), end='')
            name = input("> ")
            s.send(name.encode())

        
        print(s.recv(1024).decode(), end='')
        difficulty = input("> ")
        s.send(difficulty.encode())

        while True:
            response = s.recv(1024).decode()
            print(response, end='')

            if "Congratulations" in response or "Incorrect password" in response:
                break

            if "Enter your guess:" in response:
                guess = input("> ")
                s.send(guess.encode())

        
        final_message = s.recv(1024).decode()
        print(final_message)

if __name__ == "__main__":
    main()
