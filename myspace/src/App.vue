<template>
  <main id="app">
    <router-view/>
  </main>
</template>


<style lang='scss'>
@import "./assets/scss/main";
@import "./assets/scss/var";
@import "../node_modules/animate.css/animate.min.css";

* {
  margin: 0;
  padding: 0;
}
body {
  background-color: $main-color;
}
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
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
export default {};
</script>

