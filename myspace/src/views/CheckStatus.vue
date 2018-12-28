<template>
  <div>
    <h3>正在跳转...</h3>
  </div>
</template>

<script>
export default {
  created() {
    this.$store.dispatch("checkLoginAndPush");
  }
};
</script>
