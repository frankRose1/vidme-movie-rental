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
    For adding common functionality to our SQL models such as save(), delete(),
    and created/updated timezone aware dates
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

        :param field: Field name
        :type field: str

        :param direction: Direction
        :type direction: str

        :return: tuple
        """
        if field not in cls.__table__.columns:
            field = 'created_on'
        
        if direction not in ('asc', 'desc'):
            direction = 'asc'
        
        return field, direction

    @classmethod
    def get_bulk_action_ids(cls, scope, ids, omit_ids=[], query=''):
        """
        Determine which IDs are to be modified.

        :param scope: Affect all or only a subset of items
        :type scope: str
        :param ids: List of ids to be modified
        :type ids: list
        :param omit_ids: Remove one or more IDs from the list
        :type omit_ids: list
        :param query: Search query (if applicable)
        :type query: str
        :return: list
        """
        omit_ids = map(str, omit_ids)

        if scope == 'all_search_results':
            # Change the scope to go from selected ids to all search results
            ids = cls.query.with_entities(cls.id).filter(cls.search(query))

            # SQLAlchemy returns a  list of tuples, need a list of strs
            ids = [str(item[0]) for item in ids]

        # Remove one or more items from the list, useful for preventing the
        # current user from deleting themselves from the db
        if omit_ids:
            ids = [id for id in ids if id not in omit_ids]

        return ids


    @classmethod
    def bulk_delete(cls, ids):
        """
        Delete 1 or more model instances.

        :param ids: List of ids to be deleted
        :return: number of items deleted
        """
        delete_count = cls.query.filter(cls.id.in_(ids)).delete(
            synchronize_session=False)
        db.session.commit()

        return delete_count

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
