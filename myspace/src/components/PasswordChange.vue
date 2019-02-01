<template>
  <div>
    <form @submit.prevent>
      <div class="form-item">
        <div class="label">旧密码</div>
        <div class="input">
          <input type="password" v-model="oldpass">
        </div>
      </div>
      <div class="form-item">
        <div class="label">新密码</div>
        <div class="input">
          <input type="password" v-model="newpass1">
        </div>
      </div>
      <div class="form-item">
        <div class="label">确认新密码</div>
        <div class="input">
          <input type="password" v-model="newpass2">
        </div>
      </div>
      <div v-if="successlabel" class="form-item">
        <div class="label"></div>
        <div class="input">
          <p class="success-label">{{ successlabel }}</p>
        </div>
      </div>
      <div v-if="errorlabel" class="form-item">
        <div class="label"></div>
        <div class="input">
          <p class="error-label">{{ errorlabel }}</p>
        </div>
      </div>
      <div class="form-item">
        <div class="label"></div>
        <div>
          <input
            type="button"
            :disabled="oldpass.length === 0 || newpass1.length === 0 || newpass2.length === 0"
            class="button-style"
            value="提交"
            @click="changePassword"
          >
        </div>
      </div>
    </form>
  </div>
</template>
<script>
export default {
  data() {
    return {
      oldpass: "",
      newpass1: "",
      newpass2: "",
      errorlabel: "",
      successlabel: "",
      p_p: /^[a-zA-Z0-9,./~!@#$%^&*()_+]{8,40}$/
    };
  },
  methods: {
    changePassword: function() {
      if (this.newpass1 !== this.newpass2) {
        this.errorlabel = "新密码与确认密码不匹配！";
      } else {
        if (!this.p_p.test(this.newpass1)) {
          this.errorlabel = "密码必须符合格式且长度在区间[8-40]内";
        } else {
          this.errorlabel = "";
          this.$axios
            .post("http://192.168.1.7:8000/api/homespace/changePassword", {
              oldpass: this.oldpass,
              newpass1: this.newpass1,
              newpass2: this.newpass2
            })
            .then(response => {
              if (response.data.code === 1) {
                this.successlabel = "修改成功";
                this.$store.commit("logout");
                setTimeout(this.redirectToLogin, 1500);
              } else {
                this.errorlabel = response.data.msg;
              }
            });
        }
      }
    },
    redirectToLogin: function() {
      this.$router.push("/user/login");
    }
  }
};
</script>


<style lang="scss" scoped>
.form-item {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  justify-items: center;
  margin-bottom: 1em;
  font-weight: bold;
  .label {
    width: 25%;
    text-align: right;
    padding-right: 35px;
  }
  .input {
    width: 50%;
    input {
      width: 100%;
      border: none;
      height: auto !important;
      padding: 8px;
    }
  }
}
</style>