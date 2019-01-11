<template>
  <div class="container">
    <div class="photo-create-wrap">
      <form @submit.prevent>
        <div v-if="photoUrl" class="form-item display-photo">
          <img :src="photoUrl + '-display'" alt>
        </div>
        <div v-if="piscreate" class="form-item">
          <div class="label">*图片</div>
          <button @click="choicePhoto" :disabled="onUpload" type="button" class="button-style">
            {{ uploadLabel }}
            <input
              ref="uploadPhoto"
              class="input-file"
              type="file"
              @change="changePhoto($event)"
            >
          </button>
        </div>
        <div class="form-item">
          <div class="label">标题</div>
          <div class="input">
            <input type="text" maxlength="50" v-model="title">
          </div>
        </div>
        <div class="form-item">
          <div class="label">*说明</div>
          <div class="input">
            <textarea v-model="caption" maxlength="500"></textarea>
          </div>
        </div>
        <div class="form-item">
          <div class="label"></div>
          <input @click="submit" class="button-style" type="button" value="提交">
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      title: "",
      caption: "",
      onUpload: false,
      uploadLabel: "上传图片",
      photoUrl: "",
      used_photo: ""
    };
  },
  props: {
    photo: "",
    piscreate: true
  },
  methods: {
    initData: function() {
      this.title = "";
      this.caption = "";
      this.photoUrl = "";
      if (!this.piscreate) {
        if (this.photo) {
          this.title = this.photo.title;
          this.caption = this.photo.caption;
          this.photoUrl = this.photo.url;
        }
      }
    },
    submit: function() {
      if (!this.photoUrl) {
        alert("请选择需要上传的图片");
        return;
      }
      if (this.title.length > 50) {
        alert("标题不能超过50个字符");
        return;
      }
      if (this.caption.length === 0) {
        alert("说明不能为空");
        return;
      }
      if (this.caption.length > 500) {
        alert("说明不能超过500个字符");
        return;
      }
      let url = "http://192.168.1.7:8000/api/photo/store";
      if (!this.piscreate) {
        url = `http://192.168.1.7:8000/api/photo/${this.photo.id}/update`;
      }
      this.$axios
        .post(url, {
          photoUrl: this.photoUrl,
          title: this.title,
          caption: this.caption
        })
        .then(response => {
          if (response.data.code === 1) {
            this.$emit("photoCreateDone", response.data.msg);
          } else alert(response.data.msg);
        });
    },
    choicePhoto: function() {
      this.$refs.uploadPhoto.click();
    },
    changePhoto: function(event) {
      this.onUpload = true;
      this.uploadLabel = "上传中...";
      const photo = event.target.files[0];
      let formData = new FormData();
      formData.append("photo", photo);
      this.$axios({
        method: "post",
        url: `http://192.168.1.7:8000/api/photo/upload?used_photo=${
          this.used_photo
        }`,
        data: formData,
        headers: {
          "Content-Type": "multipart/form-data"
        }
      }).then(response => {
        this.onUpload = false;
        this.uploadLabel = "更换图片";

        if (response.data.code === 1) {
          this.photoUrl = response.data.msg;
        } else {
          alert(response.data.msg);
        }
      });
    }
  },

  mounted() {
    this.initData();
  },
  watch: {
    photoUrl(n, o) {
      this.used_photo = n;
    },
    photo(n, o) {
      this.initData();
    }
  }
};
</script>


<style lang="scss" scoped>
@import "../assets/scss/var";
.container {
  width: 100%;
  display: flex;
  justify-content: center;
}
.photo-create-wrap {
  width: 70%;
  padding: 2em 5em;
  // background-color: yellowgreen;
  text-align: start;
  margin-top: 3em;

  margin-bottom: 100px;
  border: 1px $gray solid;
  box-shadow: 5px 8px 15px rgba(0, 0, 0, 0.3);
}
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
  .input-file {
    display: none;
  }
  .input {
    width: 50%;
    input,
    textarea {
      width: 100%;
      border: none;
    }
    input {
      padding: 8px;
    }
    textarea {
      padding: 10px;
      font-size: 15px;
      min-height: 150px;
      resize: vertical;
    }
  }
}
.display-photo {
  width: 100%;
  display: flex;
  justify-content: center;
}
</style>
