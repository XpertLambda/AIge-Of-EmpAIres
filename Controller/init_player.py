from Models.Team import Team

def init_players(number_of_players, difficulty):
    players = []
    for playerId in range(number_of_players):
        team = Team(difficulty, playerId)
        players.append(team)
    return players