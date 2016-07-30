from contextlib import contextmanager

from flask import Flask, abort, jsonify
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

db_engine = create_engine('sqlite:///:memory:')
session_factory = sessionmaker(bind=db_engine)
Session = scoped_session(session_factory)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        print '[SESSION] Comitting...'
        session.commit()
    except:
        print '[SESSION] Rolling back...'
        session.rollback()
        raise
    finally:
        session.close()

BaseModel = declarative_base()


class Item(BaseModel):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(16))

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }

BaseModel.metadata.create_all(db_engine)

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(error):
    error = {'error': 'not found'}
    result = jsonify(error)
    return result, 404


@app.route("/", methods=['POST'])
def create_item():
    with session_scope() as db_session:
        item = Item()
        db_session.add(item)
        db_session.flush()

        item.name = 'Item #' + str(item.id)
        db_session.flush()

        ser_item = item.serialize()
        result = jsonify(ser_item)
        return result


@app.route("/")
def get_items():
    with session_scope() as db_session:
        items = db_session.query(Item)
        ser_items = [item.serialize() for item in items]
        result = jsonify({'items': ser_items})
        return result


@app.route("/<int:id>")
def get_item(id):
    with session_scope() as db_session:
        item = db_session.query(Item).filter(Item.id == id).first()
        if not item:
            abort(404)
        ser_item = item.serialize()
        result = jsonify(ser_item)
        return result

if __name__ == "__main__":
    app.run()
