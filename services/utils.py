from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def save_object(object: dict, db_session: Session):
    """
    Save object to database
    """
    db_session.add(object)
    db_session.commit()
    db_session.refresh(object)
    return object


def delete_object(object: dict, db_session: Session):
    """
    Delete record from database
    """
    db_session.delete(object)
    db_session.commit()
    return object


def get_object_by_id(model, object_id: int, db_session: Session):
    """
    Get object for database by id
    :param model: model class
    :param object_id: object id
    :param db_session: database session
    :param error_text: error text
    :return:
    """
    filtered_object = db_session.query(model).filter(model.id == object_id).first()
    if not filtered_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return filtered_object
