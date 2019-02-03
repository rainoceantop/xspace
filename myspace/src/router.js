import Vue from 'vue'
import Router from 'vue-router'
import store from './store'
import Home from './views/Home'


Vue.use(Router)

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: {
        title: '痕迹'
      }
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
      component: () => import('./views/Moments'),
      meta: {
        title: '关注动态'
      }
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
      component: () => import('./views/BlogInfoPage'),
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
      component: () => import('./views/PhotoInfoPage'),
      props: true
    },
    {
      path: '/:id',
      name: 'myspace',
      component: () => import('./views/MySpace'),
      props: true,
      meta: {
        title: '个人空间'
      },
      children: [
        {
          path: '/b/:blogid',
          name: 'blogInfo',
          components: {
            leftView: () => import('./components/BlogInfo')
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
            leftView: () => import('./components/PhotoInfo')
          },
          props: {
            default: true,
            leftView: true
          }
        },
        {
          path: '/create/blog',
          name: 'blogCreate',
          beforeEnter: (to, from, next) => {
            if (store.state.login) next()
            else next('/')
          },
          components: {
            leftView: () => import('./components/BlogCreate')
          },
          props: {
            default: true
          }
        },
        {
          path: '/create/photo',
          name: 'photoCreate',
          beforeEnter: (to, from, next) => {
            if (store.state.login) next()
            else next('/')
          },
          components: {
            leftView: () => import('./components/PhotoCreate')
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
        else next('/')
      },
      component: () => import('./views/ProfileEdit'),
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
router.beforeEach((to, from, next) => {
  /* 路由发生变化修改页面title */
  if (to.meta.title) {
    document.title = to.meta.title;
  }
  next();
})
export default router
