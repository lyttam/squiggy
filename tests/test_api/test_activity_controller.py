"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

import json

from flask import current_app as app
from squiggy.models.activity_type import DEFAULT_ACTIVITY_TYPE_CONFIGURATION
from squiggy.models.user import User
from tests.util import override_config


def api_get_configuration(client, expected_status_code=200):
    response = client.get('/api/activities/configuration')
    assert response.status_code == expected_status_code
    return response.json


def api_update_configuration(client, updates=None, expected_status_code=200):
    response = client.post(
        '/api/activities/configuration',
        data=json.dumps(updates),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code


class TestGetActivityConfiguration:
    """API to get activity configuration for a course."""

    def test_anonymous(self, client):
        """Denies anonymous user."""
        api_get_configuration(client, expected_status_code=401)

    def _assert_valid_configuration(self, client, fake_auth, canvas_id):
        """Return default configuration values with db-based overrides to authorized user."""
        user = User.find_by_canvas_user_id(canvas_id)
        fake_auth.login(user.id)
        response = api_get_configuration(client)

        expected_length = len(DEFAULT_ACTIVITY_TYPE_CONFIGURATION) if app.config['FEATURE_FLAG_WHITEBOARDS'] else 12
        assert len(response) == expected_length

        for config in response:
            default_config = next(c for c in DEFAULT_ACTIVITY_TYPE_CONFIGURATION if c['type'] == config['type'])
            if config['type'] == 'asset_add':
                assert config['points'] == 5
                assert config['enabled'] is True
            elif config['type'] == 'asset_comment':
                assert config['points'] == 2
                assert config['enabled'] is True
            else:
                assert config['points'] == default_config['points']
                assert config['enabled'] == default_config['enabled']

    def test_student(self, client, fake_auth):
        """Allows student."""
        self._assert_valid_configuration(client, fake_auth, canvas_id=8765432)

    def test_teacher(self, client, fake_auth):
        """Allows student."""
        self._assert_valid_configuration(client, fake_auth, canvas_id=9876543)


class TestUpdateActivityConfiguration:
    """API to ipdate activity configuration for a course."""

    def test_anonymous(self, client):
        """Denies anonymous user."""
        api_update_configuration(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        student = User.find_by_canvas_user_id(8765432)
        fake_auth.login(student.id)
        api_update_configuration(client, expected_status_code=401)

    def test_ill_formed_data(self, client, fake_auth):
        """Rejects ill-formed configurations."""
        teacher = User.find_by_canvas_user_id(9876543)
        fake_auth.login(teacher.id)
        api_update_configuration(
            client,
            updates=[
                {'type': 'asset_add', 'enabled': True, 'points': 5},
                {'type': 'asset_puree', 'enabled': False, 'points': 4000},
            ],
            expected_status_code=400,
        )

    def test_well_formed_data(self, client, fake_auth):
        for flag in (True, False):
            with override_config(app, 'FEATURE_FLAG_WHITEBOARDS', flag):
                teacher = User.find_by_canvas_user_id(9876543)
                fake_auth.login(teacher.id)

                old_points = User.find_by_id(1).points

                api_update_configuration(
                    client,
                    updates=[
                        {'type': 'asset_add', 'enabled': True, 'points': 3},
                        {'type': 'get_asset_comment', 'enabled': False, 'points': 12},
                    ],
                )
                new_config = api_get_configuration(client)
                expected_length = len(DEFAULT_ACTIVITY_TYPE_CONFIGURATION) if app.config['FEATURE_FLAG_WHITEBOARDS'] else 12
                assert len(new_config) == expected_length

                for config in new_config:
                    default_config = next(c for c in DEFAULT_ACTIVITY_TYPE_CONFIGURATION if c['type'] == config['type'])
                    if config['type'] == 'asset_add':
                        assert config['points'] == 3
                        assert config['enabled'] is True
                    elif config['type'] == 'asset_comment':
                        assert config['points'] == 2
                        assert config['enabled'] is True
                    elif config['type'] == 'get_asset_comment':
                        assert config['points'] == 12
                        assert config['enabled'] is False
                    else:
                        assert config['points'] == default_config['points']
                        assert config['enabled'] == default_config['enabled']

                assert User.find_by_id(1).points == old_points - 6

                # Reset to default.
                api_update_configuration(
                    client,
                    updates=[
                        {'type': 'asset_add', 'enabled': True, 'points': 5},
                        {'type': 'get_asset_comment', 'enabled': True, 'points': 1},
                    ],
                )
                assert User.find_by_id(1).points == old_points


class TestActivityCsvDownload:

    def _api_download_csv(self, client, expected_status_code=200):
        response = client.get('/api/activities/csv')
        assert response.status_code == expected_status_code
        return response.data

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_download_csv(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        student = User.find_by_canvas_user_id(8765432)
        fake_auth.login(student.id)
        self._api_download_csv(client, expected_status_code=401)

    def test_authorized_csv(self, client, fake_auth):
        """Default configuration values with db-based overrides are returned to authorized user."""
        teacher = User.find_by_canvas_user_id(9876543)
        fake_auth.login(teacher.id)
        response = self._api_download_csv(client)
        rows = response.decode('utf-8').split('\n')
        assert rows[0].strip() == 'user_id,user_name,action,date,score,running_total'
        parsed_rows = [r.strip().split(',') for r in rows]
        assert len(parsed_rows) > 0
        assert parsed_rows[1][0] == '1'
        assert parsed_rows[1][1] == 'Oliver Heyer'
        assert parsed_rows[1][2] == 'asset_add'
        assert parsed_rows[1][3] is not None
        assert parsed_rows[1][4] == '5'
        assert parsed_rows[1][5] == '5'
        for i in range(2, 5):
            assert int(parsed_rows[i][5]) == int(parsed_rows[i][4]) + int(parsed_rows[i - 1][5])


class TestActivitiesForUser:

    def _api_download_user_activities(self, client, user_id, expected_status_code=200):
        path = f'/api/activities/user/{user_id}'
        response = client.get(path)
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous_activities(self, client, mock_asset):
        """Denies anonymous user."""
        self._api_download_user_activities(client, user_id=mock_asset.users[0].id, expected_status_code=401)

    def test_different_course_user(self, client, fake_auth, mock_asset, mock_other_course_user):
        """Denies user in another course."""
        fake_auth.login(mock_other_course_user.id)
        user_id = mock_asset.users[0].id
        self._api_download_user_activities(client, user_id=user_id, expected_status_code=404)

    def test_get_ones_own_activities(self, client, fake_auth, mock_asset):
        user_id = mock_asset.users[0].id
        fake_auth.login(user_id)
        response = self._api_download_user_activities(client, user_id=user_id)
        creations = response['actions']['creations']
        assert len(creations) == 1
        assert creations[0]['type'] == 'asset_add'
        assert creations[0]['date']
        assert creations[0]['user']['id'] == mock_asset.users[0].id
        assert creations[0]['user']['name'] == mock_asset.users[0].canvas_full_name
        assert creations[0]['user']['image'] == mock_asset.users[0].canvas_image
        assert creations[0]['asset']['id'] == mock_asset.id
        assert creations[0]['asset']['title'] == mock_asset.title
        assert creations[0]['asset']['thumbnailUrl'] == mock_asset.thumbnail_url

        interactions = response['impacts']['interactions']
        assert len(interactions) == 2
        for interaction in interactions:
            assert interaction['type'] == 'get_asset_comment'
            assert interaction['asset']['id'] == mock_asset.id
            assert interaction['user']['id'] == mock_asset.users[0].id
            assert interaction['actorId'] == mock_asset.comments[0].user_id
            assert interaction['comment']['id']

        assert interactions[0]['comment']['body'] == 'But mostly you just make me mad, baby, you just make me mad'
        assert interactions[1]['comment']['body'] == 'And where will she go, and what shall she do, when midnight comes around?'

    def test_get_someone_elses_activities(self, client, fake_auth, mock_asset):
        user1_id = mock_asset.users[0].id
        user2_id = mock_asset.comments[0].user_id
        assert user1_id != user2_id
        fake_auth.login(user2_id)
        response = self._api_download_user_activities(client, user_id=user2_id)
        assert len(response['actions']['interactions'])
        assert len(response['impacts']['interactions'])


class TestActivityInteractions:

    def _api_download_interactions(self, client, expected_status_code=200):
        response = client.get('/api/activities/interactions')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_download_interactions(client, expected_status_code=401)

    def test_no_interactions(self, client, fake_auth):
        student = User.find_by_canvas_user_id(8765432)
        fake_auth.login(student.id)
        response = self._api_download_interactions(client)
        assert response == []

    def test_interactions(self, client, fake_auth, mock_asset):
        fake_auth.login(mock_asset.users[0].id)
        response = self._api_download_interactions(client)
        assert len(response) == 1
        assert response[0]['type'] == 'get_asset_comment'
        assert response[0]['count'] == 2
        assert response[0]['source']
        assert response[0]['target']
