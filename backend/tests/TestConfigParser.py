from unittest import TestCase

from procurvefront.ConfigParser import VlanConfig, ConfigParser


class TestConfigParser(TestCase):
    def test_range_parser(self):
        numbers = VlanConfig._parse_range('0-10,20,30-40')
        self.assertEqual(23, len(numbers))
        self.assertListEqual(list(range(0, 11)), numbers[:11])
        self.assertListEqual(list(range(30, 41)), numbers[12:])
        self.assertEqual(20, numbers[11])

    def test_parser(self):
        parser = ConfigParser(SAMPLE_CONFIG)
        self.assertEqual(7, len(parser.vlans))

        vlan = parser.vlans[0]
        self.assertEqual(1, vlan.id)
        self.assertEqual('DEFAULT_VLAN', vlan.name)
        self.assertEqual(8, len(vlan.untagged))
        self.assertEqual(40, len(vlan.no_untagged))

        vlan = parser.vlans[1]
        self.assertEqual(10, vlan.id)
        self.assertEqual('Intern', vlan.name)
        self.assertEqual(18, len(vlan.untagged))
        self.assertEqual(3, len(vlan.tagged))

    def test_port_config(self):
        parser = ConfigParser(SAMPLE_CONFIG)
        port_config = parser.create_port_config()
        port = port_config[0]
        self.assertEqual(1, port['port'])
        self.assertListEqual([10], port['untagged'])
        self.assertEqual(0, len(port['tagged']))

        port = port_config[47]
        self.assertEqual(48, port['port'])
        self.assertListEqual([1], port['untagged'])
        self.assertListEqual([10, 20, 30, 40, 100, 17], port['tagged'])


SAMPLE_CONFIG = """
Running configuration:
; J9280A Configuration Editor; Created on release #Y.11.51
hostname "ProCurve Switch 2510G-48"
time daylight-time-rule Western-Europe
interface 25
   speed-duplex 100-full
exit
ip default-gateway 10.1.1.16
snmp-server community "public"
vlan 1
   name "DEFAULT_VLAN"
   untagged 35,37-42,48
   no ip address
   no untagged 1-34,36,43-47
   exit
vlan 10
   name "Intern"
   untagged 1-16,36,46
   no ip address
   tagged 44-45,48
   exit
vlan 20
   name "Extern"
   untagged 33-34
   tagged 44-45,48
   exit
vlan 30
   name "Licht"
   untagged 17-24
   tagged 44-45,48
   exit
vlan 40
   name "Ton"
   untagged 25-32
   tagged 44-45,48
   exit
vlan 100
   name "Mgmt"
   untagged 43-45
   ip address 10.1.100.1 255.255.255.0
   tagged 48
   exit
vlan 17
   name "DMZ"
   untagged 47
   tagged 48
   exit
primary-vlan 10
password manager"""
