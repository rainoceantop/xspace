<template>
  <div>
    <div class="info">
      <div class="photo-view">
        <img
          oncontextmenu="return false"
          ondragstart="return false"
          v-show="photo"
          class="the-photo animated fadeIn"
          :src="photo.url"
          alt
        >
      </div>

      <div v-show="photo" class="caption animated fadeIn">
        <h3 v-if="photo.title">{{ photo.title }}</h3>
        <p>{{ photo.caption }}</p>
        <div class="photo-footer">
          <span>
            <span class="time-area">
              <font-awesome-icon :icon="['far', 'clock']"/>&nbsp;
              <span>{{ photo.created_at }}</span>
            </span>&emsp;
            <span class="like-area" @click="toggleLike('photo', photo)">
              <font-awesome-icon v-show="!photo.liked" :icon="['far', 'heart']"/>
              <font-awesome-icon style="color:red" v-show="photo.liked" :icon="['fas', 'heart']"/>&nbsp;
              <span>{{ photo.likes }}</span>
            </span>&emsp;
            <span class="comment-area">
              <font-awesome-icon :icon="['far', 'comment']"/>
            </span>
          </span>
          <div>
            <span class="author-area">
              <router-link :to="{name: 'myspace', params: {id: photo.author_id}}">
                <img :src="photo.author_avatar" class="avatar-xs" alt :title="photo.author">
              </router-link>
            </span>
          </div>
        </div>
      </div>
    </div>
    <div class="container">
      <Reply app="photo" :artical="photo" v-on:toggleLike="toggleLike"></Reply>
    </div>
  </div>
</template>

<script>
import Reply from "../components/sub/Reply";
export default {
  data() {
    return {
      photo: "",
      cached_photo: {}
    };
  },
  created() {
    this.getPhoto(this.photoid);
  },
  props: ["photoid"],
  components: { Reply },
  methods: {
    getPhoto: function(id) {
      if (id !== undefined) {
        this.photo = "";
        this.$axios
          .get(`http://192.168.1.7:8000/api/photo/${id}`)
          .then(response => {
            if (response.data.code === 1) {
              this.photo = response.data.msg;
              this.cached_photo[id] = response.data.msg;
            } else {
              alert(response.data.msg);
            }
          });
      }
    },
    toggleLike: function(way, item) {
      // 判断是点赞还是取消点赞
      let aor = item.liked ? "rem" : "add";
      item.likes = item.liked ? item.likes - 1 : item.likes + 1;
      // 先把样式改了
      item.liked = item.liked ? false : true;
      let url = `http://192.168.1.7:8000/api/photo/likes?way=${way}&id=${
        item.id
      }&aor=${aor}`;
      this.$axios
        .get(url)
        .then(response => {
          if (response.data.code !== 1) {
            item.likes = item.liked ? item.likes - 1 : item.likes + 1;
            item.liked = item.liked ? false : true;
            alert(response.data.msg);
          }
        })
        .catch(error => {
          item.likes = item.liked ? item.likes - 1 : item.likes + 1;
          item.liked = item.liked ? false : true;
          alert(response.data.msg);
        });
    }
  },
  watch: {
    photoid(n, o) {
      if (!this.cached_photo[n]) {
        this.getPhoto(n);
      } else {
        this.photo = this.cached_photo[n];
      }
    }
  }
};
</script>



<style lang="scss">
@import "../assets/scss/photo_info";
</style>
