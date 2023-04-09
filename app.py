    import os
    from datetime import datetime, timedelta, timezone
    import requests
    from flask import Flask, jsonify
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import func

    app = Flask(__name__)

    # Configure database
    db_type = os.environ.get('DB_TYPE', 'sqlite')
    if db_type == 'sqlite':
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLITE_DATABASE_URI', 'sqlite:///jdsports.db')
    elif db_type == 'mysql':
        db_user = os.environ.get('MYSQL_USER','jdsports_user')
        db_password = os.environ.get('MYSQL_PASSWORD','jdsports_password')
        db_host = os.environ.get('MYSQL_HOST', 'localhost')
        db_port = os.environ.get('MYSQL_PORT', '3306')
        db_name = os.environ.get('MYSQL_DATABASE','jdsports')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)

    # API Endpoints and Keys
    SALES_API_URL = "https://api.jdsports.com/sales/v1/transactions"
    INVENTORY_API_URL = "https://api.jdsports.com/inventory/v1/items"
    CAMERA_API_URL = "https://api.verkada.com/cameras/v1/devices"
    POS_API_URL = "https://api.jdsports.com/pos/v1/pos"
    STORE_API_URL = "https://api.jdsports.com/store/v1/stores"
    VERKADA_API_KEY = os.environ.get("VERKADA_API_KEY")
    VERKADA_ORG_ID = os.environ.get("VERKADA_ORG_ID")

    # Database Models
    class Store(db.Model):
        store_id = db.Column(db.Integer, primary_key=True)
        store_name = db.Column(db.String(100))
        store_address = db.Column(db.String(200))
        store_phone = db.Column(db.String(20))
        store_email = db.Column(db.String(100))

    class Camera(db.Model):
        camera_id = db.Column(db.Integer, primary_key=True)
        camera_name = db.Column(db.String(100))
        camera_model = db.Column(db.String(100))
        store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'))

    class PointOfService(db.Model):
        pos_id = db.Column(db.Integer, primary_key=True)
        pos_name = db.Column(db.String(100))
        store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'))
        camera_id = db.Column(db.Integer, db.ForeignKey('camera.camera_id'))

    class Transaction(db.Model):
        transaction_id = db.Column(db.Integer, primary_key=True)
        transaction_number = db.Column(db.String(50))
        transaction_date = db.Column(db.DateTime)
        pos_id = db.Column(db.Integer, db.ForeignKey('point_of_service.pos_id'))

    class TransactionItem(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'))
        item_name = db.Column(db.String(100))
        item_price = db.Column(db.Float)
        thumbnail_link = db.Column(db.String(500))
        footage_link = db.Column(db.String(500))

    class CameraEventUID(db.Model):
        event_type_uid = db.Column(db.String(50), primary_key=True)
        event_type_name = db.Column(db.String(100))

    # Utility Functions
    def get_footage_link(camera_id, timestamp=None):
        url = f"https://api.verkada.com/cameras/v1/footage/link?org_id={VERKADA_ORG_ID}&camera_id={camera_id}"
        
        if timestamp:
            url += f"&timestamp={timestamp}"
            
        headers = {"accept": "application/json", "x-api-key": VERKADA_API_KEY}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()["url"]
        else:
            print(f"Error fetching footage link: {response.status_code}")
            return None

    def get_thumbnail_link(camera_id, timestamp=None, expiry=86400):
        url = f"https://api.verkada.com/cameras/v1/footage/thumbnails/link?org_id={VERKADA_ORG_ID}&camera_id={camera_id}&expiry={expiry}"
        
        if timestamp:
            url += f"&timestamp={timestamp}"
            
        headers = {"accept": "application/json", "x-api-key": VERKADA_API_KEY}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()["url"]
        else:
            print(f"Error fetching thumbnail link: {response.status_code}")
            return None


    def fetch_data(url, params=None):
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching data from {url}: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None

    def fetch_transactions():
        now = datetime.now(timezone.utc)
        start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        end_time = now.strftime("%Y-%m-%dT%H:%M:%S")
        params = {"start_time": start_time, "end_time": end_time}
        return fetch_data(SALES_API_URL, params=params)

    def fetch_item(item_id):
        return fetch_data(f"{INVENTORY_API_URL}/{item_id}")

    def fetch_camera(camera_id):
        return fetch_data(f"{CAMERA_API_URL}/{camera_id}")

    def fetch_pos(camera_id):
        params = {"camera_id": camera_id}
        return fetch_data(POS_API_URL, params=params)

    def fetch_store(store_id):
        return fetch_data(f"{STORE_API_URL}/{store_id}")

    # Store data and create events
    def store_data(transactions):
        if transactions is None:
            return

        # For each transaction, fetch the item, camera, pos, and store data and create events
        for transaction in transactions:
            item = fetch_item(transaction["item_id"])
            camera = fetch_camera(transaction["camera_id"])
            pos = fetch_pos(camera["pos_id"])
            store = fetch_store(pos["store_id"])

            if store and not Store.query.get(store["store_id"]):
                new_store = Store(**store)
                db.session.add(new_store)

            if camera and not Camera.query.get(camera["camera_id"]):
                new_camera = Camera(**camera)
                db.session.add(new_camera)

            if pos and not PointOfService.query.get(pos["pos_id"]):
                new_pos = PointOfService(**pos)
                db.session.add(new_pos)

            if not Transaction.query.get(transaction["transaction_id"]):
                transaction["transaction_date"] = datetime.fromtimestamp(transaction["transaction_date"], timezone.utc)
                new_transaction = Transaction(**transaction)
                db.session.add(new_transaction)

            if item and not TransactionItem.query.filter_by(transaction_id=transaction["transaction_id"], item_name=item["item_name"]).first():
                item_data = {"transaction_id": transaction["transaction_id"], "item_name": item["item_name"], "item_price": item["item_price"]}
                new_transaction_item = TransactionItem(**item_data)
                db.session.add(new_transaction_item)

            db.session.commit()

            create_and_post_verkada_event(transaction, item, camera)

    # Create and post event to Verkada Helix
    def create_and_post_verkada_event(transaction, item, camera):
        if transaction is None or item is None or camera is None:
            return

        # This can be any event name. TODO: Make this dynamic based on the event name. Ability to create various event types. Warhouse, Customer Check in and check out, etc.
        event_type_name = "Sales Transactions"
        event_type_uid_entry = CameraEventUID.query.filter_by(event_type_name=event_type_name).first()

        if not event_type_uid_entry:
            event_type = {
                "event_schema": {
                    "item_id": "integer",
                    "transaction_id": "integer",
                    "transaction_time": "integer",
                    "thumbnail_url": "string",
                    "footage_url": "string"
                },
                "name": "Sales Transactions"
            }
            event_type_data = post_to_verkada_helix_event_type(event_type)

            if event_type_data:
                event_type_uid = event_type_data["uid"]
                new_event_uid_entry = CameraEventUID(event_type_uid=event_type_uid, event_type_name=event_type_name)
                db.session.add(new_event_uid_entry)
                db.session.commit()
            else:
                return
        else:
            event_type_uid = event_type_uid_entry.event_type_uid

        transaction_timestamp = int(transaction["transaction_date"].timestamp() * 1000)
        
        # Get thumbnail and footage links
        thumbnail_link = get_thumbnail_link(camera["camera_id"], transaction_timestamp)
        footage_link = get_footage_link(camera["camera_id"], transaction_timestamp)
        
        # Update transaction with thumbnail and footage links
        if thumbnail_link and footage_link:
            transaction_entry = Transaction.query.get(transaction["transaction_id"])
            transaction_entry.thumbnail_link = thumbnail_link
            transaction_entry.footage_link = footage_link
            db.session.commit()
        
        event_data = {
            "camera_id": camera["camera_id"],
            "event_type_uid": event_type_uid,
            "time_ms": transaction_timestamp,
            "attributes": {
                "item_id": transaction["item_id"],
                "transaction_id": transaction["transaction_id"],
                "transaction_time": transaction_timestamp,
                "thumbnail_url": thumbnail_link,
                "footage_url": footage_link
            }
        }
        post_to_verkada_helix_event(event_data)

    def post_to_verkada_helix_event(event_data):
        headers = {
            "Content-Type": "application/json",
            "x-api-key": VERKADA_API_KEY
        }
        url = f"https://api.verkada.com/cameras/v1/video_tagging/event?org_id={VERKADA_ORG_ID}"
        try:
            response = requests.post(url, headers=headers, json=event_data)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error posting data to Verkada Helix: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Error posting data to Verkada Helix: {e}")
            return None
        
    def post_to_verkada_helix_event_type(event_type):
        headers = {
            "Content-Type": "application/json",
            "x-api-key": VERKADA_API_KEY
        }
        url = f"https://api.verkada.com/cameras/v1/video_tagging/event_type?org_id={VERKADA_ORG_ID}"
        try:
            response = requests.post(url, headers=headers, json=event_type)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error posting data to Verkada Helix: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Error posting data to Verkada Helix: {e}")
            return None

    # API Endpoints

    # Fetch and store transactions and also crete and post Verkada events for every transaction
    @app.route("/fetch_and_store_transactions", methods=["GET"])
    def fetch_and_store_transactions_route():
        transactions = fetch_transactions()
        store_data(transactions)
        return jsonify({"message": "Transactions fetched and stored."})


    # List all transactions
    @app.route("/transactions", methods=["GET"])
    def get_transactions():
        transactions = Transaction.query.all()
        return jsonify([t.to_dict() for t in transactions])

    # List all the transactions for a specific store
    @app.route("/transactions/<int:store_id>", methods=["GET"])
    def get_transactions_by_store(store_id):
        transactions = Transaction.query.join(PointOfService).filter(PointOfService.store_id == store_id).all()
        return jsonify([t.to_dict() for t in transactions])

    # List all the sales in a specific store
    @app.route("/sales/<int:store_id>", methods=["GET"])
    def get_sales_by_store(store_id):
        sales = db.session.query(func.sum(TransactionItem.item_price)).join(Transaction).join(PointOfService).filter(PointOfService.store_id == store_id).scalar()
        return jsonify({"total_sales": sales})

    # List all the stores that are recorded of having atleast one transaction
    @app.route("/stores", methods=["GET"])
    def get_stores():
        stores = Store.query.all()
        return jsonify([s.to_dict() for s in stores])

    if __name__ == "__main__":
        with app.app_context():
            db.create_all()
        app.run()

                                     
