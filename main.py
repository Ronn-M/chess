from utils import utils
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from queue import Queue
from logging import log

from board_generator import GenerateBoard
from tile_update_handler import TileHandler
from move_filter import MoveFilter
from piece_config import PieceMovement 
from tile_manager import TileMapper, CheckHandler
import device_views

class pyChessGame(MDApp):
 
    def __init__(self) -> None: 
        super().__init__()
        self.utils: utils
        self.activated_tiles: Queue[tuple[str]]
        self.args: tuple[str, int]
        self.check_data: str
        self.check_details: Queue[str|None]
        self.current_location: str
        self.kingp1cd: Queue[bool|None]
        self.kingp2cd: Queue[bool|None]
        self.location: tuple[str|None]
        self.tile_handler: TileHandler
        self.piece_details: tuple[str]
        self.player: str
        self._verified_tiles: set[str]
        self._filtered_possible_moves: set[str]
        self.potential_en_passant: Queue[str|None]
        self.promotion_data: Queue[str | None]
        self.rooklp1cd: Queue[bool|None]
        self.rookrp1cd: Queue[bool|None]
        self.rooklp2cd: Queue[bool|None]
        self.rookrp2cd: Queue[bool|None]
        self.screenmanager: ScreenManager
        self._main_possible_moves: tuple[str]
        self.traded_pieces_set: Queue[set[str]|None]
        
        self.empty_tile = "pieces/tempbg.png"
        self.overlay = 'img_data/overlay.png'
        self.trade_overlay = 'img_data/trade_overlay.png' 
        self.current_overlay = 'img_data/current_overlay.png'  
        
        self.board = GenerateBoard()
        self.piece_movement = PieceMovement()
        self.player = '1'
        self.in_check = False
        self.selected_player = 0
        self.preview_counter = 1
        self._verified_tiles = set()
        self.activated_tiles = Queue()
        self.promotion_data = Queue()
        self.traded_pieces_set = Queue()
        self.potential_en_passant = Queue()
        self.kingp1cd, self.kingp2cd = Queue(), Queue()
        self.rooklp1cd, self.rooklp2cd = Queue(), Queue()
        self.rookrp1cd, self.rookrp2cd = Queue(), Queue()
        self.check_details, self.check_mate = Queue(), set()
        self.active_tile, self.next_move = Queue(), Queue() 
        
        self.kingp1cd.put(False)
        self.kingp2cd.put(False)
        self.rooklp1cd.put(False)
        self.rookrp1cd.put(False)
        self.rooklp2cd.put(False)
        self.rookrp2cd.put(False)
        self.gamelogs = list()
        self.screenmanager = ScreenManager()
        
    def build(self: MDApp) -> ScreenManager:  
        start_manu = Builder.load_file('gui/start_menu.kv')
        match_recap = Builder.load_file('gui/postgame_review.kv')
        player_select = Builder.load_file('gui/player_select.kv')
        
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = 'M3'
        self.screenmanager.add_widget(start_manu)
        self.screenmanager.add_widget(match_recap)
        self.screenmanager.add_widget(player_select)

        return self.screenmanager

    def start_manu(self: MDApp) -> None: self.screenmanager.current = 'start_manu'

    def load_match(self: MDApp, _selected_active_player: int) -> None: 
        
        if _selected_active_player != 0: self.selected_player = _selected_active_player
        if self.selected_player != 0:
            self.board.assign_player(self.selected_player)
            self.match_screen = Builder.load_file('gui/match.kv')
            self.match_reviewer = Builder.load_file('gui/postgame_viewer.kv')
            self.screenmanager.add_widget(self.match_screen)
            self.screenmanager.add_widget(self.match_reviewer)
            self.update_board()

    def player_select(self: MDApp) -> None: self.screenmanager.current = 'player_select'

    def update_widgets(self: MDApp, *args) -> None:
        self.screenmanager.current = 'match_screen'
        self.screen = self.screenmanager.current_screen 
        self.movefilter = MoveFilter(self.screen, self.board)
        self.tile_handler = TileHandler(self.screen, self.activated_tiles, self._verified_tiles)
        self.tile_mapper = TileMapper(self.screen, self.activated_tiles, self.board, self.tile_handler)
        self.checkhandler = CheckHandler(self.screen, self.board, self.movefilter, self.tile_mapper, self.tile_handler)
        self.clear_active_tiles = self.tile_handler.clear_active_tiles
        
    def movelog(self: MDApp): 
        self.active_screen = self.screenmanager.current_screen
        move_log = set()
        for name in self.active_screen.ids:
            if 'image' in name: 
                move_log.add((name, self.active_screen.ids[f'{name}'].source))
            elif 'overlay' in name: 
                if 'current_overlay' in self.active_screen.ids[f'{name}'].source: move_log.add((name, self.active_screen.ids[f'{name}'].source))
                if 'check_overlay' in self.active_screen.ids[f'{name}'].source: move_log.add((name, self.active_screen.ids[f'{name}'].source))
        if move_log not in self.gamelogs: self.gamelogs.append(move_log)

    '''for readability, the following function will be modified to reduce reading complexity'''   
    def update_piece_position(self: MDApp, _location: tuple[str, str, str]) -> None: 
        
        PIECE_HANDLERS = {}
        self.update_widgets()
        _traded_pieces_set = self.traded_pieces_set
        
        def castling_condition_evaluator(_active_move: tuple) -> None: 
            def _castling_queue_updater(active_piece_tile: Queue, player_data: str) -> None:
                rook_queues = {'rook_p1': {'a1': self.rooklp1cd, 'h1': self.rookrp1cd},
                                'rook_p2': {'a8': self.rooklp2cd, 'h8': self.rookrp2cd}}
                kings_queues = {'king_p1': self.kingp1cd, 'king_p2': self.kingp2cd}
                if player_data in rook_queues.keys(): 
                    for key in rook_queues[player_data].keys():
                        if key == active_piece_tile: 
                            rook_queues[player_data][key].put(True) 
                            break
                elif kings_queues[player_data] == Queue:
                    kings_queues[player_data].put(True)

            @self.utils.register('p1', PIECE_HANDLERS) # if 'p1' in _active_move[2] 
            def p1(): 
                _castling_queue_updater(_active_move[0][0], 'king_p1')
                _castling_queue_updater(_active_move[0][0], 'rook_p1') 

            @self.utils.register('p2', PIECE_HANDLERS) # if 'p2' in _active_move[2] 
            def p2(): 
                _castling_queue_updater(_active_move[0][0], 'king_p2')
                _castling_queue_updater(_active_move[0][0], 'rook_p2')        

            if 'king' in _active_move[1]: PIECE_HANDLERS[_active_move[2]]
            
        def move_or_trade(_location: tuple[str, str, str]=_location):
            def activate_castle(_king_eval: bool):    
                def complete_castle(_edge: str, _newloc: str):        
                    _edge_tile = self.screen.ids[_edge]  
                    _new_tile_data = self.screen.ids[_newloc]
                    _new_tile_data.source = _edge_tile.source
                    _edge_tile.source = self.empty_tile
                if _location[0] in['c1', 'c8', 'g1', 'g8'] and _king_eval == False: #castling adjacent tiles
                    _next_col_index = self.board.letters.index(_location[0][0])
                    _active_col_index = self.board.letters.index(_active_move[0][0])
                    if _active_move[0][1] == '1':   
                        if _next_col_index > _active_col_index: complete_castle('h1_image', 'f1_image')
                        elif _next_col_index < _active_col_index: complete_castle('a1_image', 'd1_image')
                    elif _active_move[0][1] == '8':
                        if _next_col_index > _active_col_index: complete_castle('h8_image', 'f8_image')
                        elif _next_col_index < _active_col_index: complete_castle('a8_image', 'd8_image')

            if not self.active_tile.empty():
                _possible_moves = self.next_move.get()
                _active_move = self.active_tile.get()
                _new_tile_data = self.screen.ids[f'{_location[0]}_image']
                _current_tile_image = self.screen.ids[f'{_active_move[0]}_image']
                activated_tile = self.screen.ids[f'{_active_move[0]}_overlay']

                if 'king' not in _new_tile_data.source:
                    if _location[0] not in _possible_moves[0]: 
                        activated_tile.source = self.empty_tile
                        self.clear_active_tiles()
                        return 'pass'
                        
                    elif _location[0] in _possible_moves[0]:
                        if _new_tile_data.source != self.empty_tile and _traded_pieces_set.empty():    
                            _pieces_set = [_new_tile_data.source]   
                            _traded_pieces_set.put(_pieces_set)
                            self.tile_handler.display_traded_pieces(_pieces_set)
                                
                        elif _new_tile_data.source != self.empty_tile and not _traded_pieces_set.empty():      
                            _pieces_set = _traded_pieces_set.get()
                            _pieces_set.append(_new_tile_data.source)
                            _traded_pieces_set.put(_pieces_set)
                            self.tile_handler.display_traded_pieces(_pieces_set)

                        _new_tile_data.source = _current_tile_image.source
                        activated_tile.source = self.current_overlay
                        _current_tile_image.source = self.empty_tile
                    
                        if 'pawn' in _active_move[1]: 
                            if not self.potential_en_passant.empty():       
                                _en_passant = self.potential_en_passant.get()
                                if _location[0] == _en_passant[1] and _en_passant[2] == True:
                                    _en_passant_trade_data = self.screen.ids[f'{_en_passant[0][0]}_image']   
                                    _en_passant_trade_data.source = self.empty_tile
                                
                            _current_location = _location[0]
                            _piece_details = _active_move[1:]
                            _current_location_row = int(_location[0][1])  
                            
                            if _current_location_row == 1: self.pawn_promotion_handler(_current_location, _piece_details)                                 
                            elif _current_location_row == 8: self.pawn_promotion_handler(_current_location, _piece_details)  

                            if ('4' in _location[0] and '2' in _active_move[0]) or ('5' in _location[0] and '7' in _active_move[0]):  
                                _en_passant = _location[0], _active_move
                                if self.potential_en_passant.empty(): self.potential_en_passant.put([_en_passant, None, None])  
                                elif not self.potential_en_passant.empty():     
                                    self.potential_en_passant.get()
                                    self.potential_en_passant.put([_en_passant, None, None])  
                                
                        elif 'king' in _active_move[1]:
                            if 'p1' in _active_move[2]: 
                                evaluation_data = self.kingp1cd.get()
                                activate_castle(evaluation_data)
                                self.kingp1cd.put(evaluation_data)
                            if 'p2' in _active_move[2]: 
                                evaluation_data = self.kingp2cd.get()
                                activate_castle(evaluation_data)
                                self.kingp2cd.put(evaluation_data)

                if 'pawn' in _active_move[1] and (_active_move[0][1] == '7' or _active_move[0][1] == '2'):
                    _current_tile_image = self.screen.ids[f'{_active_move[0]}_image']
                    _active_move = (_active_move[0],_current_tile_image.source, _active_move[2])
                self.active_tile.put(_active_move)  
            elif self.active_tile.empty(): return 'pass'        
                
        def validate_move(_activeplayer: str, _otherplayer: str) -> None:
            def active_tile_handler(_activeplayer: str=_activeplayer, _otherplayer: str=_otherplayer) -> None:
                __move_data = move_or_trade()
                if __move_data == 'pass': self.player = _activeplayer
                else:   
                    _active_move = self.active_tile.get()
                    self.active_tile.put(_active_move)
                    if 'king' or 'rook' in _active_move[1]: castling_condition_evaluator(_active_move)  
                    self.player = _otherplayer
                         
            active_tile_handler()  

            if not self.check_details.empty(): 
                self.check_data = self.check_details.get()
                self.screen.ids[f'{self.check_data[2]}_overlay'].source = self.empty_tile

        if self.player == '1': validate_move('1', '2')       
        elif self.player == '2': validate_move('2', '1')
    
    def update_board(self: MDApp, *_tile: str, _log: bool=True) -> None: 
        self.screenmanager.current = 'match_screen'
        self.update_widgets()

        #pieces_on_the_board() buggy feature, changes to be implemented in future update
        def pieces_on_the_board() -> None:
            for _row in self.board.grid:
                for _main_move in _row:
                    _tile_data = self.screen.ids[f'{_main_move}_image']
                    if 'king' not in _tile_data.source and 'rook' not in _tile_data.source and 'queen' not in _tile_data.source:
                        _tile_data.source = self.empty_tile  
        
        

        def move_handler(_player: str, _opponent: str, _piece_tile_data: str) -> None: 
            if self.next_move.empty() and _player in _piece_tile_data: self.active_piece_handler(_location)
            elif not self.next_move.empty() and _player in _piece_tile_data: self.active_piece_handler(_location)
            elif not self.next_move.empty() and ('bg' in _piece_tile_data or _opponent in _piece_tile_data): 
                _next_move_data = self.next_move.get()
                self.next_move.put(_next_move_data)
                self.update_piece_position(_location)   
                _check_evaluation_data = self.checkhandler.check_evaluator(self.board.grid, self.player)
                self.in_check = _check_evaluation_data[0]
                if self.check_details.empty():
                    if _check_evaluation_data[0] == True: self.check_details.put(_check_evaluation_data)
                if _log == True: self.movelog()
                self.clear_active_tiles()
      
        if _tile:
            _piece_tile_data = self.screen.ids[f'{_tile[0]}_image'].source
            _location = (_tile[0], _piece_tile_data, _piece_tile_data[-6:][:2])
            if self.player == '1': move_handler('p1', 'p2', _piece_tile_data)
            elif self.player == '2': move_handler('p2', 'p1', _piece_tile_data) 

            if not self.check_details.empty():
                self.check_data = self.check_details.get()
                self.check_details.put(self.check_data)
                _checked_tile_data = self.screen.ids[f'{self.check_data[2]}_image']
                for _row in self.board.grid:
                    for _current_move in _row:  
                        _piece_tile_data = self.screen.ids[f'{_current_move}_image'] 
                        if _checked_tile_data.source[-6:][:2] in _piece_tile_data.source:
                            _location = (_current_move, _piece_tile_data.source, _checked_tile_data.source[-6:][:2])
                            self._move_manager(_location, _validate_check=True)
                if not self._verified_tiles: self.match_recap(None)
            
    def promote_pawn(self: MDApp, _piece_details: tuple[int, tuple[str | int]]) -> None: 
        _promote = self.promotion_data.get()
        _promotion_display = self.promotion_data.get()
        _current_tile_image = self.screen.ids[f'{_promote}_image']
        _current_tile_image.source = _piece_details
        self.screen.remove_widget(_promotion_display[0])
        self.screen.remove_widget(_promotion_display[1])
        self.screen.remove_widget(_promotion_display[2])
        self.screen.remove_widget(_promotion_display[3])
        _check_evaluation_data = self.checkhandler.check_evaluator(self.board.grid, self.player)
        self.in_check = _check_evaluation_data[0]
        if self.check_details.empty():
            if _check_evaluation_data[0] == True: self.check_details.put(_check_evaluation_data)

    def active_piece_handler(self: MDApp, _location: tuple[str, str, str]) -> None: 
        self.screenmanager.current = 'match_screen'
        self.update_widgets()
        def possible_move_search() -> None:
            def add_defaults(activated_tile: MDApp, _position: tuple[str, str, str]) -> None:
                activated_tile.source = self.current_overlay
                self.active_tile.put(_position)
                self._move_manager(_position)

            _current_tile_image = self.screen.ids[f'{_location[0]}_image']
            _current_tile_overlay= self.screen.ids[f'{_location[0]}_overlay']
            if _current_tile_image.source == _location[1]:
                if self.active_tile.empty(): 
                    add_defaults(_current_tile_overlay, _location)
                else: 
                    self.clear_active_tiles()
                    _original_data = self.active_tile.get()
                    _previous_tile_data = self.screen.ids[f'{_original_data[0]}_overlay']
                    if _original_data == _location[0]: 
                        _previous_tile_data.source = self.empty_tile 
                    else:
                        _previous_tile_data.source = self.empty_tile
                        add_defaults(_current_tile_overlay, _location)
                   
        if "p1" in _location[2]: possible_move_search()
        elif "p2" in _location[2]: possible_move_search()   
        else: 
            self.clear_active_tiles()

    '''for readability, the following function will be modified to reduce reading complexity'''   
    def _move_manager(self: MDApp, _location: tuple[str, str, str], _validate_check=False):    
        
        self.update_widgets()
        def pawn_viable_moves(_position_data: tuple, movement_data: set[str]) -> set:
            _temp = set([item for item in movement_data]) 
            def add_move(_en_passant_move: str, _en_passant_data: list[str], movement_data: set[str]=movement_data):
                movement_data.add(_en_passant_move)
                self.potential_en_passant.put([_en_passant_data, _en_passant_move, True])
        
            def validate_en_passant_move(_en_passant_number_value: int, _position_letter_value: int, _en_passant_value: int, _en_passant_data: list[str]):
               
                _en_passant_move = f'{_en_passant_data[0][0]}{_en_passant_number_value}'
                if _en_passant_value - _position_letter_value == 1: add_move(_en_passant_move, _en_passant_data)  
                elif _en_passant_value - _position_letter_value == -1: add_move(_en_passant_move, _en_passant_data)

            for _move in _temp:     
                _move_tile = self.screen.ids[f'{_move}_image']

                if _move[0] != _position_data[0][0] and _move_tile.source == self.empty_tile: movement_data = self.movefilter.pop_item(_move, movement_data)
                elif _move[0] == _position_data[0][0] and _move_tile.source != self.empty_tile: movement_data = self.movefilter.pop_item(_move, movement_data)

                if not self.potential_en_passant.empty(): 
                    _en_passant = self.potential_en_passant.get()
                    _en_passant_data = _en_passant[0]
                    
                    if _en_passant_data[0][1] == _location[0][1]: 
                        _en_passant_number_value = int(_en_passant_data[0][1])
                        _position_letter_value = self.board.letters.index(_location[0][0])
                        _en_passant_value = self.board.letters.index(_en_passant_data[0][0])     

                        if _en_passant_number_value > int(_en_passant_data[1][0][1]): 
                            validate_en_passant_move(_en_passant_number_value - 1, _position_letter_value, _en_passant_value, _en_passant_data)  
                        elif _en_passant_number_value < int(_en_passant_data[1][0][1]):
                            validate_en_passant_move(_en_passant_number_value + 1, _position_letter_value, _en_passant_value, _en_passant_data)                            
            return movement_data
        
        def transfer_viable_moves(_viable_moves: set[str], _check_value: bool) -> None:   
            if self.next_move.empty(): self.next_move.put([_viable_moves, _check_value])
            elif not self.next_move.empty(): 
                self.next_move.get()
                self.next_move.put([_viable_moves, _check_value])  
        
        def castling_validation(_castling_moves: tuple[str]) -> tuple:
            def filter_castling_data(_temp: set[str]):
                _excluded_moves: set[str]
                _excluded_moves = set()
                
                for _move in _temp:
                    if _move[1] != _location[0][1]:
                        self._filtered_possible_moves = self.movefilter.pop_item(_move, self._filtered_possible_moves)      
                        _excluded_moves.add(_move)
                return _excluded_moves, self._filtered_possible_moves

            _castling_buffer = ['b1', 'b8']
            if _location[0][1] == '1' and self.screen.ids['b1_image'].source == self.empty_tile: self._filtered_possible_moves.add(_castling_buffer[0])
            elif _location[0][1] == '8' and self.screen.ids['b8_image'].source == self.empty_tile: self._filtered_possible_moves.add(_castling_buffer[1])

            _temp = set(item for item in self._filtered_possible_moves)
            self._filtered_possible_moves.add(_location[0])
            self._main_possible_moves.add(_location[0])
            self._main_possible_moves = sorted(self._main_possible_moves)
            self._filtered_possible_moves = sorted(self._filtered_possible_moves)
            _excluded_moves, self._filtered_possible_moves = filter_castling_data(_temp)
            _position_index = self._filtered_possible_moves.index(_location[0])
            _righthalf = self._filtered_possible_moves[_position_index:]
            _left_half = self._filtered_possible_moves[:_position_index + 1]
            
            for _move in _castling_moves:
                if _move in self._filtered_possible_moves:
                    _castlinng_move_index = self._filtered_possible_moves.index(_move)
                    if _position_index > _castlinng_move_index:
                        lefthalf_len = len(_left_half)
                        if lefthalf_len != 4: 
                            self._filtered_possible_moves = self.movefilter.pop_item(_move, self._filtered_possible_moves) 
                    elif _position_index < _castlinng_move_index: 
                        righthalf_len =  len(_righthalf)
                        if righthalf_len != 3: self._filtered_possible_moves = self.movefilter.pop_item(_move, self._filtered_possible_moves)   

            for _move in _castling_buffer:
                if _move in self._filtered_possible_moves: self._filtered_possible_moves = self.movefilter.pop_item(_move, self._filtered_possible_moves)
            self._filtered_possible_moves += _excluded_moves
            if _location[0] in self._filtered_possible_moves: self._filtered_possible_moves = self.movefilter.pop_item(_location[0], self._filtered_possible_moves)      
            return self._filtered_possible_moves

        def filter_unavailable_moves():
            _temp = [item for item in self._filtered_possible_moves]
            def initialize_castling_data(_location: tuple[str, str, str]) -> tuple: 
                _castling_moves: tuple[str, str]
                _piece_eval_data: list[bool]

                _piece_eval_data = []
                _main_possible_moves = sorted(list(self._main_possible_moves))
                _castling_moves = _main_possible_moves[0], _main_possible_moves[-1]
                def update_castling_queues(kingcd_queue: Queue[bool], rooklcd_queue: Queue[bool], rookrcd_queue: Queue[bool], _piece_eval_data: list[bool]=_piece_eval_data):
                    _piece_eval_data.append(kingcd_queue.get())
                    _piece_eval_data.append(rooklcd_queue.get())
                    _piece_eval_data.append(rookrcd_queue.get())     
                    kingcd_queue.put(_piece_eval_data[0])
                    rooklcd_queue.put(_piece_eval_data[1])
                    rookrcd_queue.put(_piece_eval_data[2])

                if 'p1' in _location[2]: update_castling_queues(self.kingp1cd, self.rooklp1cd, self.rookrp1cd)
                elif 'p2' in _location[2]: update_castling_queues(self.kingp2cd, self.rooklp2cd, self.rookrp2cd)
                return _castling_moves, _piece_eval_data[0], _piece_eval_data[1], _piece_eval_data[2]
            
            def verify_castling(_location: tuple[str, str, str]=_location, _move_filter=self.movefilter) -> set: 
                _castling_moves, _king_eval, _rookl_eval, _rookr_eval = initialize_castling_data(_location)
                if _king_eval == False and _rookl_eval == False and _rookr_eval == False and self.check_data[0] != True: 
                    self._filtered_possible_moves = castling_validation(_castling_moves)  
                elif _king_eval == True or _rookl_eval == True or _rookr_eval == True or self.check_data[0] == True: 
                    for move in _castling_moves:
                        if move in self._filtered_possible_moves: 
                            self._filtered_possible_moves = _move_filter.pop_item(move, self._filtered_possible_moves)
                return self._filtered_possible_moves

            if not self.check_details.empty():
                self.check_data = self.check_details.get()
                self.check_details.put(self.check_data)
                if 'king' in _location[1]:
                    _check_paths = self.checkhandler.check_path_verifier(self.board.grid, _location, self.player)               
                    _checker_grid_data = self.check_data[1][0], _location[1], self.check_data[1][2]
                    _checker_grid_details = self.piece_movement.piece_move_count(_checker_grid_data, self.board.grid)
                    _, _, piece_grid = self.tile_mapper.piece_possible_moves(self.board.grid, _checker_grid_data, _checker_grid_details)         
                    for _move in _temp:
                        for _path in _check_paths:
                            if _path[0]:             
                                _path, _path_source = _path[0], _path[1]            
                                if _move in _path:
                                    for _path_move in piece_grid:
                                        if self.check_data[1][1] not in _path_source and _path_move in _path and _path_move != _move: 
                                            self._filtered_possible_moves = self.movefilter.pop_item(_move, self._filtered_possible_moves)                             
                                        elif _path_move not in piece_grid:  
                                            if self.check_data[1][0] in self._filtered_possible_moves: 
                                                self.self._filtered_possible_moves = self.movefilter.pop_item(_move, self._filtered_possible_moves)                                 
                                        else: 
                                            if self.check_data[1][0] not in _move: 
                                                self._filtered_possible_moves = self.movefilter.pop_item(_move, self._filtered_possible_moves)                           
                for _move in _temp: 
                    for _moveset in self.check_data[3]: 
                        if 'king' in _location[1]: self._filtered_possible_moves = verify_castling()  
                        elif 'king' not in _location[1]:      
                            if 'knight' in self.check_data[1][1] or 'pawn' in self.check_data[1][1]:    
                                if _move not in self.check_data[1][0]: 
                                    self._filtered_possible_moves = self.movefilter.pop_item(_move, self._filtered_possible_moves)    
                            elif 'knight' not in self.check_data[1][1] or 'pawn' not in self.check_data[1][1]:            
                                if _move not in _moveset and self.check_data[1][0] in _moveset:                                    
                                    self._filtered_possible_moves = self.movefilter.pop_item(_move, self._filtered_possible_moves)

            elif self.check_details.empty(): 
                if 'king' in _location[1]:
                    _check_paths = self.checkhandler.check_path_verifier(self.board.grid, _location, self.player)            
                    for _move in _temp:
                        for _path in _check_paths:
                            if _path[0]:            
                                _path = _path[0]
                                if _move in _path: self._filtered_possible_moves = self.movefilter.pop_item(_move, self._filtered_possible_moves)  
                    _castling_moves, _king_eval, _rookl_eval, _rookr_eval = initialize_castling_data(_location)
                    if _king_eval == False and _rookl_eval == False and _rookr_eval == False: 
                        self._filtered_possible_moves = castling_validation(_castling_moves)   
                    elif _king_eval == True or _rookl_eval == True or _rookr_eval == True:    
                        for _move in _castling_moves:
                            if _move in self._filtered_possible_moves: 
                                self._filtered_possible_moves = self.movefilter.pop_item(_move, self._filtered_possible_moves)

                elif 'king' not in _location[1]:
                    _check_paths, _potential_check = self.checkhandler.check_path_verifier(self.board.grid, _location, self.player)
                    if _potential_check == True and _location[0] in _check_paths:     
                        for _move in _temp: 
                            if _move not in _check_paths: self._filtered_possible_moves = self.movefilter.pop_item(_move, self._filtered_possible_moves)

        _piece_details = self.piece_movement.piece_move_count(_location, self.board.grid)
        if 'king' not in _location[1]: 
            self._filtered_possible_moves, _, self._main_possible_moves = self.tile_mapper.piece_possible_moves(self.board.grid, _location, _piece_details, check_validation=True)
            if 'pawn' in _location[1]: 
                self._filtered_possible_moves = pawn_viable_moves(_location, self._filtered_possible_moves) 
            else: 
                self._filtered_possible_moves, _, self._main_possible_moves = self.tile_mapper.piece_possible_moves(self.board.grid, _location, _piece_details)
        elif 'king' in _location[1]: 
            self._filtered_possible_moves, _, self._main_possible_moves = self.tile_mapper.piece_possible_moves(self.board.grid, _location, _piece_details, check_validation=True)

        filter_unavailable_moves()
        
        self._verified_tiles = self._verified_tiles.union(self._filtered_possible_moves) 
        
        if _validate_check == False: 
            for _move in self._verified_tiles :
                _current_tile_overlay = self.screen.ids[f'{_move}_overlay']
                _current_tile_image = self.screen.ids[f'{_move}_image']   
                if _current_tile_image.source == self.empty_tile: _current_tile_overlay.source = self.overlay
                elif _current_tile_image.source != self.empty_tile: _current_tile_overlay.source = self.trade_overlay
            transfer_viable_moves(self._verified_tiles , False)
        elif _validate_check == True: 
            transfer_viable_moves(self._verified_tiles , True)
  
    def pawn_promotion_handler(self: MDApp, _current_location: str, _piece_details: tuple[int, tuple[str | int]]) -> None: 
        self.screenmanager.current = 'match_screen'
        def activate_promotions(_piece1: Widget, _piece2: Widget, _piece3: Widget, _piece4: Widget):
            self.screen.add_widget(_piece1)
            self.screen.add_widget(_piece2)
            self.screen.add_widget(_piece3)
            self.screen.add_widget(_piece4)
            self.promotion_data.put([_piece1, _piece2, _piece3, _piece4])
        
        self.update_widgets()
        self.promotion_data.put(_current_location)

        if _piece_details[1] == 'p1':
            activate_promotions(device_views.Player1PomortionRook(), 
                                device_views.Player1PomortionQueen(), 
                                device_views.Player1PomortionKnight(), 
                                device_views.Player1PomortionBishop())
        elif _piece_details[1] == 'p2':    
            activate_promotions(device_views.Player2PomortionRook(), 
                                device_views.Player2PomortionQueen(), 
                                device_views.Player2PomortionKnight(), 
                                device_views.Player2PomortionBishop())

    # buggy feature    
    def match_recap(self: MDApp, *args: str) -> None: 
        self.screenmanager.current = 'match_recap'

    # buggy feature 
    def reload_previous_match(self: MDApp):

        self.in_check = False
        self.match_screen = Builder.unload_file('gui/match.kv')
        self.load_match(self.selected_player)

        self.screenmanager.current = 'matchview_screen'
        self.screenmanager.current_screen.ids['match_window'].add_widget(self.match_screen)

    # buggy feature 
    def next_preview(self: MDApp):
        if len(self.gamelogs) > self.preview_counter:
            log = self.gamelogs[self.preview_counter]
            for move in log:
                _tile_data = self.match_screen.ids[f'{move[0]}']
                _tile_data.source = move[1]
            self.preview_counter += 1
            self.clear_active_tiles()

    # buggy feature     
    def previous_preview(self: MDApp):
        if self.preview_counter >= 0:
            self.preview_counter -= 1
            log = self.gamelogs[self.preview_counter]
            for move in log:
                _tile_data = self.match_screen.ids[f'{move[0]}']
                _tile_data.source = move[1]
            self.clear_active_tiles()
    
if __name__ == '__main__': 
    pyChessGame().run()