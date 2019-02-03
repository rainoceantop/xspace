<template>
  <main id="app">
    <div class="navbar-fixed">
      <nav class="blue darken-4">
        <div class="nav-wrapper container">
          <router-link class="brand-logo" @click.native="hideNotification()" :to="{name: 'home'}">痕迹</router-link>
          <a href="#" data-target="mobile-nav" class="sidenav-trigger">
            <i class="material-icons">menu</i>
          </a>
          <div class="brand-replace hide-on-med-and-down"></div>
          <div class="search-area input-field hide-on-med-and-down">
            <input type="text" v-model="searchText" placeholder="搜索" v-on:input="searchChange()">
            <div class="result-list" v-if="ss">
              <div v-if="searchResults.length > 0">
                <div v-for="result in searchResults" :key="result.id" class="result-item">
                  <router-link
                    v-if="searchType === 'user'"
                    class="result-content"
                    @click.native="hideNotification()"
                    :to="{name: 'myspace', params: {id: result.username}}"
                  >
                    <div class="result-left">
                      <img class="avatar-xs" :src="result.avatar">
                    </div>
                    <div class="result-right">
                      <div class="first-line">{{ result.nickname }}</div>
                      <span class="second-line">{{ result.username }}</span>
                    </div>
                  </router-link>
                  <router-link
                    v-if="searchType === 'tag'"
                    class="result-content"
                    @click.native="hideNotification()"
                    :to="{name: 'tag', params: {tagname: result.name}}"
                  >
                    <div class="result-left">#</div>
                    <div class="result-right">
                      <div class="first-line">{{ result.name }}</div>
                      <span class="second-line">{{ result.post_count }}&nbsp;帖子</span>
                    </div>
                  </router-link>
                </div>
              </div>
              <div class="gray center" v-else>
                <font-awesome-icon v-if="search_loading" :icon="['fas', 'spinner']" spin/>
                <span v-else>找不到结果</span>
              </div>
            </div>
          </div>
          <ul class="hide-on-med-and-down">
            <li>
              <router-link @click.native="hideNotification()" :to="{name: 'home'}">
                <i class="material-icons">explore</i>
              </router-link>
            </li>
            <li v-if="$store.state.login">
              <router-link @click.native="hideNotification()" :to="{name: 'moments'}">
                <i class="material-icons">hdr_weak</i>
              </router-link>
            </li>
            <li v-if="$store.state.login">
              <a v-if="notify_count === 0" href="javascript:void(0)">
                <i class="material-icons" @click="toggleNotification()">notifications_none</i>
              </a>
              <a v-if="notify_count > 0" href="javascript:void(0)">
                <span
                  class="new badge"
                  @click="toggleNotification()"
                >{{ notify_count > 99 ? '99+' : notify_count }}</span>
              </a>
              <section class="notification-display z-depth-3" v-if="sn">
                <header>
                  <span>通知</span>
                  <span class="notification-remove" @click="deleteNotifications()">清空</span>
                </header>

                <ul v-if="notifications.length > 0" class="collection" @click="hideNotification()">
                  <notificationItem
                    v-for="notification in notifications"
                    :key="notification.id"
                    :notification="notification"
                  />
                </ul>
                <div class="gray center" v-else>
                  <font-awesome-icon
                    v-if="notify_loading"
                    :icon="['fas', 'spinner']"
                    spin
                    size="2x"
                  />
                  <span v-else>暂无通知</span>
                </div>
              </section>
            </li>

            <li v-if="$store.state.login">
              <router-link
                @click.native="hideNotification()"
                :to="{name: 'myspace', params: {id: $store.state.id}}"
              >
                <i class="material-icons">account_circle</i>
              </router-link>
            </li>

            <li v-if="!$store.state.login">
              <router-link :to="{name: 'login'}">
                <i class="material-icons">person_outline</i>
              </router-link>
            </li>
          </ul>
        </div>

        <div v-if="sn || ss" class="top-wrap" @click="hideNotification()"></div>
      </nav>
    </div>
    <ul class="sidenav collapsible" id="mobile-nav">
      <li class="search-area input-field">
        <input
          type="text"
          v-model="searchText"
          placeholder="搜索（以#开头搜索标签）"
          v-on:input="searchChange()"
        >
        <div class="result-list" v-if="ss">
          <div v-if="searchResults.length > 0">
            <div v-for="result in searchResults" :key="result.id" class="result-item">
              <router-link
                v-if="searchType === 'user'"
                class="result-content"
                @click.native="hideNotification()"
                :to="{name: 'myspace', params: {id: result.username}}"
              >
                <div class="result-left">
                  <img class="avatar-xs" :src="result.avatar">
                </div>
                <div class="result-right">
                  <div class="first-line">{{ result.nickname }}</div>
                  <span class="second-line">{{ result.username }}</span>
                </div>
              </router-link>
              <router-link
                v-if="searchType === 'tag'"
                class="result-content"
                @click.native="hideNotification()"
                :to="{name: 'tag', params: {tagname: result.name}}"
              >
                <div class="result-left">#</div>
                <div class="result-right">
                  <div class="first-line">{{ result.name }}</div>
                  <span class="second-line">{{ result.post_count }}&nbsp;帖子</span>
                </div>
              </router-link>
            </div>
          </div>
          <div class="gray center" v-else>
            <font-awesome-icon v-if="search_loading" :icon="['fas', 'spinner']" spin/>
            <span v-else>找不到结果</span>
          </div>
        </div>
      </li>
      <li>
        <router-link @click.native="hideNotification()" :to="{name: 'home'}">
          <i class="material-icons">explore</i>首页探索
        </router-link>
      </li>
      <li v-if="$store.state.login">
        <router-link @click.native="hideNotification()" :to="{name: 'moments'}">
          <i class="material-icons">hdr_weak</i>朋友动态
        </router-link>
      </li>
      <li v-if="$store.state.login" @click="toggleNotification()">
        <a class="collapsible-header" href="javascript:void(0)">
          <i class="material-icons">notifications_none</i>消息通知
          <span
            v-if="notify_count > 0"
            class="new badge"
          >{{ notify_count > 99 ? '99+' : notify_count }}</span>
        </a>
        <div class="collapsible-body">
          <header>
            <span class="notification-remove" @click="deleteNotifications()">清空所有通知</span>
          </header>

          <ul v-if="notifications.length > 0" class="collection" @click="hideNotification()">
            <notificationItem
              v-for="notification in notifications"
              :key="notification.id"
              :notification="notification"
              :mobile="true"
            />
          </ul>
          <div class="gray center" v-else>
            <font-awesome-icon v-if="notify_loading" :icon="['fas', 'spinner']" spin size="2x"/>
            <span v-else>暂无通知</span>
          </div>
        </div>
      </li>

      <li v-if="$store.state.login">
        <router-link
          @click.native="hideNotification()"
          :to="{name: 'myspace', params: {id: $store.state.id}}"
        >
          <i class="material-icons">account_circle</i>我的空间
        </router-link>
      </li>
      <li v-if="!$store.state.login">
        <router-link :to="{name: 'login'}">
          <i class="material-icons">person_outline</i>用户登录
        </router-link>
      </li>
    </ul>
    <main id="main">
      <keep-alive>
        <router-view/>
      </keep-alive>
    </main>
    <footer class="container hide-on-med-and-down" id="app-footer">
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
      <div style="margin-right:10px;">&copy; Xspace</div>
    </footer>
  </main>
