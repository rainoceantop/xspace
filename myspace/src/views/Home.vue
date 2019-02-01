<template>
  <div class="container">
    <div v-if="tagname" class="tag-display">
      <span class="tag-hash-style">{{tagname}}</span>
    </div>
    <div class="home-page-wrap">
      <section
        class="explore-item"
        v-for="explore in explores"
        :key="explore.id"
        @mouseover="explore.cover = true"
        @mouseout="explore.cover = false"
        @click="showDetail(explore)"
      >
        <img class="photo-item" v-if="explore.app === 'photo'" :src="explore.url+'-explores'" alt>
        <div v-if="explore.app === 'blog'" class="blog-item">
          <div class="title-background">
            <span>{{ explore.title }}</span>
          </div>
        </div>
        <div v-show="explore.cover" class="cover hide-on-med-and-down">
          <div class="icons-row">
            <div class="likes-area">
              <font-awesome-icon :icon="['fas', 'heart']"></font-awesome-icon>&nbsp;
              <span>{{ explore.likes }}</span>
            </div>&emsp;
            <div class="comments-aera">
              <font-awesome-icon :icon="['fas', 'comment']"></font-awesome-icon>&nbsp;
              <span>{{ explore.replies_count }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
    <div v-if="loading" class="center">
      <font-awesome-icon :icon="['fas', 'spinner']" spin size="3x"/>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeExplores",
  data() {
    return {
      explores: [],
      tags_cached: {},
      page: 0,
      loading: false,
      end: false
    };
  },
  created() {
    this.getExplores(true);
  },
  mounted() {
    document.addEventListener("scroll", this.listenBottom, true);
  },
  props: ["tagname"],
  methods: {
    getExplores: function(fresh) {
      this.loading = true;
      let url = `http://192.168.1.7:8000/api/homespace/getExplores?tag=${
        this.tagname === undefined ? "" : this.tagname
      }&page=${this.page + 1}`;
      this.$axios.get(url).then(response => {
        if (response.data.code === 1) {
          if (response.data.msg.length !== 0) {
            this.page++;
            let items = response.data.msg.sort(this.sortExplores);
            if (!fresh) {
              for (let item of items) {
                item["cover"] = false;
                this.explores.push(item);
              }
              this.loading = false;
            } else {
              for (let item of items) {
                item["cover"] = false;
              }
              this.explores = items;
              this.tags_cached[this.tagname] = items;
              this.tags_cached[this.tagname]["end"] = false;
            }
            this.tags_cached[this.tagname]["page"] = this.page;
            this.loading = false;
          } else {
            this.end = true;
            this.loading = false;
            this.tags_cached[this.tagname]["end"] = true;
          }
        } else alert(response.data.msg);
      });
    },
    showDetail: function(explore) {
      explore.cover = false;
      this.$router.push({
        name: explore.app + "InfoPage",
        params: { photoid: explore.id, blogid: explore.id }
      });
    },
    sortExplores: function(a, b) {
      let t1 = a.timestamp;
      let t2 = b.timestamp;
      if (t1 < t2) {
        return 1;
      } else if (t1 > t2) {
        return -1;
      } else {
        return 0;
      }
    },
    listenBottom: function(e) {
      if (this.$route.path === "/") {
        let scrollT = e.target.documentElement.scrollTop;
        let scrollH = e.target.documentElement.scrollHeight;
        let screenH = e.target.documentElement.clientHeight;
        if (scrollT + screenH + 300 > scrollH) {
          if (this.end === false && this.loading === false) {
            this.loading = true;
            this.getExplores(false);
          }
        }
      }
    }
  },
  watch: {
    tagname(n, o) {
      if (this.tags_cached[n] === undefined) {
        this.end = false;
        this.page = 0;
        this.getExplores(true);
      } else {
        this.end = this.tags_cached[n]["end"];
        this.page = this.tags_cached[n]["page"];
        this.explores = this.tags_cached[n];
      }
    }
  }
};
</script>


<style lang="scss" scoped>
@import "../assets/scss/config";
@import "../assets/scss/var";

.tag-display {
  padding: 2em 5em 0 5em;
  .tag-hash-style {
    font-size: 25px;
  }
}

.home-page-wrap {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  padding: 2em 5em;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-gap: 30px;

  .explore-item {
    width: 100%;
    padding-top: 100%;
    position: relative;
    cursor: pointer;

    .photo-item {
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;
    }

    .blog-item {
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      background-image: url("../assets/images/blog.jpg");
      background-repeat: no-repeat;
      background-size: cover;
      background-position: center;
      position: absolute;
      top: 0;
      left: 0;

      .title-background {
        width: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        box-shadow: inset 0 0 25px black;
        height: 50%;
        padding: 0.5em;
        display: flex;
        justify-content: center;
        align-items: center;
        span {
          color: $main-color;
          width: 90%;
          text-align: center;
          overflow: hidden;
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          font-weight: bold;
          word-wrap: break-word;
          word-break: break-all;
        }
      }
    }
  }
}
.cover {
  position: absolute;
  top: 0;
  right: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: center;
  align-items: center;

  .icons-row {
    width: 100%;
    display: flex;
    justify-content: center;
    flex-direction: row;
    flex-wrap: wrap;
    color: $main-color;
    font-size: 20px;
  }
}
@include mediaLg {
  .tag-display {
    padding: 25px 0 0 0;
  }
  .home-page-wrap {
    padding: 25px 0 0 0;
    grid-gap: 20px;
  }
}

@include mediaMd {
  .tag-display {
    padding: 20px 0 0 0;
  }
  .home-page-wrap {
    padding: 20px 0 0 0;
    grid-gap: 15px;
  }
}
@include mediaSm {
  .tag-display {
    padding: 15px 0 0 0;
  }
  .home-page-wrap {
    padding: 15px 0 0 0;
    grid-gap: 10px;
  }
}
@include mediaXS {
  .tag-display {
    padding: 10px 0 0 0;
  }
  .home-page-wrap {
    padding: 10px 0 0 0;
    grid-gap: 2px;
  }
}
</style>
