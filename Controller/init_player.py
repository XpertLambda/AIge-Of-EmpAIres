from Models.Team import Team
from Settings.setup import DIFFICULTY

def init_players(NUMBER_OF_PLAYERS):
    players = []
    for playerId in range(NUMBER_OF_PLAYERS):
        team = Team(DIFFICULTY, playerId)
        players.append(team)
        
    return players
