<template>
  <div>
    <div class="info">
      <div class="photo-view">
        <font-awesome-icon v-if="loading" :icon="['fas', 'spinner']" size="3x" spin/>
        <img
          v-else
          oncontextmenu="return false"
          ondragstart="return false"
          v-show="photo"
          :class="['animated', 'fadeIn', 'the-photo', photo_zoom_in ? 'zoom-in' : '']"
          :src="photo.url"
          @click="toggleZoom()"
        >
        <div v-if="photo_zoom_in" class="photo-zoom-in-wrapper"></div>
      </div>

      <div v-if="photo && !loading" class="caption animated fadeIn">
        <h5 v-if="photo.title">{{ photo.title }}</h5>
        <p>{{ photo.caption }}</p>
        <div class="tag-display">
          <span class="tag-style" v-for="tag in photo.tags" :key="tag">
            <router-link class="main-color" :to="{name: 'tag', params: {tagname: tag}}">{{ tag }}</router-link>
          </span>
        </div>
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
      cached_photo: {},
      loading: true,
      photo_zoom_in: false
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
        this.loading = true;
        this.photo = "";
        this.$axios.get(`/api/photo/${id}`).then(response => {
          if (response.data.code === 1) {
            this.photo = response.data.msg;
            this.cached_photo[id] = response.data.msg;
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
      let url = `/api/photo/likes?way=${way}&id=${item.id}&aor=${aor}`;
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
    toggleZoom: function() {
      this.photo_zoom_in = this.photo_zoom_in ? false : true;
    }
  },
  activated() {
    this.photo_zoom_in = false;
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

