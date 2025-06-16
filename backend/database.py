import sqlalchemy
from databases import Database

DATABASE_URL = "sqlite:///./secure_qr_mvp.db"

database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("unique_id", sqlalchemy.String, unique=True, index=True),
    sqlalchemy.Column("product_name", sqlalchemy.String),
    sqlalchemy.Column("company_name", sqlalchemy.String),
    sqlalchemy.Column("is_authentic", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column("creation_date", sqlalchemy.DateTime, default=sqlalchemy.func.now()),
    # --- PHASE 2 ADDITION ---
    sqlalchemy.Column("master_pattern_path", sqlalchemy.String),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine) # This will safely add the new column