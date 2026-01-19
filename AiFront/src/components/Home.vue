<template>
  <div class="home">
    <h1>Menu główne</h1>

    <Button @click="test1">Opcja 1</Button>
    <Button @click="test2">Opcja 2</Button>
    <Button @click="goToNext">Przejdź do drugiego okna</Button>
    <Button @click="exitApp">Wyjście</Button>
  </div>
</template>

<script>
import Button from './Button.vue'
import { useRouter } from 'vue-router'

export default {
  components: { Button },
  setup() {
    const router = useRouter()

    const goToNext = () => router.push('/SecondPage') // przejście do drugiej strony
    const test1 = () => alert('Opcja 1')
    const test2 = () => alert('Opcja 2')
    const exitApp = () => alert('Wyjście z aplikacji') // lub logika wyjścia

    return { goToNext, test1, test2, exitApp }
  }
}
</script>

<style scoped>
.home {
  height: 100%;
  width: 100%;
  color: white;

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>