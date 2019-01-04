<template>
  <div>
    <section class="user-item" v-for="user in users" :key="user.username">
      <div class="a">
        <router-link :to="{name: 'myspace', params: {id: user.username}}">
          <img :src="user.avatar" class="avatar-sm" alt>
        </router-link>
        <div class="b">
          <p>
            <router-link :to="{name: 'myspace', params: {id: user.username}}">{{ user.nickname }}</router-link>
          </p>
          <p v-html="user.bio"></p>
        </div>
      </div>
      <div v-if="user.username !== $store.state.id" class="c">
        <span
          :class="['follow', user.followed? 'was-followed':'go-follow']"
          @click="fE(user)"
        >{{ user.followed ? '已关注' : '关注' }}</span>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  props: ["users"],
  methods: {
    fE: function(item) {
      if (this.$store.state.login) {
        if (item.followed) {
          item.followed = false;
          // 取消关注
          this.$axios
            .get(
              `http://192.168.1.7:8000/api/homespace/userFollow?identity=${
                item.username
              }&fOrUnf=unfollow`
            )
            .then(response => {
              if (response.data.code !== 1) {
                this.followed = true;
                alert(response.data.msg);
              }
            });
        } else {
          item.followed = true;
          // 关注
          this.$axios
            .get(
              `http://192.168.1.7:8000/api/homespace/userFollow?identity=${
                item.username
              }&fOrUnf=follow`
            )
            .then(response => {
              if (response.data.code !== 1) {
                item.followed = false;

                alert(response.data.msg);
              }
            });
        }
      } else {
        alert("请先登录");
        this.$router.push("/user/login");
      }
    }
  }
};
</script>
<style lang="scss" scoped>
@import "../../assets/scss/var";

.user-item {
  width: 100%;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}
.a {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 80%;
}
.b {
  line-height: 20px;
  margin-left: 10px;
  width: 90%;
  p:nth-child(1) {
    font-weight: bold;
    font-size: 13px;
    a {
      text-decoration: none;
      color: black;
    }
  }
  p:nth-child(2) {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 13px;
    color: $gray;
  }
}
.c {
  width: 20%;
  text-align: end;
}
</style>
