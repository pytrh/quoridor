class Observer:
    def update_timer(self, time: int, player_id: int):
        """Update the timer"""
        pass

    def handle_timer_end_for_player(self, player_id: int):
        """End the game or pass to another player when
        the timer stop for the current player"""
        pass
