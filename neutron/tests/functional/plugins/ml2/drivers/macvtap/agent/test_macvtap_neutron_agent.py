# Copyright (c) 2016 IBM Corp.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from neutron_lib import constants

from neutron.agent.linux import ip_lib
from neutron.plugins.ml2.drivers.macvtap.agent import macvtap_neutron_agent
from neutron.tests.common import net_helpers
from neutron.tests.functional import base as functional_base


class MacvtapAgentTestCase(functional_base.BaseSudoTestCase):
    def setUp(self):
        super(MacvtapAgentTestCase, self).setUp()
        self.mgr = macvtap_neutron_agent.MacvtapManager({})

    def test_get_all_devices(self):
        # NOTE(ralonsoh): Clean-up before testing. This test is executed with
        # concurrency=1. That means no other test is being executed at the same
        # time. Because the macvtap interface must be created in the root
        # namespace (``MacvtapManager`` cannot handle namespaces), the test
        # deletes any previous existing interface.
        for mac in self.mgr.get_all_devices():
            devices = ip_lib.IPWrapper().get_devices()
            for device in (d for d in devices if d.address == mac):
                device.link.delete()

        # Veth is simulating the hosts eth device. In this test it is used as
        # src_dev for the macvtap
        veth1, veth2 = self.useFixture(net_helpers.VethFixture()).ports
        macvtap = self.useFixture(net_helpers.MacvtapFixture(
            src_dev=veth1.name, mode='bridge',
            prefix=constants.MACVTAP_DEVICE_PREFIX)).ip_dev
        self.assertEqual(set([macvtap.link.address]),
                         self.mgr.get_all_devices())
