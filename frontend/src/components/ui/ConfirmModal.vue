<script setup>
import { AlertTriangle, Info, X } from 'lucide-vue-next'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: 'Konfirmasi Tindakan',
  },
  message: {
    type: String,
    default: 'Apakah Anda yakin ingin melanjutkan tindakan ini?',
  },
  confirmText: {
    type: String,
    default: 'Ya, Lanjutkan',
  },
  cancelText: {
    type: String,
    default: 'Batal',
  },
  isDanger: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-60 overflow-y-auto">
    <!-- Backdrop -->
    <div
      class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
      @click="emit('cancel')"
    ></div>

    <div class="flex min-h-full items-center justify-center p-4">
      <div
        class="relative w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl transition-all border border-slate-200"
      >
        <button
          @click="emit('cancel')"
          class="absolute top-4 right-4 text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
        >
          <X class="w-4 h-4" />
        </button>

        <div class="flex items-start gap-4">
          <div
            class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
            :class="isDanger ? 'bg-rose-100 text-rose-600' : 'bg-indigo-100 text-indigo-600'"
          >
            <AlertTriangle v-if="isDanger" class="w-5 h-5" />
            <Info v-else class="w-5 h-5" />
          </div>

          <div>
            <h3 class="text-base font-bold text-slate-900 leading-snug">
              {{ title }}
            </h3>
            <p class="text-xs text-slate-600 mt-1.5 leading-relaxed">
              {{ message }}
            </p>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2.5 mt-6 pt-4 border-t border-slate-100">
          <button
            type="button"
            @click="emit('cancel')"
            class="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors cursor-pointer"
          >
            {{ cancelText }}
          </button>
          <button
            type="button"
            @click="emit('confirm')"
            class="px-4 py-2 text-xs font-semibold text-white rounded-xl shadow-xs transition-all cursor-pointer"
            :class="isDanger ? 'bg-rose-600 hover:bg-rose-700' : 'bg-indigo-600 hover:bg-indigo-700'"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
