<template>
  <main id="app">
    <nav>
      <ul class="container">
        <li>
          <router-link @click.native="hideNotification()" :to="{name: 'home'}">
            <img src="./assets/images/explore.png">
          </router-link>
        </li>
        <li v-if="$store.state.login">
          <router-link @click.native="hideNotification()" :to="{name: 'moments'}">
            <img src="./assets/images/circle.png">
          </router-link>
        </li>
        <li class="notification-area" v-if="$store.state.login">
          <img
            class="notification-icon"
            src="./assets/images/bell.png"
            @click="toggleNotification()"
          >
          <div
            class="notify-count-display"
            v-if="notify_count"
            @click="toggleNotification"
          >{{ notify_count > 99 ? '99+' : notify_count }}</div>
          <div v-if="sn" class="notification-wrap" @click="hideNotification"></div>
          <transition enter-active-class="pulse" leave-active-class="zoomOut">
            <section class="notification-display animated" v-if="sn">
              <header>
                <span>通知</span>
                <span class="notification-remove" @click="deleteNotifications()">清空</span>
              </header>

              <div v-if="notifications" @click="hideNotification()">
                <notificationItem
                  v-for="notification in notifications"
                  :key="notification.id"
                  :notification="notification"
                />
              </div>
              <div class="notice">
                <span v-if="loading">
                  <font-awesome-icon :icon="['fas', 'spinner']" size="2x" spin></font-awesome-icon>
                </span>
                <p v-if="loading === false && notifications.length === 0">暂无通知</p>
              </div>
            </section>
          </transition>
        </li>
        <li v-if="$store.state.login">
          <router-link
            @click.native="hideNotification()"
            :to="{name: 'myspace', params: {id: $store.state.id}}"
          >
            <img src="./assets/images/user.png">
          </router-link>
        </li>
        <li v-if="!$store.state.login">
          <router-link :to="{name: 'login'}">登录</router-link>
        </li>
        <li v-if="!$store.state.login">
          <router-link :to="{name: 'register'}">注册</router-link>
        </li>
      </ul>
    </nav>
    <div id="nav-replace"></div>
    <main id="main">
      <keep-alive>
        <router-view/>
      </keep-alive>
    </main>
    <footer class="container" id="app-footer">
      <div id="footer-nav">
        <ul class="footer-list">
          <li>
            <a href="/">关于</a>
          </li>
          <li>
            <a href="/">支持</a>
          </li>
          <li>
            <a href="/">联系</a>
          </li>
        </ul>
      </div>
      <div>&copy; Xspace</div>
    </footer>
  </main>
</template>

<script>
import notificationItem from "./components/sub/notificationItem";
export default {
  name: "App",
  data() {
    return {
      notify_count: 0,
      sn: false,
      loading: true,
      notifications: []
    };
  },
  components: {
    notificationItem
  },
  created() {
    this.$store.dispatch("checkLogin");
  },
  mounted() {
    this.getNotifyCount();
  },
  methods: {
    getNotifyCount: function() {
      this.$axios
        .get("http://192.168.1.7:8000/api/notification/getNotifyCount")
        .then(response => {
          if (response.data.code === 1) {
            this.notify_count = response.data.msg;
          }
        });
    },
    hideNotification: function() {
      if (this.sn) this.sn = false;
    },
    toggleNotification: function() {
      // this.show_notification = this.sn ? false : true;
      if (this.sn) {
        this.sn = false;
      } else {
        this.sn = true;
        this.loading = true;
        this.getNotifications();
      }
    },
    getNotifications: function() {
      this.$axios
        .get("http://192.168.1.7:8000/api/notification/getNotifications")
        .then(response => {
          if (response.data.code === 1) {
            this.notifications = response.data.msg;
            this.notify_count = 0;
            this.loading = false;
          }
        });
    },
    deleteNotifications: function() {
      this.$axios
        .get("http://192.168.1.7:8000/api/notification/deleteNotifications")
        .then(response => {
          if (response.data.code === 1) {
            this.notifications = [];
          }
        });
    }
  },
  computed: {}
};
</script>



