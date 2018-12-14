#
# Copyright (C) 2018  Omer Akram
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import os

from flask import Flask
from flask_restful import Api, Resource, reqparse

import controller

app = Flask(__name__)
api = Api(app)


class ChangeBrightnessResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('brightness', type=float, help='Should be a number between 1 and 100', required=True)
        args = parser.parse_args(strict=True)
        brightness = args['brightness']
        # Sanitize...
        if brightness < 1:
            brightness = 1
        elif brightness > 100:
            brightness = 100
        controller.set_brightness(brightness)
        return {'brightness': controller.brightness_current_percent}, 200

    def get(self):
        return {'brightness': controller.brightness_current_percent}, 200


api.add_resource(ChangeBrightnessResource, '/api/brightness')


if __name__ == '__main__':
    if os.geteuid() != 0:
        print('Must run as root.')
        exit(1)

    controller = controller.BrightnessControl()
    app.run(
        host=os.environ.get("BRIGHTNESS_SERVER_HOST", "127.0.0.1"),
        port=os.environ.get("BRIGHTNESS_SERVER_PORT", 5020),
        debug=False
    )
