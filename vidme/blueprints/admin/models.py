from sqlalchemy import func

from vidme.blueprints.user.models import User, db

class Dashboard(object):
	"""
	This class will help with displaying certain data regarding users, as well
	as allowing admins to update modify accounts
	"""
	@classmethod
	def group_and_count_users(cls):
		"""
		Perform a group by/count on all users

		:return: dict
		"""
		return Dashboard._group_and_count(User, User.role)

	@classmethod
	def _group_and_count(cls, model, field):
		"""
		Group results for a specific model and field.

		:param model: Name of the model
		:type model: SQLAlchemy model

		:param field: Name of  the field to group on
		:type field: SQLAlchemy field

		:return: dict
		"""
		count = func.count(field)
		query = db.session.query(count, field).group_by(field).all()

		results = {
			'query': query,
			'total': model.query.count()
		}

		return results