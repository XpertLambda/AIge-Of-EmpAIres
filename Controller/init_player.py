from Models.Team import Team
from Settings.setup import DIFFICULTY

def init_players(number_of_players):
    players = []
    for playerId in range(number_of_players):
        team = Team(DIFFICULTY, playerId)
        players.append(team)
    return players
