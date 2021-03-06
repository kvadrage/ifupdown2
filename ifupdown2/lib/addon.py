# Copyright (C) 2017, 2018 Cumulus Networks, Inc. all rights reserved
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; version 2.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# https://www.gnu.org/licenses/gpl-2.0-standalone.html
#
# Author:
#       Julien Fortin, julien@cumulusnetworks.com
#
# addon -- Addon base class
#

import logging

from collections import OrderedDict

try:
    from ifupdown2.lib.io import IO
    from ifupdown2.lib.sysfs import Sysfs
    from ifupdown2.lib.iproute2 import IPRoute2
    from ifupdown2.lib.base_objects import Netlink, Cache, Requirements
except (ImportError, ModuleNotFoundError):
    from lib.io import IO
    from lib.sysfs import Sysfs
    from lib.iproute2 import IPRoute2
    from lib.base_objects import Netlink, Cache, Requirements


class Addon(Netlink, Cache):
    """
    Base class for ifupdown2 addon modules
    Provides common infrastructure methods for all addon modules
    """

    def __init__(self):
        Netlink.__init__(self)
        Cache.__init__(self)

        self.logger = logging.getLogger("ifupdown2.addons.%s" % self.__class__.__name__)

        self.io = IO()
        self.sysfs = Sysfs
        self.iproute2 = IPRoute2()
        self.requirements = Requirements()

        self.__alias_to_attribute = {}

        for attribute_name, attribute_object in self.__get_modinfo().get("attrs", {}).items():
            for alias in attribute_object.get("aliases", []):
                self.__alias_to_attribute[alias] = attribute_name

    def __get_modinfo(self) -> dict:
        try:
            return self._modinfo
        except AttributeError:
            return {}

    def translate(self, ifaceobjs):
        """
        Replace attribute aliases from user configuration with real attribute name
        """
        for ifaceobj in ifaceobjs:
            ifaceobj.config = OrderedDict(
                [
                    (self.__alias_to_attribute[user_attr], user_value)
                    if user_attr in self.__alias_to_attribute
                    else (user_attr, user_value)
                    for user_attr, user_value in ifaceobj.config.items()
                ]
            )
