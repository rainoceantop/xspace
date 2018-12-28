<template>
  <transition leave-active-class="hide" enter-active-class="animated slideInRight">
    <section class="container">
      <div id="page-info">用户注册</div>
      <form>
        <label for="username">账号：</label>
        <input
          v-model="username"
          v-on:blur="usernameOnFocus=false"
          v-on:focus="usernameOnFocus=true"
          :class="{'error': usernameerror, 'input-style':true}"
          autocomplete="off"
          type="username"
          name="username"
          placeholder=">___"
          id="username"
        >
        <div :class="{'progess-bar-0': !usernameOnFocus, 'progess-bar-1': usernameOnFocus}"></div>
        <label for="username">名称：</label>
        <input
          v-model="nickname"
          v-on:blur="nicknameOnFocus=false"
          v-on:focus="nicknameOnFocus=true"
          :class="{'error': nicknameerror, 'input-style':true}"
          autocomplete="off"
          type="text"
          name="nickname"
          placeholder=">___"
          id="nickname"
        >
        <div :class="{'progess-bar-0': !nicknameOnFocus, 'progess-bar-1': nicknameOnFocus}"></div>
        <label for="username">密码：</label>
        <input
          v-model="password1"
          v-on:blur="password1OnFocus=false"
          v-on:focus="password1OnFocus=true"
          :class="{'error': password1error, 'input-style':true}"
          type="password"
          name="password1"
          placeholder=">___"
          id="password1"
        >
        <div :class="{'progess-bar-0': !password1OnFocus, 'progess-bar-1': password1OnFocus}"></div>
        <label for="username">重复密码：</label>
        <input
          v-model="password2"
          type="password"
          v-on:blur="password2OnFocus=false"
          v-on:focus="password2OnFocus=true"
          :class="{'error': password2error, 'input-style':true}"
          name="password2"
          placeholder=">___"
          id="password2"
        >
        <div :class="{'progess-bar-0': !password2OnFocus, 'progess-bar-1': password2OnFocus}"></div>
        <p
          :class="['warn', (usernameerror || nicknameerror || password1error || password2error) ? 'show' : 'hide']"
        >* 账号只能由字母数字组成长度区间[6-20]，名称长度区间区间[1-20]，密码不能包含非法字符，长度区间[8-40]</p>
        <div class="form-footer">
          <input class="button-style" type="button" @click="registration()" value="注册">
          <router-link to="/user/login">已有账号？去登录</router-link>
        </div>
      </form>
    </section>
  </transition>
</template>

<script>
export default {
  name: "register",
  data() {
    return {
      username: "",
      nickname: "",
      password1: "",
      password2: "",

      u_p: /^[a-zA-Z0-9]{6,20}$/,
      p_p: /^[a-zA-Z0-9,./~!@#$%^&*()_+]{8,40}$/,

      usernameerror: false,
      nicknameerror: false,
      password1error: false,
      password2error: false,

      usernameOnFocus: false,
      nicknameOnFocus: false,
      password1OnFocus: false,
      password2OnFocus: false
    };
  },
  methods: {
    registration: function() {
      // 判断username
      if (!this.u_p.test(this.username)) this.usernameerror = true;
      else this.usernameerror = false;
      // 判断密码
      if (!this.p_p.test(this.password1)) this.password1error = true;
      else this.password1error = false;
      if (!this.p_p.test(this.password2) || this.password2 !== this.password1)
        this.password2error = true;
      else this.password2error = false;

      // 判断名称
      if (this.nickname.length > 20 || this.nickname.length === 0)
        this.nicknameerror = true;
      else this.nicknameerror = false;

      if (
        this.usernameerror === false &&
        this.nicknameerror === false &&
        this.password1error === false &&
        this.password2error === false
      ) {
        this.$store.dispatch("register", {
          username: this.username,
          nickname: this.nickname,
          password1: this.password1,
          password2: this.password2
        });
      }
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../assets/scss/config";
@import "../assets/scss/login_register";
</style>
