from app.services.psycopg_service import ConnectionHelper
from datetime import datetime 


class AnimesModels():
    valid_keys = ("anime", "released_date", "seasons")
    fieldnames = ["id", "anime", "released_date", "seasons"]



    def __init__(self, data):
        self.wrong_keys_sended = self._check_data_keys(data)
        self.anime = data.pop("anime", None)
        self.released_date = data.pop("released_date", None)
        self.seasons = data.pop("seasons", None)
        self._convert_anime_to_title()

    def _convert_anime_to_title(self) -> None:
        if self.anime:
            self.anime = self.anime.title()

    def _check_data_keys(self, data):
        wrong_keys = [key for key in data.keys() if key not in self.valid_keys]

        return wrong_keys

    def return_keys(self):

        keys = {
            "available_keys": self.valid_keys, 
            "wrong_keys_sended": self.wrong_keys_sended
        }

        return keys

    @staticmethod
    def _zip_animes(anime):
        zipped_anime = [dict(zip(AnimesModels.fieldnames, field)) for field in anime]

        return zipped_anime


    @staticmethod
    def _create_table(cur) -> None:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS animes (
                id BIGSERIAL PRIMARY KEY,
                anime VARCHAR(100) NOT NULL UNIQUE,
                released_date DATE NOT NULL,
                seasons INTEGER NOT NULL
            );
            """
        )


    def insert_anime(self):
        conn, cur = ConnectionHelper.get_conn_cur()
        AnimesModels._create_table(cur)
        self.released_date = datetime.strptime(self.released_date, "%d/%m/%Y")

        cur.execute(
            """
            INSERT INTO animes 
                (anime, released_date, seasons)
            VALUES
                (%(anime)s, %(released_date)s, %(seasons)s)
            RETURNING *;
            """,
            self.__dict__
        )

        created_anime = cur.fetchall()

        ConnectionHelper.close_conn_cur(conn, cur)


        return AnimesModels._zip_animes(created_anime)
    

    @staticmethod
    def get_animes():
        conn, cur = ConnectionHelper.get_conn_cur()
        AnimesModels._create_table(cur)

        cur.execute(
            """
            SELECT * FROM animes;
            """
        )

        animes = AnimesModels._zip_animes(cur.fetchall())

        ConnectionHelper.close_conn_cur(conn, cur)

        return animes

    @staticmethod
    def get_anime_by_id(id):
        conn, cur = ConnectionHelper.get_conn_cur()
        AnimesModels._create_table(cur)

        cur.execute(
            """
            SELECT * FROM animes
            WHERE id = %(id)s;
            """,
            {"id": id}
        )

        anime = AnimesModels._zip_animes(cur.fetchall())

        ConnectionHelper.close_conn_cur(conn, cur)

        if not anime:
            return False

        return anime
        

    @staticmethod
    def delete_anime(id):
        conn, cur = ConnectionHelper.get_conn_cur()
        AnimesModels._create_table(cur)
            
        cur.execute(
            """
            DELETE FROM animes
            WHERE
                id = %(id)s
            RETURNING *;
            """,
            {"id": id}
        )

        res = cur.fetchall()
        ConnectionHelper.close_conn_cur(conn, cur)

        if not res:
            return False

        return True

    
    def _update_query(self, cur, id, key, value) -> None:

        cur.execute(
            """
            UPDATE animes
            SET %(key)s = '%(value)s'
            WHERE
                id = %(id)s
            RETURNING *;
            """ %
            {"key": key, "value": value, "id": id}
        )

    def update_anime(self, id):
        fields_to_update = {key: value for key, value in self.__dict__.items() if key in self.valid_keys and value}
        conn, cur = ConnectionHelper.get_conn_cur()

        if not fields_to_update:
            raise KeyError (self.return_keys())

        self._create_table(cur)

        for key, value in fields_to_update.items():
            self._update_query(cur, id, key, value)

        res = cur.fetchall()
        ConnectionHelper.close_conn_cur(conn, cur)

        return self._zip_animes(res)