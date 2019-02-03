<template>
  <div>
    <form @submit.prevent>
      <div class="form-item">
        <div class="label">当前头像</div>
        <img class="avatar-bg" :src="avatarUrl" alt>
      </div>
      <div class="form-item">
        <div class="label"></div>
        <button @click="choiceImg" :disabled="onUpload" type="button" class="button-style">
          {{ uploadLabel }}
          <input
            ref="uploadAvatar"
            class="input-file"
            type="file"
            @change="changeAvatar($event)"
          >
        </button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      avatarUrl: this.$store.state.avatar,
      onUpload: false,
      uploadLabel: "更换头像"
    };
  },
  methods: {
    choiceImg: function() {
      this.$refs.uploadAvatar.click();
    },
    changeAvatar: function(event) {
      this.onUpload = true;
      this.uploadLabel = "上传中...";
      const avatar = event.target.files[0];
      let formData = new FormData();
      formData.append("avatar", avatar);
      this.$axios({
        method: "post",
        url: "/api/homespace/changeAvatar",
        data: formData,
        headers: {
          "Content-Type": "multipart/form-data"
        }
      }).then(response => {
        this.onUpload = false;
        this.uploadLabel = "更换头像";

        if (response.data.code === 1) {
          this.avatarUrl = response.data.msg;
        } else {
          alert(response.data.msg);
        }
      });
    }
  }
};
</script>


<style lang="scss" scoped>
.form-item {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
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
      padding: 8px;
    }
  }
  .input-file {
    display: none;
  }
}
</style>
