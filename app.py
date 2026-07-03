import random
import tkinter as tk

WORDS = ["AMIGO", "CASA", "LIVRO", "CHEIO", "MUNDO", "BRAVO", "FORTE", "SONHO", "FELIZ", "AZUL"]
ATTEMPTS = 6

COLOR_GREEN = "#6aaa64"
COLOR_YELLOW = "#c9b458"
COLOR_GRAY = "#787c7e"
COLOR_EMPTY = "#d3d6da"
COLOR_TEXT = "#ffffff"


def get_feedback(guess, target):
    guess = guess.upper()
    target = target.upper()
    feedback = [COLOR_GRAY] * len(guess)
    target_counts = {}

    for ch in target:
        target_counts[ch] = target_counts.get(ch, 0) + 1

    for i, ch in enumerate(guess):
        if ch == target[i]:
            feedback[i] = COLOR_GREEN
            target_counts[ch] -= 1

    for i, ch in enumerate(guess):
        if feedback[i] == COLOR_GRAY and target_counts.get(ch, 0) > 0:
            feedback[i] = COLOR_YELLOW
            target_counts[ch] -= 1

    return feedback


class WordGameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Jogo da Palavra Misteriosa")
        self.resizable(False, False)

        self.mode_var = tk.StringVar(value="solo")
        self.target = random.choice(WORDS)
        self.word_length = len(self.target)
        self.attempts = {1: 0, 2: 0}
        self.player_turn = 1
        self.grid_labels = {1: [], 2: []}
        self._build_interface()

    def _create_scrollable_board(self, parent, player):
        frame = tk.LabelFrame(parent, text=f"Jogador {player}", padx=5, pady=5)
        canvas = tk.Canvas(frame, width=self.word_length * 50, height=320)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        board_container = tk.Frame(canvas)
        canvas.create_window((0, 0), window=board_container, anchor="nw")

        def update_scroll_region(event, canvas=canvas):
            canvas.configure(scrollregion=canvas.bbox("all"))

        board_container.bind("<Configure>", update_scroll_region)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        row_labels = []
        for r in range(ATTEMPTS):
            row = []
            for c in range(self.word_length):
                label = tk.Label(
                    board_container,
                    text=" ",
                    width=4,
                    height=2,
                    bg=COLOR_EMPTY,
                    fg="black",
                    font=("Helvetica", 12, "bold"),
                    relief="solid",
                    borderwidth=1,
                )
                label.grid(row=r, column=c, padx=2, pady=2)
                row.append(label)
            row_labels.append(row)

        return frame, row_labels

    def _build_interface(self):
        title = tk.Label(self, text="Jogo da Palavra Misteriosa", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(10, 5))

        mode_frame = tk.Frame(self)
        mode_frame.grid(row=0, column=3, padx=(5, 10))
        tk.Radiobutton(mode_frame, text="Solo", variable=self.mode_var, value="solo", command=self._reset_game).pack(anchor="w")
        tk.Radiobutton(mode_frame, text="Duelo", variable=self.mode_var, value="duelo", command=self._reset_game).pack(anchor="w")

        instruction = tk.Label(
            self,
            text=f"Tente descobrir a palavra de {self.word_length} letras. Use a entrada abaixo e pressione Enviar.",
            font=("Helvetica", 10),
            wraplength=420,
            justify="left",
        )
        instruction.grid(row=1, column=0, columnspan=4, padx=10)

        grid_frame = tk.Frame(self)
        grid_frame.grid(row=2, column=0, columnspan=4, pady=(10, 10), padx=10)

        for player in (1, 2):
            frame, labels = self._create_scrollable_board(grid_frame, player)
            frame.grid(row=0, column=player - 1, padx=5)
            self.grid_labels[player] = labels
            if player == 2:
                self.player2_frame = frame

        self._update_mode_display()

        self.entry = tk.Entry(self, font=("Helvetica", 14), width=12, justify="center")
        self.entry.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 10))
        self.entry.bind("<Return>", lambda event: self.submit_guess())

        send_button = tk.Button(self, text="Enviar", command=self.submit_guess, font=("Helvetica", 12))
        send_button.grid(row=3, column=2, columnspan=2, padx=10, pady=(0, 10), sticky="we")

        self.status = tk.Label(self, text="", font=("Helvetica", 11), fg="black")
        self.status.grid(row=4, column=0, columnspan=4, pady=(0, 10))

        self.turn_label = tk.Label(self, text="", font=("Helvetica", 11, "bold"), fg="black")
        self.turn_label.grid(row=5, column=0, columnspan=4, pady=(0, 10))
        self._update_turn_label()

    def _update_mode_display(self):
        if self.mode_var.get() == "solo":
            self.player2_frame.grid_remove()
        else:
            self.player2_frame.grid()

    def _reset_game(self):
        self.target = random.choice(WORDS)
        self.word_length = len(self.target)
        self.attempts = {1: 0, 2: 0}
        self.player_turn = 1
        for player in (1, 2):
            for r in range(ATTEMPTS):
                for c in range(self.word_length):
                    lbl = self.grid_labels[player][r][c]
                    lbl.configure(text=" ", bg=COLOR_EMPTY, fg="black")
        self.status.configure(text="")
        self.entry.configure(state="normal")
        self._update_turn_label()
        self._update_mode_display()

    def _end_game(self, message):
        self.status.configure(text=message)
        self.entry.configure(state="disabled")
        self.after(2000, self._reset_game)

    def submit_guess(self):
        player = self.player_turn if self.mode_var.get() == "duelo" else 1
        if self.attempts[player] >= ATTEMPTS:
            self.status.configure(text=f"Jogador {player} não tem mais tentativas.")
            return

        guess = self.entry.get().strip().upper()
        if len(guess) != self.word_length:
            self.status.configure(text=f"A palavra deve ter {self.word_length} letras.")
            return

        self.entry.delete(0, tk.END)
        feedback = get_feedback(guess, self.target)

        for idx, ch in enumerate(guess):
            label = self.grid_labels[player][self.attempts[player]][idx]
            label.configure(text=ch, bg=feedback[idx], fg=COLOR_TEXT)

        if guess == self.target:
            if self.mode_var.get() == "duelo":
                self._end_game(f"Parabéns! Jogador {player} acertou a palavra: {self.target}")
            else:
                self._end_game(f"Parabéns! Você acertou a palavra: {self.target}")
            return

        self.attempts[player] += 1

        if self.mode_var.get() == "duelo":
            other = 2 if player == 1 else 1
            if self.attempts[other] < ATTEMPTS:
                self.player_turn = other
            elif self.attempts[player] < ATTEMPTS:
                self.player_turn = player
            self._update_turn_label()

            if self.attempts[1] >= ATTEMPTS and self.attempts[2] >= ATTEMPTS:
                self._end_game(f"Todas as tentativas acabaram. A palavra correta era: {self.target}")
                return
            self.status.configure(
                text=f"Tentativa {self.attempts[self.player_turn] + 1}/{ATTEMPTS} do Jogador {self.player_turn}."
            )
            return

        if self.attempts[player] >= ATTEMPTS:
            self._end_game(f"Suas tentativas acabaram. A palavra correta era: {self.target}")
            return

        self.status.configure(text=f"Tentativa {self.attempts[player] + 1}/{ATTEMPTS}.")

    def _update_turn_label(self):
        if self.mode_var.get() == "duelo":
            self.turn_label.configure(text=f"Turno: Jogador {self.player_turn}")
        else:
            self.turn_label.configure(text="")


def main():
    app = WordGameApp()
    app.mainloop()


if __name__ == "__main__":
    main()
