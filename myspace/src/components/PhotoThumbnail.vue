<template>
  <article id="thumbnails">
    <router-link
      v-for="photo in photos"
      :key="photo.id"
      :class="['the-thumbnail', $route.params.photoid == photo.id ? 'shadow':'']"
      :style="{'background-image': 'url('+photo.url+')'}"
      tabindex="-1"
      @click.native="$emit('showLeft')"
      :to="{name: 'photoInfo', params: {id: uid, photoid: photo.id}}"
    ></router-link>
  </article>
</template>

<script>
export default {
  data() {
    return {};
  },
  created() {
    this.$emit("getPhotoSet");
  },
  props: {
    photos: "",
    onfocus: false,
    uid: ""
  },
  watch: {
    uid(n, o) {
      if (n !== undefined) {
        this.$emit("getPhotoSet");
      }
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../assets/scss/var";
#thumbnails {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  padding: 10px 0;

  .the-thumbnail {
    width: 100%;
    height: 130px;
    cursor: pointer;

    background-position: center;
    background-repeat: no-repeat;

    &:hover {
      box-shadow: inset 0 0 25px $green;
    }
  }
  .shadow {
    box-shadow: inset 0 0 25px $green;
  }
}
</style>

