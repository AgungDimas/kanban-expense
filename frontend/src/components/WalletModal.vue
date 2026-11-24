<script setup>
import { ref, watch } from 'vue'
import { useWalletStore } from '../stores/walletStore'
import { useBoardStore } from '../stores/boardStore'
import { X, Wallet, AlertCircle } from 'lucide-vue-next'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close'])

const walletStore = useWalletStore()
const boardStore = useBoardStore()

const isSubmitting = ref(false)
const errorMessage = ref('')

const form = ref({
  name: '',
  balance: '0',
})

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      errorMessage.value = ''
      form.value = {
        name: '',
        balance: '0',
      }
    }
  }
)

async function handleSubmit() {
  errorMessage.value = ''
  if (!form.value.name.trim()) {
    errorMessage.value = 'Nama dompet wajib diisi.'
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      name: form.value.name.trim(),
      balance: Number(form.value.balance || 0).toFixed(2),
    }
    await walletStore.createWallet(payload)
    boardStore.showToast(`Dompet "${payload.name}" berhasil dibuat!`, 'success')
    emit('close')
  } catch (err) {
    if (err.response?.data) {
      if (typeof err.response.data === 'string') {
        errorMessage.value = err.response.data
      } else if (err.response.data.detail) {
        errorMessage.value = err.response.data.detail
      } else {
        const firstKey = Object.keys(err.response.data)[0]
        const val = err.response.data[firstKey]
        errorMessage.value = Array.isArray(val) ? `${firstKey}: ${val[0]}` : String(val)
      }
    } else {
      errorMessage.value = err.message || 'Gagal menambahkan dompet.'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <!-- Backdrop -->
    <div
      class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
      @click="emit('close')"
    ></div>

    <div class="flex min-h-full items-center justify-center p-4">
      <div
        class="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl transition-all border border-slate-200"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between pb-4 border-b border-slate-100">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Wallet class="w-5 h-5" />
            </div>
            <h2 class="text-base font-bold text-slate-800">Tambah Dompet Baru</h2>
          </div>
          <button
            @click="emit('close')"
            class="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Error Alert -->
        <div
          v-if="errorMessage"
          class="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2"
        >
          <AlertCircle class="w-4 h-4 shrink-0" />
          <span>{{ errorMessage }}</span>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="mt-4 space-y-4">
          <!-- Name -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">
              Nama Dompet / Rekening <span class="text-rose-500">*</span>
            </label>
            <input
              v-model="form.name"
              type="text"
              placeholder="Contoh: BCA, GoPay, Tunai, Jenius"
              class="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all"
              required
            />
          </div>

          <!-- Initial Balance -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">
              Saldo Awal (Rp)
            </label>
            <input
              v-model="form.balance"
              type="number"
              step="any"
              min="0"
              placeholder="0"
              class="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-semibold"
            />
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100">
            <button
              type="button"
              @click="emit('close')"
              class="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors cursor-pointer"
            >
              Batal
            </button>
            <button
              type="submit"
              :disabled="isSubmitting"
              class="px-5 py-2 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-xs transition-all disabled:opacity-50 cursor-pointer"
            >
              {{ isSubmitting ? 'Menyimpan...' : 'Simpan Dompet' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
