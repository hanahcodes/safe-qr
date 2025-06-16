import sqlalchemy
from databases import Database

# For an MVP, SQLite is perfect. It's a single file database.
DATABASE_URL = "sqlite:///./secure_qr_mvp.db"

database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Define our products table
products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("unique_id", sqlalchemy.String, unique=True, index=True),
    sqlalchemy.Column("product_name", sqlalchemy.String),
    sqlalchemy.Column("company_name", sqlalchemy.String),
    sqlalchemy.Column("is_authentic", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column("creation_date", sqlalchemy.DateTime, default=sqlalchemy.func.now()),
    # In Phase 2, we will add a column for the master pattern image path
    # sqlalchemy.Column("master_pattern_path", sqlalchemy.String),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)