<template>
  <div class="container">
    <div v-if="blog" class="blog-info-wrap">
      <div class="blog-header">
        <h3 id="title">{{ blog.title }}</h3>
      </div>
      <div v-html="blog.body" id="body"></div>
      <footer class="artical-footer">
        <aside class="left">
          <span class="like-icon">
            <font-awesome-icon
              @click="toggleLike($event, 'blog', blog)"
              :icon="blogIcon"
              size="lg"
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

      <div class="reply-area">
        <header>
          <p>{{ blog.replies_count }}条评论</p>
        </header>
        <section class="replying">
          <img class="avatar-sm" :src="$store.state.avatar" alt>
          <div
            ref="replyInput"
            contenteditable="true"
            @input="replyInput"
            class="reply-input"
            v-on:blur="replyInputOnFocus=false"
            v-on:focus="replyInputOnFocus=true; firstFocus=true"
            placeholder="评论点什么"
          ></div>
        </section>
        <div :class="{'progess-bar-0': !replyInputOnFocus, 'progess-bar-1': replyInputOnFocus}"></div>
        <section v-if="firstFocus" class="reply-button animated fadeIn">
          <span class="cancel" @click="replyCancel">取消</span>
          <input
            class="button-style"
            :disabled="this.replyInputValue.trim().length === 0"
            type="button"
            value="评论"
            @click="replySubmit"
          >
        </section>
        <div class="reply-list">
          <div
            v-for="parent_r of replies"
            v-if="parent_r.show"
            :key="parent_r.id"
            class="reply-item"
          >
            <div>
              <router-link :to="{name: 'myspace', params: {id: parent_r.from_user_id}}">
                <img class="avatar-xs" :src="parent_r.from_user_avatar" alt>
              </router-link>
            </div>
            <div class="reply-info">
              <ReplyItem
                :reply="parent_r"
                :blog="blog"
                :parent_id="parent_r.id"
                v-on:toggleLike="toggleLike"
                v-on:blogReplyDone="blogReplyDone"
              ></ReplyItem>
              <p
                class="show-sub-reply-button"
                v-show="parent_r.childs.length > 0 && parent_r.showChilds === false"
                @click="parent_r.showChilds = true"
              >显示{{ parent_r.childs.length }}条回复</p>
              <p
                class="show-sub-reply-button"
                v-show="parent_r.childs.length > 0 && parent_r.showChilds === true"
                @click="parent_r.showChilds = false"
              >隐藏回复</p>
              <div class="sub-reply-list" v-if="parent_r.showChilds">
                <div
                  v-for="child_r of parent_r.childs"
                  v-if="child_r.show"
                  :key="child_r.id"
                  class="sub-reply-item"
                >
                  <div>
                    <router-link :to="{name: 'myspace', params: {id: child_r.from_user_id}}">
                      <img class="avatar-xs" :src="child_r.from_user_avatar" alt>
                    </router-link>
                  </div>
                  <div class="reply-info">
                    <ReplyItem
                      :reply="child_r"
                      :blog="blog"
                      :parent_id="parent_r.id"
                      v-on:toggleLike="toggleLike"
                      v-on:blogReplyDone="blogReplyDone"
                    ></ReplyItem>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import ReplyItem from "@/components/sub/replyItem";
import MySpace from "../views/MySpace";
export default {
  name: "BlogInfo",
  data() {
    return {
      replyInputOnFocus: false,
      replyInputValue: "",
      firstFocus: false,
      blog: "",
      replies: ""
    };
  },

  created() {
    this.getBlog(this.blogid);
  },
  components: {
    ReplyItem
  },
  props: ["blogid"],
  methods: {
    getBlog: function(id) {
      if (id !== undefined) {
        this.$axios
          .get(`http://192.168.1.7:8000/api/blog/${id}`)
          .then(response => {
            if (response.data.code === 1) {
              this.blog = response.data.msg;
              if (response.data.addition.length > 0) {
                // 组织replies
                let temp_replies = response.data.addition;
                let parent_replies = temp_replies.filter(function(item) {
                  return item.parent_reply === 0;
                });
                let children_replies = temp_replies.filter(function(item) {
                  return item.parent_reply !== 0;
                });
                for (let parent_reply of parent_replies) {
                  parent_reply["showChilds"] = false;
                  parent_reply["replyBegin"] = false;
                  parent_reply["replyOnFocus"] = false;
                  parent_reply["replyFirstFocus"] = false;
                  parent_reply["replyInputValue"] = "";
                  parent_reply["show"] = true;
                  parent_reply["childs"] = [];
                  for (let children_reply of children_replies) {
                    if (children_reply.parent_reply === parent_reply.id) {
                      children_reply["replyBegin"] = false;
                      children_reply["replyOnFocus"] = false;
                      children_reply["replyFirstFocus"] = false;
                      children_reply["replyInputValue"] = "";
                      children_reply["show"] = true;

                      parent_reply["childs"].push(children_reply);
                    }
                  }
                }
                this.replies = parent_replies;
              } else {
                this.replies = "";
              }
            } else {
              alert(response.data.msg);
            }
          });
      }
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
                this.$emit("blogDeleteDone", blog_id);
              } else {
                alert(response.data.msg);
              }
            });
        }
      }
    },
    replyInput: function(event) {
      this.replyInputValue = event.target.innerText;
    },
    replyCancel: function(event) {
      this.replyInputOnFocus = false;
      this.replyInputValue = "";
      this.firstFocus = false;
      this.$refs.replyInput.innerText = "";
    },
    replySubmit: function() {
      if (this.replyInputValue.length > 1000) {
        alert("回复内容内容过长");
      } else {
        this.$axios
          .post("http://192.168.1.7:8000/api/blog/replyStore", {
            blog_id: this.blogid,
            to_reply: 0,
            parent_reply: 0,
            body: this.replyInputValue,
            to_user_id: this.blog.author_id
          })
          .then(response => {
            if (response.data.code === 1) {
              this.replyCancel();
              this.blogReplyDone(response.data.msg);
            } else {
              alert(response.data.msg);
            }
          });
      }
    },
    blogReplyDone: function(reply) {
      reply["replyBegin"] = false;
      reply["replyOnFocus"] = false;
      reply["replyFirstFocus"] = false;
      reply["replyInputValue"] = "";
      reply["show"] = true;
      if (reply.parent_reply === 0) {
        reply["childs"] = [];
        reply["showChilds"] = false;
        this.replies.unshift(reply);
      } else {
        for (let r of this.replies) {
          if (r.id === reply.parent_reply) {
            r["childs"].push(reply);
          }
        }
      }
    },
    toggleLike: function(e, way, item) {
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
  computed: {
    blogIcon() {
      return [this.blog.liked ? "fas" : "far", "thumbs-up"];
    }
  }
};
</script>
<style lang="scss" scoped>
@import "../assets/scss/blog_info_scoped";
</style>

<style lang="scss">
@import "../assets/scss/blog_info";
</style>
