<template>
  <div id="top-wrapper" class="blog-info container">
    <div class="blog-info-wrap">
      <div v-if="loading" class="center">
        <font-awesome-icon :icon="['fas', 'spinner']" size="3x" spin/>
      </div>
      <div v-if="blog && !loading">
        <div class="blog-header">
          <h5 id="title">{{ blog.title }}</h5>
        </div>
        <div v-html="blog.body" id="body"></div>
        <ul v-if="blog.tags" class="tag-display">
          <li class="tag-style" v-for="tag in blog.tags" :key="tag">
            <router-link class="main-color" :to="{name: 'tag', params: {tagname: tag}}">{{ tag }}</router-link>
          </li>
        </ul>
        <footer class="artical-footer">
          <aside class="left">
            <span class="like-icon">
              <font-awesome-icon
                @click="toggleLike('blog', blog)"
                :icon="blogIcon"
                size="lg"
                style="color: #007CBA"
              />
            </span>
            <span class="like-count">{{ blog.likes }}</span>
          </aside>
          <aside class="right">
            <p id="post-time">发表时间：{{ blog.created_at }}</p>
            <div class="author-detail">
              <div>
                <router-link :to="{name: 'myspace', params: {id: blog.author_id}}">
                  <img class="avatar-sm" :src="blog.author_avatar" alt>
                </router-link>
              </div>
              <div>
                <router-link
                  :to="{name: 'myspace', params: {id: blog.author_id}}"
                  id="author-name"
                >{{ blog.author }}</router-link>
                <p id="author-follows">{{ blog.author_follows }}关注·{{ blog.author_fans }}粉丝</p>
              </div>
            </div>
          </aside>
        </footer>
      </div>
      <span>{{ blog.replies_count }}条评论</span>
      <Reply app="blog" :artical="blog" v-on:toggleLike="toggleLike"></Reply>
    </div>
  </div>
</template>


<script>
import Reply from "../components/sub/Reply";
import MySpace from "../views/MySpace";
export default {
  name: "BlogInfo",
  data() {
    return {
      blog: "",
      cached_blog: {},
      loading: true
    };
  },
  created() {
    this.getBlog(this.blogid);
  },
  components: {
    Reply
  },
  props: ["blogid"],
  methods: {
    getBlog: function(id) {
      if (id !== undefined) {
        this.loading = true;
        this.$axios.get(`/api/blog/${id}`).then(response => {
          if (response.data.code === 1) {
            this.blog = response.data.msg;
            this.cached_blog[id] = response.data.msg;
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
      let url = `/api/blog/likes?way=${way}&id=${item.id}&aor=${aor}`;
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
  computed: {
    blogIcon() {
      return [this.blog.liked ? "fas" : "far", "thumbs-up"];
    }
  },
  watch: {
    blogid(n, o) {
      if (!this.cached_blog[n]) {
        this.getBlog(n);
      } else {
        this.blog = this.cached_blog[n];
      }
    }
  }
};
</script>