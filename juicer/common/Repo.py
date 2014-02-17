# -*- coding: utf-8 -*-
# Juicer - Administer Pulp and Release Carts
# Copyright © 2014, Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import json
import juicer.utils.Log
import juicer.utils
from juicer.common.Errors import JuicerRepoExclusionError


class Repo(object):
    """
    Internal representation of a repository object
    """
    def __init__(self, repo_name, env, repo_def=None, pulp_def=None):
        """
        `repo_name` - Name of this repo
        `env` - Environment the repo lives in
        `repo_def` - Repository definition as per juicer (see: docs/markdown/repo_syntax.md)
        `pulp_def` - Repository definition as per pulp (see: [1] for an example)

        Note: Only one of `repo_def` and `pulp_def` may be given during instantiation

        Note: Repo objects only handle updating `checksum_type` currently

        [1] https://pulp-dev-guide.readthedocs.org/en/pulp-2.3/integration/rest-api/repo/retrieval.html#retrieve-a-single-repository
        """
        juicer.utils.Log.log_debug("creating repo object for %s-%s" % (repo_name, env))
        if repo_def and pulp_def:
            raise JuicerRepoExclusionError("While instantiating repo '%s': 'repo_def' and 'pulp_def' cannot be set at the same time" % repo_name)

        self.spec = {}
        self['env'] = env

        if repo_def:
            self._parse_repo_def(repo_def)
        elif pulp_def:
            self._parse_pulp_def(pulp_def)
        else:
            self['repo_def'] = {}
            self['pulp_def'] = {}

        juicer.utils.Log.log_debug("instantiated Repo object for %s-%s" % (repo_name, env))

    def _parse_repo_def(self, repo_def):
        self['type'] = 'juicer'
        self['orig_def'] = repo_def
        self['name'] = repo_def['name']
        self['checksum'] = repo_def['checksum_type']

    def _parse_pulp_def(self, repo_def):
        self['type'] = 'pulp'
        self['orig_def'] = repo_def
        self['name'] = repo_def['display_name']
        self['rpm_count'] = repo_def['content_unit_counts']['rpm']
        self['srpm_count'] = repo_def['content_unit_counts']['srpm']
        self['checksum'] = repo_def['scratchpad']['checksum_type']

    def __setitem__(self, key, value):
        self.spec[key] = value

    def __getitem__(self, item):
        return self.spec[item]

    def __str__(self):
        return juicer.utils.create_json_str(self['orig_def'])

    def _repo_ds(self):
        return self['orig_def']

# Custom encoder for Repo types so we can dump them with standard json tools
class RepoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Repo):
            return obj._repo_ds()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
