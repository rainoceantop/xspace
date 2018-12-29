<template>
  <div class="container">
    <div class="blog-info-wrap">
      <div class="blog-header">
        <h3 id="title">{{ blog.title }}</h3>
        <div v-if="blog.author_id === $store.state.id" id="blog-operate-icons">
          <font-awesome-icon
            id="blog-edit-icon"
            :icon="['fas', 'edit']"
            @click="$emit('editBlog', blog)"
          />
          <font-awesome-icon
            id="blog-delete-icon"
            :icon="['fas', 'trash']"
            @click="blogDelete(blog.id, blog.author_id)"
          />
        </div>
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
              <img class="avatar-sm" :src="blog.author_avatar" alt>
            </div>
            <div>
              <p id="author-name">{{ blog.author }}</p>
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
              <img class="avatar-sm" :src="parent_r.from_user_avatar" alt>
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
                    <img class="avatar-xs" :src="child_r.from_user_avatar" alt>
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
import ReplyItem from "./sub/replyItem";
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
  props: {
    blogid: 0
  },
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
                this.$emit("blogDeleteDone");
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
      console.log(item.liked);
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
    if (this.blogid !== 0) {
      this.getBlog(this.blogid);
    }
  },
  beforeRouteUpdate(to, from, next) {
    if (to.params.blogid === "nomore") {
      alert("没有文章了");
      next(from.path);
    } else {
      next();
    }
  },
  watch: {
    blogid: function(newid, oldid) {
      this.getBlog(newid);
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
@import "../assets/scss/var";
@import "../assets/scss/config";
.container {
  width: 100%;
  display: flex;
  justify-content: center;
}
.blog-info-wrap {
  width: 70%;
  padding: 2em 5em;
  // background-color: yellowgreen;
  text-align: start;
  margin-top: 3em;
  margin-bottom: 100px;
  border: 1px $gray solid;
  box-shadow: 5px 8px 15px rgba(0, 0, 0, 0.3);

  .blog-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px $gray solid;
  }
  #blog-operate-icons {
    width: 60px;
    display: flex;
    justify-content: space-around;
    #blog-edit-icon,
    #blog-delete-icon {
      cursor: pointer;
    }
    #blog-edit-icon {
      &:hover {
        color: green;
      }
    }
    #blog-delete-icon {
      &:hover {
        color: red;
      }
    }
  }
  #title,
  #body {
    margin-bottom: 10px;
    word-wrap: break-word;
    overflow: auto;
  }
  #body {
    width: calc(100% - 2em);
    padding: 1em;
  }

  .artical-footer {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;

    .left {
    }

    .right {
      #post-time {
        color: $gray;
        font-size: 12px;
        margin-bottom: 6px;
      }
      .author-detail {
        display: flex;
        flex-direction: row;
        justify-content: start;

        #author-name {
          color: $gray;
          font-size: 15px;
          margin-left: 3px;
        }

        #author-follows {
          color: $gray;
          font-size: 13px;
          margin-left: 6px;
        }
      }
    }
  }
}
@include mediaXS {
  .container {
    width: 100%;
    padding: 0;
    margin: 0;
  }
  .blog-info-wrap {
    -moz-box-sizing: border-box;
    -webkit-box-sizing: border-box;
    -o-box-sizing: border-box;
    -ms-box-sizing: border-box;
    box-sizing: border-box;
    width: 100% !important;
    margin: 0;
    padding: 1em;
    border: none;
  }
}
@include mediaSm {
  .container {
    width: 100%;
    padding: 0;
    margin: 0;
  }
  .blog-info-wrap {
    -moz-box-sizing: border-box;
    -webkit-box-sizing: border-box;
    -o-box-sizing: border-box;
    -ms-box-sizing: border-box;
    box-sizing: border-box;
    width: 100% !important;
    margin: 0;
    padding: 1em;
    border: none;
  }
}
</style>
<style lang="scss">
@import "../assets/scss/var";
.like-icon {
  cursor: pointer;
}
.like-count {
  margin-left: 7px;
}
.reply-area {
  header {
    margin-bottom: 1em;
  }
  .reply-info {
    width: 100%;
    margin-left: 1em;
  }
  .replying {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    .reply-input {
      display: inline-block;
      width: calc(100% - 20px - 40px);
      padding: 5px 10px;
      min-height: 25px;
      background: none;
      border-bottom: 1px $gray solid;
      color: black;
      outline: none;
      box-shadow: none;
      margin-bottom: 20px;
      transition: width 0.5s ease-in-out;
      resize: none;
      &:empty:before {
        content: attr(placeholder);
        color: $gray;
      }
      &:focus:before {
        content: none;
      }
    }
  }

  .sub-replying {
    width: 100%;
    margin-top: 12px;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    .sub-reply-input {
      display: inline-block;
      width: calc(100% - 10px - 40px);
      padding: 5px;
      min-height: 20px;
      background: none;
      border-bottom: 1px $gray solid;
      color: black;
      outline: none;
      box-shadow: none;
      margin-bottom: 20px;
      transition: width 0.5s ease-in-out;
      resize: none;
      font-size: 10px;
      &:empty:before {
        content: attr(placeholder);
        color: $gray;
      }
      &:focus:before {
        content: none;
      }
    }
  }

  .reply-button {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    align-items: center;

    .cancel {
      margin-right: 1em;
      cursor: pointer;
      color: darken($color: $gray, $amount: 15);

      &:hover {
        color: black;
      }
    }
    .button-style {
      width: 80px;
    }
  }
  .reply-list {
    display: block;
    width: 100%;
    .reply-item {
      display: flex;
      flex-direction: row;
      margin-top: 2.5em;
      .reply-user-name {
        font-size: 13px;
      }
      .reply-time {
        margin-left: 5px;
        font-size: 13px;
        color: $gray;
      }
      .reply-body {
        width: 100%;
        margin-top: 7px;
        word-break: break-all;
        font-size: 15px;
      }
    }
    .reply-footer {
      margin-top: 0.8em;
      display: flex;
      flex-direction: row;
      justify-content: flex-start;
      align-items: center;
      color: darken($gray, 12);
      font-size: 14px;

      .reply-reply-button,
      .reply-delete-button {
        margin-left: 1em;
        cursor: pointer;
      }
    }
  }
  .show-sub-reply-button {
    font-size: 13px;
    margin-top: 7px;
    cursor: pointer;
    -moz-user-select: none; /*火狐*/
    -webkit-user-select: none; /*webkit浏览器*/
    -ms-user-select: none; /*IE10*/
    -khtml-user-select: none; /*早期浏览器*/
    user-select: none;
  }
  .sub-reply-list {
    display: block;
    width: 100%;
    margin-top: 1em;
    .sub-reply-item {
      display: flex;
      margin-top: 1em;
      flex-direction: row;
      .sub-reply-user-name {
        font-size: 12px;
      }
      .sub-reply-time {
        margin-left: 5px;
        font-size: 12px;
        color: $gray;
      }
      .sub-reply-body {
        width: 100%;
        margin-top: 7px;
        word-break: break-all;
        font-size: 14px;
      }
    }
  }
}
.progess-bar-1 {
  width: calc(100% - 40px);
}
.progess-bar-0,
.progess-bar-1 {
  margin-left: 40px;
}
</style>


