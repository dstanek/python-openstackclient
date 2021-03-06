#   Copyright 2012-2013 OpenStack Foundation
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

"""Identity v3 User action implementations"""

import logging
import six
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateUser(show.ShowOne):
    """Create user command"""

    log = logging.getLogger(__name__ + '.CreateUser')

    def get_parser(self, prog_name):
        parser = super(CreateUser, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<user-name>',
            help='New user name',
        )
        parser.add_argument(
            '--password',
            metavar='<user-password>',
            help='New user password',
        )
        parser.add_argument(
            '--email',
            metavar='<user-email>',
            help='New user email address',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='New default project name or ID',
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='New default domain name or ID',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='Description for new user',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable user',
        )
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable user',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        if parsed_args.project:
            project_id = utils.find_resource(
                identity_client.projects, parsed_args.project).id
        else:
            project_id = None

        if parsed_args.domain:
            domain_id = utils.find_resource(
                identity_client.domains, parsed_args.domain).id
        else:
            domain_id = None

        user = identity_client.users.create(
            parsed_args.name,
            domain_id,
            project_id,
            parsed_args.password,
            parsed_args.email,
            parsed_args.description,
            parsed_args.enabled
        )

        info = {}
        info.update(user._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteUser(command.Command):
    """Delete user command"""

    log = logging.getLogger(__name__ + '.DeleteUser')

    def get_parser(self, prog_name):
        parser = super(DeleteUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='Name or ID of user to delete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        user = utils.find_resource(
            identity_client.users, parsed_args.user)
        identity_client.users.delete(user.id)
        return


class ListUser(lister.Lister):
    """List users and optionally roles assigned to users"""

    log = logging.getLogger(__name__ + '.ListUser')

    def get_parser(self, prog_name):
        parser = super(ListUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            nargs='?',
            help='Name or ID of user to list [required with --role]',
        )
        parser.add_argument(
            '--role',
            action='store_true',
            default=False,
            help='List the roles assigned to <user>',
        )
        domain_or_project = parser.add_mutually_exclusive_group()
        domain_or_project.add_argument(
            '--domain',
            metavar='<domain>',
            help='Filter list by <domain> [Only valid with --role]',
        )
        domain_or_project.add_argument(
            '--project',
            metavar='<project>',
            help='Filter list by <project> [Only valid with --role]',
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Additional fields are listed in output',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        if parsed_args.role:
            # List roles belonging to user

            # User is required here, bail if it is not supplied
            if not parsed_args.user:
                sys.stderr.write('Error: User must be specified')
                return ([], [])

            user = utils.find_resource(
                identity_client.users,
                parsed_args.user,
            )

            # List a user's roles
            if not parsed_args.domain and not parsed_args.project:
                columns = ('ID', 'Name')
                data = identity_client.roles.list(
                    user=user,
                    domain='default',
                )
            # List a user's roles on a domain
            elif parsed_args.user and parsed_args.domain:
                columns = ('ID', 'Name', 'Domain', 'User')
                domain = utils.find_resource(
                    identity_client.domains,
                    parsed_args.domain,
                )
                data = identity_client.roles.list(
                    user=user,
                    domain=domain,
                )
                for user_role in data:
                    user_role.user = user.name
                    user_role.domain = domain.name
            # List a user's roles on a project
            elif parsed_args.user and parsed_args.project:
                columns = ('ID', 'Name', 'Project', 'User')
                project = utils.find_resource(
                    identity_client.projects,
                    parsed_args.project,
                )
                data = identity_client.roles.list(
                    user=user,
                    project=project,
                )
                for user_role in data:
                    user_role.user = user.name
                    user_role.project = project.name
            else:
                # TODO(dtroyer): raise exception here, this really is an error
                sys.stderr.write("Error: Must specify --domain or --project "
                                 "with --role\n")
                return ([], [])
        else:
            # List users
            if parsed_args.long:
                columns = ('ID', 'Name', 'Project Id', 'Domain Id',
                           'Description', 'Email', 'Enabled')
            else:
                columns = ('ID', 'Name')
            data = self.app.client_manager.identity.users.list()

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetUser(command.Command):
    """Set user command"""

    log = logging.getLogger(__name__ + '.SetUser')

    def get_parser(self, prog_name):
        parser = super(SetUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='Name or ID of user to change',
        )
        parser.add_argument(
            '--name',
            metavar='<new-user-name>',
            help='New user name',
        )
        parser.add_argument(
            '--password',
            metavar='<user-password>',
            help='New user password',
        )
        parser.add_argument(
            '--email',
            metavar='<user-email>',
            help='New user email address',
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='New domain name or ID',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='New project name or ID',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable user (default)',
        )
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable user',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        user = utils.find_resource(
            identity_client.users, parsed_args.user)
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.email:
            kwargs['email'] = parsed_args.email
        if parsed_args.password:
            kwargs['password'] = parsed_args.password
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.project:
            project_id = utils.find_resource(
                identity_client.projects, parsed_args.project).id
            kwargs['projectId'] = project_id
        if parsed_args.domain:
            domain_id = utils.find_resource(
                identity_client.domains, parsed_args.domain).id
            kwargs['domainId'] = domain_id
        if 'enabled' in parsed_args:
            kwargs['enabled'] = parsed_args.enabled

        if not len(kwargs):
            sys.stderr.write("User not updated, no arguments present")
            return
        identity_client.users.update(user.id, **kwargs)
        return


class ShowUser(show.ShowOne):
    """Show user command"""

    log = logging.getLogger(__name__ + '.ShowUser')

    def get_parser(self, prog_name):
        parser = super(ShowUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='Name or ID of user to display',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        user = utils.find_resource(
            identity_client.users, parsed_args.user)

        info = {}
        info.update(user._info)
        return zip(*sorted(six.iteritems(info)))
