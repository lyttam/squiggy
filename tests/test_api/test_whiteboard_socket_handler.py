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

from random import randint

import pytest
from squiggy import std_commit
from squiggy.api.whiteboard_socket_handler import create_whiteboard_elements, update_whiteboard_elements
from squiggy.lib.errors import BadRequestError
from squiggy.lib.login_session import LoginSession
from squiggy.lib.util import is_admin, is_teaching
from squiggy.models.course import Course


class TestWhiteboardElement:

    def test_anonymous(self, mock_whiteboard):
        """Denies anonymous user."""
        with pytest.raises(BadRequestError):
            create_whiteboard_elements(
                current_user=LoginSession(user_id=None),
                socket_id=_get_mock_socket_id(),
                whiteboard_elements=_mock_whiteboard_elements(),
                whiteboard_id=mock_whiteboard['id'],
            )

    def test_unauthorized(self, mock_whiteboard):
        """Denies unauthorized user."""
        with pytest.raises(BadRequestError):
            create_whiteboard_elements(
                current_user=_get_unauthorized_user(mock_whiteboard),
                socket_id=_get_mock_socket_id(),
                whiteboard_elements=_mock_whiteboard_elements(),
                whiteboard_id=mock_whiteboard['id'],
            )

    def test_authorized(self, mock_whiteboard):
        """Authorized creates whiteboard elements."""
        whiteboard_elements = _mock_whiteboard_elements()

        api_json = create_whiteboard_elements(
            current_user=_get_authorized_user(mock_whiteboard),
            socket_id=_get_mock_socket_id(),
            whiteboard_elements=whiteboard_elements,
            whiteboard_id=mock_whiteboard['id'],
        )
        assert len(api_json) == len(whiteboard_elements)


class TestUpdateWhiteboardElements:

    def test_anonymous(self, mock_whiteboard):
        """Denies anonymous user."""
        with pytest.raises(BadRequestError):
            update_whiteboard_elements(
                current_user=LoginSession(user_id=None),
                socket_id=_get_mock_socket_id(),
                whiteboard_elements=mock_whiteboard['whiteboardElements'],
                whiteboard_id=mock_whiteboard['id'],
            )

    def test_unauthorized(self, mock_whiteboard):
        """Denies unauthorized user."""
        with pytest.raises(BadRequestError):
            update_whiteboard_elements(
                current_user=LoginSession(user_id=None),
                socket_id=_get_mock_socket_id(),
                whiteboard_elements=mock_whiteboard['whiteboardElements'],
                whiteboard_id=mock_whiteboard['id'],
            )

    def test_authorized(self, mock_whiteboard):
        """Authorized user can update whiteboard elements."""
        whiteboard_elements = mock_whiteboard['whiteboardElements']
        whiteboard_element = whiteboard_elements[-1]
        updated_fill = 'rgb(128,255,128)'
        whiteboard_element['element']['fill'] = updated_fill

        results = update_whiteboard_elements(
            current_user=_get_authorized_user(mock_whiteboard),
            socket_id=_get_mock_socket_id(),
            whiteboard_elements=whiteboard_elements,
            whiteboard_id=mock_whiteboard['id'],
        )
        std_commit(allow_test_environment=True)

        assert len(results) == len(whiteboard_elements)
        updated_whiteboard_element = next((result for result in results if result.id == whiteboard_element['id']), None)
        assert updated_whiteboard_element
        assert updated_whiteboard_element.element['fill'] == updated_fill


def _get_authorized_user(whiteboard):
    course_id = whiteboard['courseId']
    instructors = list(filter(lambda u: is_teaching(u), Course.find_by_id(course_id).users))
    return LoginSession(user_id=instructors[0].id)


def _get_mock_socket_id():
    return str(randint(1, 9999999))


def _get_unauthorized_user(whiteboard):
    course_id = whiteboard['courseId']
    not_teaching = list(filter(lambda u: not is_admin(u) and not is_teaching(u), Course.find_by_id(course_id).users))
    return LoginSession(user_id=not_teaching[0].id)


def _mock_whiteboard_elements():
    return [
        {
            'assetId': 1,
            'element': {
                'fill': 'rgb(0,0,0)',
                'fontSize': 14,
                'text': '',
                'type': 'text',
            },
        },
        {
            'assetId': 2,
            'element': {
                'fill': 'rgb(0,0,0)',
                'shape': 'Rect:thin',
                'type': 'shape',
            },
        },
    ]