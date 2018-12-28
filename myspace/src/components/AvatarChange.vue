<template>
  <div>
    <form @submit.prevent>
      <div class="form-item">
        <div class="label">当前头像</div>
        <img class="avatar-bg" :src="$store.state.avatar" alt>
      </div>
      <div class="form-item">
        <div class="label"></div>
        <button @click="choiceImg" type="button" class="button-style">
          更换头像
          <input ref="inputfile" class="input-file" type="file" @change="changeAvatar($event)">
        </button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  methods: {
    choiceImg: function() {
      this.$refs.inputfile.click();
    },
    changeAvatar: function(event) {
      const avatar = event.target.files[0];
      this.$axios({
        method: "post",
        url: "http://192.168.1.7:8000/api/homespace/changeAvatar",
        data: {
          avatar: avatar
        },
        headers: {
          "Content-Type": "multipart/form-data"
        }
      }).then(response => {
        console.log(response.data);
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
