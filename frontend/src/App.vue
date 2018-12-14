<template>
  <div class="container" id="app">
    <MainMenu></MainMenu>
    <router-view/>
    <MainFooter></MainFooter>
  </div>
</template>

<script>
  import MainMenu from "@/components/MainMenu";
  import MainFooter from "@/components/MainFooter";

  export default {
    name: 'App',
    components: {MainFooter, MainMenu}
  }
</script>

<style>
</style>
