<template>
  <div class="container">
    <div class="moment-page-wrap">
      <aside class="left">
        <section class="moment-item" v-for="moment in moments" :key="moment.id">
          <header>
            <span>
              <router-link :to="{name: 'myspace', params: {id: moment.author_id}}">
                <img :src="moment.author_avatar" class="avatar-xs" alt>
              </router-link>&nbsp;
              <router-link
                class="author-name"
                :to="{name: 'myspace', params: {id: moment.author_id}}"
              >{{ moment.author }}</router-link>&nbsp;
              <span>&bull;</span>
              &nbsp;
              <router-link
                class="article-title"
                v-if="moment.app === 'photo'"
                :to="{name: 'photoInfoPage', params: {photoid: moment.id}}"
              >图片</router-link>
              <router-link
                class="article-title"
                v-else
                :to="{name: 'blogInfoPage', params: {blogid: moment.id}}"
              >{{ moment.title }}</router-link>
            </span>
            <span class="article-time">
              <font-awesome-icon :icon="['far', 'clock']"></font-awesome-icon>
              {{ moment.created_at }}
            </span>
          </header>
          <article>
            <div class="photo" v-if="moment.app === 'photo'">
              <img oncontextmenu="return false" ondragstart="return false" :src="moment.url" alt>
            </div>
            <div class="blog" v-if="moment.app === 'blog'" v-html="moment.body"></div>
          </article>
          <footer>
            <div class="icons-row">
              <span class="like-area" @click="toggleLike(moment.app, moment.app, moment)">
                <span v-if="moment.app === 'photo'">
                  <font-awesome-icon v-show="!moment.liked" :icon="['far', 'heart']" size="lg"></font-awesome-icon>
                  <font-awesome-icon v-show="moment.liked" :icon="['fas', 'heart']" size="lg"></font-awesome-icon>
                </span>
                <span v-else>
                  <font-awesome-icon v-show="!moment.liked" :icon="['far', 'thumbs-up']" size="lg"></font-awesome-icon>
                  <font-awesome-icon v-show="moment.liked" :icon="['fas', 'thumbs-up']" size="lg"></font-awesome-icon>
                </span>
                &nbsp;
                <span>{{ moment.likes }}</span>
              </span>
              &emsp;
              <span class="comment-area" @click="commentBegin">
                <font-awesome-icon :icon="['far', 'comment']" size="lg"></font-awesome-icon>&nbsp;
                <span>{{ moment.replies_count }}</span>
              </span>
            </div>

            <div class="photo-caption" v-if="moment.app === 'photo'">
              <router-link
                class="author-name"
                :to="{name: 'myspace', params: {id: moment.author_id}}"
              >{{ moment.author }}</router-link>&nbsp;
              <span>{{ moment.caption }}</span>
            </div>

            <p
              v-if="moment.replies_count > 0 && moment.replies.length === 0"
              @click="getReplies(moment)"
              class="view-comment"
            >加载评论</p>

            <div v-for="reply in moment['replies']" :key="reply.id" class="comment-display">
              <router-link
                class="user-name"
                :to="{name: 'myspace', params: {id: reply.from_user_id}}"
              >{{ reply.from_user_nickname }}</router-link>&nbsp;
              <span>{{ reply.body }}</span>
            </div>
            <input
              class="comment-input"
              type="text"
              autocomplete="off"
              autocorrect="off"
              placeholder="留个评论..."
              @keyup.enter="commentSubmit($event, moment)"
            >
          </footer>
        </section>
      </aside>
      <aside class="right">
        <section class="moment-item">hgfhgfh</section>
      </aside>
    </div>
  </div>
</template>

<script>
export default {
  name: "Moments",
  data() {
    return {
      moments: []
    };
  },
  created() {
    this.getMoments();
  },
  methods: {
    getMoments: function() {
      this.$axios
        .get("http://192.168.1.7:8000/api/homespace/getMoments")
        .then(response => {
          if (response.data.code === 1) {
            this.moments = response.data.msg;
          } else {
            alert(response.data.msg);
          }
        });
    },
    getReplies: function(moment) {
      this.$axios
        .get(`http://192.168.1.7:8000/api/${moment.app}/reply?id=${moment.id}`)
        .then(response => {
          moment["replies"] = response.data.msg;
        })
        .catch(error => {
          alert(error);
        });
    },
    commentBegin: function(e) {
      let p = e.target.parentNode;
      while (p.nodeName !== "FOOTER") p = p.parentNode;
      p.lastChild.focus();
    },
    commentSubmit: function(e, moment) {
      let data = e.target.value;
      e.target.value = "";
      if (data.trim().length > 0) {
        this.$axios
          .post(`http://192.168.1.7:8000/api/${moment.app}/replyStore`, {
            id: moment.id,
            body: data,
            to_user_id: moment.author_id
          })
          .then(response => {
            if (response.data.code === 1) {
              moment["replies"].push(response.data.msg);
              moment["replies_count"]++;
            } else {
              alert(response.data.msg);
            }
          });
      }
    },
    toggleLike: function(app, way, item) {
      // 判断是点赞还是取消点赞
      let aor = item.liked ? "rem" : "add";
      item.likes = item.liked ? item.likes - 1 : item.likes + 1;
      // 先把样式改了
      item.liked = item.liked ? false : true;
      let url = `http://192.168.1.7:8000/api/${app}/likes?way=${way}&id=${
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
.moment-page-wrap {
  width: 100%;
  padding: 2em 5em;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
.left {
  width: 65%;
}
.right {
  width: 30%;
}
.moment-item {
  display: block;
  width: 100%;
  border: 1px solid #e6e6e6;
  margin-bottom: 2em;
  header {
    display: flex;
    justify-content: space-between;
    padding: 1em 1.5em;
    span:nth-child(1),
    span:nth-child(2) {
      display: flex;
      align-items: center;
    }
    .author-name,
    .article-title {
      text-decoration: none;
      font-weight: bold;
      color: $darkblue;
      font-size: 14px;
      &:hover {
        text-decoration: underline;
      }
    }
    .article-time {
      font-size: 14px;
      color: $gray;
    }
  }
  article {
    font-size: 15px;
    .photo {
      display: flex;
      flex-direction: column;
      justify-content: center;
      img {
        width: 100%;
      }
    }
    .blog {
      word-wrap: break-word;
      word-break: break-all;
    }
  }
  footer {
    padding: 1em 1.5em;
    .icons-row {
      margin-bottom: 1em;
    }
    .like-area,
    .comment-area {
      cursor: pointer;
    }
    .photo-caption {
      font-size: 13px;
      margin-bottom: 1em;
      .author-name {
        text-decoration: none;
        color: $blue;
      }
    }
    .view-comment {
      font-size: 13px;
      color: $gray;
      cursor: pointer;
    }
    .comment-display {
      margin-top: 0.5em;

      font-size: 13px;
      .user-name {
        text-decoration: none;
        color: $blue;
      }
    }
    .comment-input {
      margin-top: 1em;
      background: none;
      display: block;
      outline: none;
      border: none;
      padding: 2px;
      width: 100%;
    }
  }
}
</style>

