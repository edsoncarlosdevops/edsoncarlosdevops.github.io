from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Athlete(Base):
    """Model for storing athlete information"""
    __tablename__ = 'athletes'

    id = Column(Integer, primary_key=True)
    strava_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True)
    access_token = Column(String)
    refresh_token = Column(String)
    token_expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Activity(Base):
    """Model for storing activity/run information"""
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True)
    strava_activity_id = Column(Integer, unique=True, nullable=False)
    athlete_strava_id = Column(Integer, nullable=False)
    athlete_name = Column(String, nullable=False)
    name = Column(String)
    distance = Column(Float, nullable=False)  # in kilometers
    moving_time = Column(Integer)  # in seconds
    elapsed_time = Column(Integer)  # in seconds
    activity_type = Column(String)
    start_date = Column(DateTime, nullable=False)
    notified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Manager for database operations"""

    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///data/strava_runs.db')

        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def add_athlete(self, strava_id: int, name: str, phone_number: str = None,
                   access_token: str = None, refresh_token: str = None,
                   token_expires_at: datetime = None):
        """Add or update an athlete"""
        session = self.get_session()
        try:
            athlete = session.query(Athlete).filter_by(strava_id=strava_id).first()
            if athlete:
                athlete.name = name
                if phone_number:
                    athlete.phone_number = phone_number
                if access_token:
                    athlete.access_token = access_token
                if refresh_token:
                    athlete.refresh_token = refresh_token
                if token_expires_at:
                    athlete.token_expires_at = token_expires_at
                athlete.updated_at = datetime.utcnow()
            else:
                athlete = Athlete(
                    strava_id=strava_id,
                    name=name,
                    phone_number=phone_number,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_expires_at=token_expires_at
                )
                session.add(athlete)
            session.commit()
            return athlete
        finally:
            session.close()

    def add_activity(self, strava_activity_id: int, athlete_strava_id: int,
                    athlete_name: str, name: str, distance: float,
                    moving_time: int, elapsed_time: int, activity_type: str,
                    start_date: datetime):
        """Add a new activity"""
        session = self.get_session()
        try:
            # Check if activity already exists
            existing = session.query(Activity).filter_by(
                strava_activity_id=strava_activity_id
            ).first()

            if existing:
                return existing

            activity = Activity(
                strava_activity_id=strava_activity_id,
                athlete_strava_id=athlete_strava_id,
                athlete_name=athlete_name,
                name=name,
                distance=distance,
                moving_time=moving_time,
                elapsed_time=elapsed_time,
                activity_type=activity_type,
                start_date=start_date
            )
            session.add(activity)
            session.commit()
            return activity
        finally:
            session.close()

    def mark_activity_notified(self, strava_activity_id: int):
        """Mark an activity as notified"""
        session = self.get_session()
        try:
            activity = session.query(Activity).filter_by(
                strava_activity_id=strava_activity_id
            ).first()
            if activity:
                activity.notified = True
                session.commit()
        finally:
            session.close()

    def get_activities_by_period(self, start_date: datetime, end_date: datetime):
        """Get all activities in a date range"""
        session = self.get_session()
        try:
            activities = session.query(Activity).filter(
                Activity.start_date >= start_date,
                Activity.start_date <= end_date,
                Activity.activity_type == 'Run'
            ).all()
            return activities
        finally:
            session.close()

    def get_athlete_by_strava_id(self, strava_id: int):
        """Get athlete by Strava ID"""
        session = self.get_session()
        try:
            return session.query(Athlete).filter_by(strava_id=strava_id).first()
        finally:
            session.close()
