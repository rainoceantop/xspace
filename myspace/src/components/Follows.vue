<template>
  <article>
    <header>{{ uid === $store.state.id ? '我' : 'TA' }}的关注</header>
    <UserItem :users="follows"></UserItem>
  </article>
</template>

<script>
import UserItem from "./sub/userItem";

export default {
  data() {
    return {
      follows: []
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
            `http://192.168.1.7:8000/api/homespace/getFollows?uid=${this.uid}`
          )
          .then(response => {
            if (response.data.code === 1) {
              this.follows = response.data.msg;
            } else alert(response.data.msg);
          });
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



