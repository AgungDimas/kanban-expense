<script setup>
import { ref, watch, computed } from 'vue'
import { useBoardStore } from '../stores/boardStore'
import { useWalletStore } from '../stores/walletStore'
import { formatRupiah } from '../utils/formatters'
import CustomSelect from './ui/CustomSelect.vue'
import DatePicker from './ui/DatePicker.vue'
import { X, PlusCircle, AlertCircle, RefreshCw } from 'lucide-vue-next'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  defaultColumnId: {
    type: Number,
    default: null,
  },
})

const emit = defineEmits(['close'])

const boardStore = useBoardStore()
const walletStore = useWalletStore()

const isSubmitting = ref(false)
const errorMessage = ref('')

const form = ref({
  title: '',
  amount: '',
  column: null,
  wallet: null,
  category: null,
  due_date: '',
  notes: '',
})

// Auto-fetch data if stores are empty when modal opens
watch(
  () => props.isOpen,
  async (open) => {
    if (open) {
      errorMessage.value = ''

      if (boardStore.columns.length === 0) {
        await boardStore.fetchBoard()
      }
      if (walletStore.wallets.length === 0) {
        await walletStore.fetchWallets()
      }
      if (boardStore.categories.length === 0) {
        await boardStore.fetchCategories()
      }

      const defaultCol = props.defaultColumnId || boardStore.columns[0]?.id || null
      const defaultWallet = walletStore.wallets[0]?.id || null

      form.value = {
        title: '',
        amount: '',
        column: defaultCol,
        wallet: defaultWallet,
        category: boardStore.categories[0]?.id || null,
        due_date: '',
        notes: '',
      }
    }
  }
)

// Watch columns list so form.column is set as soon as columns are loaded
watch(
  () => boardStore.columns,
  (cols) => {
    if (cols && cols.length > 0 && !form.value.column) {
      form.value.column = props.defaultColumnId || cols[0].id
    }
  },
  { immediate: true, deep: true }
)

// Watch wallets list so form.wallet is set as soon as wallets are loaded
watch(
  () => walletStore.wallets,
  (wallets) => {
    if (wallets && wallets.length > 0 && !form.value.wallet) {
      form.value.wallet = wallets[0].id
    }
  },
  { immediate: true, deep: true }
)

const columnOptions = computed(() =>
  boardStore.columns.map((c) => ({
    value: c.id,
    label: c.name,
    subtitle: c.deducts_balance ? 'Potong Saldo' : 'Rencana',
  }))
)

const walletOptions = computed(() =>
  walletStore.wallets.map((w) => ({
    value: w.id,
    label: w.name,
    subtitle: formatRupiah(w.balance),
  }))
)

const categoryOptions = computed(() => [
  { value: null, label: 'Tanpa Kategori' },
  ...boardStore.categories.map((cat) => ({
    value: cat.id,
    label: cat.name,
    color: cat.color,
  })),
])

const selectedColumn = computed(() => {
  return boardStore.columns.find((c) => c.id === form.value.column)
})

const selectedWallet = computed(() => {
  return walletStore.wallets.find((w) => w.id === form.value.wallet)
})

const willDeductBalance = computed(() => {
  return selectedColumn.value?.deducts_balance || false
})

const isBalanceInsufficient = computed(() => {
  if (!willDeductBalance.value || !selectedWallet.value || !form.value.amount) return false
  return Number(selectedWallet.value.balance) < Number(form.value.amount)
})

async function reloadModalData() {
  await Promise.all([
    boardStore.fetchBoard(),
    walletStore.fetchWallets(),
    boardStore.fetchCategories(),
  ])
}

