from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from .models import Base, URLResource, SmartContract
from config.settings import settings

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_db(self) -> Session:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def add_url_resource(self, name: str, url: str, description: str = None) -> bool:
        try:
            with self.SessionLocal() as db:
                resource = URLResource(name=name, url=url, description=description)
                db.add(resource)
                db.commit()
                return True
        except SQLAlchemyError:
            return False
    
    def get_url_resource(self, name: str) -> Optional[URLResource]:
        with self.SessionLocal() as db:
            return db.query(URLResource).filter(URLResource.name == name).first()
    
    def add_smart_contract(self, name: str, address: str, network: str = None, description: str = None) -> bool:
        try:
            with self.SessionLocal() as db:
                contract = SmartContract(name=name, address=address, network=network, description=description)
                db.add(contract)
                db.commit()
                return True
        except SQLAlchemyError:
            return False
    
    def get_smart_contract(self, name: str) -> Optional[SmartContract]:
        with self.SessionLocal() as db:
            return db.query(SmartContract).filter(SmartContract.name == name).first()
    
    def search_resources(self, query: str) -> List[URLResource]:
        with self.SessionLocal() as db:
            return db.query(URLResource).filter(
                URLResource.name.ilike(f"%{query}%") | 
                URLResource.description.ilike(f"%{query}%")
            ).all()
    
    def search_contracts(self, query: str) -> List[SmartContract]:
        with self.SessionLocal() as db:
            return db.query(SmartContract).filter(
                SmartContract.name.ilike(f"%{query}%") | 
                SmartContract.description.ilike(f"%{query}%")
            ).all()