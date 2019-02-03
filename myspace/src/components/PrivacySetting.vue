<template>
  <div>
    <section class="info-wrap">
      <div class="info-item">
        <h5>账号隐私</h5>
        <div class="info-body">
          <span @click="setPrivate()">
            <font-awesome-icon :icon="privacyIcon"/>&nbsp;
            <label class="info-label">将账号设置为隐私账号</label>
          </span>
          <p class="info-describe">将账号设置为隐私账号后，只有关注你的账号的用户才能访问你的空间。并且之后关注你的用户需要你的同意才能关注，之前的不受影响。</p>
        </div>
      </div>
    </section>

    <!-- <font-awesome-icon :icon="['far', 'square']" size="lg"/>
    <font-awesome-icon :icon="['far', 'check-square']" size="lg"/>-->
  </div>
</template>

<script>
export default {
  name: "PrivacySetting",
  data() {
    return {
      privacy: this.$store.state.private,
      showInfo: false
    };
  },
  methods: {
    setPrivate: function() {
      let operate = this.privacy ? "close" : "open";
      this.$axios
        .get(`/api/homespace/setPrivate?operate=${operate}`)
        .then(response => {
          if (response.data.code === 1) {
            this.privacy = this.privacy ? false : true;
          }
        });
    }
  },
  computed: {
    privacyIcon: function() {
      return ["far", this.privacy ? "check-square" : "square"];
    },
    showInfoIcon: function() {
      return ["far", this.showInfo ? "check-square" : "square"];
    }
  }
};
</script>


<style lang="scss" scoped>
@import "../assets/scss/var";
.info-item {
  padding-bottom: 1.5em;
  h5 {
    font-size: 25px;
    margin: 0;
  }
}
.info-body {
  padding-top: 1em;
  .info-describe {
    color: $gray;
    font-size: 14px;
    padding-top: 0.5em;
  }
  .info-label {
    color: black;
    font-weight: bold;
  }
}
</style>

