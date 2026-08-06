from flask_app.config.mysqlconnection import connectToMySQL


DATABASE = "lps_collection_schema"


class User:

    def __init__(self, data):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.email = data["email"]
        self.password = data["password"]
        self.role = data["role"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]

    @classmethod
    def save(cls, data):
        query = """
            INSERT INTO users
                (
                    first_name,
                    email,
                    password,
                    role
                )
            VALUES
                (
                    %(first_name)s,
                    %(email)s,
                    %(password)s,
                    %(role)s
                );
        """

        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def get_by_email(cls, data):
        query = """
            SELECT *
            FROM users
            WHERE email = %(email)s;
        """

        results = connectToMySQL(DATABASE).query_db(query, data)

        if not results:
            return None

        return cls(results[0])

    @classmethod
    def get_by_id(cls, data):
        query = """
            SELECT *
            FROM users
            WHERE id = %(id)s;
        """

        results = connectToMySQL(DATABASE).query_db(query, data)

        if not results:
            return None

        return cls(results[0])