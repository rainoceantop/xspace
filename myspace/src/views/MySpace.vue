<template>
  <div class="wrap">
    <section :class="['right-panel',open?'':'hide']">
      <header>
        <div id="user-detail">
          <img class="avatar-bg" :src="avatar">
          <div id="left-detail">
            <p id="nickname">
              <span>{{ nickname }}</span>
              <router-link v-show="isSelf" class="edit-profile" :to="{name: 'profileEdit'}">编辑资料</router-link>
              <span
                v-show="!isSelf"
                :class="['follow', followed? 'was-followed':'go-follow']"
                @click="followEvent"
              >{{ followed ? '已关注' : '关注' }}</span>
            </p>
            <p id="ff">
              <strong>{{ follows }}</strong>&nbsp;关注 ·
              <strong>{{ fans }}</strong>&nbsp;粉丝
            </p>
            <p id="bio" v-html="bio"></p>
            <p v-if="website.length > 0" id="website">
              <a :href="website" target="_blank">{{ website }}</a>
            </p>
          </div>
        </div>
      </header>
      <article id="channel" class="animated fadeIn">
        <div v-if="isSelf" class="new" :style="newopenstyle">
          <div class="new-icon" id="new-button-icon" @click="toggleNew"></div>
          <router-link
            class="new-icon animated fadeIn"
            id="new-photo-icon"
            v-show="newopen"
            :to="{name: 'imageCreate'}"
          ></router-link>
          <router-link
            class="new-icon animated fadeIn"
            id="new-blog-icon"
            v-show="newopen"
            @click.native="blogCreate()"
            :to="{name: 'blogCreate'}"
          ></router-link>
        </div>
        <div class="app-icons" id="photo-icon" @click="currentThumbnail = 'ImageThumbnail'"></div>
        <div class="app-icons" id="blog-icon" @click="currentThumbnail = 'BlogThumbnail'"></div>
        <div class="app-icons" id="diary-icon"></div>
        <div class="app-icons" id="photo-icon"></div>
        <div class="app-icons" id="photo-icon"></div>
      </article>
      <keep-alive>
        <component
          v-bind:is="currentThumbnail"
          v-on:showLeft="l_show=true"
          :blogs="blogs"
          :onfocus="blogid"
        ></component>
      </keep-alive>
    </section>
    <section v-show="l_show" :class="['left-viewer', open?'':'fullscreen']">
      <div class="mobile-close">
        <font-awesome-icon @click="l_show=false" :icon="['fas', 'times-circle']" size="2x"></font-awesome-icon>
      </div>
      <div class="inner">
        <router-link class="nav-next" :to="{name: 'blogInfo', params: {blogid: nextblogid}}"></router-link>
        <router-link class="nav-prev" :to="{name: 'blogInfo', params: {blogid: prevblogid}}"></router-link>
        <div :class="[open?'close-icon':'open-icon']" @click="toggle"></div>
      </div>
      <div class="content animated fadeIn">
        <router-view
          name="leftView"
          :iscreate="iscreate"
          :blog="blog"
          v-on:editBlog="editBlog"
          v-on:blogCreateDone="blogCreateDone"
          v-on:blogDeleteDone="blogDeleteDone"
        ></router-view>
      </div>
    </section>
  </div>
</template>

<script>
import BlogThumbnail from "@/components/BlogThumbnail";
import ImageThumbnail from "@/components/ImageThumbnail";
import ImageInfo from "@/components/ImageInfo";
import BlogInfo from "@/components/BlogInfo";
import ImageCreate from "@/components/ImageCreate";
import BlogCreate from "@/components/BlogCreate";

