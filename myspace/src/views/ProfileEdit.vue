<template>
  <main class="container profile-edit-wrap">
    <section class="profile-edit-area">
      <ul>
        <li>
          <router-link :to="{name: 'profileEdit'}">基本资料</router-link>
        </li>
        <li>
          <router-link :to="{name: 'avatarChange'}">更换头像</router-link>
        </li>
        <li>
          <router-link :to="{name: 'passwordChange'}">修改密码</router-link>
        </li>
      </ul>
      <keep-alive>
        <router-view class="edit-view" name="editView"></router-view>
      </keep-alive>
    </section>
  </main>
</template>

<style lang="scss" scoped>
@import "../assets/scss/var";
.profile-edit-wrap {
  padding: 50px;
  display: flex;
  flex-direction: row;
  justify-content: center;

  .profile-edit-area {
    width: 80%;
    border: 1px lightgray solid;
    min-height: 500px;
    display: flex;
    flex-direction: row;

    ul {
      width: 25%;
      height: 100%;
      border-right: 1px lightgray solid;
      list-style: none;
      li {
        display: list-item;
        padding: 25px 25px 0 25px;
        cursor: pointer;
        a {
          text-decoration: none;
          color: rgba($color: #000000, $alpha: 0.7);
          line-height: 20px;
        }

        a.router-link-exact-active {
          font-weight: bold;
          text-decoration: underline;
        }
      }
    }
    .edit-view {
      width: 75%;
      height: 100%;
      padding: 2em;
    }
  }
}
</style>

