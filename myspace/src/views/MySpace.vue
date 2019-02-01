<template>
  <div>
    <section :class="['right-panel',open?'':'right-hide']">
      <header>
        <div id="user-detail">
          <div>
            <img class="avatar-bg" :src="avatar">
            <p v-if="isSelf" class="logout" @click="$store.dispatch('logout')">退出登录</p>
          </div>
          <div id="left-detail">
            <p id="nickname">
              <span>{{ nickname }}</span>

              <router-link v-show="isSelf" class="edit-profile" :to="{name: 'profileEdit'}">编辑资料</router-link>
              <span
                v-show="!isSelf"
                :class="['follow', followed? 'was-followed':'go-follow']"
                @click="followEvent"
              >{{ followed ? '已关注' : followlabel }}</span>
            </p>
            <p id="ff">
              <span
                v-if="!isprivate || followed || isSelf"
                class="ff"
                @click="currentThumbnail = 'Follows'"
              >
                <strong>{{ follows }}</strong>&nbsp;关注
              </span>
              <span v-else>
                <strong>{{ follows }}</strong>&nbsp;关注
              </span>
              ·
              <span
                v-if="!isprivate || followed || isSelf"
                class="ff"
                @click="currentThumbnail = 'Fans'"
              >
                <strong>{{ fans }}</strong>&nbsp;粉丝
              </span>
              <span v-else>
                <strong>{{ fans }}</strong>&nbsp;粉丝
              </span>
            </p>
            <p id="bio" v-html="bio"></p>
            <p v-if="website.length > 0" id="website">
              <a :href="website" target="_blank">{{ website }}</a>
            </p>
          </div>
        </div>
      </header>
      <div v-if="!isprivate || followed || isSelf">
        <article id="channel" class="animated fadeIn">
          <div v-if="isSelf" class="new" :style="newopenstyle">
            <div class="new-icon" id="new-button-icon" @click="toggleNew"></div>
            <router-link
              class="new-icon animated fadeIn"
              id="new-photo-icon"
              v-show="newopen"
              @click.native="photoCreate()"
              :to="{name: 'photoCreate', params: {id: undefined}}"
            ></router-link>
            <router-link
              class="new-icon animated fadeIn"
              id="new-blog-icon"
              v-show="newopen"
              @click.native="blogCreate()"
              :to="{name: 'blogCreate', params: {id: undefined}}"
            ></router-link>
          </div>
          <div class="app-icons" id="photo-icon" @click="currentThumbnail = 'PhotoThumbnail'"></div>
          <div class="app-icons" id="blog-icon" @click="currentThumbnail = 'BlogThumbnail'"></div>
        </article>
        <article>
          <keep-alive>
            <component
              v-bind:is="currentThumbnail"
              v-on:showLeft="l_show=true"
              v-on:getBlogSet="getBlogSet()"
              v-on:getPhotoSet="getPhotoSet()"
              :blogs="blogs"
              :photos="photos"
              :uid="cid"
            ></component>
          </keep-alive>
        </article>
      </div>
      <div v-else>
        <h4>该账号为隐私账号</h4>
        <p>关注TA即可了解TA的所有发表</p>
      </div>
    </section>
    <section v-show="l_show" :class="['left-viewer', open?'':'fullscreen']">
      <div class="mobile-close" @click="l_show=false"></div>
      <div class="inner">
        <div :class="[open?'close-icon':'open-icon']" @click="toggle"></div>
      </div>
      <div class="content animated fadeIn">
        <keep-alive>
          <router-view
            name="leftView"
            :biscreate="biscreate"
            :blog="blog"
            v-on:editBlog="editBlog"
            v-on:blogCreateDone="blogCreateDone"
            v-on:blogDeleteDone="blogDeleteDone"
            :piscreate="piscreate"
            :photo="photo"
            v-on:editPhoto="editPhoto"
            v-on:photoCreateDone="photoCreateDone"
            v-on:photoDeleteDone="photoDeleteDone"
            :prev="prevappid"
            :next="nextappid"
            v-on:countPN="countPN"
          ></router-view>
        </keep-alive>
      </div>
    </section>
  </div>
