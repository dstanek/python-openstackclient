#   Copyright 2013 Nebula Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import copy

from openstackclient.identity.v2_0 import user
from openstackclient.tests import fakes
from openstackclient.tests.identity import fakes as identity_fakes
from openstackclient.tests import utils


IDENTITY_API_VERSION = "2.0"

user_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
user_name = 'paul'
user_description = 'Sir Paul'
user_email = 'paul@applecorps.com'

project_id = '8-9-64'
project_name = 'beatles'
project_description = 'Fab Four'

USER = {
    'id': user_id,
    'name': user_name,
    'tenantId': project_id,
    'email': user_email,
    'enabled': True,
}

PROJECT = {
    'id': project_id,
    'name': project_name,
    'description': project_description,
    'enabled': True,
}

PROJECT_2 = {
    'id': project_id + '-2222',
    'name': project_name + ' reprise',
    'description': project_description + 'plus four more',
    'enabled': True,
}


class TestUser(utils.TestCommand):

    def setUp(self):
        super(TestUser, self).setUp()
        self.app.client_manager.identity = \
            identity_fakes.FakeIdentityv2Client()

        # Get a shortcut to the TenantManager Mock
        self.projects_mock = self.app.client_manager.identity.tenants
        # Get a shortcut to the UserManager Mock
        self.users_mock = self.app.client_manager.identity.users


