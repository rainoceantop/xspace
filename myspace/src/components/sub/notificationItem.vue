<template>
  <div class="notification-item-wrap">
    <router-link :to="{name: 'myspace', params: {id: notification.from_user_id}}">
      <img
        :class="['avatar-sm', notification.viewed ? '' : 'shadow-around']"
        :src="notification.from_user_avatar"
        alt
      >
    </router-link>
    <router-link
      :to="{name: getApp(notification), params: {photoid: getId(notification), blogid: getId(notification)}}"
    >
      <div class="notification-content">
        <p>{{ notification.body }}</p>
        <span class="time">{{ notification.created_at }}</span>
      </div>
    </router-link>
  </div>
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
.notification-item-wrap {
  width: 100%;
  padding: 1em;
  display: grid;
  grid-template-columns: 60px calc(100% - 4em);

  .notification-content {
    width: 100%;
    p {
      padding-bottom: 0.5em;
    }
    .time {
      margin-top: 0.5em;
      color: $gray;
    }
  }
  &:hover {
    cursor: pointer;
    background-color: $lightgray;
  }
  .shadow-around {
    box-shadow: 0 0 15px $blue;
  }
  a {
    color: black;
    font-size: 15px;
    font-weight: normal;
  }
}
</style>
