import Vue from 'vue'
import Router from 'vue-router'
import MySpace from './views/MySpace'
import Login from './views/Login'
import store from './store'
import CheckStatus from './views/CheckStatus'
import BlogInfo from './components/BlogInfo'
import PhotoInfo from './components/PhotoInfo'
import BlogCreate from './components/BlogCreate'
import PhotoCreate from './components/PhotoCreate'
import ProfileEdit from './views/ProfileEdit'
import DetailEdit from './components/DetailEdit'
import PasswordChange from './components/PasswordChange'
import AvatarChange from './components/AvatarChange'
import BlogInfoPage from './views/BlogInfoPage'
import PhotoInfoPage from './views/PhotoInfoPage'
import Home from './views/Home'


Vue.use(Router)

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/b/:blogid',
      name: 'blogInfoPage',
      beforeEnter: (to, from, next) => {
        if (from.path === '/') {
          next()
        } else {
          next(false)
        }
      },
      component: BlogInfoPage,
      props: true
    },
    {
      path: '/p/:photoid',
      name: 'photoInfoPage',
      beforeEnter: (to, from, next) => {
        if (from.path === '/') {
          next()
        } else {
          next(false)
        }
      },
      component: PhotoInfoPage,
      props: true
    },
    {
      path: '/:id',
      name: 'myspace',
      component: MySpace,
      props: true,
      children: [
        {
          path: 'blog',
          component: MySpace,
          props: true,
        },
        {
          path: '/b/:blogid',
          name: 'blogInfo',
          components: {
            default: MySpace,
            leftView: BlogInfo
          },
          props: {
            default: true,
            leftView: true
          }
        },
        {
          path: '/p/:photoid',
          name: 'photoInfo',
          components: {
            default: MySpace,
            leftView: PhotoInfo
          },
          props: {
            default: true,
            leftView: true
          }
        },
        {
          path: '/create/blog',
          name: 'blogCreate',
          components: {
            default: MySpace,
            leftView: BlogCreate
          },
          beforeEnter: (to, from, next) => {
            if (store.state.login) next()
            else next('/user/login')
          },
          props: {
            default: true
          }
        },
        {
          path: '/create/photo',
          name: 'photoCreate',
          components: {
            default: MySpace,
            leftView: PhotoCreate
          },
          beforeEnter: (to, from, next) => {
            if (store.state.login) next()
            else next('/user/login')
          },
          props: {
            default: true
          }
        }]
    },
    {
      path: '/accounts',
      beforeEnter: (to, from, next) => {
        if (store.state.login) next()
        else next('/user/login')
      },
      component: ProfileEdit,
      children: [
        {
          path: 'edit',
          name: 'profileEdit',
          components: {
            editView: DetailEdit
          }
        },
        {
          path: 'avatar/change',
          name: 'avatarChange',
          components: {
            editView: AvatarChange
          }
        },
        {
          path: 'password/change',
          name: 'passwordChange',
          components: {
            editView: PasswordChange
          }
        }
      ],

    },
    {
      path: '/user/login',
      name: 'login',
      beforeEnter: (to, from, next) => {
        if (store.state.login) next(`/${store.state.id}`);
        else next();
      },
      component: Login
    },
    {
      path: '/user/register',
      name: 'register',
      beforeEnter: (to, from, next) => {
        if (store.state.login) next(`/${store.state.id}`);
        else next();
      },
      component: () => import('./views/Register')
    },
  ]
})

export default router
