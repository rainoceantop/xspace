<template>
  <article>
    <div v-if="uid === $store.state.id && $store.state.private">
      <header>关注请求</header>
      <UserItem
        v-if="requests.length>0"
        :users="requests"
        requests="yes"
        v-on:pass="passFollowDone"
      ></UserItem>
      <p v-else style="text-align: center;">暂无关注请求</p>
    </div>
    <div>
      <header>{{ uid === $store.state.id ? '我' : 'TA' }}的粉丝</header>
      <UserItem :users="fans"></UserItem>
    </div>
  </article>
</template>

<script>
import UserItem from "./sub/userItem";

export default {
  data() {
    return {
      fans: [],
      requests: []
    };
  },
  components: { UserItem },
  props: ["uid"],
  created() {
    this.init();
  },
  methods: {
    init: function() {
      if (this.uid !== undefined) {
        this.$axios
          .get(
            `http://192.168.1.7:8000/api/homespace/getFansAndRequests?uid=${
              this.uid
            }`
          )
          .then(response => {
            if (response.data.code === 1) {
              this.fans = response.data.msg.fans;
              this.requests = response.data.msg.requests;
            } else alert(response.data.msg);
          });
      }
    },
    passFollowDone: function(item) {
      this.fans.unshift(item);
      for (let i = 0; i < this.requests.length; i++) {
        if (this.requests[i].username === item.username) {
          this.requests.splice(i, 1);
          break;
        }
      }
    }
  },
  watch: {
    uid(n, o) {
      if (n !== undefined) {
        this.init();
      }
    }
  }
};
</script>