</template>

<script>
import notificationItem from "./components/sub/notificationItem";
import M from "materialize-css";

document.addEventListener("DOMContentLoaded", function() {
  var sidenav = document.querySelectorAll(".sidenav");
  var sidenavInstances = M.Sidenav.init(sidenav);

  var collapsible = document.querySelectorAll(".collapsible");
  var collapsibleInstances = M.Collapsible.init(collapsible);
});
export default {
  name: "App",
  data() {
    return {
      notify_count: 0,
      sn: false,
      ss: false,
      notify_loading: false,
      search_loading: false,
      searchType: "user",
      notifications: [],
      searchText: "",
      searchResults: [],
      searchCache: {}
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
      if (this.ss) this.ss = false;
    },
    toggleNotification: function() {
      // this.show_notification = this.sn ? false : true;
      if (this.sn) {
        this.sn = false;
      } else {
        this.sn = true;
        this.notify_loading = true;
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
            this.notify_loading = false;
          }
        });
    },
    deleteNotifications: function() {
      if (this.notifications.length > 0) {
        this.$axios
          .get("http://192.168.1.7:8000/api/notification/deleteNotifications")
          .then(response => {
            if (response.data.code === 1) {
              this.notifications = [];
            }
          });
      }
    },
    searchChange: function() {
      this.searchResults = [];
      this.search_loading = true;
      if (this.searchText.length >= 1) {
        this.ss = true;
        let searchText = this.searchText;
        if (this.searchCache[searchText] === undefined) {
          this.searchType = "user";
          let url = `http://192.168.1.7:8000/api/homespace/searchUsers?beginWith=${searchText}`;
          if (searchText[0] === "#") {
            this.searchType = "tag";
            url = `http://192.168.1.7:8000/api/tag/searchTags?beginWith=${searchText.substring(
              1
            )}`;
          }
          if (this.searchType === "user" || searchText.length > 1) {
            this.$axios.get(url).then(response => {
              this.searchResults = response.data.msg;
              this.searchCache[searchText] = response.data.msg;
              this.search_loading = false;
            });
          } else {
            this.search_loading = false;
          }
        } else {
          this.searchResults = this.searchCache[searchText];
          this.search_loading = false;
        }
      } else {
        this.search_loading = false;
        this.ss = false;
      }
    }
  },
  computed: {}
};
</script>



