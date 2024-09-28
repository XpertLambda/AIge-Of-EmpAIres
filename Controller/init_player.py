from Models.Team import Team
from Settings.setup import DIFFICULTY

def init_players(game_map):
    players = []
    for player in range(game_map.numberOfPlayers):
        team = Team(DIFFICULTY)
        players.append(team)
        
    return players