class TestUserCreate(TestUser):

    def setUp(self):
        super(TestUserCreate, self).setUp()

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(PROJECT),
            loaded=True,
        )
        self.users_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(USER),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = user.CreateUser(self.app, None)

    def test_user_create_no_options(self):
        arglist = [user_name]
        verifylist = [
            ('name', user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # users.create(name, password, email, tenant_id=None, enabled=True)
        self.users_mock.create.assert_called_with(
            user_name,
            None,
            None,
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(columns, collist)
        datalist = (user_email, True, user_id, user_name, project_id)
        self.assertEqual(data, datalist)

    def test_user_create_password(self):
        arglist = ['--password', 'secret', user_name]
        verifylist = [('password', 'secret')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # users.create(name, password, email, tenant_id=None, enabled=True)
        self.users_mock.create.assert_called_with(
            user_name,
            'secret',
            None,
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(columns, collist)
        datalist = (user_email, True, user_id, user_name, project_id)
        self.assertEqual(data, datalist)

    def test_user_create_email(self):
        arglist = ['--email', 'barney@example.com', user_name]
        verifylist = [('email', 'barney@example.com')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # users.create(name, password, email, tenant_id=None, enabled=True)
        self.users_mock.create.assert_called_with(
            user_name,
            None,
            'barney@example.com',
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(columns, collist)
        datalist = (user_email, True, user_id, user_name, project_id)
        self.assertEqual(data, datalist)

    def test_user_create_project(self):
        # Return the new project
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(PROJECT_2),
            loaded=True,
        )
        # Set up to return an updated user
        USER_2 = copy.deepcopy(USER)
        USER_2['tenantId'] = PROJECT_2['id']
        self.users_mock.create.return_value = fakes.FakeResource(
            None,
            USER_2,
            loaded=True,
        )

        arglist = ['--project', PROJECT_2['name'], user_name]
        verifylist = [('project', PROJECT_2['name'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': PROJECT_2['id'],
        }
        # users.create(name, password, email, tenant_id=None, enabled=True)
        self.users_mock.create.assert_called_with(
            user_name,
            None,
            None,
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(columns, collist)
        datalist = (user_email, True, user_id, user_name, PROJECT_2['id'])
        self.assertEqual(data, datalist)

    def test_user_create_enable(self):
        arglist = ['--enable', project_name]
        verifylist = [('enable', True), ('disable', False)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # users.create(name, password, email, tenant_id=None, enabled=True)
        self.users_mock.create.assert_called_with(
            project_name,
            None,
            None,
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(columns, collist)
        datalist = (user_email, True, user_id, user_name, project_id)
        self.assertEqual(data, datalist)

    def test_user_create_disable(self):
        arglist = ['--disable', project_name]
        verifylist = [('enable', False), ('disable', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': False,
            'tenant_id': None,
        }
        # users.create(name, password, email, tenant_id=None, enabled=True)
        self.users_mock.create.assert_called_with(
            project_name,
            None,
            None,
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(columns, collist)
        datalist = (user_email, True, user_id, user_name, project_id)
        self.assertEqual(data, datalist)


class TestUserDelete(TestUser):

    def setUp(self):
        super(TestUserDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(USER),
            loaded=True,
        )
        self.users_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = user.DeleteUser(self.app, None)

    def test_user_delete_no_options(self):
        arglist = [user_id]
        verifylist = [
            ('user', user_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.users_mock.delete.assert_called_with(user_id)


class TestUserList(TestUser):

    def setUp(self):
        super(TestUserList, self).setUp()

        self.users_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(USER),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = user.ListUser(self.app, None)

    def test_user_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.list.assert_called_with()

        collist = ('ID', 'Name')
        self.assertEqual(columns, collist)
        datalist = ((user_id, user_name), )
        self.assertEqual(tuple(data), datalist)

    def test_user_list_project(self):
        arglist = ['--project', project_id]
        verifylist = [('project', project_id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.list.assert_called_with()

        collist = ('ID', 'Name')
        self.assertEqual(columns, collist)
        datalist = ((user_id, user_name), )
        self.assertEqual(tuple(data), datalist)

    def test_user_list_long(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.list.assert_called_with()

        collist = ('ID', 'Name', 'Project', 'Email', 'Enabled')
        self.assertEqual(columns, collist)
        datalist = ((user_id, user_name, project_id, user_email, True), )
        self.assertEqual(tuple(data), datalist)


class TestUserSet(TestUser):

    def setUp(self):
        super(TestUserSet, self).setUp()

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(PROJECT),
            loaded=True,
        )
        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(USER),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = user.SetUser(self.app, None)

    def test_user_set_no_options(self):
        arglist = [user_name]
        verifylist = [
            ('user', user_name),
            ('enable', False),
            ('disable', False),
            ('project', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.assertFalse(self.users_mock.update.called)

    def test_user_set_name(self):
        arglist = ['--name', 'qwerty', user_name]
        verifylist = [('name', 'qwerty')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'qwerty',
        }
        self.users_mock.update.assert_called_with(user_id, **kwargs)

    def test_user_set_password(self):
        arglist = ['--password', 'secret', user_name]
        verifylist = [('password', 'secret')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.users_mock.update_password.assert_called_with(user_id, 'secret')

    def test_user_set_email(self):
        arglist = ['--email', 'barney@example.com', user_name]
        verifylist = [('email', 'barney@example.com')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'email': 'barney@example.com',
        }
        self.users_mock.update.assert_called_with(user_id, **kwargs)

    def test_user_set_project(self):
        arglist = ['--project', project_id, user_name]
        verifylist = [('project', project_id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.users_mock.update_tenant.assert_called_with(
            user_id,
            project_id,
        )

    def test_user_set_enable(self):
        arglist = ['--enable', user_name]
        verifylist = [('enable', True), ('disable', False)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
        }
        self.users_mock.update.assert_called_with(user_id, **kwargs)

    def test_user_set_disable(self):
        arglist = ['--disable', user_name]
        verifylist = [('enable', False), ('disable', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': False,
        }
        self.users_mock.update.assert_called_with(user_id, **kwargs)


class TestUserShow(TestUser):

    def setUp(self):
        super(TestUserShow, self).setUp()

        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(USER),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = user.ShowUser(self.app, None)

    def test_user_show(self):
        arglist = [user_id]
        verifylist = [('user', user_id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.get.assert_called_with(user_id)

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(columns, collist)
        datalist = (user_email, True, user_id, user_name, project_id)
        self.assertEqual(data, datalist)
