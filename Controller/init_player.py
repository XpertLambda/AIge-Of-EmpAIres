from Models.Team import Team
from Settings.setup import DIFFICULTY

def init_players(number_of_players):
    players = []
    for playerId in range(number_of_players):
        team = Team(DIFFICULTY, playerId)
        print(team.maximum_population)
        print("ENTRE DANS LA METHODE INIT_PLAYERS")
        players.append(team)
    return players
