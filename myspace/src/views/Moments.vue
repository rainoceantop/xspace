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
                :title="moment.title"
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
            <div :class="['blog', moment.fold ? 'fold': '']" v-if="moment.app === 'blog'">
              <div v-html="moment.body"></div>
              <ul v-if="moment.tags" class="tag-display">
                <li v-for="tag in moment.tags" :key="tag">
                  <router-link
                    class="tag-hash-style"
                    :to="{name: 'tag', params: {tagname: tag}}"
                  >{{ tag }}</router-link>
                </li>
              </ul>
              <div class="fold-label" v-show="moment.fold" @click="moment.fold = false">
                <p>展开剩余内容</p>
              </div>
            </div>
          </article>
          <footer>
            <div class="icons-row">
              <span class="like-area" @click="toggleLike(moment.app, moment.app, moment)">
                <span v-if="moment.app === 'photo'">
                  <font-awesome-icon v-show="!moment.liked" :icon="['far', 'heart']" size="lg"></font-awesome-icon>
                  <font-awesome-icon
                    v-show="moment.liked"
                    :icon="['fas', 'heart']"
                    size="lg"
                    style="color: red"
                  ></font-awesome-icon>
                </span>
                <span v-else>
                  <font-awesome-icon v-show="!moment.liked" :icon="['far', 'thumbs-up']" size="lg"></font-awesome-icon>
                  <font-awesome-icon
                    v-show="moment.liked"
                    :icon="['fas', 'thumbs-up']"
                    size="lg"
                    style="color: #007CBA"
                  ></font-awesome-icon>
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
              <ul v-if="moment.tags" class="tag-display">
                <li v-for="tag in moment.tags" :key="tag">
                  <router-link
                    class="tag-hash-style"
                    :to="{name: 'tag', params: {tagname: tag}}"
                  >{{ tag }}</router-link>
                </li>
              </ul>
            </div>

            <div v-for="reply in moment['replies']" :key="reply.id" class="comment-display">
              <router-link
                class="user-name"
                :to="{name: 'myspace', params: {id: reply.from_user_id}}"
              >{{ reply.from_user_nickname }}</router-link>&nbsp;
              <span>{{ reply.body }}</span>
            </div>
            <p
              v-if="moment.replies_count > 0 && moment.end === false && moment.loading_replies === false"
              @click="getReplies(moment)"
              class="view-comment"
            >加载评论</p>
            <span v-if="moment.loading_replies">
              <font-awesome-icon :icon="['fas', 'spinner']" spin/>
            </span>
            
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
        <div v-if="loading" class="center">
          <font-awesome-icon :icon="['fas', 'spinner']" spin size="2x"/>
        </div>
      </aside>
      <aside class="right hide-on-med-and-down">
        <section class="moment-item">其他展示位</section>
      </aside>
    </div>
  </div>
</template>

<script>
export default {
  name: "Moments",
  data() {
    return {
      moments: [],
      loading: true
    };
  },
  created() {
    this.getMoments();
  },
  methods: {
    getMoments: function() {
      this.$axios.get("/api/homespace/getMoments").then(response => {
        if (response.data.code === 1) {
          let items = response.data.msg;
          for (let i = 0; i < items.length; i++) {
            items[i]["fold"] = true;
            items[i]["page"] = 0;
            items[i]["end"] = false;
            items[i]["loading_replies"] = false;
          }
          this.moments = items;
        } else {
          alert(response.data.msg);
        }
        this.loading = false;
      });
    },
    getReplies: function(moment) {
      moment.loading_replies = true;
      this.$axios
        .get(`/api/${moment.app}/reply?id=${moment.id}&page=${moment.page + 1}`)
        .then(response => {
          let items = response.data.msg;
          for (let item of items) {
            moment["replies"].push(item);
          }
          if (items.length < 10) {
            moment["end"] = true;
          }
          moment["page"] += 1;
          moment["loading_replies"] = false;
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
          .post(`/api/${moment.app}/replyStore`, {
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
      let url = `/api/${app}/likes?way=${way}&id=${item.id}&aor=${aor}`;
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
@import "../assets/scss/config";
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
  border: 1px solid $lightgray;
  margin-bottom: 2em;
  header {
    display: flex;
    justify-content: space-between;
    padding: 0.5em 1em;
    span:nth-child(1),
    span:nth-child(2) {
      display: flex;
      align-items: center;
    }
    span:nth-child(1) {
      max-width: 80%;
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
    .author-name {
      white-space: nowrap;
    }
    .article-title {
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
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
      width: 100%;
      word-wrap: break-word;
      word-break: break-all;
      position: relative;
    }
    .fold {
      text-align: start;
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 7;
      -webkit-box-orient: vertical;
    }
    .fold-label {
      color: $blue;
      font-weight: bold;
      text-align: center;
      font-size: 13px;
      line-height: 25px;
      cursor: pointer;
      background-image: -webkit-linear-gradient(
        bottom,
        rgba(245, 245, 245, 1),
        rgba(245, 245, 245, 0.75) 80%,
        rgba(245, 245, 245, 0)
      );
      -moz-box-sizing: border-box;
      -webkit-box-sizing: border-box;
      -o-box-sizing: border-box;
      -ms-box-sizing: border-box;
      box-sizing: border-box;
      width: inherit;
      position: absolute;
      bottom: 0;
      left: 0;
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
      color: darken($color: $gray, $amount: 15);
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
      height: auto;
      padding-bottom: 5px;
      margin-top: 1em;
      background: none;
      display: block;
      outline: none;
      border: none;
      width: 100%;
    }
  }
}

@include mediaLg {
}

@include mediaMd {
}
@include mediaSm {
  .moment-page-wrap {
    padding: 0;
  }
  .left {
    width: 100%;
  }
  .moment-item {
    header {
      padding: 0.5em;
    }
  }
}
@include mediaXS {
  .moment-page-wrap {
    padding: 0;
  }
  .left {
    width: 100%;
  }
  .moment-item {
    header {
      padding: 0.5em;
    }
  }
}
</style>

