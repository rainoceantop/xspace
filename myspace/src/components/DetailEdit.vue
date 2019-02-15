<template>
  <div>
    <form @submit.prevent>
      <div class="form-item">
        <div class="label">名称</div>
        <div class="input">
          <input type="text" v-model="nickname">
        </div>
      </div>
      <div class="form-item">
        <div class="label">网站</div>
        <div class="input">
          <input type="text" v-model="website">
        </div>
      </div>
      <div class="form-item">
        <div class="label">个人简介</div>
        <div class="input">
          <textarea v-model="bio"></textarea>
        </div>
      </div>
      <div class="form-item">
        <div class="label"></div>
        <div>
          <span style="color: gray; font-size: 13px;">私人信息</span>
        </div>
      </div>
      <div class="form-item">
        <div class="label">邮箱</div>
        <div class="input">
          <input type="email" v-model="email">
        </div>
      </div>
      <div class="form-item">
        <div class="label">姓名</div>
        <div class="input">
          <input type="text" v-model="firstname">
        </div>
      </div>
      <div class="form-item">
        <div class="label"></div>
        <div>
          <input type="button" class="button-style" @click="updateDetail" value="提交">
        </div>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      nickname: this.$store.state.nickname,
      website: "",
      bio: this.$store.state.bio,
      email: "",
      firstname: "",
      w_p: /^(https?):\/\/(-\.)?([^\s\/?\.#-]+\.?)+(\/[^\s]*)?$/,
      e_p: /^(?:[a-zA-Z0-9]+[_\-\+\.]?)*[a-zA-Z0-9]+@(?:([a-zA-Z0-9]+[_\-]?)*[a-zA-Z0-9]+\.)+([a-zA-Z]{2,})+$/
    };
  },
  created() {
    this.getUpdateData();
  },
  methods: {
    getUpdateData: function() {
      this.$axios.get("/api/homespace/getUpdateData").then(response => {
        if (response.data.code === 1) {
          let data = response.data.msg;
          this.nickname = data.nickname;
          this.website = data.website;
          this.bio = data.bio;
          this.email = data.email;
          this.firstname = data.firstname;
        } else {
          alert(response.data.msg);
        }
      });
    },
    updateDetail: function() {
      if (this.nickname.length === 0) {
        alert("名称不能为空");
        return;
      }
      if (this.nickname.length > 20) {
        alert("名称有效长度区间[1-20]");
        return;
      }
      if (this.website.length > 0) {
        if (!this.w_p.test(this.website)) {
          alert("网址格式错误");
          return;
        }
      }
      if (this.email.length > 0) {
        if (!this.e_p.test(this.email)) {
          alert("email格式错误");
          return;
        }
      }
      if (this.bio.length > 150) {
        alert("个人简介不得超过150个字");
        return;
      }
      if (this.firstname.length > 30) {
        alert("姓名有效长度区间[1-30]");
        return;
      }

      this.$axios
        .post("/api/homespace/updateDetail", {
          nickname: this.nickname,
          website: this.website,
          bio: this.bio,
          email: this.email,
          firstname: this.firstname
        })
        .then(response => {
          alert(response.data.msg);
        });
    }
  }
};
</script>


<style lang="scss" scoped>
@import "../assets/scss/config";
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
    input,
    textarea {
      width: 100%;
      border: none;
    }
    input {
      height: auto !important;
      padding: 8px;
    }
    textarea {
      padding: 10px;
      font-size: 15px;
      min-height: 100px;
      resize: vertical;
    }
  }
}

@include mediaSm {
  .form-item {
    flex-direction: column;
    .label,
    .input {
      text-align: start;
      width: 100%;
    }
  }
}
</style>

