from kivy.weakproxy import WeakProxy
from kivy.uix.widget import Widget
from queue import Queue
from logging import log

# local Module
from board_generator import GenerateBoard
from tile_update_handler import TileHandler
from move_filter import MoveFilter
from piece_config import PieceMovement

class TileMapper:
    
    def __init__(self, _screen: Widget, _activated_tiles: Queue[set[str]], board: GenerateBoard, _tile_handler: TileHandler):
        self.board = board
        self.screen = _screen 
        self.piece_movement = PieceMovement()
        self._activated_tiles = _activated_tiles
        self.piece_ref = list()
        self.empty_tile = "pieces/tempbg.png"
        self.check_overlay ='img_data/check_overlay.png'
        self._tile_handler = _tile_handler

    def movement_handler(self, _location: tuple[str, str, str], _possible_moves: set, _check_validation: bool): 
        _categorzed_moves: set | dict[str, set[set[str]]]
        _filtered_moves: set 
        _tile_possession_tile_data: set 
  
        _filtered_moves = set()
        _categorzed_moves = set()
        _tile_possession_tile_data = set()
        _movefilter = MoveFilter(self.screen, self.board)

        # rook rules
        if 'rook' in _location[1]: 
            _categorzed_moves = _movefilter.lolat_move_assigner(_location, _filtered_moves, _tile_possession_tile_data)
        # bishop rules
        elif 'bishop' in _location[1]: 
            _categorzed_moves = _movefilter.diagonal_move_assigner(_location, _filtered_moves, _tile_possession_tile_data)
        # pawn rules
        elif 'pawn' in _location[1]: 
            self.pawn_move_assigner(_location, _possible_moves, _filtered_moves, _tile_possession_tile_data)    
        # king rules
        elif 'king' in _location[1]: 
            _movefilter.king_move_assigner(_location, _possible_moves, _filtered_moves, _tile_possession_tile_data)          
        # knight rules
        elif 'knight' in _location[1]: 
            _movefilter.knight_filtered_moves(_location, _possible_moves, _filtered_moves, _tile_possession_tile_data, _check_validation)
        # queen rules
        elif 'queen' in _location[1]: 
            def confirmed_queen_moves(_movefilter=_movefilter, _filtered_moves=_filtered_moves, _tile_possession_tile_data=_tile_possession_tile_data):
                _diagonal_movement = _movefilter.diagonal_move_assigner(_location, _filtered_moves, _tile_possession_tile_data)
                _vetical_horizontal_movement = _movefilter.lolat_move_assigner(_location, _filtered_moves, _tile_possession_tile_data)
                _keys = list(_vetical_horizontal_movement.keys()) + list(_diagonal_movement.keys())
                _values = list(_vetical_horizontal_movement.values()) + list(_diagonal_movement.values())
                return dict(zip(_keys, _values))
              
            _categorzed_moves = confirmed_queen_moves()
        return _filtered_moves, _tile_possession_tile_data, _categorzed_moves

    # remove repetative code
    def pawn_move_assigner(self, _location: tuple[str, str, str], _possible_moves: set[str], _filtered_moves_set: set[str], _tile_possession_tile_data_set: set[str]):
        _movefilter = MoveFilter(self.screen, self.board)
        def evaluate_trades(_tile1: str, _tile2: str):

            def check_pawn_tiles(__tile):
                _active_tile = self.screen.ids[ f'{__tile}_overlay']
                _trade_tile = self.screen.ids[ f'{__tile}_image']

                if 'king' not in _trade_tile.source and _location[2] not in _trade_tile.source:  
                    _filtered_moves_set.add(__tile)
                    _tile_possession_tile_data_set.add(__tile)

                elif 'king' in _trade_tile.source and _location[2] not in _trade_tile.source: 
                    _active_tile.source = self.check_overlay
                    _filtered_moves_set.add(__tile)
                    _tile_possession_tile_data_set.add(__tile)
                    return 'check'

            _tile_data = []
            if _tile1: _tile_data.append(check_pawn_tiles(_tile1))
            if _tile2: _tile_data.append(check_pawn_tiles(_tile2)) 
            if 'check' in _tile_data: return 'check'

        _tile1, _tile2 = _movefilter.pawn_tile_possession_handler(_location)
        _check_eval = evaluate_trades(_tile1, _tile2)    
        if _check_eval == 'check': return 'check'
        elif _check_eval != 'check':
            for _move in _possible_moves:
                _tile_data = self.screen.ids[ f'{_move}_image']
                if _tile_data.source != self.empty_tile and _location[2] in _tile_data.source: break
                else: 
                    _filtered_moves_set.add(_move)
                    _tile_possession_tile_data_set.add(_move)
        
    def piece_possible_moves(self, grid: list[list[str]], _location: tuple[str, str, str], _piece_details: tuple[int, tuple[str, str, int]], check_validation: bool=True) -> tuple | None: 
        print()
        PIECE_HANDLERS = {}
        possible_moves = set()
        for _grid_index in range(8): # row
            for _index, _tile in enumerate(grid[_grid_index]): # column
                if _piece_details[1]: 
                    if _piece_details[1][0] in _tile: 
                        self.piece_ref = [_grid_index, _index]    
        if self.piece_ref:
            _col = self.piece_ref[1]
            _row = self.piece_ref[0]

            def register(name):
                def decorator(func):
                    PIECE_HANDLERS[name] = func
                    return func
                return decorator
            
            # king movement
            @register('king')
            def active_tile_king(_location=_location, _piece_details=_piece_details, _row=_row, _col=_col, possible_moves=possible_moves, grid=grid): 
                self.piece_movement.king_movement(_location, _piece_details, _row, _col, possible_moves, grid, check_validation) 
            # knight movement
            @register('knight')             
            def active_tile_knight(_location=_location, _row=_row, _col=_col, possible_moves=possible_moves, grid=grid): 
                self.piece_movement.knight_movement(_location, _row, _col, possible_moves, grid)
            # bishop movement
            @register('bishop')
            def active_tile_bishop(_location=_location, _row=_row, _col=_col, possible_moves=possible_moves, grid=grid): 
                self.piece_movement.bishop_movement(_location, _row, _col, possible_moves, grid)
            # pawn movement
            @register('pawn')   
            def active_tile_pawn(_location=_location, _piece_details=_piece_details, _row=_row, _col=_col, possible_moves=possible_moves, grid=grid): 
                ###log(1, f'active_tile_pawn: {possible_moves}')
                self.piece_movement.pawn_movement(_location, _piece_details, _row, _col, possible_moves, grid)    
            # rook movement  
            @register('rook') 
            def active_tile_rook(_location=_location, _piece_details=_piece_details, _row=_row, _col=_col, possible_moves=possible_moves, grid=grid): 
                self.piece_movement.rook_movement(_location, _piece_details, _row, _col, possible_moves, grid)
            # queen movement
            @register('queen')
            def active_tile_queen(_location=_location, _piece_details=_piece_details, _row=_row, _col=_col, possible_moves=possible_moves, grid=grid): 
                self.piece_movement.queen_movement(_location, _piece_details, _row, _col, possible_moves, grid)
            
            try: PIECE_HANDLERS[_location[1]]()
            except KeyError: 
                try: PIECE_HANDLERS[_location[1][:-3]]()
                except: PIECE_HANDLERS[_location[1][7:][:-7]]()
                
            _filtered_possible_moves, _tile_possession_moves, _categorized_moveset = self.movement_handler(_location, possible_moves, check_validation)
            for _move in _tile_possession_moves: self._activated_tiles.put(_move)
            return _filtered_possible_moves, dict(_categorized_moveset), possible_moves

