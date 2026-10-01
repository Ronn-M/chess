from logging import log
from queue import Queue

from kivy.uix.widget import Widget
from kivymd.uix.button.button import MDExtendedFabButtonIcon

from ui_assets import PlayerTradedPieceList 

class TileHandler:
    def __init__(self, screen: Widget, _activated_tiles: Queue[set[str]], _verified_tiles: set[str]) -> None:
        self.screen = screen
        self._verified_tiles = _verified_tiles
        self.activated_tiles = _activated_tiles
        self.empty_tile = "pieces/tempbg.png"

    def clear_active_tiles(self) -> None: 
        while not self.activated_tiles.empty():
            _active_move = self.activated_tiles.get()
            if _active_move != 'break':
                if _active_move != None and self.screen.ids[ f'{_active_move}_overlay'].source != self.empty_tile: 
                    self.screen.ids[ f'{_active_move}_overlay'].source = self.empty_tile
        self._verified_tiles.clear()

    '''for readability, the following function will be modified as it currently produces bugs during gameplay'''   
    def display_traded_pieces(self, _pieces_set: set[str]): 
        def add_traded(_x_data: float, _y_data: float, _piece: str):
            self.screen.add_widget(PlayerTradedPieceList(MDExtendedFabButtonIcon(source=_piece), 
                                                            pos_hint={"center_x": _x_data,
                                                                        "center_y": _y_data}))   
            _y_data += 0.019
            return _y_data

        def position_updater(_piece: str, piece_data: dict):
            _x1, _x2, _y1, _y2 = piece_data['x1'], piece_data['x2'], piece_data['y1'], piece_data['y2']
            if 'p1' in _piece: piece_data['y1'] = add_traded(_x1, _y1, _piece)
            if 'p2' in  _piece: piece_data['y2'] = add_traded(_x2, _y2 , _piece)
        self._rook_data = {'x1': 0.95,  'x2': 0.09, 'y1': 0.715, 'y2': 0.275}
        self._pawn_data = {'x1': 0.885, 'x2': 0.155, 'y1': 0.625, 'y2': 0.185}
        self._queen_data = {'x1': 0.885, 'x2': 0.155, 'y1': 0.825, 'y2': 0.385}
        self._bishop_data = {'x1': 0.95,  'x2': 0.09, 'y1': 0.807, 'y2': 0.365}
        self._knight_data = {'x1': 0.95,  'x2': 0.09, 'y1': 0.625, 'y2': 0.185}
        for _piece in _pieces_set:
            if 'pawn' in _piece: position_updater(_piece, self._pawn_data) 
            elif 'rook' in _piece: position_updater(_piece, self._rook_data)
            elif 'queen' in _piece: position_updater(_piece, self._queen_data)
            elif 'bishop' in _piece: position_updater(_piece, self._bishop_data)
            elif 'knight' in _piece: position_updater(_piece, self._knight_data)
    