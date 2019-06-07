import datetime

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator

from lib.util_datetime import timezone_aware_datetime
from vidme.extensions import db

class AwareDateTime(TypeDecorator):
    """
    A DateTime type which can only store tz-aware DateTimes.

    Source:
        https://gist.github.com/inklesspen/90b554c864b99340747e
    """
    impl = DateTime(timezone=True)

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
            raise ValueError('{!r} must be TZ-aware'.format(value))
        return value

    def __repr__(self):
        return 'AwareDateTime()'

class ResourceMixin(object):
    """
    For adding common functionality to our SQL models
    """
    # Keep track of when records are created and updated
    created_on = db.Column(AwareDateTime(), 
                            default=timezone_aware_datetime)
    updated_on = db.Column(AwareDateTime(),
                            default=timezone_aware_datetime,
                            onupdate=timezone_aware_datetime)
    
    @classmethod
    def sort_by(cls, field, direction):
        """
        Validate the sort field and direction.
        """
        pass

    @classmethod
    def bulk_delete(cls, ids):
        """
        Delete 1 or more model instances.

        :param ids: List of ids to be deleted
        """
        pass

    def save(self):
        """
        Save a model instance.

        :return: Model instance
        """
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """
        Delete a model instance.

        :return: db.session.commit() result
        """
        db.session.delete(self)
        return db.session.commit()