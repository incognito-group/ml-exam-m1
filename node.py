class Node:
    X = 1
    O = -1
    
    def __init__(self):
        self.etat = [0] * 9
        self.tour = self.X
        self.best = None
        self.evaluation = 0
        self.x_wins = 0
        self.is_draw = 0
    
    @staticmethod
    def get_char(state):
        if state == Node.X:
            return "X"
        elif state == Node.O:
            return "O"
        else:
            return " "
    
    def __str__(self):
        temp = ""
        for i in range(len(self.etat)):
            temp += "|" + self.get_char(self.etat[i])
            if i % 3 == 2:
                temp += "|\n"
        return temp
    
    def to_string_with_indent(self, indent):
        spaces = "\t" * indent
        temp = spaces
        for i in range(len(self.etat)):
            temp += "|" + self.get_char(self.etat[i])
            if i % 3 == 2:
                temp += "|\n" + spaces
        return temp
    
    def play(self, position):
        self.etat[position] = self.tour
        self.tour = -self.tour
    
    def copier(self):
        copie = Node()
        for i in range(len(self.etat)):
            copie.etat[i] = self.etat[i]
        copie.x_wins = self.x_wins
        copie.is_draw = self.is_draw
        copie.tour = self.tour
        copie.evaluation = self.evaluation
        return copie
    
    def to_csv_row(self):
        """Convert board state to CSV row format according to specification"""
        row = []
        # Cell features for X (c0_x, c1_x, ..., c8_x)
        for i in range(9):
            row.append(1 if self.etat[i] == Node.X else 0)
        # Cell features for O (c0_o, c1_o, ..., c8_o)
        for i in range(9):
            row.append(1 if self.etat[i] == Node.O else 0)
        # Targets: x_wins and is_draw
        row.append(self.x_wins)
        row.append(self.is_draw)
        return row
    
    @staticmethod
    def csv_header():
        """Return CSV header row according to specification"""
        headers = []
        # X cells
        for i in range(9):
            headers.append(f"c{i}_x")
        # O cells
        for i in range(9):
            headers.append(f"c{i}_o")
        # Targets
        headers.extend(["x_wins", "is_draw"])
        return headers
    
    def get_succ(self):
        succ = []
        for i in range(len(self.etat)):
            if self.etat[i] == 0:  # case vide
                fils = self.copier()
                fils.play(i)
                succ.append(fils)
        return succ
    
    def eval_heuristique(self, joueur):
        # lignes horizontales
        for i in range(0, 9, 3):
            if self.etat[i] == self.etat[i+1] == self.etat[i+2] and self.etat[i] != 0:
                return self.etat[i] * joueur * 100
        
        # lignes verticales
        for i in range(3):
            if self.etat[i] == self.etat[i+3] == self.etat[i+6] and self.etat[i] != 0:
                return self.etat[i] * joueur * 100
        
        # diagonales
        if self.etat[0] == self.etat[4] == self.etat[8] and self.etat[0] != 0:
            return self.etat[0] * joueur * 100
        if self.etat[2] == self.etat[4] == self.etat[6] and self.etat[2] != 0:
            return self.etat[2] * joueur * 100
        return 0
    
    def is_full(self):
        for i in range(len(self.etat)):
            if self.etat[i] == 0:
                return False
        return True
    
    def is_terminal(self):
        return self.eval_heuristique(1) != 0 or self.is_full()
    
    @staticmethod
    def print_tree(nd, prof):
        Node._do_print_tree(nd, prof, prof)
    
    @staticmethod
    def _do_print_tree(nd, prof, max_indent):
        print(nd.to_string_with_indent(max_indent - prof), end="")
        if prof > 0:
            for fils in nd.get_succ():
                Node._do_print_tree(fils, prof - 1, max_indent)
    
    @staticmethod
    def minimax(nd, prof, joueur):
        if prof == 0 or nd.is_terminal():
            return nd.eval_heuristique(joueur)
        
        succ = nd.get_succ()
        nd.best = None
        
        if nd.tour == joueur:  # maximizing player
            best_value = float('-inf')
            for fils in succ:
                val = Node.minimax(fils, prof - 1, joueur)
                if val > best_value:
                    best_value = val
                    nd.best = fils
        else:  # minimizing player
            best_value = float('inf')
            for fils in succ:
                val = Node.minimax(fils, prof - 1, joueur)
                if val < best_value:
                    nd.best = fils
                    best_value = val
        
        return best_value
    
    @staticmethod
    def minimax_with_data(nd, prof, joueur, data_list):
        """Minimax that also collects game states and evaluations only for X's turn"""
        if prof == 0 or nd.is_terminal():
            eval_val = nd.eval_heuristique(joueur)
            nd.evaluation = eval_val
            
            # Determine outcomes based on evaluation
            if eval_val > 0:  # X wins
                nd.x_wins = 1
                nd.is_draw = 0
            elif eval_val == 0:  # Draw
                nd.x_wins = 0
                nd.is_draw = 1
            else:  # O wins
                nd.x_wins = 0
                nd.is_draw = 0
            
            return eval_val
        
        succ = nd.get_succ()
        nd.best = None
        
        if nd.tour == joueur:  # maximizing player
            best_value = float('-inf')
            for fils in succ:
                val = Node.minimax_with_data(fils, prof - 1, joueur, data_list)
                if val > best_value:
                    best_value = val
                    nd.best = fils
        else:  # minimizing player
            best_value = float('inf')
            for fils in succ:
                val = Node.minimax_with_data(fils, prof - 1, joueur, data_list)
                if val < best_value:
                    nd.best = fils
                    best_value = val
        
        nd.evaluation = best_value
        
        # Determine outcomes
        if best_value > 0:  # X wins
            nd.x_wins = 1
            nd.is_draw = 0
        elif best_value == 0:  # Draw
            nd.x_wins = 0
            nd.is_draw = 1
        else:  # O wins
            nd.x_wins = 0
            nd.is_draw = 0
        
        # Only add to dataset if it's X's turn
        if nd.tour == Node.X:
            data_list.append(nd.to_csv_row())
        
        return best_value
