from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, declarative_base, relationship

DATABASE_URL = "sqlite:///CRUDOperations.db"
engine = create_engine(DATABASE_URL, echo=True)
# conn = engine.connect()

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    user_id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False)

    blogs = relationship("Blog", back_populates="author")

class Blog(Base):
    __tablename__ = "blog"
    blog_id: int = Column(Integer, primary_key=True)
    title: str = Column(String, nullable=False)
    description: str = Column(String, nullable=False)
    author_id: int = Column(Integer, ForeignKey("user.user_id"))

    author = relationship("User", back_populates="blogs")

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

new_user = User(name="Kavin", email="kavin090305@gmail.com")
session.add(new_user)
session.commit()
