import Vue from 'vue'
import Router from 'vue-router'
import MySpace from './views/MySpace'
import store from './store'
import BlogInfo from './components/BlogInfo'
import PhotoInfo from './components/PhotoInfo'
import ProfileEdit from './views/ProfileEdit'
import BlogInfoPage from './views/BlogInfoPage'
import PhotoInfoPage from './views/PhotoInfoPage'
import BlogCreate from './components/BlogCreate'
import Home from './views/Home'


Vue.use(Router)

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/tag/:tagname',
      name: 'tag',
      component: Home,
      props: true
    },
    {
      path: '/moments',
      name: 'moments',
      component: () => import('./views/Moments')
    },
    {
      path: '/b/:blogid',
      name: 'blogInfoPage',
      beforeEnter: (to, from, next) => {
        if (to.params.id === undefined) {
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
        if (to.params.id === undefined) {
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
            leftView: () => import('./components/PhotoCreate')
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
            editView: () => import('./components/DetailEdit')
          }
        },
        {
          path: 'avatar/change',
          name: 'avatarChange',
          components: {
            editView: () => import('./components/AvatarChange')
          }
        },
        {
          path: 'password/change',
          name: 'passwordChange',
          components: {
            editView: () => import('./components/PasswordChange')
          }
        },
        {
          path: 'privacy/setting',
          name: 'privacySetting',
          components: {
            editView: () => import('./components/PrivacySetting')
          }
        }
      ],

    },
    {
      path: '/accounts/password/reset',
      name: 'passwordReset',
      component: () => import('./views/PasswordReset')
    },
    {
      path: '/accounts/password/reset/confirm/:uid/:token',
      name: 'passwordResetConfirm',
      component: () => import('./views/PasswordResetConfirm'),

      props: true
    },
    {
      path: '/user/login',
      name: 'login',
      beforeEnter: (to, from, next) => {
        if (store.state.login) next(`/${store.state.id}`);
        else next();
      },
      component: () => import('./views/Login')
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
  ],

  scrollBehavior(to, from, savedPosition) {
    return { x: 0, y: 0 }
  },
})

export default router
