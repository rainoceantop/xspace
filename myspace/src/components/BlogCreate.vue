<template>
  <div class="container">
    <div class="blog-create-wrap">
      <header class="title-area">
        <label for="title">标题</label>
        <input v-model="title" type="text" name="title" id="title">
      </header>
      <section class="body-area">
        <label for="body">内容</label>
        <ckeditor :editor="editor" :config="editorConfig" v-model="editorData"></ckeditor>
      </section>
      <section class="tag-area">
        <label for="tag">标签</label>
        <input
          v-model="tag"
          type="text"
          name="tag"
          id="tag"
          placeholder="按回车键添加标签"
          @keyup.enter="addTag(tag)"
        >
      </section>
      <ul class="tag-display">
        <li
          v-for="tag in tags"
          :key="tag"
          class="tag-style"
          :title="'点击移除标签：'+tag"
          @click="removeTag(tag)"
        >{{ tag }}</li>
      </ul>
      <footer class="buttons-area">
        <input class="button-style" type="button" @click="submit" value="提交">
      </footer>
    </div>
  </div>
</template>

<script>
import CKFinder from "@ckeditor/ckeditor5-ckfinder/src/ckfinder";
import ClassicEditor from "@ckeditor/ckeditor5-build-classic";
import "@ckeditor/ckeditor5-build-classic/build/translations/zh-cn";
import CKEditor from "@ckeditor/ckeditor5-vue";

export default {
  name: "BlogCreate",
  data: function() {
    return {
      prevUrl: "",
      title: "",
      editorData: "",
      tags: [],
      tag: "",
      editor: ClassicEditor,
      editorConfig: {
        toolbar: [
          "heading",
          "bold",
          "italic",
          "NumberedList",
          "BulletedList",
          "blockQuote",
          "|",
          "link",
          "insertTable",
          "|",
          "imageUpload",
          "imageTextAlternative",
          "imageStyle:full",
          "imageStyle:side"
        ],
        // plugins: [CKFinder],
        language: "zh-cn",
        ckfinder: {
          uploadUrl:
            "/api/blog/fileupload?command=QuickUpload&type=Files&responseType=json"
        }
      }
    };
  },
  props: {
    blog: "",
    biscreate: true
  },
  components: {
    ckeditor: CKEditor.component
  },
  methods: {
    submit: function() {
      if (this.title.length < 1 || this.title.length > 100)
        alert("标题过长或过短");
      else if (this.editorData.length < 100) alert("内容至少一百字以上");
      else if (this.tags.length === 0) alert("请至少添加一个标签");
      else {
        let url = "/api/blog/store";
        if (!this.biscreate) {
          url = `/api/blog/${this.blog.id}/update`;
        }
        this.$axios({
          url: url,
          method: "POST",
          data: { title: this.title, body: this.editorData, tags: this.tags },
          headers: {
            "Content-type": "application/json"
          }
        }).then(response => {
          if (response.data.code === 1) {
            this.initData();
            this.$emit("blogCreateDone", response.data.msg);
          } else alert(response.data.msg);
        });
      }
    },
    initData: function() {
      this.title = "";
      this.editorData = "";
      this.tags = [];
      if (!this.biscreate) {
        setTimeout(this.updateData, 1);
      }
    },
    updateData: function() {
      this.title = this.blog.title;
      this.editorData = this.blog.body;
      this.tags = this.blog.tags;
    },
    addTag: function(tag) {
      this.tag = "";
      tag = tag.replace(/[\s#]+/g, "");
      if (tag) this.tags.push(tag);
    },
    removeTag: function(tag) {
      for (let i = 0; i < this.tags.length; i++) {
        if (this.tags[i] === tag) {
          this.tags.splice(i, 1);
          break;
        }
      }
    }
  },
  mounted: function() {
    this.initData();
  },
  watch: {
    blog: function(newblog, oldblog) {
      this.initData();
    }
  }
};
</script>
<style lang="scss" scoped>
@import "../assets/scss/var";
@import "../assets/scss/config";
.container {
  width: 100%;
  display: flex;
  justify-content: center;
}
.blog-create-wrap {
  width: 70%;
  padding: 2em 5em;
  // background-color: yellowgreen;
  text-align: start;
  margin-top: 3em;

  margin-bottom: 100px;
  border: 1px $gray solid;
  box-shadow: 5px 8px 15px rgba(0, 0, 0, 0.3);

  .title-area,
  .body-area,
  .tag-area {
    width: 100%;
    margin-bottom: 25px;
  }
  .buttons-area {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  #title,
  #tag {
    display: block;
    padding: 2px 10px;
    width: 100%;
    height: 25px;
  }

  #body {
    width: 100%;
  }
}

@include mediaSm {
  .blog-create-wrap {
    width: 100%;
    padding: 1em 0.5em 0 0.5em;
    border: none;
    box-shadow: none;
    margin-top: 0;
  }
}
</style>

