from typing import List

import sqlalchemy as sq
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError

metadata = MetaData()
Base = declarative_base()


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)


class ViewedTableInterface:
    def __init__(self, db_url_object: str):
        self.engine = create_engine(db_url_object)
        Base.metadata.create_all(self.engine)

    def add_record(self, profile_id: int, worksheet_id: int) -> None:
        try:
            with Session(self.engine) as session:
                view = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
                session.add(view)
                session.commit()
        except SQLAlchemyError as e:
            print('При записи данных о просмотренных страницах произошла ошибка')
            print(e)

    def get_all_viewed_from_profile_id(self, profile_id: int) -> List:
        try:
            with Session(self.engine) as session:
                get_records_query = session.query(Viewed).filter(Viewed.profile_id==profile_id).all()
                worksheet_ids = [item.worksheet_id for item in get_records_query]
                return worksheet_ids
        except SQLAlchemyError as e:
            print('При считывании данных о просмотренных страницах произошла ошибка')
            print(e)
            return []
