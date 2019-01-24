<template>
  <div style="position:relative">
    <div class="inner">
      <router-link
        v-show="next"
        class="nav-next animated zoomIn"
        :to="{name: 'blogInfo', params: {id:undefined, blogid: next}}"
      ></router-link>
      <router-link
        v-show="prev"
        class="nav-prev animated zoomIn"
        :to="{name: 'blogInfo', params: {id:undefined, blogid: prev}}"
      ></router-link>
    </div>
    <div class="container">
      <font-awesome-icon v-if="loading" :icon="['fas', 'spinner']" size="5x" spin/>
      <div v-else class="blog-info-wrap">
        <div class="blog-header">
          <h3 id="title">{{ blog.title }}</h3>
          <div v-if="blog.author_id === $store.state.id" id="blog-operate-icons">
            <font-awesome-icon id="blog-edit-icon" :icon="['fas', 'edit']" @click="blogEdit(blog)"/>
            <font-awesome-icon
              id="blog-delete-icon"
              :icon="['fas', 'trash']"
              @click="blogDelete(blog.id, blog.author_id)"
            />
          </div>
        </div>
        <div v-html="blog.body" id="body"></div>
        <ul v-if="blog.tags" class="tag-display">
          <li class="tag-style" v-for="tag in blog.tags" :key="tag">{{ tag }}</li>
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

        <span>{{ blog.replies_count }}条评论</span>
        <Reply app="blog" :artical="blog" v-on:toggleLike="toggleLike"></Reply>
      </div>
    </div>
  </div>
</template>


<script>
import Reply from "./sub/Reply";
import MySpace from "../views/MySpace";
export default {
  name: "BlogInfo",
  data() {
    return {
      blog: "",
      cached_blogs: {},
      loading: true
    };
  },
  created() {
    this.$emit("countPN", this.blogid);
    this.getBlog(this.blogid);
  },
  components: {
    Reply
  },
  props: ["blogid", "prev", "next"],
  methods: {
    getBlog: function(id) {
      if (id !== undefined) {
        this.loading = true;
        this.$axios
          .get(`http://192.168.1.7:8000/api/blog/${id}`)
          .then(response => {
            if (response.data.code === 1) {
              this.blog = response.data.msg;
              this.cached_blogs[id] = response.data.msg;
            } else {
              alert(response.data.msg);
            }
            this.loading = false;
          });
      }
    },
    blogEdit: function(blog) {
      delete this.cached_blogs[blog.id];
      this.$emit("editBlog", blog);
    },
    blogDelete: function(blog_id, author_id) {
      if (author_id !== this.$store.state.id) {
        alert("抱歉，你无权删除");
      } else {
        if (confirm("确定删除这篇博客吗？")) {
          this.$axios
            .get(`http://192.168.1.7:8000/api/blog/${blog_id}/delete`)
            .then(response => {
              if (response.data.code === 1) {
                delete this.cached_blogs[blog_id];
                this.$emit("blogDeleteDone", blog_id);
              } else {
                alert(response.data.msg);
              }
            });
        }
      }
    },
    toggleLike: function(way, item) {
      // 判断是点赞还是取消点赞
      let aor = item.liked ? "rem" : "add";
      item.likes = item.liked ? item.likes - 1 : item.likes + 1;
      // 先把样式改了
      item.liked = item.liked ? false : true;
      let url = `http://192.168.1.7:8000/api/blog/likes?way=${way}&id=${
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
  activated() {
    if (!this.cached_blogs[this.blogid]) this.getBlog(this.blogid);
    // 获取博客上下文博客
    this.$emit("countPN", this.blogid);
  },
  watch: {
    blogid: function(newid, oldid) {
      // 获取博客
      if (this.cached_blogs[newid] === undefined) this.getBlog(newid);
      else this.blog = this.cached_blogs[newid];
      // 获取博客上下文博客
      this.$emit("countPN", this.blogid);
    }
  },
  computed: {
    blogIcon() {
      return [this.blog.liked ? "fas" : "far", "thumbs-up"];
    }
  }
};
</script>
<style lang="scss" scoped>
@import "../assets/scss/blog_info";
</style>

