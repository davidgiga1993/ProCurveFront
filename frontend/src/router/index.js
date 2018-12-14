import Vue from 'vue'
import Router from 'vue-router'
import Overview from '@/components/pages/OverviewPage'

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Overview',
      component: Overview
    }
  ]
})
