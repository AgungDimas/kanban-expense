<script setup>
import { computed } from 'vue'
import { useBoardStore } from '../stores/boardStore'
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-vue-next'

const boardStore = useBoardStore()
const toast = computed(() => boardStore.toast)

const bgClasses = computed(() => {
  switch (toast.value.type) {
    case 'success':
      return 'bg-emerald-600 text-white shadow-emerald-200'
    case 'info':
      return 'bg-blue-600 text-white shadow-blue-200'
    case 'error':
    default:
      return 'bg-rose-600 text-white shadow-rose-200'
  }
})
</script>

<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="transform translate-y-4 opacity-0 scale-95"
    enter-to-class="transform translate-y-0 opacity-100 scale-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="transform translate-y-0 opacity-100 scale-100"
    leave-to-class="transform translate-y-4 opacity-0 scale-95"
  >
    <div
      v-if="toast.show"
      class="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-xl max-w-md border border-white/20 backdrop-blur-md"
      :class="bgClasses"
    >
      <CheckCircle2 v-if="toast.type === 'success'" class="w-5 h-5 shrink-0" />
      <Info v-else-if="toast.type === 'info'" class="w-5 h-5 shrink-0" />
      <AlertCircle v-else class="w-5 h-5 shrink-0" />

      <p class="text-sm font-medium leading-relaxed">{{ toast.message }}</p>

      <button
        @click="boardStore.hideToast()"
        class="ml-auto text-white/80 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/10"
      >
        <X class="w-4 h-4" />
      </button>
    </div>
  </Transition>
</template>
