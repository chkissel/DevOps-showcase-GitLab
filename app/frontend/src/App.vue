<template>
  <div id="app">
    <v-app dark>
      <v-content>
        <ImageForm/>
      </v-content>
    </v-app>
  </div>
</template>

<script>
import ImageForm from './components/ImageForm';

export default {
  name: 'App',
  components: {
    ImageForm,
  },
  data: () => ({
    image: ''
  }),
  methods: {
    
  }
};
</script>
