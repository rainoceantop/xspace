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
          v-if="requests !== 'yes'"
          :class="['follow', user.followed? 'was-followed':'go-follow']"
          @click="fE(user)"
        >{{ user.followlabel ? user.followlabel : user.followlabel = ( user.followed ? '已关注' : '关注') }}</span>
        <span v-if="requests === 'yes'" class="follow go-follow" @click="fR(user, 'pass')">通过</span>
        <span v-if="requests === 'yes'" class="follow was-followed" @click="fR(user, 'cancel')">取消</span>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  data() {
    return {};
  },
  props: ["users", "requests"],
  methods: {
    fE: function(item) {
      if (this.$store.state.login) {
        if (item.followed) {
          item.followed = false;
          item.followlabel = "关注";

          // 取消关注
          this.$axios
            .get(
              `/api/homespace/userFollow?identity=${
                item.username
              }&fOrUnf=unfollow`
            )
            .then(response => {
              if (response.data.code !== 1) {
                this.followed = true;
                item.followlabel = "已关注";

                alert(response.data.msg);
              }
            });
        } else {
          item.followed = true;
          item.followlabel = "已关注";
          if (item.private) {
            item.followed = false;
            item.followlabel = "请求中";
          }
          // 关注
          this.$axios
            .get(
              `/api/homespace/userFollow?identity=${
                item.username
              }&fOrUnf=follow`
            )
            .then(response => {
              if (response.data.code !== 1) {
                item.followed = false;
                item.followlabel = "关注";

                alert(response.data.msg);
              }
            });
        }
      } else {
        alert("请先登录");
        this.$router.push("/user/login");
      }
    },
    fR: function(item, way) {
      this.$axios
        .get(`/api/homespace/followRequest?uid=${item.username}&way=${way}`)
        .then(response => {
          if (response.data.code === 1) {
            this.$emit(way, item);
          } else {
            alert(response.data.msg);
          }
        });
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
  padding: 10px;
}
.a {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 70%;
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
  width: 30%;
  text-align: end;
  font-size: 13px;
}
</style>
