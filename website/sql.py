
from sqlalchemy.sql import text
from . import db


def top_10_winrates():

    return db.session.execute(text("""SELECT 
  user.first_name AS player, 
  TRUNCATE(ROUND(COUNT(CASE WHEN victory = 1 THEN 1 ELSE NULL END) / COUNT(*) * 100, 0), 0) AS winrate,
  user.id AS id,
  user.photo AS photo
FROM rounds 
JOIN user_rounds ON rounds.id = user_rounds.round_id
JOIN user ON user_rounds.user_id = user.id
GROUP BY player 
HAVING COUNT(*) > 0
ORDER BY winrate DESC 
LIMIT 10;"""))


def games_query():
    return db.session.execute(text("""SELECT DISTINCT games.place, games_details.game_number, rounds.number, rounds.victory, user.first_name
FROM games
LEFT JOIN games_details ON games.id = games_details.game_number
LEFT JOIN rounds ON games_details.round = rounds.id
LEFT JOIN user ON rounds.player = user.id
ORDER BY games.place"""))
