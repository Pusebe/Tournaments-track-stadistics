
from sqlalchemy.sql import text
from . import db


def get_users_by_winrate(year=None, limit=None):
    """
    Obtiene usuarios ordenados por winrate, con opción de filtrar por año y limitar resultados.
    
    :param year: Año para filtrar los resultados (opcional, None para todos los años).
    :param limit: Número máximo de resultados (opcional, None para todos).
    :return: Resultado de la consulta SQL.
    """
    query = """
    SELECT 
        ROW_NUMBER() OVER (ORDER BY TRUNCATE(ROUND(COUNT(CASE WHEN victory = 1 THEN 1 ELSE NULL END) / COUNT(*) * 100, 0), 0) DESC) AS position,
        TRUNCATE(ROUND(COUNT(CASE WHEN victory = 1 THEN 1 ELSE NULL END) / COUNT(*) * 100, 0), 0) AS winrate,
        COUNT(victory) AS played,
        SUM(victory) AS won,
        user.*
    FROM rounds 
    JOIN user_rounds ON rounds.id = user_rounds.round_id
    JOIN user ON user_rounds.user_id = user.id
    JOIN games ON rounds.game_number = games.id
    """

    # Agregar filtro por año si se proporciona
    if year is not None:
        query += " WHERE EXTRACT(YEAR FROM rounds.created_at) = :year"

    query += """
    GROUP BY user.id
    HAVING COUNT(*) > 0
    ORDER BY winrate DESC
    """

    # Agregar límite si se proporciona
    if limit is not None:
        query += " LIMIT :limit"

    query += ";"

    # Ejecutar la consulta con parámetros vinculados
    params = {}
    if year is not None:
        params['year'] = year
    if limit is not None:
        params['limit'] = limit

    return db.session.execute(text(query), params)

def games_query():
    return db.session.execute(text("""SELECT DISTINCT games.place, games_details.game_number, rounds.number, rounds.victory, user.first_name
FROM games
LEFT JOIN games_details ON games.id = games_details.game_number
LEFT JOIN rounds ON games_details.round = rounds.id
LEFT JOIN user ON rounds.game_number = games.id
ORDER BY games.place"""))
