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

from datetime import datetime

from squiggy.lib.aws import get_s3_signed_url, is_s3_preview_url


class TestAws:
    """AWS utility module."""

    def test_identifies_preview_urls(self):
        assert is_s3_preview_url('https://suitec-preview-images-dev.s3-us-west-2.amazonaws.com/deadd00d')
        assert is_s3_preview_url('https://suitec-preview-images-qa.s3-us-west-2.amazonaws.com/8675309')
        assert is_s3_preview_url('https://suitec-preview-images-prod.s3-us-west-2.amazonaws.com/abba1974')
        assert not is_s3_preview_url('https://xkcd.com/1636/')

    def test_recognizes_valid_presigned_url(self):
        presigned = f'https://suitec-preview-images-dev.s3-us-west-2.amazonaws.com/deadd00d?Expires={int(datetime.utcnow().timestamp()) + 4000}'
        assert get_s3_signed_url(presigned) == presigned
