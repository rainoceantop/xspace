<template>
  <div class="container info-wrap">
    <section class="panel">
      <form v-if="authenticate" @submit.prevent>
        <header>Xspace</header>
        <div :class="['form-item',newpass1OnInput]">
          <label>新密码</label>
          <input type="password" v-model="newpass1">
        </div>
        <div :class="['form-item',newpass2OnInput]">
          <label>确认新密码</label>
          <input type="password" v-model="newpass2">
        </div>
        <div v-if="error" class="form-item">
          <p class="error-label">{{ errorlabel }}</p>
        </div>
        <div v-if="successlabel" class="form-item">
          <p class="success-label">{{ successlabel }}</p>
        </div>
        <div class="form-item">
          <input class="button-style" type="button" value="修改密码" @click="changePassword">
        </div>
      </form>
      <h3 v-else>token认证失败</h3>
    </section>
  </div>
</template>
<script>
export default {
  name: "PasswordResetConfirm",
  data() {
    return {
      authenticate: false,
      newpass1: "",
      newpass2: "",
      error: false,
      errorlabel: "",
      successlabel: "",
      p_p: /^[a-zA-Z0-9,./~!@#$%^&*()_+]{8,40}$/
    };
  },
  props: ["uid", "token"],
  created() {
    this.checkToken();
  },
  methods: {
    checkToken: function() {
      this.$axios
        .get(
          `http://192.168.1.7:8000/api/homespace/changePasswordCheckToken?uid=${
            this.uid
          }&token=${this.token}`
        )
        .then(response => {
          if (response.data.code === 1) {
            this.authenticate = true;
          } else {
            this.authenticate = false;
          }
        });
    },
    changePassword: function() {
      if (!this.p_p.test(this.newpass1)) {
        this.error = true;
        this.errorlabel = "密码出现非法字符或长度不在区间[8-40]范围内";
        return;
      }
      if (this.newpass2 !== this.newpass1) {
        this.error = true;
        this.errorlabel = "确认密码与密码不一致，请检查";
        return;
      }
      this.error = false;
      this.$axios
        .post(
          `http://192.168.1.7:8000/api/homespace/changePasswordByEmailConfirm?uid=${
            this.uid
          }&token=${this.token}`,
          {
            newpass1: this.newpass1,
            newpass2: this.newpass2
          }
        )
        .then(response => {
          if (response.data.code === 1) {
            this.successlabel = "修改成功，正在跳转...";
            this.$store.commit("login", response.data.msg);
            setTimeout(this.redirectToSpace, 1500, response.data.msg.username);
          } else {
            this.error = true;
            this.errorlabel = response.data.msg;
          }
        });
    },
    redirectToSpace: function(id) {
      this.$router.push({ name: "myspace", params: { id: id } });
    }
  },
  computed: {
    newpass1OnInput: function() {
      return this.newpass1.length === 0 ? "" : "small-label";
    },
    newpass2OnInput: function() {
      return this.newpass2.length === 0 ? "" : "small-label";
    }
  }
};
</script>
<style lang="scss" scoped>
@import "../assets/scss/login_register";
</style>

