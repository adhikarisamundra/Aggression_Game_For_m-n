import random
import time
import sys

class AggressionGame:
    def __init__(self):
        self.rows = 0
        self.cols = 0
        self.total_troops = 0
        self.grid = {} 
        self.p1_troops_remaining = 0
        self.p2_troops_remaining = 0
        self.current_turn = 1 
        self.ai_opponent = None 
        self.player_names = {1: "You", 2: "Player 2"}

    def setup_game(self):
        print("\n" + "="*40)
        print("       WELCOME TO AGGRESSION")
        print("="*40)
        print("Based on the original game by MathPickle.")
        print("For more info, visit: https://mathpickle.com/project/a-little-bit-of-aggression/")
        print("-" * 40)
        
        # 1. Grid Dimensions
        print("\n--- Step 1: Set Up the Board ---")
        while True:
            try:
                r_in = input("How many rows should the board have? (Standard is 5): ")
                r = int(r_in) if r_in.strip() else 5
                
                c_in = input("How many columns? (Standard is 5): ")
                c = int(c_in) if c_in.strip() else 5

                if 2 <= r <= 8 and 2 <= c <= 8:
                    self.rows, self.cols = r, c
                    break
                print(" -> Please keep the size between 2x2 and 8x8 to keep the game fast.")
            except ValueError:
                print(" -> That didn't look like a number. Please try again.")

        # 2. Troop Count 
        default_troops = self.rows * self.cols
        print(f"\n--- Step 2: Troop Limits ---")
        print(f"Normally, you would play with {default_troops} troops each.")
        
        while True:
            choice = input(f"Do you want to change this number? (y/n): ").lower()
            if choice == 'n':
                self.total_troops = default_troops
                break
            elif choice == 'y':
                try:
                    max_troops = self.rows * self.cols * 3
                    t = int(input(f"Enter total troops per player [1-{max_troops}]: "))
                    if 1 <= t <= max_troops:
                        self.total_troops = t
                        break
                    print(f" -> Let's keep it reasonable (between 1 and {max_troops}).")
                except ValueError:
                    print(" -> Please enter a valid number.")
            else:
                print(" -> Please type 'y' for yes or 'n' for no.")

        self.p1_troops_remaining = self.total_troops
        self.p2_troops_remaining = self.total_troops

        # 3. Game Mode
        print("\n--- Step 3: Choose Your Opponent ---")
        print("1. Play against a Human (Hotseat)")
        print("2. Play against the Computer (AI)")
        
        while True:
            mode = input("Type 1 or 2: ")
            if mode == '1':
                self.ai_opponent = None
                self.player_names[2] = "Player 2"
                break
            elif mode == '2':
                self.player_names[2] = "Computer"
                self.choose_ai_difficulty()
                break

        # Initialize Grid
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[(r, c)] = None 

        self.play_placement_phase()

    def choose_ai_difficulty(self):
        print("\n--- Step 4: AI Difficulty ---")
        print("Which computer personality do you want to play against?")
        print("1. Weak AI: Plays randomly. Good for learning the rules.")
        print("2. Strategic AI: Likes to group up. Attacks big stacks.")
        print("3. Smart AI: Calculates threats. Attacks whatever endangers it most.")
        
        while True:
            choice = input("Type 1, 2, or 3: ")
            if choice == '1':
                self.ai_opponent = "Weak"
                break
            elif choice == '2':
                self.ai_opponent = "Strategic"
                break
            elif choice == '3':
                self.ai_opponent = "Smart"
                break

    def print_grid(self):
        """Prints a clean, easy-to-read board."""
        print(f"\n   [ Board State ]")
        # Header numbers
        print("     ", end="")
        for c in range(self.cols):
            print(f" {c}   ", end="")
        print()
        
        print("   " + "-----" * self.cols)
        for r in range(self.rows):
            print(f" {r} |", end="")
            for c in range(self.cols):
                cell = self.grid.get((r, c))
                if cell is None:
                    print("  .  ", end="")
                else:
                    # Determine symbol
                    owner = "P1" if cell['player'] == 1 else "P2"
                    if self.player_names[2] == "Computer" and cell['player'] == 2:
                        owner = "AI"
                    
                    count = cell['count']
                    # Add colors if supported, else just text
                    color = "\033[94m" if cell['player'] == 1 else "\033[91m"
                    reset = "\033[0m"
                    print(f"{color}{owner}:{count:<2}{reset}", end="") 
            print("|")
        print("   " + "-----" * self.cols)

    # --- PLACEMENT PHASE ---
    def play_placement_phase(self):
        print("\n" + "="*40)
        print("       PHASE 1: PLACEMENT")
        print("="*40)
        print("GOAL: Put your troops on the board.")
        print("HOW:  Pick a row and column. You can dump many troops on one spot.")
        print("NOTE: We keep going until everyone is out of troops.")
        
        # Coin toss
        if random.choice([True, False]):
            self.current_turn = 1
        else:
            self.current_turn = 2
            
        print(f"\nResult: {self.player_names[self.current_turn]} goes first!")

        while self.p1_troops_remaining > 0 or self.p2_troops_remaining > 0:
            self.print_grid()
            current_troops = self.p1_troops_remaining if self.current_turn == 1 else self.p2_troops_remaining
            
            if current_troops <= 0:
                print(f"\n-> {self.player_names[self.current_turn]} has no troops left. Skipping turn.")
                self.switch_turn()
                continue

            print(f"\n--- {self.player_names[self.current_turn]}'s Turn ---")
            print(f"Troops in hand: {current_troops}")

            if self.is_ai_turn():
                move = self.get_ai_placement_move()
                print(f"Computer places {move['amount']} troops at Row {move['r']}, Col {move['c']}.")
                self.execute_placement(move['r'], move['c'], move['amount'])
            else:
                self.get_human_placement_move(current_troops)
            
            self.switch_turn()

        print("\nAll troops placed! Get ready for battle...")
        time.sleep(1.5)
        self.play_attack_phase()

    def get_human_placement_move(self, max_troops):
        while True:
            try:
                txt = input("Enter 'row col amount' (e.g., 2 3 5): ")
                parts = list(map(int, txt.split()))
                if len(parts) != 3:
                    print(" -> Please type 3 numbers separated by spaces.")
                    continue
                r, c, amount = parts
                
                # Validation
                if not (0 <= r < self.rows and 0 <= c < self.cols):
                    print(f" -> Coordinates must be between 0 and {self.rows-1}.")
                    continue
                if amount < 1 or amount > max_troops:
                    print(f" -> You only have {max_troops} troops left.")
                    continue
                
                cell = self.grid.get((r, c))
                # Can only place on empty spots or own territory
                if cell is not None and cell['player'] != self.current_turn:
                    print(" -> You can't add troops to your enemy's territory!")
                    continue
                
                self.execute_placement(r, c, amount)
                break
            except ValueError:
                print(" -> Invalid input. Please enter numbers.")

    def execute_placement(self, r, c, amount):
        cell = self.grid.get((r, c))
        if cell is None:
            self.grid[(r, c)] = {'player': self.current_turn, 'count': amount}
        else:
            self.grid[(r, c)]['count'] += amount
            
        if self.current_turn == 1:
            self.p1_troops_remaining -= amount
        else:
            self.p2_troops_remaining -= amount

    # --- ATTACK PHASE ---
    def play_attack_phase(self):
        print("\n" + "="*40)
        print("       PHASE 2: ATTACK")
        print("="*40)
        print("GOAL: Remove enemy territories.")
        print("HOW:  Choose an enemy spot to attack.")
        print("MATH: We sum up ALL your troops sitting next to that spot.")
        print("      If Your Sum > Their Count, you win that spot.")
        
        self.current_turn = 1 
        consecutive_passes = 0

        while True:
            self.print_grid()
            print(f"\n--- {self.player_names[self.current_turn]}'s Turn ---")
            
            if self.is_ai_turn():
                time.sleep(1) 
                target = self.get_ai_attack_move()
                if target is None:
                    print("Computer chooses to PASS.")
                    consecutive_passes += 1
                else:
                    print(f"Computer attacks Row {target[0]}, Col {target[1]}!")
                    self.execute_attack(target[0], target[1])
                    consecutive_passes = 0
            else:
                print("Type coordinates to attack (e.g., '1 2') OR type 'p' to pass.")
                user_in = input("Action: ").strip().lower()
                
                if user_in == 'p':
                    print("You passed.")
                    consecutive_passes += 1
                else:
                    try:
                        coords = list(map(int, user_in.split()))
                        if len(coords) != 2:
                            print(" -> Invalid format. Type 'row col' or 'p'.")
                            continue
                        
                        r, c = coords
                        if self.validate_attack(r, c):
                            self.execute_attack(r, c)
                            consecutive_passes = 0
                        else:
                            continue 
                    except ValueError:
                        print(" -> Invalid input.")
                        continue

            if consecutive_passes >= 2:
                print("\nBoth players passed consecutively. GAME OVER.")
                break
                
            self.switch_turn()
            
        self.determine_winner()

    def validate_attack(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            print(" -> That coordinate is off the board.")
            return False
        
        target_cell = self.grid.get((r, c))
        if target_cell is None:
            print(" -> There is nothing there to attack.")
            return False
        if target_cell['player'] == self.current_turn:
            print(" -> You can't attack yourself!")
            return False
            
        power = self.calculate_attack_power(r, c, self.current_turn)
        print(f" -> Attack Check: Your Surrounding Power ({power}) vs Enemy Defense ({target_cell['count']})")
        
        if power > target_cell['count']:
            return True
        else:
            print(" -> Attack Failed: You don't have enough surrounding power.")
            return False

    def calculate_attack_power(self, target_r, target_c, attacker_id):
        power = 0
        # Check 8 neighbors
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = target_r + dr, target_c + dc
                
                neighbor = self.grid.get((nr, nc))
                if neighbor is not None and neighbor['player'] == attacker_id:
                    power += neighbor['count']
        return power

    def execute_attack(self, r, c):
        print(f" -> SUCCESS! Territory at ({r},{c}) was neutralized.")
        self.grid[(r, c)] = None

    def determine_winner(self):
        p1_area = 0
        p2_area = 0
        for cell in self.grid.values():
            if cell is not None:
                if cell['player'] == 1:
                    p1_area += 1
                else:
                    p2_area += 1
        
        print("\n" + "="*40)
        print("       FINAL SCORE")
        print("="*40)
        print(f"Player 1 Territories: {p1_area}")
        print(f"Player 2 Territories: {p2_area}")
        
        if p1_area > p2_area:
            print("RESULT: Player 1 Wins!")
        elif p2_area > p1_area:
            print("RESULT: Player 2 Wins!")
        else:
            print("RESULT: It's a Tie!")

    # --- AI LOGIC ---
    def is_ai_turn(self):
        return self.current_turn == 2 and self.ai_opponent is not None

    def get_ai_placement_move(self):
        remaining = self.p2_troops_remaining
        
        # WEAK AI: Random
        if self.ai_opponent == "Weak":
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            amt = random.randint(1, min(remaining, 5))
            
            # Retry a few times if invalid
            for _ in range(20):
                cell = self.grid.get((r,c))
                if cell is None or cell['player'] == 2:
                    break
                r = random.randint(0, self.rows - 1)
                c = random.randint(0, self.cols - 1)
            return {'r': r, 'c': c, 'amount': amt}

        # SMART/STRATEGIC
        else:
            best_score = -999
            best_move = (0, 0)
            
            # Simple heuristic: try to place near existing allies
            for r in range(self.rows):
                for c in range(self.cols):
                    cell = self.grid.get((r, c))
                    # Cannot place on enemy
                    if cell is not None and cell['player'] == 1: continue 
                    
                    score = 0
                    friendly_power = self.calculate_attack_power(r, c, 2)
                    score += friendly_power
                    if cell is None: score += 2 
                    score += random.random()
                    
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
            
            amt = min(remaining, random.randint(3, 6))
            return {'r': best_move[0], 'c': best_move[1], 'amount': amt}

    def get_ai_attack_move(self):
        possible_attacks = []
        
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid.get((r, c))
                if cell is not None and cell['player'] == 1:
                    power = self.calculate_attack_power(r, c, 2)
                    if power > cell['count']:
                        possible_attacks.append( {'r':r, 'c':c, 'target_val': cell['count']} )

        if not possible_attacks:
            return None

        if self.ai_opponent == "Weak":
            choice = random.choice(possible_attacks)
            return (choice['r'], choice['c'])

        if self.ai_opponent == "Strategic":
            # Attack biggest stack
            best = max(possible_attacks, key=lambda x: x['target_val'])
            return (best['r'], best['c'])

        if self.ai_opponent == "Smart":
            # Attack enemy that threatens us most
            best = None
            max_val = -1
            
            for att in possible_attacks:
                r, c = att['r'], att['c']
                # Count how many AI units are neighbors to this enemy target
                threat_score = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                         if dr==0 and dc==0: continue
                         nr, nc = r+dr, c+dc
                         friend = self.grid.get((nr,nc))
                         if friend and friend['player'] == 2:
                             threat_score += 1
                
                val = att['target_val'] + (threat_score * 3)
                if val > max_val:
                    max_val = val
                    best = att
            return (best['r'], best['c'])

    def switch_turn(self):
        self.current_turn = 1 if self.current_turn == 2 else 2

# --- SAFETY WRAPPER ---
if __name__ == "__main__":
    try:
        game = AggressionGame()
        game.setup_game()
    except KeyboardInterrupt:
        print("\n\nGame stopped by user (Ctrl+C). Goodbye!")
    except Exception as e:
        print(f"\n\nERROR: The game crashed unexpectedly.")
        print(f"Error details: {e}")
        print("Please report this error.")
        input("Press Enter to close...")
