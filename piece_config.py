from logging import log 
#   an active and inactive piece row and column data as the variable grid_tile, 
#   the set of possible moves available to all pieces on the board with a clear path to the active tile
#   the boards grid data
#   the location of the active or inactive tile and tile data
# it is responsible for adding tiles that are not in conflict with active tile and the 
class PieceMovement:

    def piece_moves( self, _location: tuple[str, str, str]): 
        if 'pawn' in _location[1]: return _location[0], 'pawn', 2
        elif 'king' in _location[1]: return _location[0], 'king', 1
        elif 'rook' in _location[1]: return _location[0], 'rook', 8
        elif 'queen'  in _location[1]: return _location[0], 'queen', 8
        elif 'knight' in _location[1]: return _location[0], 'knight', 3
        elif 'bishop' in _location[1]: return _location[0], 'bishop', 8
 
    def piece_move_count(self, _location: tuple[str, str, str], grid: list[list[str]]):
        for index in range(8):
            for _tiles in grid:
                for _tile in _tiles:
                    if _tile in _location:  
                        _piece_details = self.piece_moves(_location)
                        if _location[0] in grid[index] and _piece_details != None: 
                            row = index + 1
                            return row, _piece_details
        return 0, ('', '', 0)    

    def showpath(self, grid_tile: tuple[int, int], _possible_moves: set[str], grid: list[list[str]], _location: tuple[str, str, str]):    
        if grid_tile[0] < 8 and grid_tile[1] < 8 and grid_tile[0] >= 0 and grid_tile[1] >= 0:
            _active = grid[grid_tile[0]][grid_tile[1]]       
            if _active not in _possible_moves and _active not in _location[0]: 
                return _possible_moves.add(_active)

    def horizontal_vertical_movement(self, _location: tuple[str, str, str], _row: int,  _col: int,_move:int, _possible_moves: set[str], grid: list[list[str]]):
        move_sets = ((_row - _move, _col), (_row, _col - _move),
                    (_row + _move, _col), (_row, _col + _move))
        for move_set in move_sets: _ = self.showpath(move_set, _possible_moves, grid, _location )
        
    def diagonal_movement(self, _location: tuple[str, str, str], _row: int,  _col: int,_move:int, _possible_moves: set[str], grid: list[list[str]]):
        move_sets_p1 = ((_row - _move, _col - _move), (_row + _move, _col - _move),
                        (_row - _move, _col + _move), (_row + _move, _col + _move))
        move_sets_p2 = ((_row - _move, _col + _move), (_row + _move, _col + _move),
                        (_row + _move, _col - _move), (_row - _move, _col - _move))
        if 'p1' in _location[2]:
            for move_set in move_sets_p1: _ = self.showpath(move_set, _possible_moves, grid, _location )
        elif 'p2' in _location[2]:
            for move_set in move_sets_p2: _ = self.showpath(move_set, _possible_moves, grid, _location )

    def king_movement(self, _location: tuple[str, str, str], _piece_details: tuple[int, tuple[str, str, int]],_row: int,  _col: int, _possible_moves: set[str], grid: list[list[str]], check_piece):
        for _move in range(1, _piece_details[1][2] + 1): 
            _move_grid = [(_row, _col), (_row, _col + _move), (_row, _col - _move), (_row - _move, _col), (_row + _move, _col), (_row - 1, _col - _move),
                        (_row - 1, _col + _move), (_row + 1, _col - _move), (_row + 1, _col + _move)]
            # add castling tiles
            if check_piece: 
                _move_grid.insert(0, (_row, _col - _move - 1))
                _move_grid.append((_row, _col + _move + 1))
            for indx in range(len(_move_grid)):   
                _active = _move_grid[indx]
                _ = self.showpath((_active[0], _active[1]), _possible_moves, grid, _location)

    def knight_movement(self,_location: tuple[str, str, str], _row: int,  _col: int, _possible_moves: set[str], grid: list[list[str]]):           
        _grid_pos_set1 = ((_row + 2, _col - 1), (_row + 2, _col + 1), (_row + 1, _col - 2), (_row + 1, _col + 2))
        _grid_pos_set2 = ((_row - 2, _col + 1), (_row - 2, _col - 1), (_row - 1, _col + 2), (_row - 1, _col - 2))

        def incremental_movement(_row: int=_row, _possible_moves: set[str]=_possible_moves, grid: list[list[str]]=grid, _location:  tuple[str, str, str]=_location):
            if _row!= 7 and _row!= 0: 
                for _data in _grid_pos_set1: _ = self.showpath(_data, _possible_moves, grid, _location)   
            for _data in _grid_pos_set2: _ = self.showpath(_data, _possible_moves, grid, _location) 
            
        def decremental_movement(_row: int=_row, _possible_moves: set[str]=_possible_moves, grid: list[list[str]]=grid, _location:  tuple[str, str, str]=_location):
            if _row!= 7 and _row!= 0: 
                for _data in _grid_pos_set2: _ = self.showpath(_data, _possible_moves, grid, _location)     
            for _data in _grid_pos_set1: _ = self.showpath(_data, _possible_moves, grid, _location) 

        _active_row = int(_location[0][1])
        if   _active_row < 5: incremental_movement()
        elif _active_row > 4: decremental_movement() 
        
    def bishop_movement(self, _location: tuple[str, str, str], _row: int,  _col: int, _possible_moves: set[str], grid: list[list[str]]):
        for _move in range(1,  9): self.diagonal_movement(_location, _row, _col, _move, _possible_moves, grid)

    def pawn_movement(self, _location: tuple[str, str, str], _piece_details: tuple[int, tuple[str, str, int]],_row: int,  _col: int, _possible_moves: set[str], grid: list[list[str]]):

        for _move in range( 1, _piece_details[1][2] + 1 ): 
            active_row = int(_location[0][1])
            move_set = ((_row - _move, _col), (_row - 1, _col), (_row + _move, _col), (_row + 1, _col))

            if 'p1' in _location[2]: 
                # if the player is p1 moves direction is 1 -> 8 
                if active_row == 2: 
                    _ = self.showpath(move_set[0], _possible_moves, grid, _location)  # move_set[0] is used for the first pawn move for p1
                else: 
                    _ = self.showpath(move_set[1], _possible_moves, grid, _location) # move_set[1] is used for any other pawn move for p1
                    break
            # if the player is p1 moves direction is 8 -> 1 
            elif 'p2' in _location[2]:
                if active_row == 7: 
                    _ = self.showpath(move_set[2], _possible_moves, grid, _location) # move_set[0] is used for the first pawn move for p2
                else: 
                    _ = self.showpath(move_set[3], _possible_moves, grid, _location) # move_set[1] is used for any other pawn move for p2
                    break

    def rook_movement(self, _location: tuple[str, str, str], _piece_details: tuple[int, tuple[str, str, int]],_row: int,  _col: int, _possible_moves: set[str], grid: list[list[str]]):
        for _move in range( 1, _piece_details[1][2] + 1 ): self.horizontal_vertical_movement(_location,_row, _col, _move, _possible_moves, grid)

    def queen_movement(self, _location: tuple[str, str, str], _piece_details: tuple[int, tuple[str, str, int]],_row: int,  _col: int, _possible_moves: set[str], grid: list[list[str]]):
        for _move in range(1, _piece_details[1][2] + 1): self.horizontal_vertical_movement(_location,_row, _col, _move, _possible_moves, grid)
        for _move in range(1,  9): self.diagonal_movement(_location, _row, _col, _move, _possible_moves, grid)