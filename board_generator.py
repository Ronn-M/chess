
'''This module is responsible generating a chess board grid set and uses functions to create the game ui using the kivy design language
creating a .kv file of the match when the grid and the ui elements are generated and pieced together without errors'''

class GenerateBoard:

    def __init__(self) -> None:
        self.letters: str
        self.numbers: str
        self.player_set: str

        self.letters, self.numbers = 'abcdefgh', '87654321'
        self.grid = [[letter + number for letter in self.letters] for number in self.numbers]
        self.pieces = {
                        'Player2': {
                                    'pieces': 
                                            {
                                            'king'  : 'pieces/king-p2.png',  'queen' : 'pieces/queen-p2.png',
                                            'rook'  : 'pieces/rook-p2.png',  'bishop': 'pieces/bishop-p2.png',
                                            'knight': 'pieces/knight-p2.png', 'pawn' : 'pieces/pawn-p2.png'
                                            }
                                    }, 
                        'Player1': {
                                    'pieces': 
                                            {
                                            'king'  : 'pieces/king-p1.png', 'queen' : 'pieces/queen-p1.png',
                                            'rook'  : 'pieces/rook-p1.png', 'bishop': 'pieces/bishop-p1.png',
                                            'knight': 'pieces/knight-p1.png','pawn' : 'pieces/pawn-p1.png'
                                            }
                                    }
                    }

    '''for readability and functionality, the following function will be modified to better fit game options and user requirements'''   
    def assign_player(self, selectedplayer: int):

        def add_lines_and_tabs(lines: int=0, tabs: int=0):
            tab = '\t'
            newline = '\n'

            if lines == 0 and tabs != 0: return (tab * tabs)
            elif lines != 0 and tabs == 0: return (newline * lines)
            else: return (newline * lines) + (tab * tabs)
        
        player_set = ''
    
        def show_pieces(player: str, x: float, y: float):
            promotions = self.pieces[player]['pieces']
            possible_pieces = list(promotions.keys())[1:][:-1]
            tile_string = []
            for piece in possible_pieces:
                pomortion_pieces = str(f'<{player}Pomortion{piece}>:' + add_lines_and_tabs(1, 1) + 'md_bg_color: "#FFD740" ' + add_lines_and_tabs(1, 1) + 'pos_hint: {"center_x": ' + 
                                       f'{x}' + ', "center_y": ' + f'{y}' + '}' + add_lines_and_tabs(1, 1) + 'size_hint: 0.075, 0.075')
                pomortion_pieces += str(add_lines_and_tabs(1, 1) + f'id: ' + player + piece + add_lines_and_tabs(1, 1) + f'name: "{promotions[piece]}"' + add_lines_and_tabs(1, 1) + 
                                    'on_press: app.promote_pawn(self.name)' + add_lines_and_tabs(1, 1) + 'MDButtonIcon:' + add_lines_and_tabs(1, 2) + f'id: "{promotions[piece]}"' + 
                                    add_lines_and_tabs(1, 2) + f'source: "{promotions[piece]}"' + add_lines_and_tabs(2, 0)) 
                x += 0.085 
                tile_string.append(pomortion_pieces)  
            return tile_string   
        
        size_hint = 'size_hint: 1, 1' + add_lines_and_tabs(1, 0)
        tile_i = str('Square_i:' + add_lines_and_tabs(1, 5)  + 'canvas.before:' + add_lines_and_tabs(1, 6) + 'Color:' + add_lines_and_tabs(1, 7) + 'rgba: get_color_from_hex("#FFFFFF")' + 
                    add_lines_and_tabs(1, 6) + 'Rectangle:' + add_lines_and_tabs(1, 7) + 'pos: (0.5, 0.5)'  + add_lines_and_tabs(1, 7) +  'size: self.size' + add_lines_and_tabs(2, 5) + size_hint)       
        tile_ii = str('Square_ii:' + add_lines_and_tabs(2, 5) + 'canvas.before:' + add_lines_and_tabs(1, 6) + 'Color:' + add_lines_and_tabs(2, 7) + 'rgba: get_color_from_hex("#000000")' + 
                    add_lines_and_tabs(1, 6) + 'Rectangle:' + add_lines_and_tabs(1, 7) + 'pos: (0.5, 0.5)'  + add_lines_and_tabs(1, 7) +  'size: self.size' + add_lines_and_tabs(2, 5) + size_hint)
        PlayerTradedPieceList = str('<PlayerTradedPieceList>:' + add_lines_and_tabs(1, 1) + 'line_color: "#121212"' + add_lines_and_tabs(1, 1) + 'md_bg_color: "#121212"' + add_lines_and_tabs(1, 1) + 
                                'size_hint: 0.075, 0.075' + add_lines_and_tabs(1, 1) + 'min_state_time: 0' + add_lines_and_tabs(1))
        h_oriantation   = add_lines_and_tabs(2, 4) + "orientation: 'horizontal'" + add_lines_and_tabs(1)
    
        __Player1 = 'HorizontalLineP1: ' + h_oriantation 
        __Player2 = 'HorizontalLineP2: ' + h_oriantation
        __Player1pawns = 'HorizontalLineP1p:' + h_oriantation
        __Player2pawns = 'HorizontalLineP2p:' + h_oriantation
        __Player1_promotions = show_pieces('Player1', x=0.3945, y=0.9) 
        __Player2_promotions = show_pieces('Player2', x=0.3945, y=0.1)  
        
        def invert_sequence(piece: str, name: str):
            return str(add_lines_and_tabs(1, 4) + tile_ii  + add_lines_and_tabs(0, 5) + f'id: ' + name + add_lines_and_tabs(1, 5) + f'name: "{name}"' + add_lines_and_tabs(1, 5) + 'on_press:' + add_lines_and_tabs(1, 6) + 
                #'bind: app.movelog()' + add_lines_and_tabs(1, 6) + 
                'app.update_board(self.name)' + add_lines_and_tabs(2, 5) + 'MDButtonIcon:' + add_lines_and_tabs(1, 6) + f'id: {name}_overlay' + 
                add_lines_and_tabs(1, 6) + 'size: "50sp", "50sp"' + add_lines_and_tabs(1, 6) + f'source: ""' + add_lines_and_tabs(1, 6) + 'pos_hint: {"center_x": 0.5, "center_y": 0.5}' + add_lines_and_tabs(2, 5) + 
                'MDButtonIcon:' + add_lines_and_tabs(1, 6) + f'id: {name}_image' + add_lines_and_tabs(1, 6) + 'size: "50sp", "50sp"' + add_lines_and_tabs(1, 6) + f'source: "{piece}"' + add_lines_and_tabs(1, 6) + 
                'pos_hint: {"center_x": 0.5, "center_y": 0.5}' + add_lines_and_tabs(1)) 
                                                
        def standard_sequence(piece: str, name: str):
            return str(add_lines_and_tabs(1, 4) + tile_i  + add_lines_and_tabs(0, 5) + f'id: ' + name + add_lines_and_tabs(1, 5) + f'name: "{name}"' + add_lines_and_tabs(1, 5) + 
                'on_press:' + add_lines_and_tabs(1, 6) + 
                #'bind: app.movelog()' + add_lines_and_tabs(1, 6) + 
                'app.update_board(self.name)' +
                add_lines_and_tabs(2, 5) + 'MDButtonIcon:' + add_lines_and_tabs(1, 6) + f'id: {name}_overlay' + add_lines_and_tabs(1, 6) + 
                'size: "50sp", "50sp"' + add_lines_and_tabs(1, 6) + f'source: ""' + add_lines_and_tabs(1, 6) + 
                'pos_hint: {"center_x": 0.5, "center_y": 0.5}' + add_lines_and_tabs(2, 5) + 'MDButtonIcon:' + add_lines_and_tabs(1, 6) + 
                f'id: {name}_image' + add_lines_and_tabs(1, 6) + 'size: "50sp", "50sp"' + add_lines_and_tabs(1, 6) + f'source: "{piece}"' + 
                add_lines_and_tabs(1, 6) + 'pos_hint: {"center_x": 0.5, "center_y": 0.5}' + add_lines_and_tabs(1))

        def add_edge_pieces(player: str, letter: str, number: str):
            name = letter + number         
            index = self.letters.index(letter)
            __piece = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
            p1 = self.pieces['Player1']['pieces'][__piece[index]]
            p2 = self.pieces['Player2']['pieces'][__piece[index]]
            if number == '1':
                if index == 0 or index % 2 == 0: player += invert_sequence(p1, name)  
                elif index != 0 or index % 2 != 0: player += standard_sequence(p1, name)        
            else:
                if index == 0 or index % 2 == 0: player += standard_sequence(p2, name) 
                elif index != 0 or index % 2 != 0: player += invert_sequence(p2, name)       
            return player
        
        def add_pawn_pieces(player: str, piece: str, letter: str, number: str):
            name = letter + number
            index = self.letters.index(letter)
            if index == 0 or index % 2 == 0:
                if 'p1' in piece: 
                    player += standard_sequence(piece, name)
                if 'p2' in piece: 
                    player += invert_sequence(piece, name)   
            elif index != 0 or index % 2 != 0:
                if 'p1' in piece: 
                    player += invert_sequence(piece, name)     
                if 'p2' in piece: 
                    player += standard_sequence(piece, name)      
            return player
        
        def detail_empties(update_board_seq: str, letter: str, number: str, invert: bool):
            name = letter + number
            index = self.letters.index(letter)  
            si_tile = str(add_lines_and_tabs(0, 4) + tile_i + add_lines_and_tabs(0, 5) + f'id: ' + name + add_lines_and_tabs(1, 5) + f'name: "{name}"' + add_lines_and_tabs(1, 5) + 'on_press:' + add_lines_and_tabs(1, 6) + 
                        #'bind: app.movelog()' + add_lines_and_tabs(1, 6) + 
                        'app.update_board(self.name)' + add_lines_and_tabs(1, 5) + 'MDButtonIcon:' + add_lines_and_tabs(1, 6) + f'id: {name}_overlay' 
                        + add_lines_and_tabs(1, 6) + f'source: ""' + add_lines_and_tabs(1, 6) + 'pos_hint: {"center_x": 0.5, "center_y": 0.5}' + add_lines_and_tabs(1, 5) + 'MDButtonIcon:' + add_lines_and_tabs(1, 6) + 
                        f'id: {name}_image'  + add_lines_and_tabs(1, 6) + f'source: "pieces/tempbg.png"' + add_lines_and_tabs(1, 6) + 'pos_hint: {"center_x": 0.5, "center_y": 0.5}' + add_lines_and_tabs(1))
            sii_tile = str(add_lines_and_tabs(0, 4) + tile_ii + add_lines_and_tabs(0, 5) + f'id: ' + name + add_lines_and_tabs(1, 5) + f'name: "{name}"' + add_lines_and_tabs(1, 5) + 'on_press:' + add_lines_and_tabs(1, 6) + 
                        #'bind: app.movelog()' + add_lines_and_tabs(1, 6) + 
                        'app.update_board(self.name)' + add_lines_and_tabs(1, 5) + 'MDButtonIcon:' + add_lines_and_tabs(1, 6) + f'id: {name}_overlay' 
                        + add_lines_and_tabs(1, 6) + f'source: ""' + add_lines_and_tabs(1, 6) + 'pos_hint: {"center_x": 0.5, "center_y": 0.5}' + add_lines_and_tabs(1, 5) + 'MDButtonIcon:' + add_lines_and_tabs(1, 6) + 
                        f'id: {name}_image' + add_lines_and_tabs(1, 6) + f'source: "pieces/tempbg.png"' + add_lines_and_tabs(1, 6) + 'pos_hint: {"center_x": 0.5, "center_y": 0.5}' + add_lines_and_tabs(1))
            
            if invert == True:
                if index == 0 or index % 2 == 0: update_board_seq += si_tile       
                elif index != 0 or index % 2 != 0: update_board_seq += sii_tile
                
            else:
                if index == 0 or index % 2 == 0: update_board_seq += sii_tile         
                elif index != 0 or index % 2 != 0: update_board_seq += si_tile
                   
            return update_board_seq 
        update_board_seq1 = update_board_seq2 = update_board_seq3 = update_board_seq4 = ""
        
        for row in self.grid:
            for tile in row:
                __p1pawn = self.pieces['Player1']['pieces']['pawn']
                __p2pawn = self.pieces['Player2']['pieces']['pawn']
                if   tile[1] == '1': __Player1 = add_edge_pieces(__Player1, tile[0], tile[1]) 
                elif tile[1] == '2': __Player1pawns = add_pawn_pieces(__Player1pawns, __p1pawn, tile[0], tile[1])
                elif tile[1] == '8': __Player2 = add_edge_pieces(__Player2, tile[0], tile[1])    
                elif tile[1] == '7': __Player2pawns = add_pawn_pieces(__Player2pawns, __p2pawn, tile[0], tile[1])
                elif tile[1] == '6': update_board_seq1 = detail_empties(update_board_seq1, tile[0], tile[1], True)
                elif tile[1] == '5': update_board_seq2 = detail_empties(update_board_seq2, tile[0], tile[1], False)
                elif tile[1] == '4': update_board_seq3 = detail_empties(update_board_seq3, tile[0], tile[1], True)
                elif tile[1] == '3': update_board_seq4 = detail_empties(update_board_seq4, tile[0], tile[1], False) 

        HorizontalBox1 = 'HorizontalBox1:' + h_oriantation + update_board_seq1 + (add_lines_and_tabs(1) * 2)
        HorizontalBox2 = 'HorizontalBox2:' + h_oriantation + update_board_seq2 + (add_lines_and_tabs(1) * 2)    
        HorizontalBox3 = 'HorizontalBox3:' + h_oriantation + update_board_seq3 + (add_lines_and_tabs(1) * 2)
        HorizontalBox4 = 'HorizontalBox4:' + h_oriantation + update_board_seq4 + (add_lines_and_tabs(1) * 2)              
        update_boardlayout1 = add_lines_and_tabs(1, 3) + HorizontalBox1 + add_lines_and_tabs(1, 3) + HorizontalBox2 + add_lines_and_tabs(1, 3) + HorizontalBox3 + add_lines_and_tabs(1, 3) + HorizontalBox4 
        update_boardlayout2 = add_lines_and_tabs(1, 3) + HorizontalBox4 + add_lines_and_tabs(1, 3) + HorizontalBox3 + add_lines_and_tabs(1, 3) + HorizontalBox2 + add_lines_and_tabs(1, 3) + HorizontalBox1    
        if selectedplayer == 1:           
            update_board_p1_tp = add_lines_and_tabs(1, 3) + __Player1pawns + add_lines_and_tabs(1, 3) + __Player1
            update_board_p2 = add_lines_and_tabs(1, 3) + __Player2 + add_lines_and_tabs(1, 3) + __Player2pawns
            player_set = update_board_p2 + update_boardlayout1 + update_board_p1_tp  
        elif selectedplayer == 2:
            update_board_p2_tp = add_lines_and_tabs(1, 3) + __Player2pawns + add_lines_and_tabs(1, 3) + __Player2  
            update_board_p1    = add_lines_and_tabs(1, 3) + __Player1 + add_lines_and_tabs(1, 3) + __Player1pawns
            player_set = update_board_p1 + update_boardlayout2 + update_board_p2_tp
        
        def viewset(sizel: str, sizew: str, posx: str, posy: str):
            return str(add_lines_and_tabs(1, 1) + 'MDRelativeLayout:' + add_lines_and_tabs(1, 2) + "md_bg_color: '#344C4D'" + add_lines_and_tabs(1, 2) + 'size_hint:' + sizel + ', ' + sizew + add_lines_and_tabs(1, 2) + 
                       "pos_hint: {'center_x': " + posx + ", 'center_y': " + posy + '}' + add_lines_and_tabs(1, 2) + 'MDBoxLayout:' + add_lines_and_tabs(1, 3) + "orientation: 'vertical'" + add_lines_and_tabs(1) )
        
        #view_set_mv = viewset('0.8', '0.4', '0.5', '0.5')     
        view_set_tv = viewset('0.6', '0.7', '0.5', '0.5')    
        #view_set_dv = viewset('0.4', '0.6', '0.5', '0.5')  

        with open('gui/match.kv', 'w') as file:
            MainScreen = str(add_lines_and_tabs(1) + '#:import get_color_from_hex kivy.utils.get_color_from_hex \nMDScreen:' +  add_lines_and_tabs(1, 1) + 'id: match_screen' + add_lines_and_tabs(1, 1) + 
                            'name: "match_screen"' + add_lines_and_tabs(1, 1) + "md_bg_color: '#344C4D'" + view_set_tv + player_set)
            for text in __Player1_promotions: file.write(text)
            for text in __Player2_promotions: file.write(text)
            file.write(PlayerTradedPieceList)
            file.write(MainScreen)
            file.close()
