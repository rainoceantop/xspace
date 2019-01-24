<template>
  <div>
    <div class="info">
      <div class="inner">
        <router-link
          v-show="next"
          class="nav-next animated zoomIn"
          :to="{name: 'photoInfo', params: {id:undefined, photoid: next}}"
        ></router-link>
        <router-link
          v-show="prev"
          class="nav-prev animated zoomIn"
          :to="{name: 'photoInfo', params: {id:undefined, photoid: prev}}"
        ></router-link>
      </div>

      <div class="photo-view">
        <font-awesome-icon v-if="loading" :icon="['fas', 'spinner']" size="5x" spin/>
        <img
          v-else
          oncontextmenu="return false"
          ondragstart="return false"
          v-show="photo"
          class="the-photo animated fadeIn"
          :src="photo.url"
          alt
        >
      </div>

      <div v-show="photo && !loading" class="caption animated fadeIn">
        <h3 v-if="photo.title">{{ photo.title }}</h3>
        <p>{{ photo.caption }}</p>
        <ul v-if="photo.tags" class="tag-display">
          <li class="tag-style" v-for="tag in photo.tags" :key="tag">{{ tag }}</li>
        </ul>
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
              <font-awesome-icon :icon="['far', 'comment']"/>&nbsp;
              <span>{{ photo.replies_count }}</span>
            </span>&emsp;
            <span
              v-if="photo.author_id === $store.state.id"
              class="edit-area"
              @click="photoEdit(photo)"
            >
              <font-awesome-icon :icon="['far', 'edit']"></font-awesome-icon>&nbsp;
              <span>编辑</span>
            </span>&emsp;
            <span
              v-if="photo.author_id === $store.state.id"
              class="delete-area"
              @click="photoDelete(photo.id, photo.author_id)"
            >
              <font-awesome-icon :icon="['far', 'trash-alt']"></font-awesome-icon>&nbsp;
              <span>删除</span>
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
      <Reply v-if="!loading" app="photo" :artical="photo" v-on:toggleLike="toggleLike"></Reply>
    </div>
  </div>
</template>

<script>
import Reply from "./sub/Reply";
export default {
  data() {
    return {
      photo: "",
      cached_photos: {},
      loading: true
    };
  },
  created() {
    this.$emit("countPN", this.photoid);

    this.getPhoto(this.photoid);
  },
  props: ["photoid", "prev", "next"],
  components: { Reply },
  methods: {
    getPhoto: function(id) {
      if (id !== undefined) {
        this.loading = true;
        this.photo = "";
        this.$axios
          .get(`http://192.168.1.7:8000/api/photo/${id}`)
          .then(response => {
            if (response.data.code === 1) {
              this.photo = response.data.msg;
              this.cached_photos[id] = response.data.msg;
            } else {
              alert(response.data.msg);
            }
            this.loading = false;
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
    },
    photoEdit: function(photo) {
      delete this.cached_photos[photo.id];
      this.$emit("editPhoto", photo);
    },
    photoDelete: function(photo_id, author_id) {
      if (author_id !== this.$store.state.id) {
        alert("抱歉，你无权删除");
      } else {
        if (confirm("确定删除该图片吗？")) {
          this.$axios
            .get(`http://192.168.1.7:8000/api/photo/${photo_id}/delete`)
            .then(response => {
              if (response.data.code === 1) {
                delete this.cached_photos[photo_id];
                this.$emit("photoDeleteDone", photo_id);
              } else {
                alert(response.data.msg);
              }
            });
        }
      }
    }
  },
  activated() {
    // 获取图片
    if (!this.cached_photos[this.photoid]) this.getPhoto(this.photoid);

    // 获取图片上下文图片
    this.$emit("countPN", this.photoid);
  },
  watch: {
    photoid(n, o) {
      // 获取当前图片
      if (this.cached_photos[n] === undefined) this.getPhoto(n);
      else {
        this.photo = this.cached_photos[n];
      }
      // 获取图片上下文图片
      this.$emit("countPN", this.photoid);
    }
  }
};
</script>


<style lang="scss">
@import "../assets/scss/photo_info";
</style>