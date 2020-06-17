# project/test_tasks.py


import os
import unittest

from views import app, db
from _config import basedir
from models import User


TEST_DB = 'test.db'



class TaskTests(unittest.TestCase):


	############################
	#### setup and teardown ####
	############################


	# executed prior to each test
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
			os.path.join(basedir, TEST_DB)
		self.app = app.test_client()
		db.create_all()


	# executed after each test
	def tearDown(self):
		db.session.remove()
		db.drop_all()


	########################
	#### helper methods ####
	########################


	def login(self, name, password):
		return self.app.post('/', data=dict(
			name=name, password=password), follow_redirects=True)


	def register(self, name, email, password, confirm):
		return self.app.post(
			'register/',
			data=dict(
				name=name,
				email=email,
				password=password,
				confirm=confirm
			),
			follow_redirects=True
		)


	def logout(self):
		return self.app.get('logout/', follow_redirects=True)


	def create_user(self, name, email, password):
		new_user = User(name=name, email=email, password=password)
		db.session.add(new_user)
		db.session.commit()


	def create_task(self):
		return self.app.post('add/', data=dict(
			name='Go to the bank',
			due_date='10/08/2016',
			priority='1',
			posted_date='10/08/2016',
			status='1'
		), follow_redirects=True)


	###############
	#### tests ####
	###############


	# form is present page
	def test_form_is_present(self):
		response = self.app.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Please login to access your task list.', response.data)


	# users can access tasks
	def test_logged_in_users_can_access_tasks_page(self):
		self.register(
			'Fletcher', 'fletcher@realpython.com', 'python101', 'python101'
		)
		self.login('Fletcher', 'python101')
		response = self.app.get('tasks/')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Add a new task:', response.data)


	def test_not_logged_in_users_cannot_access_tasks_page(self):
		response = self.app.get('tasks/', follow_redirects=True)
		self.assertIn(b'You need to login first.', response.data)

	# users can add tasks (form validation)
	def test_users_can_add_tasks(self):
		self.create_user('Michael', 'michael@realpython.com', 'python')
		self.login('Michael', 'python')
		self.app.get('tasks/', follow_redirects=True)
		response = self.create_task()
		self.assertIn(
			b'New entry was successfully posted. Thanks.', response.data)


	def test_users_cannot_add_tasks_when_error(self):
		self.create_user('Michael', 'michael@realpython.com', 'python')
		self.login('Michael', 'python')
		self.app.get('tasks/', follow_redirects=True)
		response = self.app.post('add/', data=dict(
			name='Go to the bank',
			due_date='',
			priority='1',
			posted_date='02/05/2014',
			status='1'
		), follow_redirects=True)
		self.assertIn(b'This field is required.', response.data)


	# users can complete tasks
	def test_users_can_complete_tasks(self):
		self.create_user('Michael', 'michael@realpython.com', 'python')
		self.login('Michael', 'python')
		self.app.get('tasks/', follow_redirects=True)
		self.create_task()
		response = self.app.get('complete/1/', follow_redirects=True)
		self.assertIn(b'The task was marked as complete.', response.data)


	# users can delete tasks
	def test_users_can_delete_tasks(self):
		self.create_user('Michael', 'michael@realpython.com', 'python')
		self.login('Michael', 'python')
		self.app.get('tasks/', follow_redirects=True)
		self.create_task()
		response = self.app.get('delete/1/', follow_redirects=True)
		self.assertIn(b'The task was deleted.', response.data)


	def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
		self.create_user('Michael', 'michael@realpython.com', 'python')
		self.login('Michael', 'python')
		self.app.get('tasks/', follow_redirects=True)
		self.create_task()
		self.logout()
		self.create_user('Fletcher', 'fletcher@realpython.com', 'python101')
		self.login('Fletcher', 'python101')
		self.app.get('tasks/', follow_redirects=True)
		response = self.app.get('complete/1/', follow_redirects=True)
		self.assertNotIn(b'The task was marked as complete.', response.data)


if __name__ == "__main__":
	unittest.main()