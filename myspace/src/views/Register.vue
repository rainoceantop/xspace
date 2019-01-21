<template>
  <div class="container info-wrap">
    <section class="panel">
      <form @submit.prevent>
        <header>Xspace</header>
        <div :class="['form-item',usernameOnInput]">
          <label>用户名</label>
          <input type="text" v-model="username">
        </div>
        <div :class="['form-item',nicknameOnInput]">
          <label>名称</label>
          <input type="text" v-model="nickname">
        </div>
        <div :class="['form-item',password1OnInput]">
          <label>密码</label>
          <input type="password" v-model="password1">
        </div>
        <div :class="['form-item',password2OnInput]">
          <label>确认密码</label>
          <input type="password" v-model="password2">
        </div>
        <div v-if="error" class="form-item">
          <p class="error-label">{{ errorlabel }}</p>
        </div>
        <div class="form-item">
          <input
            class="button-style"
            :disabled="loginButtonDisable"
            type="button"
            value="登录"
            @click="register"
          >
        </div>
      </form>
    </section>
    <section class="panel">
      <p class="link-label">已有账户？
        <router-link :to="{name: 'login'}">登录</router-link>
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
      nickname: "",
      password1: "",
      password2: "",
      u_p: /^[a-zA-Z0-9]{6,20}$/,
      p_p: /^[a-zA-Z0-9,./~!@#$%^&*()_+]{8,40}$/,
      error: false,
      errorlabel: ""
    };
  },
  methods: {
    register: function() {
      if (!this.u_p.test(this.username)) {
        this.error = true;
        this.errorlabel = "账号只能由字母数字组成且长度在区间[6-20]范围内";
        return;
      }
      if (this.nickname.length > 20 || this.nickname.length === 0) {
        this.error = true;
        this.errorlabel = "名称长度区间[1-20]";
        return;
      }
      if (!this.p_p.test(this.password1)) {
        this.error = true;
        this.errorlabel = "密码出现非法字符或长度不在区间[8-40]范围内";
        return;
      }
      if (this.password2 !== this.password1) {
        this.error = true;
        this.errorlabel = "确认密码与密码不一致，请检查";
        return;
      }
      this.error = false;
      this.$store.dispatch("register", {
        username: this.username,
        nickname: this.nickname,
        password1: this.password1,
        password2: this.password2
      });
    }
  },
  computed: {
    usernameOnInput: function() {
      return this.username.length === 0 ? "" : "small-label";
    },
    nicknameOnInput: function() {
      return this.nickname.length === 0 ? "" : "small-label";
    },
    password1OnInput: function() {
      return this.password1.length === 0 ? "" : "small-label";
    },
    password2OnInput: function() {
      return this.password2.length === 0 ? "" : "small-label";
    },
    loginButtonDisable: function() {
      return (
        this.username.length === 0 ||
        this.nickname.length === 0 ||
        this.password1.length === 0 ||
        this.password2.length === 0
      );
    }
  }
};
</script>
<style lang="scss" scoped>
@import "../assets/scss/login_register";
</style>

