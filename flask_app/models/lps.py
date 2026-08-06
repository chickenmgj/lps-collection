from flask_app.config.mysqlconnection import connectToMySQL


DATABASE = "lps_collection_schema"


class Lps:

    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.generation = data["generation"]
        self.category = data["category"]
        self.year = data["year"]
        self.species = data["species"]
        self.image = data["image"]
        self.status = data["status"]
        self.priority = data["priority"]
        self.favorite = data["favorite"]
        self.trade = data["trade"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]

    @classmethod
    def get_all(cls):
        query = """
            SELECT *
            FROM lps
            ORDER BY generation ASC, id ASC;
        """

        results = connectToMySQL(DATABASE).query_db(query)

        if not results:
            return []

        return [cls(row) for row in results]

    @classmethod
    def get_by_status(cls, status):
        query = """
            SELECT *
            FROM lps
            WHERE status = %(status)s
            ORDER BY
                priority DESC,
                favorite DESC,
                generation ASC,
                id ASC;
        """

        data = {
            "status": status
        }

        results = connectToMySQL(DATABASE).query_db(query, data)

        if not results:
            return []

        return [cls(row) for row in results]

    @classmethod
    def get_for_trade(cls):
        query = """
            SELECT *
            FROM lps
            WHERE trade = TRUE
            ORDER BY
                priority DESC,
                favorite DESC,
                generation ASC,
                id ASC;
        """

        results = connectToMySQL(DATABASE).query_db(query)

        if not results:
            return []

        return [cls(row) for row in results]

    @classmethod
    def save(cls, data):
        query = """
            INSERT INTO lps
                (
                    id,
                    name,
                    generation,
                    category,
                    year,
                    species,
                    image,
                    status,
                    priority,
                    favorite,
                    trade
                )
            VALUES
                (
                    %(id)s,
                    %(name)s,
                    %(generation)s,
                    %(category)s,
                    %(year)s,
                    %(species)s,
                    %(image)s,
                    %(status)s,
                    %(priority)s,
                    %(favorite)s,
                    %(trade)s
                );
        """

        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def get_by_id(cls, data):
        query = """
            SELECT *
            FROM lps
            WHERE id = %(id)s;
        """

        results = connectToMySQL(DATABASE).query_db(query, data)

        if not results:
            return None

        return cls(results[0])

    @classmethod
    def update(cls, data):
        query = """
            UPDATE lps
            SET
                name = %(name)s,
                generation = %(generation)s,
                category = %(category)s,
                year = %(year)s,
                species = %(species)s,
                image = %(image)s,
                status = %(status)s,
                priority = %(priority)s,
                favorite = %(favorite)s,
                trade = %(trade)s
            WHERE id = %(id)s;
        """

        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def delete(cls, data):
        query = """
            DELETE FROM lps
            WHERE id = %(id)s;
        """

        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def get_counts(cls):
        query = """
            SELECT
                SUM(status = 'owned') AS owned_count,
                SUM(status = 'wishlist') AS wishlist_count,
                SUM(trade = TRUE) AS trade_count
            FROM lps;
        """

        results = connectToMySQL(DATABASE).query_db(query)

        if not results:
            return {
                "owned_count": 0,
                "wishlist_count": 0,
                "trade_count": 0
            }

        counts = results[0]

        return {
            "owned_count": counts["owned_count"] or 0,
            "wishlist_count": counts["wishlist_count"] or 0,
            "trade_count": counts["trade_count"] or 0
        }

    @staticmethod
    def get_order_by(order):
        order_options = {
            "priority": """
                priority DESC,
                favorite DESC,
                generation ASC,
                id ASC
            """,

            "favorite": """
                favorite DESC,
                priority DESC,
                generation ASC,
                id ASC
            """,

            "name_asc": """
                name ASC
            """,

            "name_desc": """
                name DESC
            """,

            "year_asc": """
                year ASC,
                name ASC
            """,

            "year_desc": """
                year DESC,
                name ASC
            """
        }

        return order_options.get(
            order,
            order_options["priority"]
        )

    @classmethod
    def search_by_status(cls, data):
        order_by = cls.get_order_by(data.get("order"))

        query = """
            SELECT *
            FROM lps
            WHERE status = %(status)s
              AND (
                    name LIKE %(search)s
                    OR CAST(id AS CHAR) LIKE %(search)s
                    OR generation LIKE %(search)s
                    OR category LIKE %(search)s
                    OR species LIKE %(search)s
              )
        """

        if data.get("generation"):
            query += """
                AND generation = %(generation)s
            """

        query += f"""
            ORDER BY {order_by};
        """

        results = connectToMySQL(DATABASE).query_db(query, data)

        if not results:
            return []

        return [cls(row) for row in results]

    @classmethod
    def search_for_trade(cls, data):
        order_by = cls.get_order_by(data.get("order"))

        query = """
            SELECT *
            FROM lps
            WHERE trade = TRUE
              AND (
                    name LIKE %(search)s
                    OR CAST(id AS CHAR) LIKE %(search)s
                    OR generation LIKE %(search)s
                    OR category LIKE %(search)s
                    OR species LIKE %(search)s
              )
        """

        if data.get("generation"):
            query += """
                AND generation = %(generation)s
            """

        query += f"""
            ORDER BY {order_by};
        """

        results = connectToMySQL(DATABASE).query_db(query, data)

        if not results:
            return []

        return [cls(row) for row in results]