export default {
  name: "MySpace",
  components: {
    BlogThumbnail,
    ImageThumbnail,
    ImageInfo,
    BlogInfo,
    ImageCreate,
    BlogCreate
  },
  data() {
    return {
      // 用户信息
      nickname: "",
      bio: "",
      website: "",
      avatar: "",
      follows: 0,
      fans: 0,
      followed: false,

      greetings: "",
      open: true,
      newopen: false,
      newopenstyle: "width:60px",
      currentThumbnail: BlogThumbnail,

      prevblogid: "nomore",
      iscreate: true, // 是否创建，否为编辑
      blog: "", // 更新博客需要参数
      nextblogid: "nomore",
      blogs: "",

      l_show: true
    };
  },

  created() {
    const d = new Date();
    let h = d.getHours();
    if (h >= 6 && h < 12) this.greetings = "上午好";
    else if (h >= 12 && h < 14) this.greetings = "中午好";
    else if (h >= 14 && h < 19) this.greetings = "下午好";
    else this.greetings = "晚上好";

    this.$store.dispatch("checkLogin");
    this.init();
  },
  props: ["id", "blogid"],
  methods: {
    init() {
      this.getUserDetail();
      // 获取当前的thumbnail
      this.getBlogSet();
    },
    getUserDetail() {
      this.$axios
        .get(
          `http://192.168.1.7:8000/api/homespace/getUserDetail?uid=${this.id}`
        )
        .then(response => {
          if (response.data.code === 1) {
            let data = response.data.msg;
            this.nickname = data.nickname;
            this.avatar = data.avatar;
            this.bio = data.bio;
            this.website = data.website;
            this.follows = data.follows;
            this.fans = data.fans;
            this.followed = data.followed;
          } else {
            alert(response.data.msg);
            this.$router.go(-1);
          }
        });
    },
    followEvent: function() {
      if (this.$store.state.login) {
        if (this.followed) {
          this.followed = false;
          this.fans--;
          // 取消关注
          this.$axios
            .get(
              `http://192.168.1.7:8000/api/homespace/userFollow?identity=${
                this.id
              }&fOrUnf=unfollow`
            )
            .then(response => {
              if (response.data.code !== 1) {
                this.followed = true;
                this.fans++;

                alert(response.data.msg);
              }
            });
        } else {
          this.followed = true;
          this.fans++;

          // 关注
          this.$axios
            .get(
              `http://192.168.1.7:8000/api/homespace/userFollow?identity=${
                this.id
              }&fOrUnf=follow`
            )
            .then(response => {
              if (response.data.code !== 1) {
                this.followed = false;
                this.fans--;

                alert(response.data.msg);
              }
            });
        }
      } else {
        alert("请先登录");
        this.$router.push("/user/login");
      }
    },
    toggle: function() {
      if (this.open) this.open = false;
      else this.open = true;
    },
    toggleNew: function() {
      if (this.newopen) {
        this.newopen = false;
        this.newopenstyle = "width:60px";
      } else {
        this.newopen = true;
        this.newopenstyle = "width:180px";
      }
    },
    togglePanel: function() {
      if (this.panel === "right") this.panel = "left";
      else this.panel = "right";
    },
    getBlogSet: function() {
      // 获取博客
      this.$axios
        .get(`http://192.168.1.7:8000/api/blog/${this.id}/blogset`)
        .then(response => {
          if (response.data.code === 1) {
            this.blogs = response.data.msg;
            if (this.iscreate) {
              if (this.blogs[0].id !== undefined) {
                if (!this.blogid) {
                  this.showBlog(this.blogs[0].id);
                }
                this.countBlogPN(this.blogid);
              }
            }
          } else {
            this.blogs = [];
          }
        });
    },
    blogCreateDone: function(id) {
      this.getBlogSet();
      this.showBlog(id);
    },
    blogDeleteDone: function() {
      this.getBlogSet();
    },
    showBlog: function(id) {
      this.$router.push({ name: "blogInfo", params: { blogid: id } });
    },
    editBlog: function(blog) {
      this.iscreate = false;
      this.blog = blog;
      this.$router.push({ name: "blogCreate" });
    },
    imageCreate: function() {},
    blogCreate: function() {
      this.iscreate = true;
      this.blog = "";
      this.l_show = true;
    },
    countBlogPN: function(id) {
      for (let i = 0; i < this.blogs.length; i++) {
        if (this.blogs[i].id == id) {
          if (this.blogs[i - 1] !== undefined) {
            this.prevblogid = this.blogs[i - 1].id;
          } else {
            this.prevblogid = "nomore";
          }
          if (this.blogs[i + 1] !== undefined) {
            this.nextblogid = this.blogs[i + 1].id;
          } else {
            this.nextblogid = "nomore";
          }
        }
      }
    }
  },
  computed: {
    isSelf: function() {
      return this.id == this.$store.state.id;
    }
  },
  watch: {
    blogid(newid, oldid) {
      this.countBlogPN(newid);
    },
    id(newid, oldid) {
      this.init();
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../assets/scss/config";
@import "../assets/scss/var";
.wrap {
  width: 100%;
  height: 100%;
}
.right-panel {
  width: 25em;
  height: 100%;
  background: rgba(255, 250, 250, 0.825);
  position: fixed;
  top: 0;
  right: 0;
  outline: 0;
  display: block;
  visibility: visible;
  overflow-x: hidden;
  overflow-y: auto;
  text-align: start;
  z-index: 10;
  padding: 0 0.75em;
  @include easeOut;

  header {
    padding: 0.75em;
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

    #user-detail {
      display: flex;
      flex-direction: row;
      justify-content: first baseline;
      align-items: flex-start;
      flex-wrap: nowrap;
      margin-top: 1em;
      #left-detail {
        padding: 0;
        margin-left: 1em;
        #nickname {
          font-size: 22px;
          margin-bottom: 1em;
        }
        #ff {
          font-size: 15px;
          margin-bottom: 1em;
        }
        #bio {
          font-size: 13px;
          margin-bottom: 1em;
        }
        #website {
          width: 90%;
          word-break: break-all;

          a {
            color: $blue;
            text-decoration: none;
          }
        }
      }
      .edit-profile {
        font-size: 15px;
        padding: 3px 8px;
        border-radius: 3px;
        cursor: pointer;
        color: $gray;
        border: 1px $gray solid;
        margin-left: 0.5em;
      }
    }
  }

  #channel {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    align-items: flex-start;
  }

  .app-icons {
    width: 100px;
    height: 100px;
    background-repeat: no-repeat;
    background-size: 80px 80px;
    background-position: center;
    cursor: pointer;
  }

  .new {
    height: 100px;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    .new-icon {
      width: 48px;
      height: 48px;
      background-size: 48px 48px;
      background-position: center;
      background-repeat: no-repeat;
      cursor: pointer;
    }

    #new-button-icon {
      background-image: url("../assets/images/new-icon.png");
    }

    #new-photo-icon {
      background-image: url("../assets/images/new-photo-icon.png");
    }

    #new-blog-icon {
      background-image: url("../assets/images/new-blog-icon.png");
    }
  }

  #blog-icon {
    background-image: url("../assets/images/blog-icon.png");
  }
  #diary-icon {
    background-image: url("../assets/images/diary-icon.png");
  }
  #photo-icon {
    background-image: url("../assets/images/photo-icon.png");
  }
}

