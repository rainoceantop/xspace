<template>
  <div>
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
            @click="$emit('toggleLike', 'breply', reply)"
            :icon="[reply.liked ? 'fas' : 'far','thumbs-up']"
            size="sm"
          />
        </span>
        <span class="like-count">{{ reply.likes }}</span>
      </div>
      <div>
        <span class="reply-reply-button" @click="reply.replyBegin = true;">回复</span>
        <span
          v-if="reply.from_user_id === $store.state.id"
          class="reply-delete-button"
          @click="replyDelete(reply.id, reply.from_user_id)"
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
      >{{ reply.from_user_nickname }}&nbsp;</div>
    </section>
    <div :class="{'progess-bar-0': !reply.replyOnFocus, 'progess-bar-1': reply.replyOnFocus}"></div>
    <section v-if="reply.replyFirstFocus" class="reply-button animated fadeIn">
      <span class="cancel" @click="replyreplyCancel(reply)">取消</span>
      <input
        class="button-style"
        :disabled="reply.replyInputValue.trim().length === 0"
        type="button"
        value="回复"
        @click="replyreplySubmit(parent_id, reply)"
      >
    </section>
  </div>
</template>

<script>
export default {
  name: 'replyItem',
  props: {
    forid: "",
    reply: "",
    parent_id: 0
  },
  methods: {
    replyDelete: function(reply_id, from_user_id) {
      if (from_user_id !== this.$store.state.id) {
        alert("抱歉，你无权删除");
      } else {
        if (confirm("确定删除该评论吗？")) {
          this.$axios
            .get(`http://192.168.1.7:8000/api/blog/reply/${reply_id}/delete`)
            .then(response => {
              if (response.data.code === 1) {
                this.reply["show"] = false;
              } else {
                alert(response.data.msg);
              }
            });
        }
      }
    },

    replyreplyInput: function(event, reply) {
      event.preventDefault();
      reply.replyInputValue = event.target.innerText;
    },
    replyreplyCancel: function(reply) {
      reply["replyBegin"] = false;
      reply["replyOnFocus"] = false;
      reply["replyFirstFocus"] = false;
      reply["replyInputValue"] = "";
    },
    replyreplySubmit: function(parent_id, reply) {
      if (reply.replyInputValue.length > 1000) {
        alert("回复内容内容过长");
      } else {
        this.$axios
          .post("http://192.168.1.7:8000/api/blog/replyStore", {
            blog_id: this.forid,
            to_reply: reply.id,
            parent_reply: parent_id,
            body: reply.replyInputValue,
            to_user_id: reply.from_user_id
          })
          .then(response => {
            if (response.data.code === 1) {
              this.replyreplyCancel(this.reply);
              this.$emit("blogReplyDone", response.data.msg);
            } else {
              alert(response.data.msg);
            }
          });
      }
    }
  }
};
</script>