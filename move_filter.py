
from kivy.uix.widget import Widget
from board_generator import GenerateBoard


class MoveFilter:
    
    def __init__(self, screen: Widget, board: GenerateBoard):
        self.board = board
        self.screen = screen
        self.empty_tile = "pieces/tempbg.png"
        self.overlay = 'img_data/overlay.png' 
        self.check_overlay ='img_data/check_overlay.png'

    def pawn_tile_possession_handler(self, _location: tuple[str, str, str]): 
    
            _tile1, _tile2 = '', ''
            _letter_index, _number_index = self.board.letters.index(_location[0][0]), self.board.numbers.index(_location[0][1]) 
            if _location[2] == 'p1':
                if _location[0][0] == 'h':   _tile1 = self.board.letters[_letter_index - 1] + self.board.numbers[_number_index - 1] 
                elif _location[0][0] == 'a': _tile2 = self.board.letters[_letter_index + 1] + self.board.numbers[_number_index - 1]
                else:
                    _tile1 = self.board.letters[_letter_index - 1] + self.board.numbers[_number_index - 1]
                    _tile2 = self.board.letters[_letter_index + 1] + self.board.numbers[_number_index - 1]
            elif _location[2] == 'p2':  
                if _location[0][0] == 'h':   _tile1 = self.board.letters[_letter_index - 1] + self.board.numbers[_number_index + 1] 
                elif _location[0][0] == 'a': _tile2 = self.board.letters[_letter_index + 1] + self.board.numbers[_number_index + 1]
                else:
                    _tile1 = self.board.letters[_letter_index - 1] + self.board.numbers[_number_index + 1]
                    _tile2 = self.board.letters[_letter_index + 1] + self.board.numbers[_number_index + 1]
            return _tile1, _tile2

    def pop_item(self: object, _item: str, _dataset: set[str]) -> set:  
        if _item in _dataset:          
            _dataset.remove(_item)       
        return _dataset

    '''for readability, the following function will be modified to reduce reading complexity'''   
    def lolat_move_assigner(self, _location: tuple[str, str, str], _filtered_moves_set: set[str], _tile_possession_tile_data_set: set[str]): 
        _lolat_piecepaths_dict = {}
        def tile_checker(_location: tuple[str, str, str]=_location, _tile_possession_tile_data_set: set[str]=_tile_possession_tile_data_set):           
            def vertical_checks(_location: tuple[str, str, str]=_location, _tile_possession_tile_data_set: set[str]=_tile_possession_tile_data_set):            
                _verticalset1 = set()
                _verticalset2 = set()
                _verticalset3 = set()
                _verticalset4 = set()
                
                # vertical checks
                if int(_location[0][1]) < 5:
                    for _letter in self.board.letters:
                        for _indx, _number in enumerate(reversed(self.board.numbers)):                            
                            if _indx >= int(_location[0][1]):
                                if int(_number) > int(_location[0][1]) and _letter in _location[0]: 
                                    _move = _letter + _number
                                    _moveset = self.add_move_assigner(_move, _location, _verticalset1, _tile_possession_tile_data_set)
                                    if _moveset == 'break': break

                    for _letter in self.board.letters:
                        for _number in self.board.numbers:
                            if int(_number) <= int(_location[0][1]):
                                if int(_number) < int(_location[0][1]) and _letter in _location[0]: 
                                    _move = _letter + _number
                                    _moveset = self.add_move_assigner(_move, _location, _verticalset2, _tile_possession_tile_data_set)
                                    if _moveset == 'break': break
                
                if int(_location[0][1]) > 4:
                    for _letter in self.board.letters:
                        for _number in self.board.numbers:      
                            if int(_number) <= int(_location[0][1]):
                                if int(_number) < int(_location[0][1]) and _letter in _location[0]:                   
                                    _move = _letter + _number
                                    _moveset = self.add_move_assigner(_move, _location, _verticalset3, _tile_possession_tile_data_set)
                                    if _moveset == 'break': break
                        
                    for _letter in self.board.letters:
                        for _number in reversed(self.board.numbers):
                            if int(_number) >= int(_location[0][1]):
                                if int(_number) > int(_location[0][1]) and _letter in _location[0]:     
                                    _move = _letter + _number
                                    _moveset = self.add_move_assigner(_move, _location, _verticalset4, _tile_possession_tile_data_set)
                                    if _moveset == 'break': break
                _lolat_piecepaths_dict['lolat_vertical'] = [_verticalset1, _verticalset2, _verticalset3, _verticalset4]
            
            def horizontal_checks(_location: tuple[str, str, str]=_location, _tile_possession_tile_data_set: set[str]=_tile_possession_tile_data_set):
                _horizontalset1 = set()
                _horizontalset2 = set()
                _horizontalset3 = set()
                _horizontalset4 = set()
                
                # horizontal checks   
                _pos_letter_index = self.board.letters.index(_location[0][0]) + 1
                if _pos_letter_index < 5:
                    for _number in reversed(self.board.numbers):
                        for _indx, _letter in enumerate(self.board.letters):   
                            _letter_index = self.board.letters.index(_letter) + 1 
                            if _indx >= _pos_letter_index:
                                if _number in _location[0] and _letter_index > _pos_letter_index:              
                                    _move = _letter + _number
                                    _moveset = self.add_move_assigner(_move, _location, _horizontalset1, _tile_possession_tile_data_set)
                                    if _moveset == 'break': break

                    for _number in reversed(self.board.numbers):
                        for _letter in reversed(self.board.letters):     
                            _letter_index = self.board.letters.index(_letter) + 1 
                            if _letter_index <= _pos_letter_index:
                                if _number in _location[0] and _letter_index < _pos_letter_index:               
                                    _move = _letter + _number
                                    _moveset = self.add_move_assigner(_move, _location, _horizontalset2, _tile_possession_tile_data_set)
                                    if _moveset == 'break': break
                                    
                if _pos_letter_index > 4:
                    for _number in reversed(self.board.numbers):
                        for _letter in reversed(self.board.letters):        
                            _letter_index = self.board.letters.index(_letter) + 1 
                            if _letter_index <= _pos_letter_index:
                                if _number in _location[0] and _letter_index < _pos_letter_index:                  
                                    _move = _letter + _number
                                    _moveset = self.add_move_assigner(_move, _location, _horizontalset3, _tile_possession_tile_data_set)
                                    if _moveset == 'break': break
                    
                    for _number in reversed(self.board.numbers):
                        for _letter in self.board.letters:        
                            _letter_index = self.board.letters.index(_letter) + 1 
                            if _letter_index >= _pos_letter_index:
                                if _number in _location[0] and _letter_index > _pos_letter_index:                 
                                    _move = _letter + _number
                                    _moveset = self.add_move_assigner(_move, _location, _horizontalset4, _tile_possession_tile_data_set)
                                    if _moveset == 'break': break
                _lolat_piecepaths_dict['lolat_horizontal'] = [_horizontalset1, _horizontalset2, _horizontalset3, _horizontalset4]
            
            vertical_checks()
            horizontal_checks()
        
        def merge_filtered_moves(_sets: dict, _filtered_moves_set: set[str]=_filtered_moves_set):
            for _dataset in _sets.values():
                for _data in _dataset: 
                    for _move in _data: _filtered_moves_set.add(_move)
    
        tile_checker()                
        merge_filtered_moves(_lolat_piecepaths_dict)      
        return _lolat_piecepaths_dict

    '''for readability, the following function will be modified to reduce reading complexity'''   
    def diagonal_move_assigner(self, _location: tuple[str, str, str], _filtered_moves_set: set[str], _tile_possession_tile_data_set: set[str]): 
        _diagonal_piecepaths_dict = {}
        
        def tile_checker(_location: tuple[str, str, str]=_location, _tile_possession_tile_data_set: set[str]=_tile_possession_tile_data_set): 
            # vertical \/ checks 
            def vertical_td_checks(_location: tuple[str, str, str]=_location, _tile_possession_tile_data_set: set[str]=_tile_possession_tile_data_set):             
                _diagonal_td_set1 = set()
                _diagonal_td_set2 = set()
                _diagonal_td_set3 = set()
                _diagonal_td_set4 = set()
                
                numbers_set = [item for item in reversed(self.board.numbers)]
                _pos_letter_index = self.board.letters.index(_location[0][0]) + 1
                _pos_number_index = numbers_set.index(_location[0][1]) + 1    

                # validate moveset functions to be refactored in future update
                def validate_moveset_1(_diagonal_set): 
                    for _letter in self.board.letters:
                        _letter_index = self.board.letters.index(_letter) + 1                       
                        _new_number = _pos_letter_index - _letter_index + _pos_number_index
                        _move = _letter + str(_new_number)                      
                        if _letter_index >= _pos_letter_index and _new_number > 0 and _new_number < 9:
                            if str(_new_number) not in _location[0] and _new_number <= _pos_number_index: 
                                _moveset = self.add_move_assigner(_move, _location, _diagonal_set, _tile_possession_tile_data_set)
                                if _moveset == 'break': break

                def validate_moveset_2(_diagonal_set):
                    for _letter in reversed(self.board.letters):
                        _letter_index = self.board.letters.index(_letter) + 1                        
                        _new_number = _letter_index - _pos_letter_index + _pos_number_index
                        _move = _letter + str(_new_number)                       
                        if _letter_index <= _pos_letter_index and _new_number > 0 and _new_number < 9: 
                            if str(_new_number) not in _location[0] and _new_number <= _pos_number_index:                            
                                _moveset = self.add_move_assigner(_move, _location, _diagonal_set, _tile_possession_tile_data_set)
                                if _moveset == 'break': break
                                                         
                if _pos_letter_index > 4:    
                    validate_moveset_1(_diagonal_td_set1)
                    validate_moveset_2(_diagonal_td_set2)    
                if _pos_letter_index < 5:   
                    validate_moveset_1(_diagonal_td_set3)
                    validate_moveset_2(_diagonal_td_set4)                         
                _diagonal_piecepaths_dict['diagonal_vertical_td'] = [_diagonal_td_set1, _diagonal_td_set2, _diagonal_td_set3, _diagonal_td_set4]
            
            # vertical /\ checks                         
            def vertical_bu_checks(_location: tuple[str, str, str]=_location, _tile_possession_tile_data_set: set[str]=_tile_possession_tile_data_set):
                diagonal_bu_set1 = set()
                diagonal_bu_set2 = set()
                diagonal_bu_set3 = set()
                diagonal_bu_set4 = set()
                    
                numbers_set = [item for item in reversed(self.board.numbers)]
                _pos_letter_index = self.board.letters.index(_location[0][0]) + 1
                _pos_number_index = numbers_set.index(_location[0][1]) + 1
                def validate_moveset_1(_diagonal_set): # rename function
                    for _letter in reversed(self.board.letters):
                        _letter_index = self.board.letters.index (_letter) + 1                        
                        _new_number = _pos_letter_index - _letter_index + _pos_number_index
                        _move = _letter + str(_new_number)                       
                        if _letter_index <= _pos_letter_index and _new_number > 0 and _new_number < 9:
                            if str(_new_number) not in _location[0] and _new_number >= _pos_number_index: 
                                _moveset = self.add_move_assigner(_move, _location, _diagonal_set, _tile_possession_tile_data_set)
                                if _moveset == 'break': break

                def validate_moveset_2(_diagonal_set): # rename function
                    for _letter in self.board.letters:
                        _letter_index = self.board.letters.index (_letter) + 1 
                        _new_number = _letter_index - _pos_letter_index + _pos_number_index
                        _move = _letter + str(_new_number) 
                        if _letter_index >= _pos_letter_index and _new_number > 0 and _new_number < 9:
                            if str(_new_number) not in _location[0] and _new_number >= _pos_number_index:
                                _moveset = self.add_move_assigner(_move, _location, _diagonal_set, _tile_possession_tile_data_set)
                                if _moveset == 'break': break

                if _pos_letter_index < 5: 
                    validate_moveset_1(diagonal_bu_set1) 
                    validate_moveset_2(diagonal_bu_set2)                          
                if _pos_letter_index > 4:
                    validate_moveset_1(diagonal_bu_set3)
                    validate_moveset_2(diagonal_bu_set4)           
                _diagonal_piecepaths_dict['diagonal_vertical_bu'] = [diagonal_bu_set1, diagonal_bu_set2, diagonal_bu_set3, diagonal_bu_set4]
            
            vertical_td_checks()
            vertical_bu_checks()
        
        def merge_filtered_moves(sets: dict, _filtered_moves_set: set[str]=_filtered_moves_set):

            for _dataset in sets.values():
                for _data in _dataset: 
                    for _move in _data:_filtered_moves_set.add(_move)
        
        tile_checker()                  
        merge_filtered_moves(_diagonal_piecepaths_dict)
        return _diagonal_piecepaths_dict    

    '''for readability, the following function will be modified to reduce reading complexity'''   
    def add_move_assigner(self, _move: str, _location: tuple[str, str, str], _filtered_moves_set: set[str], _tile_possession_tile_data_set: set[str]): 

        _current_tile_overlay = self.screen.ids[f'{_move}_overlay']
        _current_tile_image = self.screen.ids[f'{_move}_image']
        
        if _location[2] in _current_tile_image.source: return 'break'
        else:
            if 'king' not in _location[1]:
                if 'king' in _current_tile_image.source and _location[2] not in _current_tile_image.source: 
                    if _current_tile_image.source != self.empty_tile:
                        _current_tile_overlay.source = self.check_overlay
                        _filtered_moves_set.add(_move)
                        _tile_possession_tile_data_set.add(_move)
                        return 'check'
                elif 'king' not in _current_tile_image.source and _current_tile_image.source != self.empty_tile:
                    if _move not in _filtered_moves_set:
                        _filtered_moves_set.add(_move)
                        _tile_possession_tile_data_set.add(_move)
                        return 'break' 
                elif 'king' not in _current_tile_image.source and _current_tile_image.source == self.empty_tile:
                    if _move not in _filtered_moves_set:
                        _filtered_moves_set.add(_move)
                        _tile_possession_tile_data_set.add(_move)

            elif 'king' in _location[1]: #checked king error
                if 'king' not in _current_tile_image.source and _current_tile_image.source != self.empty_tile:
                    if _move not in _filtered_moves_set:
                        _filtered_moves_set.add(_move)
                        _tile_possession_tile_data_set.add(_move)
                        return 'break' 
                elif 'king' not in _current_tile_image.source and _current_tile_image.source == self.empty_tile:
                    if _move not in _filtered_moves_set:
                        _filtered_moves_set.add(_move)
                        _tile_possession_tile_data_set.add(_move)      

    def king_move_assigner(self, _location: tuple[str, str, str], _possible_moves: set, _filtered_moves_set: set[str], _tile_possession_tile_data_set: set[str]): 
        for _move in _possible_moves:
            _current_tile_image = self.screen.ids[f'{_move}_image']
            if _location[2] in _current_tile_image.source: pass
            else:      
                _filtered_moves_set.add(_move)
                _tile_possession_tile_data_set.add(_move)

    def knight_filtered_moves(self, _location: tuple[str, str, str], _possible_moves: set, _filtered_moves_set: set[str], _tile_possession_tile_data_set: set[str], validate=True):
   
        if _possible_moves:
            for _move in _possible_moves:
                from logging import log
                _current_tile_overlay = self.screen.ids[f'{_move}_overlay']
                _current_tile_image = self.screen.ids[f'{_move}_image']
                if 'king' in _current_tile_image.source and _location[2] not in _current_tile_image.source:
                    if _current_tile_image.source != self.empty_tile:
                        if validate == True:
                            _current_tile_overlay.source = self.check_overlay
                        _filtered_moves_set.add(_move)
                        _tile_possession_tile_data_set.add(_move) 
                        return True

                elif  'king' not in _current_tile_image.source and _location[2] not in _current_tile_image.source:
                    if _location[2] in _current_tile_image.source: pass
                    elif _current_tile_image.source != self.empty_tile:
                        if _move not in _filtered_moves_set:
                            _filtered_moves_set.add(_move)
                            _tile_possession_tile_data_set.add(_move)      
                    elif _current_tile_image.source == self.empty_tile:
                        if _move not in _filtered_moves_set:
                            _filtered_moves_set.add(_move)
                            _tile_possession_tile_data_set.add(_move)