.hide {
  visibility: hidden;
  right: -25em;
}
.left-viewer {
  width: calc(100% - 25em - 1.5em);
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  visibility: visible;
  @include easeOut;
  .mobile-close {
    display: none;
  }
  .inner {
    pointer-events: none;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 2;

    * {
      pointer-events: auto;
    }

    .nav-next {
      -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
      position: absolute;
      right: 0;
      top: 50vh;
      width: 6em;
      height: 6em;
      margin-top: -3em;
      background-image: url("../assets/images/arrow.svg");
      background-position: center;
      background-repeat: no-repeat;
      background-size: contain;
      cursor: pointer;
    }

    .nav-prev {
      -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
      position: absolute;
      transform: scaleX(-1);
      left: 0;
      top: 50vh;
      width: 6em;
      height: 6em;
      margin-top: -3em;
      background-image: url("../assets/images/arrow.svg");
      background-position: center;
      background-repeat: no-repeat;
      background-size: contain;
      cursor: pointer;
    }

    .open-icon,
    .close-icon {
      -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
      position: fixed;
      top: 0;
      width: 4em;
      height: 4em;
      background-repeat: no-repeat;
      background-size: 64px 64px;
      cursor: pointer;
      z-index: 1;
      background-position: calc(100% - 0.75em) 0.75em;
      color: $gray;
      @include easeOut;
    }
    .open-icon {
      right: 0;
      background-image: url("../assets/images/open.svg");
    }
    .close-icon {
      right: 26em;
      background-size: 56px 56px;
      background-image: url("../assets/images/close-small-alt.svg");
    }
  }

  .content {
    width: 100%;
    height: 100%;
    @include easeOut;
  }
}

.fullscreen {
  width: 100%;
  height: 100%;
}

.test {
  display: none;
}
@include mediaXS {
  .right-panel {
    width: 100% !important;
    padding: 0;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1;
  }
  .open-icon,
  .close-icon {
    display: none;
  }
  .left-viewer {
    width: 100vw !important;
    min-height: 100%;
    background: rgba($color: #1d1e09, $alpha: 0.95);
    color: whitesmoke;
    padding: 0;
    position: fixed;
    left: 0;
    top: 0;
    z-index: 2;
    .mobile-close {
      margin: 1em;
      display: flex;
      flex-direction: row;
      justify-content: center;
    }
  }
  #channel {
    height: 80px;
    display: -webkit-box !important;
    white-space: nowrap;
    overflow-x: scroll;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
  }

  .app-icons {
    width: 60px;
    height: 60px;
    background-repeat: no-repeat;
    background-size: 50px 50px;
    background-position: center;
  }
}
@include mediaSm {
  .right-panel {
    width: 100% !important;
    padding: 0;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1;
  }
  .open-icon,
  .close-icon {
    display: none;
  }
  .left-viewer {
    width: 100vw !important;
    min-height: 100%;
    background: rgba($color: #1d1e09, $alpha: 0.95);
    color: whitesmoke;
    padding: 0;
    position: absolute;
    left: 0;
    top: 0;
    z-index: 2;
    .mobile-close {
      margin: 1em;
      display: flex;
      flex-direction: row;
      justify-content: center;
    }
  }
  #channel {
    height: 100px;
    display: -webkit-box !important;
    overflow-x: scroll;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
    white-space: nowrap;
  }

  .app-icons {
    width: 80px;
    height: 80px;
    background-repeat: no-repeat;
    background-size: 60px 60px;
    background-position: center;
  }
}

@include mediaMd {
  .right-panel {
    width: 19em;
  }
  .left-viewer {
    width: 100%;
  }
  .close-icon {
    position: absolute;
    left: calc(100% - 19em - 80px) !important;
    top: 0;
    @include easeOut;
  }
  .nav-prev,
  .nav-next {
    display: none;
  }
}
</style>
