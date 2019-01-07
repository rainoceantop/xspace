<template>
  <div class="info">
    <div class="photo-view">
      <img
        oncontextmenu="return false"
        ondragstart="return false"
        v-show="photo"
        class="the-photo animated fadeIn"
        :src="photo.url"
        alt
      >
    </div>

    <div v-show="photo" class="caption animated fadeIn">
      <h3 v-if="photo.title">{{ photo.title }}</h3>
      <p>{{ photo.caption }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      photo: ""
    };
  },
  created() {
    this.getPhoto(this.photoid);
  },
  props: ["photoid"],
  methods: {
    getPhoto: function(id) {
      if (id !== undefined) {
        this.photo = "";
        this.$axios
          .get(`http://192.168.1.7:8000/api/photo/${id}`)
          .then(response => {
            if (response.data.code === 1) {
              this.photo = response.data.msg;
            } else {
              alert(response.data.msg);
            }
          });
      }
    }
  }
};
</script>



<style lang="scss" scoped>
@import "../assets/scss/var";
@import "../assets/scss/config";
.info {
  width: 100%;
  height: calc(100vh - 60px);
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  @include easeOut;
  .photo,
  .photo-view {
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.8);
    @include easeOut;
  }
  .photo {
    background-size: cover;
    background-position: left center;
  }
  .photo-view {
    display: flex;
    justify-content: center;
    align-items: center;
  }
}
.the-photo {
  max-width: 100%;
  max-height: 100%;
}
.caption {
  background-image: -webkit-linear-gradient(
    bottom,
    rgba(16, 16, 16, 0.75),
    rgba(16, 16, 16, 0.25) 80%,
    rgba(16, 16, 16, 0)
  );
  -moz-box-sizing: border-box;
  -webkit-box-sizing: border-box;
  -o-box-sizing: border-box;
  -ms-box-sizing: border-box;
  box-sizing: border-box;
  width: inherit;
  position: absolute;
  bottom: 0;
  left: 0;
  padding: 2em;
  h3,
  p {
    color: $main-color;
    z-index: 1;
  }
  h3 {
    padding-bottom: 15px;
  }
}
</style>
