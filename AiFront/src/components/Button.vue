<template>
  <button class="menu-btn" @click="$emit('click')">
    <slot />
  </button>
</template>

<style scoped>
.menu-btn {
  background: rgba(0,0,0,0.6);
  padding: 12px 25px;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 20px;
  cursor: pointer;
  margin: 10px;
  transition: 0.3s;
}

.menu-btn:hover {
  background: rgba(255,255,255,0.2);
}
</style>
