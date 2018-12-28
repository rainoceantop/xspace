<template>
  <div class="info">
    <div class="image"></div>
    <div class="caption">
      <p>晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多晚上好，卡西莫多</p>
    </div>
  </div>
</template>


<style lang="scss" scoped>
@import "../assets/scss/config";
.info {
  width: 100%;
  height: 100%;
  .image {
    width: 100%;
    height: 100%;
    background-image: url("../assets/images/sunset.jpg");
    background-size: cover;
    background-position: left center;
    @include easeOut;
  }
  .caption {
    background-image: -webkit-linear-gradient(
      bottom,
      rgba(16, 16, 16, 0.75),
      rgba(16, 16, 16, 0.25) 80%,
      rgba(16, 16, 16, 0)
    );
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    p {
      color: rgba(255, 255, 255, 0.5);
      z-index: 1;
      padding: 2em;
    }
  }
}
</style>
