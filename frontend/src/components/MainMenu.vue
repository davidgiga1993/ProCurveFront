<template>
  <div>
    <b-navbar toggleable="md" type="dark" variant="dark">
      <b-navbar-toggle target="nav_collapse"></b-navbar-toggle>
      <b-navbar-brand href="#">ProCurve Front</b-navbar-brand>
      <b-collapse is-nav id="nav_collapse">
        <b-navbar-nav>
          <b-nav-item v-for="route in routes" :key="route.path" :to="route" exact>{{route.meta.title}}</b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
  </div>
</template>

<script>
  export default {
    name: "MainMenu",
    components: {},
    computed: {
      routes() {
        const routes = [];
        for (let i in this.$router.options.routes) {
          if (!this.$router.options.routes.hasOwnProperty(i)) {
            continue
          }
          const route = this.$router.options.routes[i];
          if (route.hasOwnProperty('meta') && route.meta.showInMenu) {
            routes.push(route);
          }
        }
        return routes;
      },
      currentUser() {
        return this.$root.state.user;
      },
      isLoggedIn() {
        return this.$root.state.isLoggedIn;
      }
    }
  }
</script>

<style scoped>
  .ml-auto {
    color: white;
  }
</style>
