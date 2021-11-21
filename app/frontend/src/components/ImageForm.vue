<template>
  <v-container>
    <h1>PyCanny</h1> 
    <div v-if="load">
      <v-progress-circular
        :size="200"
        :width="7"
        :font-size="60"
        color="#651FFF"
        indeterminate>
      loading..
      </v-progress-circular>
    </div>
    <v-layout row wrap v-if="!load">
      <v-flex xs4 class="py-2">
        <h3 v-if="!imageUrl">
            {{ headers.uploadHeader }}
        </h3>
        <h3 v-if="imageUrl">
            {{ headers.resultHeader }}
        </h3>
        <v-form
        ref="form"
        class="image-form"
        lazy-validation>
          <div v-if="!imageUrl">
            <v-text-field
              label="Select Image"
              @click="pickFile"
              filled
              light
              v-model="imageName"
              ></v-text-field>
            <input
              type="file"
              style="display: none"
              ref="image"
              accept="image/*"
              @change="onFilePicked">
            <v-btn
              @click="sendImage"
              large
              color="#651FFF">
              SEND
            </v-btn>
          </div>
          <div class="image-container" v-if="imageUrl">
            <img :src=imageUrl width="600"/>
            <v-btn
              @click="clearImage"
              large
              color="#651FFF">
              Cancel
            </v-btn>
          </div>
        </v-form>
        <br><br>
        <div v-if="!imageUrl && images.length > 0">
          <h3>
            {{ headers.gallery }}
          </h3>
          <p>click for large view</p>
          <div 
            v-for="img in images" 
            :key="img">
            <img  
              :src=img 
              @click="imageUrl = img"
              height="100px"/>
            <br> 
          </div>
        </div>
      </v-flex>
    </v-layout>
  </v-container>
</template>
<script>
import FormData from 'form-data'
export default {
  data() {
    return {
      headers: {
        uploadHeader: 'Upload picture',
        resultHeader: 'Result',
        gallery: 'Gallery'
      },
      imageName: '',
      imageUrl: '',
      image: '',
      images: [],
      apiUrl: process.env.VUE_APP_API_URL,
      apiPort: process.env.VUE_APP_API_PORT,
      dataPort: '5000',
      load: false,
    };
  },
  created() {
    this.fetchImages()
  }, 
  methods: {
    pickFile() {
      this.$refs.image.click();
    },
    onFilePicked(e) {
      const files = e.target.files;
      if (files[0] !== undefined) {
        this.imageName = files[0].name;
        if (this.imageName.lastIndexOf('.') <= 0) {
          return;
        }
        this.image = files[0]; 
      } else {
        this.imageName = '';
        this.image = '';
        this.imageUrl = '';
      }
    },
    clearImage() {
      this.imageName = '';
      this.imageUrl = '';
      this.image = '';
    },
    checkExistence(element, array) {
      return array.includes(element);
    },
    sendImage() {
      let data = new FormData();
      data.append('file', this.image, 'image.jpg');
      this.load = true;
      var request = new XMLHttpRequest();
      request.open('POST', `${this.apiUrl}${this.apiPort}`);
      request.send(data);
      var self = this; 
      request.onreadystatechange = function() {
        if (request.status >= 200 && request.status < 300) {
          self.imageUrl = `${self.apiUrl}${self.dataPort}/static/${request.responseText}`
          self.load = false;
          self.fetchImages();
        } else {
          console.warn('Error');
        }
      };
    },
    fetchImages() {
      var request = new XMLHttpRequest();
      var self = this;
      request.open('GET',`${this.apiUrl}${this.dataPort}/fetch`);
      request.send();
      request.onreadystatechange = function() {
        if (request.status >= 200 && request.status < 300) {
          var image_list = [];
          let test
          try {
            test = JSON.parse(request.responseText);
          } catch (e) {
            //pass
          }
          for (let i in test) {
            image_list.push(`${self.apiUrl}${self.dataPort}/static/${test[i]}`);
          }
          self.images = image_list;
        } else {
          console.warn(request.statusText, request.responseText);
        }
      };
    }     

  }
};
</script>