<template>
  <div class="reply-area">
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
    <div :class="replyInputOnFocus ? 'progess-bar-1': 'progess-bar-0'"></div>

    <section v-if="firstFocus" class="reply-button animated fadeIn">
      <span class="cancel" @click="replyCancel">取消</span>
      <input
        v-show="!replyOnSubmit"
        class="button-style"
        :disabled="this.replyInputValue.trim().length === 0"
        type="button"
        value="评论"
        @click="replySubmit"
      >
      <button v-show="replyOnSubmit" class="button-style" disabled>
        <font-awesome-icon :icon="['fas', 'spinner']" spin/>
      </button>
    </section>

    <div class="reply-list">
      <div
        v-for="reply of replies.filter(item => {return item.show === true;})"
        :key="reply.id"
        class="reply-item"
      >
        <div>
          <router-link :to="{name: 'myspace', params: {id: reply.from_user_id}}">
            <img class="avatar-sm" :src="reply.from_user_avatar" alt>
          </router-link>
        </div>

        <div class="reply-info">
          <p>
            <router-link
              class="reply-user-name"
              :to="{name: 'myspace', params: {id: reply.from_user_id}}"
            >{{ reply.from_user_nickname }}</router-link>
            <span class="reply-time">{{ reply.created_at }}</span>
          </p>
          <p class="reply-body">{{ reply.body }}</p>

          <div class="reply-footer">
            <div>
              <span class="like-icon">
                <font-awesome-icon
                  @click="$emit('toggleLike', app === 'photo' ? 'preply' : 'breply', reply)"
                  :icon="[reply.liked ? 'fas' : 'far','thumbs-up']"
                  size="sm"
                />
              </span>
              <span class="like-count">{{ reply.likes }}</span>
            </div>
            <div>
              <span class="reply-reply-button" @click="replyreplyBegin($event, reply)">回复</span>
              <span
                v-if="reply.from_user_id === $store.state.id"
                class="reply-delete-button"
                @click="replyDelete(reply, 'reply')"
              >删除</span>
            </div>
          </div>

          <section v-if="reply.replyBegin" class="sub-replying">
            <img class="avatar-xs" :src="$store.state.avatar" alt>
            <div
              contenteditable="plaintext-only"
              class="sub-reply-input"
              v-on:blur="reply.replyOnFocus=false"
              v-on:focus="reply.replyOnFocus=true; reply.replyFirstFocus=true"
              @input="replyreplyInput($event, reply)"
            ></div>
          </section>
          <div :class="reply.replyOnFocus ? 'progess-bar-1': 'progess-bar-0'"></div>

          <section v-if="reply.replyFirstFocus" class="reply-button animated fadeIn">
            <span class="cancel" @click="replyreplyCancel(reply)">取消</span>
            <input
              v-show="!reply.replyOnSubmit"
              class="button-style"
              :disabled="reply.replyInputValue.trim().length === 0"
              type="button"
              value="回复"
              @click="replyreplySubmit(reply, reply, 'reply')"
            >
            <button v-show="reply.replyOnSubmit" class="button-style" disabled>
              <font-awesome-icon :icon="['fas', 'spinner']" spin/>
            </button>
          </section>
          <p
            class="show-sub-reply-button"
            v-show="reply.sub_replies_count > 0 && reply.displayChilds === false"
            @click="showSubReplies(reply)"
          >
            <span>显示{{ reply.sub_replies_count }}条回复</span>
            <font-awesome-icon :icon="['fas', 'chevron-down']"></font-awesome-icon>
          </p>
          <p
            class="show-sub-reply-button"
            v-show="reply.displayChilds === true"
            @click="reply.displayChilds = false"
          >
            <span>隐藏回复</span>
            <font-awesome-icon :icon="['fas', 'chevron-up']"></font-awesome-icon>
          </p>

          <div class="sub-reply-list animated fadeIn" v-show="reply.displayChilds">
            <div
              v-for="sub_reply of reply.childs.filter(item => {return item.show === true})"
              :key="sub_reply.id"
              class="sub-reply-item"
            >
              <div>
                <router-link :to="{name: 'myspace', params: {id: sub_reply.from_user_id}}">
                  <img class="avatar-xs" :src="sub_reply.from_user_avatar" alt>
                </router-link>
              </div>
              <div class="reply-info">
                <p>
                  <router-link
                    class="reply-user-name"
                    :to="{name: 'myspace', params: {id: sub_reply.from_user_id}}"
                  >{{ sub_reply.from_user_nickname }}</router-link>
                  <span class="reply-time">{{ sub_reply.created_at }}</span>
                </p>
                <p class="reply-body">{{ sub_reply.body }}</p>

                <div class="reply-footer">
                  <div>
                    <span class="like-icon">
                      <font-awesome-icon
                        @click="$emit('toggleLike', app === 'photo' ? 'psreply' : 'bsreply', sub_reply)"
                        :icon="[sub_reply.liked ? 'fas' : 'far','thumbs-up']"
                        size="sm"
                      />
                    </span>
                    <span class="like-count">{{ sub_reply.likes }}</span>
                  </div>
                  <div>
                    <span class="reply-reply-button" @click="replyreplyBegin($event, sub_reply)">回复</span>
                    <span
                      v-if="sub_reply.from_user_id === $store.state.id"
                      class="reply-delete-button"
                      @click="replyDelete(sub_reply, 'subreply')"
                    >删除</span>
                  </div>
                </div>

                <section v-if="sub_reply.replyBegin" class="sub-replying">
                  <img class="avatar-xs" :src="$store.state.avatar" alt>
                  <div
                    contenteditable="plaintext-only"
                    class="sub-reply-input"
                    v-on:blur="sub_reply.replyOnFocus=false"
                    v-on:focus="sub_reply.replyOnFocus=true; sub_reply.replyFirstFocus=true"
                    @input="replyreplyInput($event, sub_reply)"
                  ></div>
                </section>

                <div :class="sub_reply.replyOnFocus ? 'progess-bar-1': 'progess-bar-0'"></div>

                <section v-if="sub_reply.replyFirstFocus" class="reply-button animated fadeIn">
                  <span class="cancel" @click="replyreplyCancel(sub_reply)">取消</span>
                  <input
                    v-show="!sub_reply.replyOnSubmit"
                    class="button-style"
                    :disabled="sub_reply.replyInputValue.trim().length === 0"
                    type="button"
                    value="回复"
                    @click="replyreplySubmit(reply, sub_reply, 'subreply')"
                  >
                  <button v-show="sub_reply.replyOnSubmit" class="button-style" disabled>
                    <font-awesome-icon :icon="['fas', 'spinner']" spin/>
                  </button>
                </section>
              </div>
            </div>
            <p
              v-if="reply.end === false && reply.loading_replies === false"
              @click="getSubReplies(reply)"
              class="more-replies-button"
            >加载更多评论</p>
            <span v-if="reply.loading_replies">
              <font-awesome-icon :icon="['fas', 'spinner']" spin/>
            </span>
          </div>
        </div>
      </div>
      <div
        class="more-replies-button"
        v-if="end === false && loading === false"
        @click="getReplies(app, artical, false);"
      >查看更多评论</div>
      <div v-if="loading" class="center">
        <font-awesome-icon :icon="['fas', 'spinner']" spin size="lg"/>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Reply",
  data() {
    return {
      replyInputOnFocus: false,
      replyInputValue: "",
      firstFocus: false,
      replyOnSubmit: false,
      page: 0,
      end: false,
      loading: true,
      replies: [],
      cached_replies: {}
    };
  },
  props: ["app", "artical"],
  methods: {
    getReplies: function(app, artical, fresh) {
      this.loading = true;
      this.$axios
        .get(`/api/${this.app}/reply?id=${artical.id}&page=${this.page + 1}`)
        .then(response => {
          this.page++;
          let rs = response.data.msg;
          if (fresh) {
            for (let r of rs) {
              r["displayChilds"] = false;
              r["replyBegin"] = false;
              r["replyOnFocus"] = false;
              r["replyFirstFocus"] = false;
              r["replyOnSubmit"] = false;
              r["replyInputValue"] = "";
              r["page"] = 0;
              r["end"] = false;
              r["loading_replies"] = false;
              r["show"] = true;
              r["getChilds"] = false;
              r["childs"] = [];
            }
            this.replies = rs;
            this.cached_replies[this.app + artical.id] = rs;
            this.loading = false;
          } else {
            for (let r of rs) {
              r["displayChilds"] = false;
              r["replyBegin"] = false;
              r["replyOnFocus"] = false;
              r["replyOnSubmit"] = false;
              r["replyFirstFocus"] = false;
              r["page"] = 0;
              r["end"] = false;
              r["loading_replies"] = false;
              r["replyInputValue"] = "";
              r["show"] = true;
              r["getChilds"] = false;
              r["childs"] = [];
              this.replies.push(r);
            }
            this.loading = false;
          }
          this.cached_replies[this.app + artical.id]["page"] = this.page;
          if (rs.length < 10) {
            this.end = true;
            this.cached_replies[this.app + artical.id]["end"] = true;
          } else {
            this.end = false;
            this.cached_replies[this.app + artical.id]["end"] = false;
          }
        })
        .catch(error => {});
    },
    showSubReplies: function(reply) {
      reply.displayChilds = true;
      if (!reply.getChilds) {
        reply.childs = [];
        this.getSubReplies(reply);
        reply.getChilds = true;
      }
    },
    getSubReplies: function(reply) {
      reply.loading_replies = true;
      this.$axios
        .get(`/api/${this.app}/subReply?id=${reply.id}&page=${reply.page + 1}`)
        .then(response => {
          let rs = response.data.msg;
          for (let sr of rs) {
            sr["replyBegin"] = false;
            sr["replyOnFocus"] = false;
            sr["replyFirstFocus"] = false;
            sr["replyOnSubmit"] = false;
            sr["replyInputValue"] = "";
            sr["show"] = true;
            reply.childs.push(sr);
          }
          if (rs.length < 10) {
            reply.end = true;
          }
          reply.page += 1;
          reply.loading_replies = false;
        });
    },

    replyreplyBegin: function(event, reply) {
      reply.replyBegin = true;
      setTimeout(() => {
        event.target.parentNode.parentNode.parentNode
          .querySelector(".sub-reply-input")
          .focus();
      }, 100);
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
        this.replyOnSubmit = true;
        this.$axios
          .post(`/api/${this.app}/replyStore`, {
            id: this.artical.id,
            body: this.replyInputValue,
            to_user_id: this.artical.author_id
          })
          .then(response => {
            if (response.data.code === 1) {
              this.replyCancel();
              let reply = response.data.msg;
              reply["displayChilds"] = false;
              reply["replyBegin"] = false;
              reply["replyOnFocus"] = false;
              reply["replyFirstFocus"] = false;
              reply["replyOnSubmit"] = false;
              reply["page"] = 0;
              reply["end"] = false;
              reply["loading_replies"] = false;
              reply["replyInputValue"] = "";
              reply["show"] = true;
              reply["getChilds"] = false;
              reply["childs"] = [];
              this.replies.unshift(reply);
              this.replyOnSubmit = false;
            } else {
              alert(response.data.msg);
              this.replyOnSubmit = false;
            }
          });
      }
    },
    replyDelete: function(reply, level) {
      if (reply.from_user_id !== this.$store.state.id) {
        alert("抱歉，你无权删除");
      } else {
        if (confirm("确定删除该评论吗？")) {
          this.$axios
            .get(`/api/${this.app}/reply/${reply.id}/delete?level=${level}`)
            .then(response => {
              if (response.data.code === 1) {
                reply["show"] = false;
              } else {
                alert(response.data.msg);
              }
            });
        }
      }
    },

    replyreplyInput: function(event, reply) {
      reply.replyInputValue = event.target.innerText;
    },
    replyreplyCancel: function(reply) {
      reply["replyBegin"] = false;
      reply["replyOnFocus"] = false;
      reply["replyFirstFocus"] = false;
      reply["replyOnSubmit"] = false;
      reply["replyInputValue"] = "";
    },
    replyreplySubmit: function(parent_reply, reply, level) {
      if (reply.replyInputValue.length > 1000) {
        alert("回复内容内容过长");
      } else {
        reply.replyOnSubmit = true;
        let url = `/api/${this.app}/subReplyStore`;
        let reply_id = reply.id;
        let to_reply = 0;

        if (level === "subreply") {
          reply_id = reply.reply_id;
          to_reply = reply.id;
        }
        this.$axios
          .post(url, {
            id: this.artical.id,
            reply_id: reply_id,
            to_reply: to_reply,
            body: reply.replyInputValue,
            to_user_id: reply.from_user_id
          })
          .then(response => {
            if (response.data.code === 1) {
              let sr = response.data.msg;
              sr["replyBegin"] = false;
              sr["replyOnFocus"] = false;
              sr["replyFirstFocus"] = false;
              sr["replyOnSubmit"] = false;
              sr["replyInputValue"] = "";
              sr["show"] = true;

              parent_reply.childs.push(sr);
              parent_reply.displayChilds = true;
              parent_reply.sub_replies_count++;
              this.replyreplyCancel(reply);
            } else {
              alert(response.data.msg);
              reply.replyOnSubmit = true;
            }
          });
      }
    }
  },
  watch: {
    artical(n, o) {
      if (this.cached_replies[this.app + n.id] === undefined) {
        this.page = 0;
        this.end = false;
        this.getReplies(this.app, n, true);
      } else {
        this.page = this.cached_replies[this.app + n.id].page;
        this.end = this.cached_replies[this.app + n.id].end;
        this.replies = this.cached_replies[this.app + n.id];
      }
    }
  }
};
</script>

<style lang="scss">
@import "../../assets/scss/var";
@import "../../assets/scss/config";
.reply-area {
  padding: 1.5em 0.5em;
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
      width: calc(100% - 50px);
      min-height: 25px;
      background: none;
      padding: 0 10px 4px 10px;
      margin: 10px 0 20px 0;
      border-bottom: 1px $gray solid;
      color: black;
      outline: none;
      box-shadow: none;
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
      width: calc(100% - 50px);
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
        text-decoration: none;
        color: black;
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
    color: darken($color: $gray, $amount: 60);
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
  @include mediaSm {
    .reply-list {
      .reply-item {
        margin-top: 1.5em;
      }
    }
  }
}
.more-replies-button {
  cursor: pointer;
  color: black;
  margin-top: 1em;
}
.progess-bar-1 {
  width: calc(100% - 50px);
}
.progess-bar-0,
.progess-bar-1 {
  margin-left: 50px;
}
</style>