'''for readability, the following class will be modified to reduce reading complexity'''   
class CheckHandler:
    def __init__(self, _screen: Widget, board: GenerateBoard, _movefilter: MoveFilter, _moveassigner: TileMapper, _tile_handler: TileHandler) -> None:
        self.board = board
        self.screen = _screen  
        self.piece_movement = PieceMovement()
        self.empty_tile = "pieces/tempbg.png"
        self._moveassigner = _moveassigner
        self._movefilter = _movefilter
        self._tile_handler = _tile_handler

    def check_evaluator(self, grid: list[list[str]], _player: str):
        def checkpath_scan(self, _main_move: str):
            _filtered_moves: set
            _main_move_tile_data: WeakProxy[int | str]
            _main_move_tile_player_data: str 
            _pawn_reference: tuple[str, str, str]
            _knight_reference: tuple[str, str, str]
            _knight_reference_details: tuple[int, tuple[str, str, int]]
            _pawn_reference_details: tuple[int, tuple[str, str, int]]

            _filtered_moves = set()

            _main_move_tile_data = self.screen.ids[f'{_main_move}_image']
            _main_move_tile_player_data = _main_move_tile_data.source[-6:][:2]
            _location = _main_move, _main_move_tile_data.source, _main_move_tile_player_data

            _diagonal_data = self._movefilter.diagonal_move_assigner(_location, _filtered_moves,set())
            _lolat_data = self._movefilter.lolat_move_assigner(_location, _filtered_moves,set())

            _pawn_reference = (_main_move, 'pawn', _main_move_tile_player_data)
            _knight_reference = (_main_move, 'knight', _main_move_tile_player_data)

            _knight_reference_details = self.piece_movement.piece_move_count(_knight_reference, grid)
            _pawn_reference_details = self.piece_movement.piece_move_count(_pawn_reference, grid)

            _pawn_possible_moves = self._moveassigner.piece_possible_moves(grid, _pawn_reference, _pawn_reference_details) 
            _knight_possible_moves = self._moveassigner.piece_possible_moves(grid, _knight_reference, _knight_reference_details, check_validation=False) 

            self._movefilter.knight_filtered_moves(_knight_reference, _knight_possible_moves[0], _filtered_moves,set(), validate=False)
            self._moveassigner.pawn_move_assigner(_pawn_reference, _pawn_possible_moves[0], _filtered_moves,set())

            _checkpaths = [_pawn_possible_moves[0], _knight_possible_moves]
            for _key in _lolat_data.keys():
                for _set_data in _lolat_data[_key]: _checkpaths.append(_set_data)
            for _key in _diagonal_data.keys():
                for _set_data in _diagonal_data[_key]: _checkpaths.append(_set_data)
            return _filtered_moves, _checkpaths

        # king condition
        for _row in grid:
            for _main_move in _row:
                _tile_data = self.screen.ids[f'{_main_move}_image']
                if 'king' in _tile_data.source:
                    if _player in _tile_data.source: 
                        _filtered_moves, _unavailable_moves = checkpath_scan(self, _main_move)
                        for _move in _filtered_moves:
                            _current_tile_image = self.screen.ids[f'{_move}_image']
                            if _current_tile_image.source != self.empty_tile:
                                _player_details = _move, _current_tile_image.source, _current_tile_image.source[-6:][:2]
                                _piece_details = self.piece_movement.piece_move_count(_player_details, grid)
                                _possible_check_moves = self._moveassigner.piece_possible_moves(grid, _player_details, _piece_details)    

                                if 'pawn' in _player_details[1] and _possible_check_moves:
                                    for _tile in _possible_check_moves[0]:
                                        if _tile != 'break':
                                            _main_tile_data = self.screen.ids[f'{_tile}_image']  
                                            if 'king' in _main_tile_data.source and _player_details[2] not in _main_tile_data.source: 
                                                return True, _player_details, _tile, _unavailable_moves
                                elif 'pawn' not in _player_details[1] and _possible_check_moves:
                                    for _tile in _possible_check_moves[2]:
                                        if _tile != 'break':
                                            _main_tile_data = self.screen.ids[f'{_tile}_image']
                                            if 'king' in _main_tile_data.source and _player_details[2] not in _main_tile_data.source: 
                                                return True, _player_details, _tile, _unavailable_moves
                        return False, _filtered_moves, _unavailable_moves
    
    def check_path_verifier(self, grid: list[list[str]], _current_location: tuple[str, str, str], _player: str):

        _check_paths, _checker_tiles = list(),set()
        _king_tile, _player_check_tile = '', ('', '', ''), 
        
        for _row in grid:
            for _main_move in _row:
                _tile_data = self.screen.ids[f'{_main_move}_image']
                if 'king' in _tile_data.source:
                    if _player in _tile_data.source: 
                        _king_tile = _main_move
                        _player_check_tile = _main_move, _tile_data.source, _tile_data.source[-6:][:2]
                        _piece_details = self.piece_movement.piece_move_count(_player_check_tile, grid)
        
        if 'king' in _current_location[1]:
            for _row in grid:
                for _main_move in _row:
                    _tile_data = self.screen.ids[f'{_main_move}_image']

                    if _player not in _tile_data.source and self.empty_tile not in _tile_data.source: 
                        _piece_location = _main_move, _tile_data.source, _tile_data.source[-6:][:2]

                        if 'pawn' in _piece_location[1]: 
                            _checkpath_moves = set(self._movefilter.pawn_tile_possession_handler(_piece_location))
                            _checkpath_moves.add(_piece_location[0])
                            if [_checkpath_moves, _piece_location] not in _check_paths: _check_paths.append([sorted(_checkpath_moves), _piece_location]) 
                            
                        elif 'pawn' not in _piece_location[1]: 
                            _piece_details = self.piece_movement.piece_move_count(_piece_location, grid)
                            _checkpath_moves = self._moveassigner.piece_possible_moves(grid, _piece_location, _piece_details)
                            if _checkpath_moves:
                                _potential_mate_data = [_item for _item in _checkpath_moves[0] if _item != None]
                                for _tile in _checkpath_moves[2]:
                                    if _tile != None:  
                                        _tile_check_data = self.screen.ids[f'{_tile}_image'] 
                                        if _piece_location[2] in _tile_check_data.source: _potential_mate_data.append(_tile)
                                if [_potential_mate_data, _piece_location] not in _check_paths: _check_paths.append([sorted(_potential_mate_data), _piece_location])                      
            return _check_paths
        
        elif 'king' not in _current_location[1]:

            def check_potential_counter(_check_paths: list[str], _potential_mate: bool, _current_location: tuple[str, str, str], _direct_checkpath: set[str]):
                _nullify_potential_mate = 0
                for _null_tile in _direct_checkpath:
                    _null_tile_data = self.screen.ids[f'{_null_tile}_image']
                    if _null_tile_data.source != self.empty_tile and _current_location[2] in _null_tile_data.source: _nullify_potential_mate += 1
                if _nullify_potential_mate == 2:
                    _potential_mate = True
                    _check_paths += _direct_checkpath
                    _checker_tiles.add(_main_move)   
                return _check_paths, _potential_mate
            
            _potential_mate = False 
            for _row in grid:
                for _main_move in _row:
                    _tile_data = self.screen.ids[f'{_main_move}_image']
                    if 'king' not in _tile_data.source:  
                        if _player not in _tile_data.source and self.empty_tile not in _tile_data.source:                                 
                            _piece_location = _main_move, _tile_data.source, _tile_data.source[-6:][:2]
                            log(1, f'king not in tile data source: _player: {_player} _current_location: {_current_location} _piece_location: {_piece_location} _tile_data.source: {_tile_data.source}')
                            _checkpath_moves = set()
                            if 'pawn' in _piece_location[1]: 
                                _checkpath_moves = set(self._movefilter.pawn_tile_possession_handler(_piece_location))
                                _checkpath_moves.add(_piece_location[0])
                                _checkpath_moves = _checkpath_moves 
                            elif 'pawn' not in _piece_location[1]:      
                                _piece_details = self.piece_movement.piece_move_count(_piece_location, grid)
                                _checkpath_moves = self._moveassigner.piece_possible_moves(grid, _piece_location, _piece_details) 

                                if _checkpath_moves:
                                    if _player_check_tile[0] in _checkpath_moves[2] and _current_location[0] in _checkpath_moves[0]:
                                        _checking_letter = self.board.letters.index(_main_move[0])
                                        _checked_letter = self.board.letters.index(_king_tile[0])
                                        _checked_number: int = int(_king_tile[1])
                                        _checking_number: int = (int(_main_move[1]))
                                        _direct_checkpath: set[str] = set()
                                        
                                        # utilized when a contested tile possesses a king  
                                        def validate_pinning(condition, _check_tile, _nummin=0, _nummax=0, _letmin=0, _letmax=0, _direct_checkpath=_direct_checkpath, 
                                                            _check_paths=_check_paths, _potential_mate=_potential_mate, _current_location=_current_location):

                                            if condition == 'condition_one':
                                                for _number in range(_nummin, _nummax + 1): 
                                                    _direct_checkpath.add(f'{_check_tile}{_number}') 
                                            elif condition == 'condition_two':
                                                for _letter in range(_letmin, _letmax + 1):
                                                    _direct_checkpath.add(f'{self.board.letters[_letter]}{_check_tile}') 
                                            elif condition == 'condition_three':
                                                while _letmin <= _letmax and _nummax >= _nummin:
                                                    _direct_checkpath.add(f'{self.board.letters[_letmin]}{_nummax}')
                                                    _letmin += 1
                                                    _nummax -= 1
                                            elif condition == 'condition_four':
                                                while _nummax >= _letmin and _nummin <= _nummax: 
                                                    _direct_checkpath.add(f'{self.board.letters[_letmax]}{_nummin}')
                                                    _letmax -= 1
                                                    _nummin += 1
                                            elif condition == 'condition_five':
                                                while _letmin <= _letmax and _nummin <= _nummax: 
                                                    _direct_checkpath.add(f'{self.board.letters[_letmin]}{_nummin}')
                                                    _letmin += 1
                                                    _nummin += 1
                                            elif condition == 'condition_six':       
                                                while _letmax >=_letmin and _nummax >= _nummin: 
                                                    _direct_checkpath.add(f'{self.board.letters[_letmax]}{_nummax}')
                                                    _letmax -= 1
                                                    _nummax -= 1
                                            return check_potential_counter(_check_paths, _potential_mate, _current_location, _direct_checkpath)
                                        
                                        # condition 1
                                        if _checking_letter == _checked_letter: 
                                            if _checking_number < _checked_number:
                                                _check_paths, _potential_mate = validate_pinning('condition_one', _king_tile[0], 
                                                                                                _nummin=_checking_number, _nummax=_checked_number)
                                            elif _checking_number > _checked_number:         
                                                _check_paths, _potential_mate = validate_pinning('condition_one', _king_tile[0], 
                                                                                                _nummin=_checked_number, _nummax=_checking_number)                            
                                        # condition 2 
                                        elif _checking_number == _checked_number: 
                                            if _checking_letter < _checked_number:       
                                                _check_paths, _potential_mate = validate_pinning('condition_two', _king_tile[1], 
                                                                                                _letmin=_checking_letter, _letmax=_checked_letter)                                 
                                            elif _checking_letter > _checked_letter:    
                                                _check_paths, _potential_mate = validate_pinning('condition_two', _king_tile[1], 
                                                                                                _letmin=_checked_letter, _letmax=_checking_letter)                                    
                                        # condition 3
                                        elif _checking_letter < _checked_letter and _checking_number > _checked_number:
                                            _check_paths, _potential_mate = validate_pinning('condition_three', _king_tile[1], 
                                                                                            _nummin=_checked_number, _nummax=_checking_number, 
                                                                                            _letmin=_checking_letter, _letmax=_checked_letter)    
                                        # condition 4
                                        elif _checking_letter > _checked_letter and _checking_number < _checked_number: 
                                            _check_paths, _potential_mate = validate_pinning('condition_four', _king_tile[1], 
                                                                                            _nummin=_checking_number, _nummax=_checked_number, 
                                                                                            _letmin=_checked_letter, _letmax=_checking_letter) 
                                        # condition 5
                                        elif _checking_letter < _checked_letter and _checking_number < _checked_number:            
                                            _check_paths, _potential_mate = validate_pinning('condition_five', _king_tile[1], 
                                                                                            _nummin=_checking_number, _nummax=_checked_number, 
                                                                                            _letmin=_checking_letter , _letmax=_checked_letter) 
                                        # condition 6
                                        elif _checking_letter > _checked_letter and _checking_number > _checked_number:    
                                            _check_paths, _potential_mate = validate_pinning('condition_six', _king_tile[1], 
                                                                                            _nummin=_checked_number, _nummax=_checking_number, 
                                                                                            _letmin=_checked_letter, _letmax=_checking_letter) 
            log(2, f'check path verifier king not in current location:{sorted(_check_paths), _potential_mate}\n\n')
            return sorted(_check_paths), _potential_mate