</template>

<script>
import BlogThumbnail from "@/components/BlogThumbnail";
import PhotoThumbnail from "@/components/PhotoThumbnail";
import Fans from "@/components/Fans";
import Follows from "@/components/Follows";
export default {
  name: "MySpace",
  components: {
    BlogThumbnail,
    PhotoThumbnail,
    Fans,
    Follows
  },
  data() {
    return {
      // 用户信息
      cid: "", //当前面板用户id
      nickname: "",
      bio: "",
      website: "",
      avatar: "",
      isprivate: 0,
      follows: 0,
      fans: 0,
      followed: false,
      followlabel: "关注",

      greetings: "",
      open: true,
      newopen: false,
      newopenstyle: "width:60px",
      currentThumbnail: "BlogThumbnail",

      biscreate: true, // 是否创建，否为编辑
      blog: "", // 更新博客需要参数
      blogs: "",

      piscreate: true,
      photo: "",
      photos: "",

      prevappid: "",
      nextappid: "",

      l_show: false
    };
  },

  created() {
    if (this.id !== undefined) {
      this.cid = this.id;
      this.init();
    }
  },
  props: ["id"],
  methods: {
    init: function() {
      this.getUserDetail();
    },
    listenBottom: function(e) {
      console.log("---");
    },
    getUserDetail: function() {
      this.$axios
        .get(
          `http://192.168.1.7:8000/api/homespace/getUserDetail?username=${
            this.id
          }`
        )
        .then(response => {
          if (response.data.code === 1) {
            let data = response.data.msg;
            this.nickname = data.nickname;
            this.avatar = data.avatar;
            this.bio = data.bio;
            this.website = data.website;
            this.isprivate = data.private;
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
          if (!this.isprivate) {
            this.followed = true;
            this.fans++;
            this.followlabel = "已关注";
          } else {
            this.followlabel = "请求中";
          }

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
                this.followlabel = "关注";
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
        .get(`http://192.168.1.7:8000/api/blog/${this.cid}/blogset`)
        .then(response => {
          if (response.data.code === 1) {
            this.blogs = response.data.msg;
          } else {
            this.blogs = [];
          }
        });
    },
    getPhotoSet: function() {
      // 获取图片
      this.$axios
        .get(`http://192.168.1.7:8000/api/photo/${this.cid}/photoset`)
        .then(response => {
          if (response.data.code === 1) {
            this.photos = response.data.msg;
          } else {
            this.photos = [];
          }
        });
    },
    blogCreateDone: function(data) {
      this.currentThumbnail = "BlogThumbnail";
      if (this.biscreate) {
        if (this.blogs) {
          this.blogs.unshift(data);
        }
        this.showBlog(data.id);
      } else {
        this.showBlog(data);
      }
    },
    blogDeleteDone: function(id) {
      for (let i = 0; i < this.blogs.length; i++) {
        if (this.blogs[i].id === id) {
          this.blogs.splice(i, 1);
          break;
        }
      }
      this.showBlog(this.nextappid === "" ? this.prevappid : this.nextappid);
    },
    photoCreateDone: function(data) {
      this.currentThumbnail = "PhotoThumbnail";
      if (this.piscreate) {
        if (this.photos) {
          this.photos.unshift(data);
        }
        this.showPhoto(data.id);
      } else {
        this.showPhoto(data);
      }
    },
    photoDeleteDone: function(id) {
      for (let i = 0; i < this.photos.length; i++) {
        if (this.photos[i].id === id) {
          this.photos.splice(i, 1);
          break;
        }
      }
      this.showPhoto(this.nextappid === "" ? this.prevappid : this.nextappid);
    },
    showBlog: function(id) {
      this.$router.push({
        name: "blogInfo",
        params: { id: undefined, blogid: id }
      });
    },
    showPhoto: function(id) {
      this.$router.push({
        name: "photoInfo",
        params: { id: undefined, photoid: id }
      });
    },
    editBlog: function(blog) {
      this.biscreate = false;
      this.blog = blog;
      this.$router.push({ name: "blogCreate", params: { id: undefined } });
    },
    editPhoto: function(photo) {
      this.piscreate = false;
      this.photo = photo;
      this.$router.push({ name: "photoCreate", params: { id: undefined } });
    },
    photoCreate: function() {
      this.piscreate = true;
      this.photo = "";
      this.l_show = true;
    },
    blogCreate: function() {
      this.biscreate = true;
      this.blog = "";
      this.l_show = true;
    },
    countPN: function(id) {
      let app = this.photos;
      if (this.appid === "blog") app = this.blogs;
      for (let i = 0; i < app.length; i++) {
        if (app[i].id == id) {
          if (app[i - 1] !== undefined) {
            this.prevappid = app[i - 1].id;
          } else {
            this.prevappid = "";
          }
          if (app[i + 1] !== undefined) {
            this.nextappid = app[i + 1].id;
          } else {
            this.nextappid = "";
          }
          break;
        }
      }
    }
  },
  computed: {
    isSelf: function() {
      return this.cid == this.$store.state.id;
    },
    appid: function() {
      return this.currentThumbnail === "PhotoThumbnail" ? "photo" : "blog";
    }
  },
  watch: {
    id(newid, oldid) {
      if (newid !== undefined) {
        if (this.cid != newid) {
          this.cid = newid;
          this.currentThumbnail = "BlogThumbnail";
          this.init();
        }
      }
    }
  }
};
</script>


<style lang="scss" scoped>
@import "../assets/scss/config";
@import "../assets/scss/var";
.right-panel {
  width: 25em;
  height: calc(100% - 60px);
  background: rgba(255, 250, 250, 0.825);
  position: fixed;
  top: $navheight;
  right: 0;
  outline: 0;
  display: block;
  visibility: visible;
  overflow-x: hidden;
  overflow-y: scroll;

  text-align: start;
  z-index: 10;
  padding: 0 0.75em;
  @include easeOut;

  header {
    padding: 0.75em;

    #user-detail {
      display: flex;
      flex-direction: row;
      justify-content: flex-start;
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
          .ff {
            cursor: pointer;
          }
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
      .logout {
        text-align: center;
        cursor: pointer;
        font-size: 13px;
        padding: 3px;
        color: $gray;
        &:hover {
          color: darken($gray, 15);
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
  #photo-icon {
    background-image: url("../assets/images/photo-icon.png");
  }
}

.right-hide {
  visibility: hidden;
  right: -25em;
}
.left-viewer {
  width: calc(100% - 25em);
  height: calc(100% - 64px);
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

    .open-icon,
    .close-icon {
      -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
      position: fixed;
      top: $navheight;
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
  height: calc(100% - 64px);
}
@include mediaSm {
  .right-panel {
    width: 100%;
    top: 56px;
    padding: 0;
    z-index: 1;
    height: calc(100% - 56px);
  }
  .open-icon,
  .close-icon {
    display: none;
  }
  .left-viewer {
    background-color: $main-color;
    position: fixed;
    overflow-y: auto;
    width: 100%;
    height: calc(100% - 56px);
    left: 0;
    top: 56px;
    z-index: 2;
    .mobile-close {
      display: block;
      position: fixed;
      right: 10px;
      top: 66px;
      width: 2.5em;
      height: 2.5em;
      z-index: 3;
      background-image: url("../assets/images/close-small-alt.svg");
      background-position: center;
      background-repeat: no-repeat;
      background-size: contain;
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
</style>
