import Vue from 'vue'
import Router from 'vue-router'
import MySpace from './views/MySpace'
import Login from './views/Login'
import store from './store'
import CheckStatus from './views/CheckStatus'
import BlogInfo from './components/BlogInfo'
import imageInfo from './components/ImageInfo'
import BlogCreate from './components/BlogCreate'
import ImageCreate from './components/ImageCreate'
import ProfileEdit from './views/ProfileEdit'
import DetailEdit from './components/DetailEdit'
import PasswordChange from './components/PasswordChange'
import AvatarChange from './components/AvatarChange'
import BlogInfoPage from './views/BlogInfoPage'
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
        },]
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
