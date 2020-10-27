from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Date, Table, ForeignKey, DateTime, func
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
    #
    # def get_score(self):
    #     return "Score"


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
    points = Column(Integer)
    receiver_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    giver_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    receiver = relationship("User", backref="points_received", foreign_keys=[receiver_id])
    giver = relationship("User", backref="points_given", foreign_keys=[giver_id])
    team_id = Column(Integer, ForeignKey('team.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # def award_points(self, giver, points, receiver, team):
    #     giving_user = s.query(User).filter(User.username.match(giver)).first()
    #     receiving_user = s.query(User).filter(User.username.match(receiver)).first()
    #     p = Point(giver=giving_user, points=points, receiver=receiving_user)
    #     s.add(p)
    #     s.commit()
    #     s.close()



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
