<template>
  <div class="container info-wrap">
    <section class="panel">
      <form @submit.prevent>
        <header>痕·迹</header>
        <div :class="['form-item',usernameOnInput]">
          <label>用户名</label>
          <input type="text" v-model="username">
        </div>
        <div :class="['form-item',passwordOnInput]">
          <label>密码</label>
          <input type="password" v-model="password">
        </div>
        <div v-if="error" class="form-item">
          <p class="error-label">账号或密码有误，请检查后重新输入</p>
        </div>
        <div class="form-item">
          <input
            class="button-style"
            :disabled="loginButtonDisable"
            type="button"
            value="登录"
            @click="login"
          >
        </div>
        <div class="form-item">
          <p class="link-label">
            <router-link :to="{name: 'passwordReset'}">忘记密码？</router-link>
          </p>
        </div>
      </form>
    </section>
    <section class="panel">
      <p class="link-label">没有账户？
        <router-link :to="{name: 'register'}">注册</router-link>
      </p>
    </section>
  </div>
</template>

<script>
export default {
  name: "Login",
  data() {
    return {
      username: "",
      password: "",
      u_p: /^[a-zA-Z0-9]{6,20}$/,
      p_p: /^[a-zA-Z0-9,./~!@#$%^&*()_+]{8,40}$/,
      error: false
    };
  },
  methods: {
    login: function() {
      if (!(this.u_p.test(this.username) && this.p_p.test(this.password))) {
        this.error = true;
      } else {
        this.error = false;
        this.$store.dispatch("login", {
          username: this.username,
          password: this.password
        });
      }
    }
  },
  computed: {
    usernameOnInput: function() {
      return this.username.length === 0 ? "" : "small-label";
    },
    passwordOnInput: function() {
      return this.password.length === 0 ? "" : "small-label";
    },
    loginButtonDisable: function() {
      return this.username.length === 0 || this.password.length === 0;
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../assets/scss/login_register";
</style>
