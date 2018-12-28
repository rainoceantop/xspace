<template>
  <transition leave-active-class="hide" enter-active-class="animated slideInLeft">
    <section class="container">
      <div id="page-info">用户登录</div>
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
        <label for="username">密码：</label>
        <input
          v-model="password"
          v-on:blur="passwordOnFocus=false"
          v-on:focus="passwordOnFocus=true"
          :class="{'error': passworderror, 'input-style':true}"
          type="password"
          name="password1"
          placeholder=">___"
          id="password1"
        >
        <div :class="{'progess-bar-0': !passwordOnFocus, 'progess-bar-1': passwordOnFocus}"></div>
        <p
          :class="['warn', (usernameerror || passworderror) ? 'show' : 'hide']"
        >* 账号只能由字母数字组成，长度区间[6-20]，密码不能包含非法字符，长度区间[8-40]</p>
        <div class="form-footer">
          <input class="button-style" type="button" @click="login" value="登录">
          <router-link to="/user/register">还没账号？去注册</router-link>
        </div>
      </form>
    </section>
  </transition>
</template>

<script>
export default {
  name: "login",
  data() {
    return {
      username: "",
      password: "",

      u_p: /^[a-zA-Z0-9]{6,20}$/,
      p_p: /^[a-zA-Z0-9,./~!@#$%^&*()_+]{8,40}$/,

      usernameerror: false,
      passworderror: false,

      usernameOnFocus: false,
      passwordOnFocus: false
    };
  },
  methods: {
    login: function() {
      // 判断username
      if (!this.u_p.test(this.username)) this.usernameerror = true;
      else this.usernameerror = false;
      // 判断密码
      if (!this.p_p.test(this.password)) this.passworderror = true;
      else this.passworderror = false;

      if (this.usernameerror === false && this.passworderror === false) {
        this.$store.dispatch("login", {
          username: this.username,
          password: this.password
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