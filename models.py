from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Date, Table, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from crud import s

Base = declarative_base()


association_table = Table('association', Base.metadata,
                          Column('team_id', Integer, ForeignKey('team.id')),
                          Column('user_id', Integer, ForeignKey('user.id'))
                          )


class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship("User",
                         secondary=association_table,
                         back_populates="teams")
    points = relationship("Point")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return self.name

    def get_score(self):
        user_score = {}
        for p in self.points:
            try:
                user_score[p.point_receiver] += p.points
            except KeyError:
                user_score[p.point_receiver] = p.points

        return user_score


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    teams = relationship(
        "Team",
        secondary=association_table,
        back_populates="users")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return self.username


class Point(Base):
    __tablename__ = 'point'
    id = Column(Integer, primary_key=True)
    description = Column(Text)
    points = Column(Integer)
    giver_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    point_giver = relationship(User, foreign_keys=giver_id, backref='points_given')
    point_receiver = relationship(User, foreign_keys=receiver_id, backref='points_received')
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# class Wager(Base):
#     __tablename__ = 'wager'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('user.id'))
#     user = relationship("User", back_populates="wagers")
#     points = Column(Integer)
#     description = Column(String)
#     result = Column(Boolean)
#     start_time = Column(Date)
#     end_time = Column(Date)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())