import sqlalchemy as sa
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint, PrimaryKeyConstraint


conn_string = (
    r"Driver={ODBC Driver 17 for SQL Server};"
    r"Server=localhost;"
    r"Database=testdb;"
    r"uid=sa;"
    r"pwd=kalalokia;"
    r"Integrated Security=false;"
)

conn_url = URL.create("mssql+pyodbc", query={"odbc_connect": conn_string})

engine = sa.create_engine(conn_url, connect_args={"timeout": 5})

Base = declarative_base()


class Category(Base):
    __tablename__ = "tbl_Category"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.NVARCHAR(15), unique=True, nullable=False)
    sap_code = sa.Column(sa.VARCHAR(1), unique=True, nullable=True)


class Color(Base):
    __tablename__ = "tbl_Color"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.NVARCHAR(50), unique=True, nullable=False)
    sap_code = sa.Column(sa.VARCHAR(2), unique=True, nullable=True)
    alt_name = sa.Column(sa.NVARCHAR(50), nullable=True)


class SoleColor(Base):
    __tablename__ = "tbl_SoleColor"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.NVARCHAR(50), unique=True, nullable=False)
    alt_name = sa.Column(sa.NVARCHAR(50), nullable=True)
    color_outer = sa.Column(sa.NVARCHAR(25), nullable=True)  # may not necessary
    color_mid = sa.Column(sa.NVARCHAR(25), nullable=True)  # may not necessary


class Machine(Base):

    __tablename__ = "tbl_Machine"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.NVARCHAR(50), unique=True, nullable=False)
    machine_type = sa.Column(sa.NVARCHAR(50), nullable=False)
    stations = sa.Column(sa.Integer, nullable=False)
    rotation_time = sa.Column(sa.Integer, nullable=False)
    specification = sa.Column(sa.NVARCHAR(25), nullable=False)
    made_in = sa.Column(sa.NVARCHAR(25), nullable=True)
    manufacturer = sa.Column(sa.NVARCHAR(25), nullable=True)


class MouldModel(Base):
    """Base model for mould"""

    __tablename__ = "tbl_MouldModel"

    id = sa.Column(sa.Integer, primary_key=True)
    mould_no = sa.Column(sa.NVARCHAR(30), unique=True, nullable=False)
    alt_name = sa.Column(sa.NVARCHAR(50), nullable=True)
    model = sa.Column(sa.NVARCHAR(30), nullable=True)
    style = sa.Column(sa.NVARCHAR(20), nullable=True)
    notes = sa.Column(sa.TEXT, nullable=True)


class MouldSet(Base):
    """Base model for mould"""

    __tablename__ = "tbl_MouldSet"

    id = sa.Column(sa.Integer, primary_key=True)
    mould_model = sa.Column(
        "mould_model_id", sa.Integer, ForeignKey(MouldModel.id), nullable=False
    )
    mould_type = sa.Column(sa.NVARCHAR(30), nullable=False)
    category = sa.Column(
        "category_id", sa.Integer, ForeignKey(Category.id), nullable=False
    )
    machines = sa.Column(sa.NVARCHAR(12), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "mould_model_id", "category_id", "mould_type", name="_mould_set_uc"
        ),
    )


class Mould(Base):

    __tablename__ = "tbl_Mould"

    id = sa.Column(sa.Integer, primary_key=True)
    mould_set = sa.Column(
        "mould_set_id", sa.Integer, ForeignKey(MouldSet.id), nullable=False
    )
    size = sa.Column(sa.Integer, nullable=False)
    quantity = sa.Column(sa.Integer, default=0)

    __table_args__ = (UniqueConstraint("mould_set_id", "size", name="_mould_uc"),)


class ArticleModel(Base):
    """Article base model"""

    __tablename__ = "tbl_ArticleModel"

    id = sa.Column(sa.Integer, primary_key=True)
    art_no = sa.Column(sa.NVARCHAR(10), unique=True, nullable=False)
    article_type = sa.Column(sa.NVARCHAR(50), nullable=True)
    brand = sa.Column(sa.NVARCHAR(50), nullable=True)
    licensed = sa.Column(sa.Boolean, default=0)


class Article(Base):
    """Article base model"""

    __tablename__ = "tbl_Article"

    id = sa.Column(sa.Integer, primary_key=True)
    article = sa.Column(
        "article_model_id", sa.Integer, ForeignKey(ArticleModel.id), nullable=False
    )
    color = sa.Column("color_id", sa.Integer, ForeignKey(Color.id), nullable=False)
    category = sa.Column(
        "category_id", sa.Integer, ForeignKey(Category.id), nullable=False
    )
    mould = sa.Column(
        "mould_set_id", sa.Integer, ForeignKey(MouldSet.id), nullable=False
    )
    sole_color = sa.Column(
        "sole_color_id", sa.Integer, ForeignKey(SoleColor.id), nullable=False
    )
    sole_type = sa.Column(sa.NVARCHAR(30), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "article_model_id", "color_id", "category_id", name="_article_uc"
        ),
    )


class PackingStyle(Base):
    """Packing style"""

    __tablename__ = "tbl_PackingStyle"

    id = sa.Column(sa.Integer, primary_key=True)
    category = sa.Column(
        "category_id", sa.Integer, ForeignKey(Category.id), nullable=False
    )
    size_matrix = sa.Column(sa.NVARCHAR(25), nullable=False)
    pairs = sa.Column(sa.Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "category_id", "size_matrix", "pairs", name="_packing_style_uc"
        ),
    )


class PackingOrder(Base):
    """Packing order for size 1 -13"""

    __tablename__ = "tbl_PackingOrder"

    id = sa.Column(sa.Integer, primary_key=True)
    packing = sa.Column(
        "packing_style_id", sa.Integer, ForeignKey(PackingStyle.id), nullable=False
    )
    size = sa.Column(sa.Integer, nullable=False)
    quantity = sa.Column(sa.Integer, default=0)

    __table_args__ = (
        UniqueConstraint("packing_style_id", "size", name="_packing_order_uc"),
    )


class PlanCurrent(Base):
    """Current month plan"""

    __tablename__ = "tbl_PlanCurrent"

    art_no = sa.Column(sa.NVARCHAR(8), nullable=False)
    size = sa.Column(sa.NVARCHAR(6), nullable=False)
    color = sa.Column("color", sa.NVARCHAR(30), nullable=False)  # color name
    category = sa.Column("category", sa.NVARCHAR(18), nullable=False)  # category name
    mould_no = sa.Column(sa.NVARCHAR(50), nullable=True)
    pairs = sa.Column(sa.Integer, nullable=False)
    plan = sa.Column(sa.Integer, nullable=False)

    __table_args__ = (PrimaryKeyConstraint(art_no, size, color, category, pairs), {})


Base.metadata.create_all(engine)
