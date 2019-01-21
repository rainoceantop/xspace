<template>
  <article id="thumbnails">
    <router-link
      v-for="blog in blogs"
      :key="blog.id"
      :class="['the-thumbnail', $route.params.blogid == blog.id ? 'shadow':'']"
      @click.native="$emit('showLeft')"
      :to="{name: 'blogInfo', params: {id: uid, blogid: blog.id}}"
    >
      <p>{{ blog.title }}</p>
    </router-link>
  </article>
</template>


<script>
export default {
  name: "BlogThumbnail",
  data() {
    return {};
  },
  created() {
    this.$emit("getBlogSet");
  },
  props: {
    blogs: "",
    onfocus: false,
    uid: ""
  },
  watch: {
    uid(n, o) {
      if (n !== undefined) {
        this.$emit("getBlogSet");
      }
    }
  }
};
</script>


<style lang='scss' scoped>
@import "../assets/scss/var";
#thumbnails {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  padding: 10px 0;

  a {
    position: relative;
    text-decoration: none;
    color: rgba($color: #000000, $alpha: 0.7);
  }

  .the-thumbnail {
    width: 100%;
    height: 130px;
    cursor: pointer;

    display: flex;
    justify-content: center;
    align-items: center;

    background-image: url("../assets/images/02.jpg");
    background-position: center;
    background-repeat: no-repeat;

    &:hover {
      box-shadow: inset 0 0 25px $green;
    }

    p {
      text-align: start;
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      font-weight: bold;
      word-wrap: break-word;
      word-break: break-all;
    }
  }
  .shadow {
    box-shadow: inset 0 0 25px $green;
  }
}
</style>
