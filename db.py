from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    address = Column(String)
    description = Column(Text)
    status = Column(String)
    media = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    updates = relationship("OrderUpdate", back_populates="order")

class OrderUpdate(Base):
    __tablename__ = "order_updates"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"))
    update_type = Column(String)
    media = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="updates")

def init_db():
    Base.metadata.create_all(bind=engine)

def add_order(data: dict):
    session = SessionLocal()
    if session.query(Order).filter_by(id=data["id"]).first():
        print(f"🔁 Заказ уже существует: {data['id']}")
        session.close()
        return

    new_order = Order(
        id=data["id"],
        name=data["name"],
        phone=data["phone"],
        address=data["address"],
        description=data["description"],
        status=data.get("status", "новая"),
        media=data.get("media"),
    )
    session.add(new_order)
    session.commit()
    session.close()

def update_status(order_id: str, status: str):
    session = SessionLocal()
    order = session.query(Order).filter_by(id=order_id).first()
    if order:
        order.status = status
        session.commit()
    session.close()

def add_order_update(order_id: str, update_type: str, media: str = None, comment: str = None):
    session = SessionLocal()
    update = OrderUpdate(
        order_id=order_id,
        update_type=update_type,
        media=media,
        comment=comment
    )
    session.add(update)
    session.commit()
    session.close()

def get_order(order_id: str):
    session = SessionLocal()
    order = session.query(Order).filter_by(id=order_id).first()
    session.close()
    if order:
        return {
            "id": order.id,
            "name": order.name,
            "phone": order.phone,
            "address": order.address,
            "description": order.description,
            "status": order.status,
            "media": order.media
        }
    return None

def get_updates_by_order_id(order_id: str):
    session = SessionLocal()
    updates = session.query(OrderUpdate).filter_by(order_id=order_id).order_by(OrderUpdate.timestamp).all()
    session.close()
    return [(u.update_type, u.media, u.comment, u.timestamp) for u in updates]

if __name__ == "__main__":
    init_db()
    print("✅ База PostgreSQL и таблицы инициализированы.")