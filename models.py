from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Date, Table, ForeignKey, DateTime, func, Text, and_
from sqlalchemy.orm import relationship
from crud import s
from datetime import datetime

Base = declarative_base()


association_table = Table('association', Base.metadata,
                          Column('team_id', Integer, ForeignKey('team.id')),
                          Column('user_id', Integer, ForeignKey('user.id'))
                          )


class Local(Base):
    __tablename__ = 'local'
    id = Column(Integer, primary_key=True)
    state = Column(String, unique=False)
    county = Column(String, unique=False)
    team_id = Column(Integer, ForeignKey('team.id'))


class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship("User",
                         secondary=association_table,
                         back_populates="teams")
    points = relationship("Point")
    wagers = relationship("Wager")
    local = relationship("Local")
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

    def get_wagers(self):
        return s.query(Wager).filter(Team.wagers.any(Wager.is_closed==False)).all()

    def wager_exists(self, description):
        return s.query(Wager).filter(and_(Team.wagers.any(Wager.is_closed == 'false'),
                                          Team.wagers.any(Wager.description == description))).all()

    def get_wager(self, wager_id):
        return s.query(Wager).filter(Team.wagers.any(Wager.id == wager_id)).first()


class Bet(Base):
    __tablename__ = 'bet'
    left_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    right_id = Column(Integer, ForeignKey('wager.id'), primary_key=True)
    points = Column(Integer)
    position = Column(Boolean, nullable=False)
    result = Column(Boolean, nullable=True, default=None)
    wager = relationship("Wager", back_populates="bets")
    user = relationship("User", back_populates="bets")

    def __repr__(self):
        return str([self.left_id, self.right_id, self.points, self.position, self.user])


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    teams = relationship(
        "Team",
        secondary=association_table,
        back_populates="users")
    bets = relationship("Bet", back_populates="user")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return self.username

    def get_bets(self):
        return s.query(Bet).filter(User.bets).all()


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


class Wager(Base):
    __tablename__ = 'wager'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)
    points = Column(Integer)
    description = Column(String)
    result = Column(Boolean)
    is_closed = Column(Boolean, default=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    bets = relationship("Bet", back_populates="wager")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def already_bet(self, user):
        for bet in self.bets:
            if bet.user == user:
                return bet
        return False

    def et(self):
        return self.end_time.strftime('%d-%m %I:%M %p')

    # def min_left(self):
    #     td = self.end_time - datetime.now()

        # return td.min

    def st(self):
        return self.start_time.strftime('%d-%m %I:%M %p')

    def __repr__(self):
        return f'#{self.id} "{self.description}"'
               # f'Start Time: {self.start_time.strftime("%m-%d %I:%M %p")}\n' \
               # f'End Time: {self.end_time.strftime("%m-%d %I:%M %p")}'
