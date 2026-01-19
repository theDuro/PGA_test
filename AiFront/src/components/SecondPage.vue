<template>
  <div class="page">
    <h1>Production Parameters</h1>

    <div class="grid">
      <div class="field" v-for="(field, index) in fields" :key="index">
        <label :for="'input' + index">{{ field.label }}</label>
        <input
          type="number"
          :id="'input' + index"
          v-model.number="field.value"
        />
      </div>
    </div>

    <div class="buttons">
      <button @click="sendData">Send</button>
      <button @click="goBack">Back</button>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const router = useRouter()

    const fields = ref([
      { key: 'sheet_width', label: 'Sheet width (mm)', value: null },
      { key: 'sheet_thickness', label: 'Sheet thickness (mm)', value: null },
      { key: 'rolling_force', label: 'Rolling force (kN)', value: null },
      { key: 'motor_power', label: 'Motor power (kW)', value: null },
      { key: 'line_speed', label: 'Line speed (m/min)', value: null },
      { key: 'process_time', label: 'Process time (s)', value: null }
    ])

    const goBack = () => router.push('/')

    const sendData = async () => {
      // Tworzymy JSON dokładnie taki, jaki backend oczekuje
      const payload = {}
      fields.value.forEach(f => {
        payload[f.key] = f.value
      })

      console.log('Sending payload to backend:', payload)

      try {
        const response = await fetch('http://localhost:8000/data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })

        if (!response.ok) {
          const text = await response.text()
          throw new Error(text)
        }

        const resp = await response.json()
        console.log('Backend response:', resp)
        alert('Data sent to backend and RabbitMQ')
      } catch (err) {
        console.error('Error sending data:', err)
        alert('Error sending data')
      }
    }

    return { fields, goBack, sendData }
  }
}
</script>

<style scoped>
.page { padding: 20px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
.field { display: flex; flex-direction: column; }
.buttons { display: flex; gap: 10px; }
</style>
