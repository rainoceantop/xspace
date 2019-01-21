<template>
  <div class="container info-wrap">
    <section class="panel">
      <form @submit.prevent>
        <div :class="['form-item', usernameOnInput]">
          <label>用户名或邮箱</label>
          <input type="text" v-model="username">
        </div>
        <div v-if="successMessage" class="form-item">
          <p class="success-label">{{ successMessage }}</p>
        </div>
        <div v-if="error" class="form-item">
          <p class="error-label">账号或邮箱格式错误，请检查</p>
        </div>
        <div class="form-item">
          <input
            class="button-style"
            :disabled="sendMailButtonDisable"
            type="button"
            :value="sendButtonMsg"
            @click="sendEmail"
          >
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
  name: "PasswordReset",
  data() {
    return {
      username: "",
      error: false,
      successMessage: "",
      sendButtonMsg: "发送邮件",
      onSend: false,
      onBreak: false,
      u_p: /^[a-zA-Z0-9]{6,20}$/,
      e_p: /^(?:[a-zA-Z0-9]+[_\-\+\.]?)*[a-zA-Z0-9]+@(?:([a-zA-Z0-9]+[_\-]?)*[a-zA-Z0-9]+\.)+([a-zA-Z]{2,})+$/
    };
  },
  methods: {
    sendEmail: function() {
      if (!(this.u_p.test(this.username) || this.e_p.test(this.username))) {
        this.error = true;
      } else {
        this.error = false;
        this.onSend = true;
        this.sendButtonMsg = "正在发送";
        this.$axios
          .get(
            `http://192.168.1.7:8000/api/homespace/changePasswordByEmail?email=${
              this.username
            }`
          )
          .then(response => {
            if (response.data.code === 1) {
              this.onBreak = true;
              this.timeBreak(10);
              this.successMessage =
                "邮件发送成功，请前往邮箱查看并点击链接修改密码！";
            } else {
              this.error = true;
              this.onSend = false;
              this.sendButtonMsg = "重新发送";
            }
          });
      }
    },
    timeBreak: function(s) {
      let t;
      if (s > 0) {
        s -= 1;
        this.sendButtonMsg = `${s}秒后重新发送`;
        t = setTimeout(this.timeBreak, 1000, s);
      } else {
        clearTimeout(t);
        this.sendButtonMsg = "重新发送";
        this.onBreak = false;
        this.onSend = false;
      }
    }
  },
  computed: {
    usernameOnInput: function() {
      return this.username.length === 0 ? "" : "small-label";
    },
    sendMailButtonDisable: function() {
      return this.username.length === 0 || this.onSend || this.onBreak;
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../assets/scss/login_register";
</style>
