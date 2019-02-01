<template>
  <li class="collection-item avatar">
    <router-link :to="{name: 'myspace', params: {id: notification.from_user_id}}">
      <img
        :class="['circle', notification.viewed ? '' : 'z-depth-3']"
        :src="notification.from_user_avatar"
        alt
      >
    </router-link>
    <router-link
      :to="{name: getApp(notification), params: {photoid: getId(notification), blogid: getId(notification)}}"
    >
      <span class="title">{{ notification.body }}</span>
      <p class="time">{{ notification.created_at }}</p>
    </router-link>
  </li>
</template>
<script>
export default {
  name: "notificationItem",
  props: {
    notification: Object
  },
  methods: {
    getApp: function(notification) {
      if (notification.app.split(":")[0] === "photo") return "photoInfoPage";
      if (notification.app.split(":")[0] === "blog") return "blogInfoPage";
      return "photoInfo";
    },
    getId: function(notification) {
      return notification.app.split(":")[1];
    }
  }
};
</script>
<style lang="scss" scoped>
@import "../../assets/scss/var";
a {
  color: black;
}
.collection-item {
  width: 100%;
}
.time {
  margin-top: 0.5em;
  color: $gray;
}
</style>