<style lang='scss'>
@import "./assets/scss/main";
@import "./assets/scss/var";
@import "../node_modules/animate.css/animate.min.css";

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.follow {
  font-size: 15px;
  padding: 3px 8px;
  border-radius: 3px;
  cursor: pointer;
  color: $main-color;
  font-weight: bold;
  margin-left: 0.5em;
}
.go-follow {
  background-color: $blue;
}
.was-followed {
  background-color: $gray;
}
body {
  background-color: $main-color;
}
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  width: 100%;
}
.notice {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
nav {
  width: 100%;
  height: 60px;
  background: $main-color;

  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  ul {
    height: 100%;
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    align-items: center;
    list-style: none;
    li {
      width: 50px;
      position: relative;
      display: flex;
      justify-content: flex-end;
    }
    .notification-icon {
      cursor: pointer;
    }
    .notification-wrap {
      position: fixed;
      left: 0;
      top: 40px;
      width: 100%;
      height: 100%;
      z-index: 100;
    }
    .notify-count-display {
      width: 24px;
      height: 24px;
      background-color: red;
      color: $main-color;
      font-size: 13px;
      font-weight: bold;
      position: absolute;
      right: -5px;
      top: -5px;
      border-radius: 12px;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
    }
    .notification-remove {
      cursor: pointer;
      &:hover {
        font-weight: bold;
      }
    }

    .notification-display {
      width: 450px;
      height: 600px;
      background-color: $main-color;
      position: absolute;
      top: 40px;
      box-shadow: 3px 3px 20px rgba(0, 0, 0, 0.3);
      display: flex;
      justify-content: flex-start;
      flex-direction: column;
      padding: 0.5em 1em;
      z-index: 1001;
      overflow-y: auto;
      &::-webkit-scrollbar {
        display: none;
      }

      header {
        display: flex;
        justify-content: space-between;
        padding-bottom: 1.5em;
      }
    }
  }

  a {
    font-weight: bold;
    color: #2c3e50;
    text-decoration: none;
  }

  a.router-link-exact-active {
    color: #42b983;
  }
}
#nav-replace {
  display: block;
  width: 100%;
  height: 60px;
}
#main {
  width: 100%;
  height: calc(100% - 60px);
  min-height: calc(100vh - 60px - 60px);
  .like-icon {
    cursor: pointer;
  }
  .like-count {
    margin-left: 7px;
  }

  .inner {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 2;
    pointer-events: none;

    * {
      pointer-events: auto;
    }

    .nav-next,
    .nav-prev {
      -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
      position: absolute;
      top: calc((100vh - 60px) / 2);
      width: 6em;
      height: 6em;
      margin-top: -3em;
      background-position: center;
      background-repeat: no-repeat;
      background-size: contain;
      cursor: pointer;
    }

    .nav-next {
      right: 0;
      background-image: url("./assets/images/arrow.svg");
    }

    .nav-prev {
      transform: scaleX(-1);
      left: 0;
      background-image: url("./assets/images/arrow.svg");
    }
  }
}

#app-footer {
  width: 100%;
  height: 60px;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  color: $gray;
  font-size: 13px;

  #footer-nav {
    .footer-list {
      list-style: none;
      li {
        display: inline-block;
        padding: 5px 10px;

        a {
          text-decoration: none;
          color: $blue;
        }
      }
    }
  }
}

figure img {
  max-width: 100%;
}
.image {
  position: relative;
  overflow: hidden;
  clear: both;
  text-align: center;
  margin: 1em 0;
}
.image > figcaption {
  color: #333;
  background-color: #f7f7f7;
  padding: 0.6em;
  font-size: 0.75em;
  outline-offset: -1px;
}
.image-style-side {
  float: right;
  margin-left: 1.5em;
  max-width: 50%;
}
.ck-editor {
  width: 100% !important;
}
.ck-content {
  min-height: 550px;
}

blockquote {
  overflow: hidden;
  padding-right: 1.5em;
  padding-left: 1.5em;
  margin-left: 0;
  font-style: italic;
  border-left: 5px solid #ccc;
}
</style>

<script>
import notificationItem from "./components/sub/notificationItem";
export default {
  name: "App",
  data() {
    return {
      notify_count: 0,
      sn: false,
      loading: true,
      notifications: []
    };
  },
  components: {
    notificationItem
  },
  created() {
    this.$store.dispatch("checkLogin");
  },
  mounted() {
    this.getNotifyCount();
  },
  methods: {
    getNotifyCount: function() {
      this.$axios
        .get("http://192.168.1.7:8000/api/notification/getNotifyCount")
        .then(response => {
          if (response.data.code === 1) {
            this.notify_count = response.data.msg;
          }
        });
    },
    hideNotification: function() {
      if (this.sn) this.sn = false;
    },
    toggleNotification: function() {
      // this.show_notification = this.sn ? false : true;
      if (this.sn) {
        this.sn = false;
      } else {
        this.sn = true;
        this.loading = true;
        this.getNotifications();
      }
    },
    getNotifications: function() {
      this.$axios
        .get("http://192.168.1.7:8000/api/notification/getNotifications")
        .then(response => {
          if (response.data.code === 1) {
            this.notifications = response.data.msg;
            this.notify_count = 0;
            this.loading = false;
          }
        });
    },
    deleteNotifications: function() {
      this.$axios
        .get("http://192.168.1.7:8000/api/notification/deleteNotifications")
        .then(response => {
          if (response.data.code === 1) {
            this.notifications = [];
          }
        });
    }
  },
  computed: {}
};
</script>

