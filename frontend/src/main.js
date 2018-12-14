import Vue from 'vue'
import App from './App'
import router from './router'
// Bootstrap
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

// Ajax
import VueResource from 'vue-resource'

// Misc
import AppState from "@/app/AppState";


Vue.use(VueResource);
Vue.use(BootstrapVue);

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  render: h => h(App),
  data: {
    state: AppState
  }
});
