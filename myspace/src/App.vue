<template>
  <main id="app">
    <nav>
      <ul class="container">
        <router-link :to="{name: 'home'}">
          <img src="./assets/images/explore.png">
        </router-link>
        <router-link v-if="$store.state.login" :to="{name: 'moments'}">
          <img src="./assets/images/circle.png">
        </router-link>
        <router-link
          v-if="$store.state.login"
          :to="{name: 'myspace', params: {id: $store.state.id}}"
        >
          <img src="./assets/images/user.png">
        </router-link>
        <router-link v-if="!$store.state.login" :to="{name: 'login'}">登录</router-link>
        <router-link v-if="!$store.state.login" :to="{name: 'register'}">注册</router-link>
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
export default {
  created() {
    this.$store.dispatch("checkLogin");
  }
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
nav {
  width: 100%;
  height: 60px;
  border-bottom: 1px solid lightgray;
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
  }

  a {
    font-weight: bold;
    color: #2c3e50;
    margin-left: 1em;
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
export default {
  created() {
    this.$store.dispatch("checkLogin");
  }
};
</script>

