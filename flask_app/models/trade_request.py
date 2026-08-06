from flask_app.config.mysqlconnection import connectToMySQL


DATABASE = "lps_collection_schema"


class TradeRequest:

    def __init__(self, data):
        self.id = data["id"]
        self.user_id = data["user_id"]
        self.lps_id = data["lps_id"]

        self.instagram_username = data["instagram_username"]
        self.offered_item = data["offered_item"]
        self.item_condition = data["item_condition"]
        self.proof_link = data["proof_link"]
        self.message = data["message"]

        self.first_trade_send_first_accepted = data.get(
            "first_trade_send_first_accepted",
            0
        )

        self.was_first_trade = data.get(
            "was_first_trade",
            0
        )

        self.verification_photo = data["verification_photo"]
        self.additional_photo_1 = data["additional_photo_1"]
        self.additional_photo_2 = data["additional_photo_2"]
        self.additional_photo_3 = data["additional_photo_3"]

        self.status = data["status"]

        # Datos de envío de la administradora.
        self.admin_shipping_company = data.get(
            "admin_shipping_company"
        )
        self.admin_tracking_number = data.get(
            "admin_tracking_number"
        )
        self.admin_tracking_url = data.get(
            "admin_tracking_url"
        )
        self.admin_shipping_note = data.get(
            "admin_shipping_note"
        )
        self.admin_package_photo = data.get(
            "admin_package_photo"
        )
        self.admin_shipped_at = data.get(
            "admin_shipped_at"
        )

        # Datos de envío del usuario.
        self.user_shipping_company = data.get(
            "user_shipping_company"
        )
        self.user_tracking_number = data.get(
            "user_tracking_number"
        )
        self.user_tracking_url = data.get(
            "user_tracking_url"
        )
        self.user_shipping_note = data.get(
            "user_shipping_note"
        )
        self.user_package_photo = data.get(
            "user_package_photo"
        )
        self.user_shipped_at = data.get(
            "user_shipped_at"
        )

        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]

        # Datos obtenidos con JOIN.
        self.user_name = data.get("user_name")
        self.user_email = data.get("user_email")
        self.lps_name = data.get("lps_name")
        self.lps_image = data.get("lps_image")
        self.lps_generation = data.get("lps_generation")

    @classmethod
    def user_has_completed_trade(cls, data):
        query = """
            SELECT COUNT(*) AS completed_count
            FROM trade_requests
            WHERE user_id = %(user_id)s
              AND status = 'completed';
        """

        results = connectToMySQL(DATABASE).query_db(
            query,
            data
        )

        if not results:
            return False

        return results[0]["completed_count"] > 0

    @classmethod
    def save(cls, data):
        query = """
            INSERT INTO trade_requests
                (
                    user_id,
                    lps_id,
                    instagram_username,
                    offered_item,
                    item_condition,
                    proof_link,
                    message,
                    first_trade_send_first_accepted,
                    was_first_trade,
                    verification_photo,
                    additional_photo_1,
                    additional_photo_2,
                    additional_photo_3
                )
            VALUES
                (
                    %(user_id)s,
                    %(lps_id)s,
                    %(instagram_username)s,
                    %(offered_item)s,
                    %(item_condition)s,
                    %(proof_link)s,
                    %(message)s,
                    %(first_trade_send_first_accepted)s,
                    %(was_first_trade)s,
                    %(verification_photo)s,
                    %(additional_photo_1)s,
                    %(additional_photo_2)s,
                    %(additional_photo_3)s
                );
        """

        return connectToMySQL(DATABASE).query_db(
            query,
            data
        )

    @classmethod
    def get_by_id(cls, data):
        query = """
            SELECT
                trade_requests.*,
                users.first_name AS user_name,
                users.email AS user_email,
                lps.name AS lps_name,
                lps.image AS lps_image,
                lps.generation AS lps_generation
            FROM trade_requests
            JOIN users
                ON users.id = trade_requests.user_id
            JOIN lps
                ON lps.id = trade_requests.lps_id
            WHERE trade_requests.id = %(id)s;
        """

        results = connectToMySQL(DATABASE).query_db(
            query,
            data
        )

        if not results:
            return None

        return cls(results[0])

    @classmethod
    def get_by_user_id(cls, data):
        query = """
            SELECT
                trade_requests.*,
                lps.name AS lps_name,
                lps.image AS lps_image,
                lps.generation AS lps_generation
            FROM trade_requests
            JOIN lps
                ON lps.id = trade_requests.lps_id
            WHERE trade_requests.user_id = %(user_id)s
            ORDER BY trade_requests.created_at DESC;
        """

        results = connectToMySQL(DATABASE).query_db(
            query,
            data
        )

        if not results:
            return []

        return [cls(row) for row in results]

    @classmethod
    def get_all(cls):
        query = """
            SELECT
                trade_requests.*,
                users.first_name AS user_name,
                users.email AS user_email,
                lps.name AS lps_name,
                lps.image AS lps_image,
                lps.generation AS lps_generation
            FROM trade_requests
            JOIN users
                ON users.id = trade_requests.user_id
            JOIN lps
                ON lps.id = trade_requests.lps_id
            ORDER BY trade_requests.created_at DESC;
        """

        results = connectToMySQL(DATABASE).query_db(
            query
        )

        if not results:
            return []

        return [cls(row) for row in results]

    @classmethod
    def update_status(cls, data):
        query = """
            UPDATE trade_requests
            SET status = %(status)s
            WHERE id = %(id)s;
        """

        return connectToMySQL(DATABASE).query_db(
            query,
            data
        )

    @classmethod
    def update_admin_shipping(cls, data):
        query = """
            UPDATE trade_requests
            SET
                admin_shipping_company =
                    %(admin_shipping_company)s,
                admin_tracking_number =
                    %(admin_tracking_number)s,
                admin_tracking_url =
                    %(admin_tracking_url)s,
                admin_shipping_note =
                    %(admin_shipping_note)s,
                admin_package_photo =
                    %(admin_package_photo)s,
                admin_shipped_at = NOW(),
                status = CASE
                    WHEN user_shipped_at IS NOT NULL
                        THEN 'both_shipped'
                    ELSE 'admin_shipped'
                END
            WHERE id = %(id)s;
        """

        return connectToMySQL(DATABASE).query_db(
            query,
            data
        )

    @classmethod
    def update_user_shipping(cls, data):
        query = """
            UPDATE trade_requests
            SET
                user_shipping_company =
                    %(user_shipping_company)s,
                user_tracking_number =
                    %(user_tracking_number)s,
                user_tracking_url =
                    %(user_tracking_url)s,
                user_shipping_note =
                    %(user_shipping_note)s,
                user_package_photo =
                    %(user_package_photo)s,
                user_shipped_at = NOW(),
                status = CASE
                    WHEN admin_shipped_at IS NOT NULL
                        THEN 'both_shipped'
                    ELSE 'user_shipped'
                END
            WHERE id = %(id)s
              AND user_id = %(user_id)s;
        """

        return connectToMySQL(DATABASE).query_db(
            query,
            data
        )

    @classmethod
    def delete_pending_by_user(cls, data):
        query = """
            DELETE FROM trade_requests
            WHERE id = %(id)s
              AND user_id = %(user_id)s
              AND status = 'pending';
        """

        return connectToMySQL(DATABASE).query_db(
            query,
            data
        )
    @classmethod
    def delete_completed(cls, data):
        query = """
            DELETE FROM trade_requests
            WHERE id = %(id)s
            AND status = 'completed';
        """

        return connectToMySQL(DATABASE).query_db(
            query,
            data
        )