<template>
  <li :class="['collection-item', mobile ? '' : 'avatar']">
    <router-link v-if="!mobile" :to="{name: 'myspace', params: {id: notification.from_user_id}}">
      <img
        :class="['circle', notification.viewed ? '' : 'z-depth-3']"
        :src="notification.from_user_avatar"
        alt
      >
    </router-link>
    <router-link
      v-if="notification.app.split(':')[0] === 'photo'"
      :to="{name: 'photoInfoPage', params: {photoid: getId(notification)}}"
    >
      <span :class="[mobile ? '' : 'title']">{{ notification.body }}</span>
      <p class="time">{{ notification.created_at }}</p>
    </router-link>
    <router-link
      v-if="notification.app.split(':')[0] ===  'blog'"
      :to="{name: 'blogInfoPage', params: {blogid: getId(notification)}}"
    >
      <span :class="[mobile ? '' : 'title']">{{ notification.body }}</span>
      <p class="time">{{ notification.created_at }}</p>
    </router-link>
    <router-link
      v-if="notification.app.split(':')[0] ===  'user'"
      :to="{name: 'myspace', params: {id: getId(notification)}}"
    >
      <span :class="[mobile ? '' : 'title']">{{ notification.body }}</span>
      <p class="time">{{ notification.created_at }}</p>
    </router-link>
  </li>
</template>
<script>
export default {
  name: "notificationItem",
  props: {
    notification: Object,
    mobile: false
  },
  methods: {
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

.time {
  margin-top: 0.5em;
  color: $gray;
}
</style>