<style lang='scss'>
@import url("https://fonts.googleapis.com/icon?family=Material+Icons");
@import url("https://fonts.googleapis.com/css?family=Noto+Sans+SC");
@import "../node_modules/materialize-css/dist/css/materialize.min.css";
@import "./assets/scss/main";
@import "./assets/scss/var";
@import "./assets/scss/config";
@import "./assets/scss/fonts";
@import "../node_modules/animate.css/animate.min.css";
@import "./assets/scss/photo_info";
@import "./assets/scss/blog_info";

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
input {
  &:focus {
    border-bottom: 1px solid #0d47a1 !important;
  }
}
.follow {
  font-size: 13px;
  padding: 3px 8px;
  border-radius: 3px;
  cursor: pointer;
  color: $main-color;
  font-weight: bold;
  margin-left: 0.5em;
}
.sidenav {
  .collapsible-header {
    height: 48px !important;
    line-height: 48px !important;
    padding: 0 32px !important;
  }
  .collapsible-body {
    header {
      width: 100%;
      padding-left: 1em;
    }
  }
  .collection {
    .collection-item {
      padding: 0;
      a {
        padding: 10px 1em;
        height: auto;
        line-height: normal;
      }
    }
  }
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
  font-family: "Noto Sans SC", roboto, HelveticaNeue, Helvetica, Arial,
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  width: 100%;
}
.progress {
  margin: 0;
}
.nav-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  .brand-replace {
    width: 6em;
  }
}
.search-area {
  position: relative;
  width: 250px;
  height: auto;
  input[type="text"] {
    color: $main-color;
    height: auto;
    padding: 10px 5px;
  }
  .result-list {
    position: absolute;
    left: 0;
    top: 60px;
    width: 280px;
    max-height: 500px;
    overflow-y: scroll;
    background-color: $main-color;
    border: 1px solid $lightgray;
    z-index: 1001;
    .result-item {
      width: 100%;
      padding: 5px 10px;
      line-height: normal;
      .result-content {
        height: 60px;
        display: flex;
        flex-direction: row;
        flex-wrap: nowrap;
        color: black;
        .result-left {
          display: flex;
          align-items: center;
          flex-wrap: nowrap;
          justify-content: center;
          width: 50px;
        }
        .result-right {
          display: flex;
          width: calc(100% - 50px);
          padding: 5px;
          justify-content: flex-start;
          align-items: center;
          flex-wrap: wrap;
          .first-line {
            width: 100%;
          }
          .second-line {
            color: $gray;
          }
        }
      }
    }
  }
}

@include mediaSm {
  .container {
    width: 100% !important;
  }
  .search-area {
    width: 100%;
    input[type="text"] {
      color: black;
      padding: 5px;
    }
    .result-list {
      width: 100%;
      max-height: 400px;
    }
  }
}
.top-wrap {
  position: fixed !important;
  left: 0;
  top: 60px;
  width: 100%;
  height: 100%;
  z-index: 100;
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
  top: 60px;
  display: flex;
  justify-content: flex-start;
  flex-direction: column;
  padding: 0.5em 1em;
  z-index: 1001;

  header {
    width: 100%;
    line-height: 2em;
    display: flex;
    justify-content: space-between;
    color: black;
  }

  .collection {
    overflow-y: auto;
    overflow-x: hidden;
    overflow: -moz-scrollbars-none;

    &::-webkit-scrollbar {
      display: none;
    }
  }
}

#main {
  width: 100%;
  height: calc(100% - 64px);
  min-height: calc(100vh - 60px - 64px);
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

    @include mediaSm {
      .nav-next,
      .nav-prev {
        width: 3em;
        height: 3em;
        position: fixed;
      }
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
  min-height: 400px;
}
</style>
