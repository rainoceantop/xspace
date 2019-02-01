import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import router from './router'


Vue.use(Vuex)


export default new Vuex.Store({
  state: {
    // 判断是否登录
    login: false,
    id: 0,
    nickname: '',
    avatar: '',
    bio: '',
    private: 0
  },
  mutations: {
    login(state, user_detail) {
      state.login = true,
        state.id = user_detail.username
      state.nickname = user_detail.nickname,
        state.avatar = user_detail.avatar,
        state.bio = user_detail.bio,
        state.private = user_detail.private
    },
    logout(state) {
      state.login = false,
        state.id = 0,
        state.nickname = '',
        state.avatar = '',
        state.bio = '',
        state.private = false
    }
  },
  actions: {
    login(context, user) {
      axios.post("http://192.168.1.7:8000/api/homespace/login", {
        username: user.username,
        password: user.password
      })
        .then(response => {
          if (response.data.code === 1) {
            context.commit('login', response.data.msg);
            router.push(`/${context.state.id}`);
          }
          else {
            alert(response.data.msg);
            context.commit('logout');
            router.push("/user/login");
          }
        })
        .catch(error => {
          alert(error)
        });
    },
    logout(context) {
      axios.get('http://192.168.1.7:8000/api/homespace/logout').then(response => {
        if (response.data.code === 1) {
          context.commit('logout')
          router.push("/user/login");

        }
        else
          alert(response.data.msg)
      })
    },
    register(context, user) {
      axios.post("http://192.168.1.7:8000/api/homespace/register", {
        username: user.username,
        nickname: user.nickname,
        password1: user.password1,
        password2: user.password2
      })
        .then(response => {
          if (response.data.code === 1) {
            context.commit("login", response.data.msg);
            router.push(`/${context.state.id}`);
          }
          else {
            alert(response.data.msg);
            context.commit('logout');
            router.push("/user/login");
          }
        })
        .catch(error => {
          alert(error)
        });;
    },
    checkLoginAndPush(context) {
      axios.get('http://192.168.1.7:8000/api/homespace/checkLogin')
        .then(response => {
          if (response.data.code === 1) {
            context.commit("login", response.data.msg);
            router.push(`/${context.state.id}`);
          }
          else {
            alert(response.data.msg);
            context.commit('logout');
            router.push("/user/login");
          }
        })
        .catch(error => {
          alert(error)
        });
    },
    checkLogin(context) {
      axios.get('http://192.168.1.7:8000/api/homespace/checkLogin')
        .then(response => {
          if (response.data.code === 1) {
            context.commit("login", response.data.msg);
          }
          else {
            context.commit('logout');
          }
        })
        .catch(error => {
          alert(error)
        });
    }
  }
})