async function handleSubmit() {
  errorMessage.value = ''
  if (!form.value.title.trim()) {
    errorMessage.value = 'Judul pengeluaran wajib diisi.'
    return
  }
  if (!form.value.amount || Number(form.value.amount) <= 0) {
    errorMessage.value = 'Nominal harus lebih besar dari 0.'
    return
  }
  if (!form.value.column) {
    errorMessage.value = 'Pilih kolom status tujuan.'
    return
  }
  if (!form.value.wallet) {
    errorMessage.value = 'Pilih dompet pembayaran.'
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      title: form.value.title.trim(),
      amount: Number(form.value.amount).toFixed(2),
      column: form.value.column,
      wallet: form.value.wallet,
      category: form.value.category || null,
      due_date: form.value.due_date || null,
      notes: form.value.notes.trim(),
    }
    await boardStore.createExpense(payload)
    emit('close')
  } catch (err) {
    if (err.response?.data) {
      if (typeof err.response.data === 'string') {
        errorMessage.value = err.response.data
      } else if (err.response.data.balance) {
        errorMessage.value = err.response.data.balance
      } else if (err.response.data.detail) {
        errorMessage.value = err.response.data.detail
      } else {
        const firstKey = Object.keys(err.response.data)[0]
        const val = err.response.data[firstKey]
        errorMessage.value = Array.isArray(val) ? `${firstKey}: ${val[0]}` : String(val)
      }
    } else {
      errorMessage.value = err.message || 'Gagal menyimpan pengeluaran.'
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
        class="relative w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl transition-all border border-slate-200"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between pb-4 border-b border-slate-100">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <PlusCircle class="w-5 h-5" />
            </div>
            <h2 class="text-base font-bold text-slate-800">Tambah Pengeluaran / Tagihan</h2>
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
          <!-- Title -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">
              Judul Pengeluaran / Tagihan <span class="text-rose-500">*</span>
            </label>
            <input
              v-model="form.title"
              type="text"
              placeholder="Contoh: Tagihan Listrik PLN, Belanja Mingguan"
              class="w-full px-3.5 py-2 text-xs rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-medium"
              required
            />
          </div>

          <!-- Nominal -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">
              Nominal (Rp) <span class="text-rose-500">*</span>
            </label>
            <input
              v-model="form.amount"
              type="number"
              step="any"
              min="1"
              placeholder="Contoh: 150000"
              class="w-full px-3.5 py-2 text-xs rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-bold text-slate-900"
              required
            />
          </div>

          <!-- Column & Wallet Grid with CustomSelect -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <!-- Kolom Kanban -->
            <div>
              <div class="flex items-center justify-between mb-1">
                <label class="block text-xs font-semibold text-slate-700">
                  Kolom Status <span class="text-rose-500">*</span>
                </label>
                <button
                  type="button"
                  @click="reloadModalData"
                  title="Muat ulang opsi kolom"
                  class="text-[11px] text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer"
                >
                  <RefreshCw class="w-3 h-3" />
                  <span>Reload</span>
                </button>
              </div>
              <CustomSelect
                v-model="form.column"
                :options="columnOptions"
                placeholder="Pilih Kolom Status..."
              />
              <p v-if="boardStore.columns.length === 0" class="text-[11px] text-amber-600 mt-1">
                Belum ada kolom. Klik "Reload" di atas atau refresh halaman.
              </p>
            </div>

            <!-- Dompet -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">
                Dompet Sumber <span class="text-rose-500">*</span>
              </label>
              <CustomSelect
                v-model="form.wallet"
                :options="walletOptions"
                placeholder="Pilih Dompet..."
              />
              <p v-if="walletStore.wallets.length === 0" class="text-[11px] text-amber-600 mt-1">
                Belum ada dompet. Tambah dompet terlebih dahulu.
              </p>
            </div>
          </div>

          <!-- Warning if deducting balance and balance is low -->
          <div
            v-if="willDeductBalance"
            class="p-2.5 rounded-lg text-xs"
            :class="isBalanceInsufficient ? 'bg-amber-50 text-amber-800 border border-amber-200' : 'bg-emerald-50 text-emerald-800 border border-emerald-200'"
          >
            <span v-if="isBalanceInsufficient" class="font-semibold">
              ⚠️ Peringatan: Saldo dompet terpilih ({{ formatRupiah(selectedWallet?.balance) }}) kurang dari nominal. Transaksi akan ditolak jika dilanjutkan.
            </span>
            <span v-else class="font-medium">
              ℹ️ Kartu ini akan langsung memotong saldo {{ selectedWallet?.name }}.
            </span>
          </div>

          <!-- Category & Due Date Grid with CustomSelect & DatePicker -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <!-- Category -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Kategori</label>
              <CustomSelect
                v-model="form.category"
                :options="categoryOptions"
                placeholder="Pilih Kategori..."
              />
            </div>

            <!-- Due Date -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Jatuh Tempo</label>
              <DatePicker
                v-model="form.due_date"
                placeholder="Pilih Tanggal Jatuh Tempo..."
              />
            </div>
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Catatan (Opsional)</label>
            <textarea
              v-model="form.notes"
              rows="2"
              placeholder="Catatan tambahan atau rincian item..."
              class="w-full px-3.5 py-2 text-xs rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all resize-none"
            ></textarea>
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
              :disabled="isSubmitting || boardStore.columns.length === 0"
              class="px-5 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs transition-all disabled:opacity-50 cursor-pointer"
            >
              {{ isSubmitting ? 'Menyimpan...' : 'Simpan Pengeluaran' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
