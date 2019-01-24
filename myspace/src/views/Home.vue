<template>
  <div class="container">
    <div class="home-page-wrap">
      <section
        class="explore-item"
        v-for="explore in explores"
        :key="explore.id"
        @mouseover="explore.cover = true"
        @mouseout="explore.cover = false"
      >
        <img class="photo-item" v-if="explore.app === 'photo'" :src="explore.url+'-explores'" alt>
        <div v-if="explore.app === 'blog'" class="blog-item">
          <p>{{ explore.title }}</p>
        </div>
        <div v-show="explore.cover" class="cover" @click="showDetail(explore)">
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
  </div>
</template>

<script>
export default {
  name: "HomeExplores",
  data() {
    return {
      explores: []
    };
  },
  created() {
    this.getExplores();
  },
  methods: {
    getExplores: function() {
      this.$axios
        .get("http://192.168.1.7:8000/api/homespace/getExplores")
        .then(response => {
          if (response.data.code === 1) {
            let items = response.data.msg;
            for (let i = 0; i < items.length; i++) {
              items[i]["cover"] = false;
            }
            this.explores = items.sort(this.sortExplores);
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
    }
  }
};
</script>


<style lang="scss" scoped>
@import "../assets/scss/var";

.container {
  width: 100%;
  display: flex;
  justify-content: center;
}
.home-page-wrap {
  width: 100%;
  padding: 2em 5em;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-gap: 30px;

  .explore-item {
    width: 300px;
    height: 300px;
    position: relative;
    cursor: pointer;

    .blog-item {
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      background-image: url("../assets/images/02.jpg");
      background-repeat: no-repeat;
      background-size: cover;
      background-position: center;

      p {
        width: 80%;
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
</style>
