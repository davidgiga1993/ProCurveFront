<template>
  <div>
    <h1>Ports</h1>
    <table class="table table-sm table-dark">
      <tbody>
      <tr v-for="row in rows">
        <td v-for="port in row" :id="'port-' +port.port" :class="{highlight: port.highlight}">
          {{port.port}}<br>
          {{port.vlanNames}}
        </td>
      </tr>
      </tbody>
    </table>
    <b-tooltip v-for="port in config.ports" :target="'port-'+port.port" placement="bottom">
      Port {{port.port}}<br>
      VLans:
      <ul>
        <li v-for="name in port.taggedNames">[T] {{name}}</li>
        <li v-for="name in port.untaggedNames">[U] {{name}}</li>
      </ul>

    </b-tooltip>

    <h1>VLans</h1>
    <div v-for="vlan in config.vlans">
      <h4>{{vlan.name}}</h4>
      <b-button @click="highlightVlan(vlan.id)"
                :variant="vlanButtonVariant(vlan.id)">Highlight
      </b-button>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'OverviewPage',
    data() {
      return {
        config: {
          ports: [],
          vlans: []
        },
        vlanMap: {},

        highlightedVlan: -1
      }
    },
    computed: {
      rows() {
        const ports = this.config.ports;
        // Two rows (all odd, all even)
        const rows = [[], []];
        for (let X = 0; X < ports.length; X++) {
          const port = ports[X];
          rows[X % 2].push(port);
        }
        return rows;
      }
    }, methods: {
      getVlanNames(vlanMap, port) {
        let names = '';
        for (let X = 0; X < port.tagged.length; X++) {
          names += vlanMap[port.tagged[X]].shortName;
        }
        for (let X = 0; X < port.untagged.length; X++) {
          names += vlanMap[port.untagged[X]].shortName;
        }
        return names;
      },

      vlanButtonVariant(vlanId) {
        if (this.highlightedVlan === vlanId) {
          return 'primary';
        }
        return 'default';
      },

      highlightVlan(vlanId) {
        if (this.highlightedVlan === vlanId) {
          // Disable highlight again
          vlanId = -1;
        }
        this.highlightedVlan = vlanId;
        const ports = this.config.ports;
        for (let X = 0; X < ports.length; X++) {
          const port = ports[X];
          port.highlight = port.tagged.includes(vlanId) ||
            port.untagged.includes(vlanId);
        }
      }
    },
    created() {
      this.$http.get('static/portConfig.json').then(response => {
        const config = response.body;

        const vlanMap = {};
        for (let X = 0; X < config.vlans.length; X++) {
          const vlan = config.vlans[X];
          vlan.shortName = vlan.name.substring(0, 1);
          vlanMap[vlan.id] = vlan;
        }
        for (let X = 0; X < config.ports.length; X++) {
          const port = config.ports[X];
          port.vlanNames = this.getVlanNames(vlanMap, port);
          port.taggedNames = port.tagged.map(vlanId => {
            return vlanMap[vlanId].name
          });
          port.untaggedNames = port.untagged.map(vlanId => {
            return vlanMap[vlanId].name
          });
          port.highlight = false;
        }

        this.vlanMap = vlanMap;
        this.config = config;
      }, response => {

      });
    }
  }
</script>

<style>
  ul {
    text-align: left;
  }

  td {
    width: 4%;
    text-align: center;
    padding: 20px;
    border: 0.15rem solid;
  }

  tr td:nth-child(6), tr td:nth-child(12), tr td:nth-child(18) {
    border-right: 0.15rem solid white !important;
  }

  .highlight {
    background-color: #007bff;
  }

</style>
