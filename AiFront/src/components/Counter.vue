<template>
  <div class="counter-wrapper">
    <p>Licznik: {{ count }}</p>
    <button @click="increment">Dodaj 1</button>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'Counter',
  setup() {
    const count = ref(0)
    const increment = () => count.value--
    return { count, increment }
  }
}
</script>

<style scoped>
.counter-wrapper {
  background-color: rgba(0,0,0,0.5); /* półprzezroczyste tło */
  padding: 15px 25px;
  border-radius: 10px;
  color: white;
  margin-top: 20px;
}

button {
  padding: 5px 15px;
  margin-top: 10px;
  cursor: pointer;
}
</style>