import tkinter as tk
from tkinter import messagebox
import random
import time

# Größe des Spielfelds (10x10)
BOARD_SIZE = 10

# Schiffsgrößen gemäß klassischem Regelwerk
SHIP_SIZES = [5, 4, 3, 3, 2]


class StartScreen:
    """
    Startbildschirm – wird beim Programmstart angezeigt.
    Der Spieler wählt zwischen 'Gegen CPU' und 'Gegen Spieler 2'.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Schiffe versenken – Startmenü")
        self.root.resizable(False, False)

        # Titel
        tk.Label(
            root,
            text="⚓ Schiffe versenken",
            font=("Arial", 22, "bold")
        ).pack(pady=30)

        tk.Label(
            root,
            text="Wähle einen Spielmodus:",
            font=("Arial", 13)
        ).pack(pady=10)

        # Button: Gegen CPU spielen
        tk.Button(
            root,
            text="🤖  Gegen CPU spielen",
            font=("Arial", 13),
            width=22,
            bg="#4a90d9",
            fg="white",
            command=self.start_vs_cpu
        ).pack(pady=8)

        # Button: Gegen zweiten Spieler spielen
        tk.Button(
            root,
            text="👥  Gegen Spieler 2 spielen",
            font=("Arial", 13),
            width=22,
            bg="#2ecc71",
            fg="white",
            command=self.start_vs_player
        ).pack(pady=8)

        # Button: Beenden
        tk.Button(
            root,
            text="❌  Beenden",
            font=("Arial", 11),
            width=22,
            command=root.destroy
        ).pack(pady=20)

    def start_vs_cpu(self):
        """Startet das Spiel im CPU-Modus."""
        self.root.destroy()
        root = tk.Tk()
        BattleshipGame(root, vs_cpu=True)
        root.mainloop()

    def start_vs_player(self):
        """Startet das Spiel im Zwei-Spieler-Modus."""
        self.root.destroy()
        root = tk.Tk()
        BattleshipGame(root, vs_cpu=False)
        root.mainloop()


class BattleshipGame:
    """
    Hauptklasse des Spiels.
    Verwaltet zwei getrennte Spielfelder, die Spiellogik und die grafische Oberfläche.
    """

    def __init__(self, root, vs_cpu=False):
        self.root = root
        self.root.title("Schiffe versenken")
        self.root.resizable(False, False)

        # Spielmodus speichern (True = gegen CPU, False = zwei Spieler)
        self.vs_cpu = vs_cpu

        # Aktueller Spieler (1 oder 2)
        self.current_player = 1

        # Spielfelder: boards[1] = Schiffe von Spieler 1, boards[2] = Schiffe von Spieler 2
        self.boards = {
            1: self.create_board(),
            2: self.create_board()
        }

        # Trefferkarten: Was hat Spieler X beim Gegner bereits beschossen?
        # " " = unbekannt, "X" = Treffer, "O" = Fehlschuss
        self.shots = {
            1: self.create_board(),  # Schüsse von Spieler 1 auf Spieler 2
            2: self.create_board()   # Schüsse von Spieler 2 auf Spieler 1
        }

        # Schiffe auf beiden Feldern zufällig platzieren
        self.place_all_ships(1)
        self.place_all_ships(2)

        # Grafische Oberfläche aufbauen
        self.setup_ui()
        self.update_status()

    # ─────────────────────────────────────────────
    # Spielfeld-Logik
    # ─────────────────────────────────────────────

    def create_board(self):
        """Erstellt ein leeres 10x10 Spielfeld als verschachtelte Liste."""
        return [[" " for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def place_all_ships(self, player):
        """
        Platziert alle Schiffe aus SHIP_SIZES zufällig auf dem Spielfeld
        des angegebenen Spielers. Wiederholt, bis eine überschneidungsfreie
        Position gefunden wurde.
        """
        for ship_size in SHIP_SIZES:
            placed = False
            while not placed:
                horizontal = random.choice([True, False])

                if horizontal:
                    row = random.randint(0, BOARD_SIZE - 1)
                    col = random.randint(0, BOARD_SIZE - ship_size)
                    positions = [(row, col + i) for i in range(ship_size)]
                else:
                    row = random.randint(0, BOARD_SIZE - ship_size)
                    col = random.randint(0, BOARD_SIZE - 1)
                    positions = [(row + i, col) for i in range(ship_size)]

                # Nur platzieren wenn alle Felder frei sind
                if self.can_place_ship(player, positions):
                    for r, c in positions:
                        self.boards[player][r][c] = "S"
                    placed = True

    def can_place_ship(self, player, positions):
        """Gibt True zurück wenn alle gewünschten Felder noch frei sind."""
        for r, c in positions:
            if self.boards[player][r][c] == "S":
                return False
        return True

    # ─────────────────────────────────────────────
    # Grafische Oberfläche
    # ─────────────────────────────────────────────

    def setup_ui(self):
        """
        Baut die gesamte GUI auf:
        - Statusleiste oben
        - Zwei nebeneinanderliegende Spielfelder
        - Neustart-Button unten
        """

        # ── Statusbereich ──
        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 14, "bold")
        )
        self.status_label.pack(pady=8)

        self.info_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 11),
            fg="#333333"
        )
        self.info_label.pack(pady=3)

        # ── Spielfeld-Container (beide Felder nebeneinander) ──
        fields_frame = tk.Frame(self.root)
        fields_frame.pack(padx=15, pady=10)

        # Linkes Feld: Eigenes Feld von Spieler 1 (zeigt eigene Schiffe)
        left_frame = tk.Frame(fields_frame, bd=2, relief="groove")
        left_frame.grid(row=0, column=0, padx=15)

        self.left_title = tk.Label(
            left_frame,
            text="🚢 Dein Feld (Spieler 1)",
            font=("Arial", 11, "bold"),
            fg="#2c3e50"
        )
        self.left_title.pack(pady=4)

        # Rechtes Feld: Gegnerfeld (Schüsse des aktuellen Spielers)
        right_frame = tk.Frame(fields_frame, bd=2, relief="groove")
        right_frame.grid(row=0, column=1, padx=15)

        self.right_title = tk.Label(
            right_frame,
            text="🎯 Gegnerfeld",
            font=("Arial", 11, "bold"),
            fg="#c0392b"
        )
        self.right_title.pack(pady=4)

        # Spielfeld-Grids zeichnen
        self.left_grid_frame = tk.Frame(left_frame)
        self.left_grid_frame.pack(padx=5, pady=5)

        self.right_grid_frame = tk.Frame(right_frame)
        self.right_grid_frame.pack(padx=5, pady=5)

        # Buttons für beide Felder erstellen
        # own_buttons = eigenes Feld (nur Anzeige, nicht klickbar)
        # enemy_buttons = Gegnerfeld (hier wird geklickt um zu schießen)
        self.own_buttons = self.build_grid(self.left_grid_frame, clickable=False)
        self.enemy_buttons = self.build_grid(self.right_grid_frame, clickable=True)

        # ── Neustart-Button ──
        tk.Button(
            self.root,
            text="🔄 Neues Spiel",
            command=self.restart_game,
            font=("Arial", 11),
            width=18
        ).pack(pady=12)

        # Eigenes Feld von Spieler 1 sofort mit Schiffen befüllen
        self.refresh_own_board()

    def build_grid(self, parent, clickable):
        """
        Erstellt ein 10x10 Button-Grid mit Achsenbeschriftung.
        clickable=True → Buttons lösen shoot() aus
        clickable=False → Buttons dienen nur zur Anzeige
        """
        buttons = []

        # Spaltenzahlen (1–10) oben
        for i in range(BOARD_SIZE):
            tk.Label(parent, text=str(i + 1), font=("Arial", 9, "bold"), width=3).grid(row=0, column=i + 1)

        for r in range(BOARD_SIZE):
            # Zeilenbuchstaben (A–J) links
            tk.Label(parent, text=chr(65 + r), font=("Arial", 9, "bold")).grid(row=r + 1, column=0)

            row_buttons = []
            for c in range(BOARD_SIZE):
                if clickable:
                    # Schuss-Button: Klick löst shoot() für dieses Feld aus
                    btn = tk.Button(
                        parent,
                        text="",
                        width=2,
                        height=1,
                        font=("Arial", 11, "bold"),
                        command=lambda row=r, col=c: self.shoot(row, col)
                    )
                else:
                    # Anzeigebutton: Nicht klickbar, zeigt nur eigene Schiffe
                    btn = tk.Button(
                        parent,
                        text="",
                        width=2,
                        height=1,
                        font=("Arial", 11, "bold"),
                        state="disabled",
                        disabledforeground="black"
                    )
                btn.grid(row=r + 1, column=c + 1, padx=1, pady=1)
                row_buttons.append(btn)
            buttons.append(row_buttons)

        return buttons

    def refresh_own_board(self):
        """
        Aktualisiert das linke (eigene) Spielfeld des aktuellen Spielers.
        Schiffe werden als blaue Felder angezeigt, leere Felder grau.
        """
        player = self.current_player
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell = self.boards[player][r][c]
                shot = self.shots[2 if player == 1 else 1][r][c]

                if shot == "X":
                    # Eigenes Schiff wurde vom Gegner getroffen → rot
                    self.own_buttons[r][c].config(text="X", bg="red")
                elif shot == "O":
                    # Gegner hat daneben geschossen → hellblau
                    self.own_buttons[r][c].config(text="O", bg="lightblue")
                elif cell == "S":
                    # Eigenes Schiff, noch ungetroffen → blaugrau
                    self.own_buttons[r][c].config(text="", bg="#5b8fa8")
                else:
                    # Leeres Feld → Standardfarbe
                    self.own_buttons[r][c].config(text="", bg="SystemButtonFace")

    def refresh_enemy_board(self):
        """
        Aktualisiert das rechte (Gegner-)Spielfeld mit den bisherigen Schüssen
        des aktuellen Spielers. Unbekannte Felder bleiben leer.
        """
        player = self.current_player
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                shot = self.shots[player][r][c]

                if shot == "X":
                    self.enemy_buttons[r][c].config(text="X", bg="red", fg="white")
                elif shot == "O":
                    self.enemy_buttons[r][c].config(text="O", bg="lightblue")
                else:
                    # Noch nicht beschossenes Feld
                    self.enemy_buttons[r][c].config(text="", bg="SystemButtonFace", state="normal")

    # ─────────────────────────────────────────────
    # Spiellogik
    # ─────────────────────────────────────────────

    def shoot(self, row, col):
        """
        Verarbeitet einen Schuss des aktuellen Spielers auf (row, col).
        Aktualisiert die Felder, prüft auf Gewinner und wechselt den Spieler.
        """
        opponent = 2 if self.current_player == 1 else 1

        # Bereits beschossenes Feld abweisen
        if self.shots[self.current_player][row][col] != " ":
            messagebox.showinfo("Hinweis", "Dieses Feld wurde bereits beschossen!")
            return

        # Treffer oder Fehlschuss?
        if self.boards[opponent][row][col] == "S":
            self.shots[self.current_player][row][col] = "X"
            self.info_label.config(text=f"💥 Spieler {self.current_player} hat getroffen!")
        else:
            self.shots[self.current_player][row][col] = "O"
            self.info_label.config(text=f"🌊 Spieler {self.current_player} hat verfehlt!")

        # Gegnerfeld visuell aktualisieren
        self.refresh_enemy_board()

        # Gewinner prüfen
        if self.check_winner(opponent):
            name = "CPU" if (self.vs_cpu and self.current_player == 2) else f"Spieler {self.current_player}"
            messagebox.showinfo("🎉 Spielende", f"{name} hat gewonnen!\nAlle Schiffe versenkt!")
            self.disable_all_buttons()
            return

        # Spieler wechseln
        self.current_player = opponent
        self.update_status()
        self.refresh_own_board()
        self.refresh_enemy_board()

        # Falls CPU dran ist, automatisch schießen lassen
        if self.vs_cpu and self.current_player == 2:
            self.root.after(800, self.cpu_shoot)  # 800ms Verzögerung für realistisches Gefühl

    def cpu_shoot(self):
        """
        CPU-Zug: Wählt zufällig ein noch nicht beschossenes Feld und schießt darauf.
        Nutzt dieselbe shoot()-Methode wie ein menschlicher Spieler.
        """
        available = [
            (r, c)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if self.shots[2][r][c] == " "  # Noch nicht beschossene Felder
        ]

        if available:
            row, col = random.choice(available)  # Zufälliges Feld auswählen
            self.shoot(row, col)

    def check_winner(self, player):
        """
        Prüft ob alle Schiffe von 'player' versenkt wurden.
        Gibt True zurück wenn der Gegner gewonnen hat.
        """
        shooter = 2 if player == 1 else 1
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                # Gibt es noch ein Schiffsfeld, das nicht getroffen wurde?
                if self.boards[player][r][c] == "S" and self.shots[shooter][r][c] != "X":
                    return False
        return True

    def update_status(self):
        """
        Aktualisiert Statuslabel und Feldüberschriften je nach aktuellem Spieler.
        Im CPU-Modus wird 'Spieler 2' als 'CPU' angezeigt.
        """
        if self.vs_cpu and self.current_player == 2:
            name = "CPU"
        else:
            name = f"Spieler {self.current_player}"

        self.status_label.config(text=f"🎯 {name} ist dran")

        # Feldtitel anpassen – zeigt immer das eigene und das Gegnerfeld korrekt an
        opponent = 2 if self.current_player == 1 else 1
        opponent_name = "CPU" if (self.vs_cpu and opponent == 2) else f"Spieler {opponent}"

        self.left_title.config(text=f"🚢 Dein Feld (Spieler {self.current_player})")
        self.right_title.config(text=f"🎯 Gegnerfeld ({opponent_name})")

    def disable_all_buttons(self):
        """Deaktiviert alle Schuss-Buttons nach Spielende."""
        for row in self.enemy_buttons:
            for btn in row:
                btn.config(state="disabled")

    def restart_game(self):
        """
        Setzt das Spiel vollständig zurück:
        - Neue leere Spielfelder
        - Neue Schiffsplatzierung
        - Spieler 1 beginnt wieder
        - Alle Buttons zurückgesetzt
        """
        self.current_player = 1
        self.boards = {1: self.create_board(), 2: self.create_board()}
        self.shots = {1: self.create_board(), 2: self.create_board()}

        self.place_all_ships(1)
        self.place_all_ships(2)

        # Alle Buttons visuell zurücksetzen
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                self.own_buttons[r][c].config(text="", bg="SystemButtonFace")
                self.enemy_buttons[r][c].config(text="", bg="SystemButtonFace", state="normal")

        self.refresh_own_board()
        self.update_status()
        self.info_label.config(text="Klicke auf ein Feld um zu schießen.")


# ─────────────────────────────────────────────
# Programmeinstieg
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    StartScreen(root)   # Zuerst den Startbildschirm anzeigen
    root.mainloop()