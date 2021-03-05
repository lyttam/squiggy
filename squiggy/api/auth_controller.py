"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from flask import current_app as app, request, session
from flask_login import current_user, login_required, login_user, logout_user
from squiggy.api.errors import ResourceNotFoundError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.util import to_int
from squiggy.models.authorized_user import AuthorizedUser
from squiggy.models.course import Course


@app.route('/api/auth/dev_auth_login', methods=['POST'])
def dev_auth_login():
    params = request.get_json() or {}
    if app.config['DEVELOPER_AUTH_ENABLED']:
        uid = params.get('uid')
        password = params.get('password')
        logger = app.logger
        if password != app.config['DEVELOPER_AUTH_PASSWORD']:
            logger.error('Dev auth: Wrong password')
            return tolerant_jsonify({'message': 'Invalid credentials'}, 401)
        user = AuthorizedUser.find_by_uid(uid)
        if user is None:
            logger.error(f'Dev auth: User with UID {uid} is not registered as an administrator.')
            return tolerant_jsonify({'message': f'Sorry, user with UID {uid} is not registered as an administrator.'}, 403)

        canvas_api_domain = params.get('canvasApiDomain')
        canvas_course_id = to_int(params.get('canvasCourseId'))
        if None in [canvas_api_domain, canvas_course_id]:
            return tolerant_jsonify({'message': 'You must provide valid Canvas course information.'}, 401)
        else:
            course = Course.find_by_canvas_course_id(canvas_api_domain, canvas_course_id)
            if not course:
                logger.error("Dev auth: Invalid 'canvasApiDomain' and/or 'canvasCourseId'")
                return tolerant_jsonify(
                    {
                        'message': f'{canvas_api_domain}:{canvas_course_id} is an invalid Canvas course ID.',
                    },
                    401,
                )
            logger.info(f'Dev auth used to log in as UID {uid}')
            if login_user(user, force=True, remember=True):
                session['course'] = course.to_api_json()
            return tolerant_jsonify(current_user.to_api_json())
    else:
        raise ResourceNotFoundError('Unknown path')


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return tolerant_jsonify(current_user.to_api_json())
