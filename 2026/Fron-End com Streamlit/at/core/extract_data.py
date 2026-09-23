from statsbombpy import sb
import pandas as pd


def extract_competitions_info(competition_id: int | None = 43) -> pd.DataFrame:
    """Acessa a API da StatsBomb e retorna as competições disponíveis.
    Se um ID for fornecido, filtra apenas as temporadas daquela competição.
    """
    competitions = sb.competitions()

    if competition_id is None:
        return competitions
    
    filtered_competitions = competitions[competitions['competition_id'] == competition_id]
    return filtered_competitions


def extract_matches_info(competitions_df: pd.DataFrame) -> pd.DataFrame:
    """Recebe um DataFrame de competições (filtradas ou completas) e extrai 
    todas as partidas de cada temporada listada, identificando o ID do torneio dinamicamente.
    """
    if competitions_df.empty:
        return pd.DataFrame()

    matches_list = []

    for _, row in competitions_df.iterrows():
        competition_id = row['competition_id']
        season_id = row['season_id']

        try:
            match = sb.matches(competition_id=competition_id, season_id=season_id)
            matches_list.append(match)
        except Exception as e:
            print(f"Erro ao buscar partidas da competição {competition_id}, temporada {season_id}: {e}")

    if not matches_list:
        return pd.DataFrame()

    matches = pd.concat(matches_list, ignore_index=True)
    seasons_map = competitions_df.set_index('season_id')['season_name'].to_dict()
    matches['season'] = matches['season_id'].map(seasons_map)

    final_columns = ['match_id', 'match_date', 'home_team', 'away_team', 'home_score', 'away_score', 'season']
    matches = matches[final_columns]

    return matches


def extract_players_info(matches_df: pd.DataFrame) -> pd.DataFrame:
    """Recebe o DataFrame de partidas e extrai uma lista única de jogadores 
    que atuaram nelas, vinculando-os ao time e à respectiva temporada.
    """
    if matches_df.empty:
        return pd.DataFrame()

    players = []
    
    match_to_season_map = matches_df.set_index('match_id')['season'].to_dict()

    for match_id in matches_df['match_id'].unique():
        try:
            lineup = sb.lineups(match_id=match_id)
            
            for team_name, players_df in lineup.items():
                players_df['team_name'] = team_name
                players_df['season'] = match_to_season_map.get(match_id)
                players.append(players_df)
        except Exception:
            continue

    if not players:
        return pd.DataFrame()

    all_players_df = pd.concat(players, ignore_index=True)
    
    final_columns = ['player_id', 'player_name', 'player_nickname', 'jersey_number', 'country', 'team_name', 'season']
    final_players_df = all_players_df[final_columns].drop_duplicates()

    return final_players_df