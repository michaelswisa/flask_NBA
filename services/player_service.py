from db import db
from models.player import Player
from requests import request


def get_players(year):
    url_players = rf'http://b8c40s8.143.198.70.30.sslip.io/api/PlayerDataTotals/query?season={year}&&pageSize=1000'
    players_response = request(url=url_players, method='GET')
    return players_response.json()


def load_data_players_from_request(*args):
    players_list = []
    for year in args:
        response = get_players(year)
        players_list.extend(response)
    return players_list


def create_player_to_db(player):
    avg_points = get_avg_points_per_season(player['position'], player['season'])

    if player['games'] != 0 and avg_points != 0:
        PPG_Ratio = (player['points'] / player['games']) / avg_points
    else:
        PPG_Ratio = 0
    player_model = Player(
        playerName=player['playerName'],
        team=player['team'],
        position=player['position'],
        points=player['points'],
        season=player['season'],
        games=player['games'],
        twoPercent=player['twoPercent'],
        threePercent=player['threePercent'],
        ATR=player['assists'] / player['turnovers'] if player['turnovers'] > 0 else 0,
        playerId=player['playerId'],
        PPG_Ratio=PPG_Ratio
    )
    return player_model


def save_player_to_db(player):
    try:
        db.session.add(player)
        db.session.commit()
    except Exception as e:
        print(f'Error while saving player to DB: {e}')
        db.session.rollback()


def load_and_save_players_to_db(years_list):
    players = load_data_players_from_request(*years_list)
    for player in players:
        player_model = create_player_to_db(player)
        save_player_to_db(player_model)
    return


def get_avg_points_per_season(position, season):
    players = Player.query.filter_by(position=position, season=season).all()
    total_points = sum(player.points for player in players)
    total_games = sum(player.games for player in players)
    return total_points / total_games if total_games!= 0 else 0







if __name__ == '__main__':
    load_and_save_players_to_db([2022, 2023, 2024])
