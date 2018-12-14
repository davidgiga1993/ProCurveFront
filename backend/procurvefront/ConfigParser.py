import re


class VlanConfig:
    UNASSIGNED = 0
    UNTAGGED = 1
    TAGGED = 2

    def __init__(self):
        self.id = 0
        self.name = ''
        self.tagged = []
        self.untagged = []
        self.no_untagged = []

    def set_config(self, key: str, value: str):
        if key == 'name':
            self.name = value.replace('"', '')
            return
        if key == 'untagged':
            self.untagged = self._parse_range(value)
            return
        if key == 'tagged':
            self.tagged = self._parse_range(value)
            return
        if key == 'no untagged':
            self.no_untagged = self._parse_range(value)
            return

    def has_port(self, port: int):
        """
        Checks if the given port is associated with this vlan (tagged or untagged)

        :param port: Port index (1-n)
        :return: 0 if not associated, 1 if untagged, 2 if tagged
        :rtype: int
        """
        if port in self.tagged:
            return VlanConfig.TAGGED
        if port in self.untagged:
            return VlanConfig.UNTAGGED
        return VlanConfig.UNASSIGNED

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def _parse_range(num_range: str):
        """
        Parses a given number range

        :param num_range: Range in the format n-m,a,...
        :return: List of numbers included in the range
        :rtype: List[int]
        """
        numbers = []
        for range_part in num_range.split(','):
            start_end = range_part.split('-')
            if len(start_end) == 1:
                # Single number
                numbers.append(int(range_part))
                continue
            if len(start_end) == 2:
                # Simple n-m range
                numbers.extend(list(range(int(start_end[0]), int(start_end[1]) + 1)))
                continue
            # Unknown
            raise Exception('Unknown range format: ' + range_part)
        return numbers


class ConfigParser:
    SEARCH_VLAN_BLOCK = 0
    IN_VLAN_BLOCK = 1

    VLAN_MATCHER = re.compile(r'^vlan ([0-9]+) *')
    ATTR_MATCHER = re.compile(r'^ +([a-z ]+) (.+)')

    def __init__(self, config: str):
        self._config = config
        self.vlans = []
        """
        Parsed vlan configuration
        
        :type _vlans: List[VlanConfig]
        """
        self._parse()

    def create_port_config(self):
        """
        Transforms the vlan config into a per port config

        :return: List of port configuration
        :rtype: List[dict(str, any)]
        """
        port_cfg = []
        for port_idx in range(1, 48 + 1):  # Switch got 48 ports
            vlans = self._get_vlans(port_idx)
            untagged_ids = [vlan.id for vlan in vlans[VlanConfig.UNTAGGED]]
            tagged_ids = [vlan.id for vlan in vlans[VlanConfig.TAGGED]]

            port_cfg.append({
                'port': port_idx,
                'tagged': tagged_ids,
                'untagged': untagged_ids
            })
        return port_cfg

    def get_vlans_dict(self):
        """
        Returns the vlan configuration as list of dict

        :return: List of dicts
        :rtype: List[dict(str, any)]
        """
        out = []
        for vlan in self.vlans:
            out.append(vlan.to_dict())
        return out

    def _parse(self):
        """
        Parses the configuration
        """
        mode = ConfigParser.SEARCH_VLAN_BLOCK

        current_vlan = None
        for line in self._config.splitlines():
            if mode == ConfigParser.SEARCH_VLAN_BLOCK:
                match = ConfigParser.VLAN_MATCHER.match(line)
                if match is None:
                    continue
                # Found the start of a vlan block
                mode = ConfigParser.IN_VLAN_BLOCK

                current_vlan = VlanConfig()
                current_vlan.id = int(match.group(1))
                continue

            if mode == ConfigParser.IN_VLAN_BLOCK:
                # Parse the vlan attributes
                match = ConfigParser.ATTR_MATCHER.match(line)
                if match is None:
                    # "exit" or similar
                    continue
                key = match.group(1)
                value = match.group(2).strip()
                if value == 'exit':
                    # End of vlan block
                    mode = ConfigParser.SEARCH_VLAN_BLOCK
                    self.vlans.append(current_vlan)
                    continue
                current_vlan.set_config(key, value)

    def _get_vlans(self, port_idx: int):
        """
        Returns the config of the vlan assigned to the port with the given index

        :param port_idx: Port index
        :return: Vlan configs
        :rtype: dict(int, VlanConfig)
        """
        vlans = {
            VlanConfig.UNTAGGED: [],
            VlanConfig.TAGGED: []
        }
        for vlan in self.vlans:
            assignment = vlan.has_port(port_idx)
            if assignment > VlanConfig.UNASSIGNED:
                vlans[assignment].append(vlan)
        return vlans
