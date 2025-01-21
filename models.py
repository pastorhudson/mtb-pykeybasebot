from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey, DateTime, func, Text, and_
from sqlalchemy.orm import relationship
from crud import s
import pytz
from sqlalchemy import Column, DateTime, String, Enum
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

from datetime import datetime

Base = declarative_base()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.environ['REFRESH_TOKEN_EXPIRE_MINUTES'])
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']   # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']    # should be kept secret


association_table = Table('association', Base.metadata,
                          Column('team_id', Integer, ForeignKey('team.id')),
                          Column('user_id', Integer, ForeignKey('user.id'))
                          )


class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)
    state = Column(String, unique=False)
    county = Column(String, unique=False)
    team_id = Column(Integer, ForeignKey('team.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"state: {self.state}, county: {self.county}"


class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship("User",
                         secondary=association_table,
                         back_populates="teams")
    points = relationship("Point", cascade="all, delete-orphan", lazy='dynamic', passive_deletes=True)
    wagers = relationship("Wager", order_by="Wager.id")
    tills = relationship("Till", order_by="Till.event", lazy="dynamic")
    sinces = relationship("Since", order_by="Since.event", lazy="dynamic")
    location = relationship("Location", lazy="dynamic")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return self.name

    def get_score(self, year):
        user_score = {}
        for user in self.users:
            user_score[user] = 0
        for p in self.points.filter(and_(
                Point.created_at >= datetime.utcnow().replace(year=year - 1,
                                                              month=12,
                                                              day=31,
                                                              hour=23,
                                                              minute=59)),
                Point.created_at <= datetime.utcnow().replace(year=year,
                                                              month=12,
                                                              day=31,
                                                              hour=23,
                                                              minute=59),
                # Point.receiver_id != 2  # Exclude points received by user with giver_id 2

        ):
            try:
                user_score[p.point_receiver] += p.points
            except KeyError:
                user_score[p.point_receiver] = p.points

        return user_score

    def get_most_generous(self, year):
        user_generosity = {}
        for user in self.users:
            user_generosity[user] = 0
        for p in self.points.filter(and_(
                Point.created_at >= datetime.utcnow().replace(year=year - 1,
                                                              month=12,
                                                              day=31,
                                                              hour=23,
                                                              minute=59)),
                Point.created_at <= datetime.utcnow().replace(year=year,
                                                              month=12,
                                                              day=31,
                                                              hour=23,
                                                              minute=59),
                Point.description.notin_(["sent msg", "msg", "react"]),
                # Point.giver_id != 2  # Exclude points given by user with giver_id 2
        ):
            try:
                user_generosity[p.point_giver] += p.points
            except KeyError:
                user_generosity[p.point_giver] = p.points
        return user_generosity

    def get_leading_person(self, year):
        leading_person = {}

        generosity = self.get_most_generous(year)
        score = self.get_score(year)

        # Exclude user with giver_id 2
        generosity.pop(2, None)
        score.pop(2, None)

        for p in generosity:
            leading_person[p] = 0
        for p in score:
            leading_person[p] = 0
        for k in leading_person:
            try:
                leading_person[k] = int((generosity[k] + score[k]) / 2)
            except Exception as e:
                print(type(e))
                print(e)
        return leading_person

    def get_wagers(self):
        return s.query(Wager).filter(Team.wagers.any(Wager.is_closed == False)).all()

    def wager_exists(self, description):
        return s.query(Wager).filter(and_(Team.wagers.any(Wager.is_closed == 'false'),
                                          Team.wagers.any(Wager.description == description))).all()

    def get_wager(self, wager_id):
        return s.query(Wager).filter(Team.wagers.any(Wager.id == wager_id)).first()

    def get_states(self):
        states = []
        for s in self.location.all():
            states.append(s.state)
        return set(states)


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
    messages = relationship("MessageQueue", back_populates="user")  # New Line: Relationship with MessageQueue
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return self.username

    def create_access_token(self, conversation_id: str, expires_delta: timedelta = None) -> str:

        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode = {"exp": expires_delta, "user": self.username, "conversation_id": conversation_id}
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, conversation_id: str, expires_delta: timedelta = None) -> str:

        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

        to_encode = {"exp": expires_delta, "user": self.username, "conversation_id": conversation_id, "refresh_token": True}
        encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
        return encoded_jwt

    def get_bets(self):
        return s.query(Bet).filter(User.bets).all()

    def get_tills(self):
        all_tills = []
        for team in self.teams:
            all_tills.extend(team.tills.all())
        return all_tills


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

    def __repr__(self):
        return f"Point - description: {self.description}, points: {self.points}, giver_id: {self.giver_id}\n" \
               f"point_receiver: {self.point_receiver} - {self.giver_id}, point_giver: {self.point_giver} - {self.receiver_id},\n" \
               f"team_id: {self.team_id}, id: {self.id}"


class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    msg_id = Column(String, index=True, unique=True)
    conv_id = Column(String, index=True)
    wager_id = Column(Integer, ForeignKey('wager.id'), nullable=False)
    wager = relationship("Wager", back_populates="messages")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"{self.msg_id},{self.wager_id}"


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
    messages = relationship("Message", back_populates="wager", lazy="dynamic")

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


class Till(Base):
    __tablename__ = 'till'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)
    name = Column(String)
    event = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        tspan = self.event - datetime.now(pytz.timezone('America/New_York'))
        s = tspan.seconds
        # m, remainder = divmod(s, 60)
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)

        print(tspan.days)
        if tspan.days > 0:
            return f"`{tspan.days} Days` till: {self.name}"

        elif tspan.seconds > 3600:
            return f"`{hours} Hours` till:{self.name}"

        else:
            return f"`{minutes} Minutes {seconds} Seconds` till:{self.name}"


class Since(Base):
    __tablename__ = 'since'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)
    name = Column(String)
    event = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        tspan = datetime.now(pytz.timezone('America/New_York')) - self.event
        s = tspan.seconds
        # m, remainder = divmod(s, 60)
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)

        if tspan.days > 0:
            return f"`{tspan.days} Days` since: {self.name} #{self.id}"

        elif tspan.seconds > 3600:
            return f"`{hours} Hours` since:{self.name} #{self.id}"

        else:
            return f"`{minutes} Minutes {seconds} Seconds` since:{self.name} #{self.id}"


class CompletedTasks(Base):
    __tablename__ = 'completed_tasks'
    id = Column(Integer, primary_key=True)
    task_name = Column(String)
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"Task Name: {self.task_name} Completed At: {self.completed_at}"

    def completed_at_in_ny(self):
        """
        Returns the completed_at time in 'America/New_York' timezone
        """
        if self.completed_at:
            ny_tz = ZoneInfo("America/New_York")
            return self.completed_at.astimezone(ny_tz)
        return None


class StatusEnum(PyEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DONE = "DONE"


class MessageQueue(Base):
    __tablename__ = "message_queue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String, nullable=False)
    sender = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))  # New Line: Foreign Key to User table
    user = relationship("User", back_populates="messages")  # New Line: Relationship with User
    ip = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.PENDING, nullable=False)
    destination = Column(Text, nullable=True)

    def mark_as_processing(self, session):
        self.status = StatusEnum.PROCESSING
        session.commit()

    def mark_as_done(self, session):
        self.status = StatusEnum.DONE
        session.commit()
