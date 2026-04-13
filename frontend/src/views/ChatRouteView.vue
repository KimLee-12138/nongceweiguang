<script setup>
import UserRouteGate from '../components/auth/UserRouteGate.vue'
import ChatPage from './ChatPage.vue'
</script>

<template>
  <UserRouteGate>
    <ChatPage />
  </UserRouteGate>
</template>
