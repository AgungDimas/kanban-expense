<script setup>
import { ref, watch, computed } from 'vue'
import { useBoardStore } from '../stores/boardStore'
import { useWalletStore } from '../stores/walletStore'
import { formatRupiah, formatDate } from '../utils/formatters'
import CustomSelect from './ui/CustomSelect.vue'
import DatePicker from './ui/DatePicker.vue'
import ConfirmModal from './ui/ConfirmModal.vue'
import {
  X,
  CreditCard,
  Calendar,
  CheckCircle2,
  Clock,
  Trash2,
  Edit3,
  FileText,
  Tag,
  AlertCircle,
  Save,
} from 'lucide-vue-next'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  card: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['close'])

const boardStore = useBoardStore()
const walletStore = useWalletStore()

const isEditing = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')

const isDeleteConfirmOpen = ref(false)

const editForm = ref({
  title: '',
  amount: '',
  column: null,
  wallet: null,
  category: null,
  due_date: '',
  notes: '',
})

watch(
  () => props.card,
  (c) => {
    if (c) {
      isEditing.value = false
      errorMessage.value = ''
      editForm.value = {
        title: c.title || '',
        amount: String(c.amount || ''),
        column: c.column,
        wallet: c.wallet,
        category: c.category || null,
        due_date: c.due_date || '',
        notes: c.notes || '',
      }
    }
  },
  { immediate: true }
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

const currentColumn = computed(() => {
  if (!props.card) return null
  return boardStore.columns.find((col) => col.id === props.card.column)
})

async function handleSaveEdit() {
  if (!editForm.value.title.trim()) {
    errorMessage.value = 'Judul pengeluaran wajib diisi.'
    return
  }
  if (!editForm.value.amount || Number(editForm.value.amount) <= 0) {
    errorMessage.value = 'Nominal harus lebih besar dari 0.'
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''
  try {
    const payload = {
      title: editForm.value.title.trim(),
      amount: Number(editForm.value.amount).toFixed(2),
      column: editForm.value.column,
      wallet: editForm.value.wallet,
      category: editForm.value.category || null,
      due_date: editForm.value.due_date || null,
      notes: editForm.value.notes.trim(),
    }
    await boardStore.updateExpense(props.card.id, payload)
    isEditing.value = false
    emit('close')
  } catch (err) {
    errorMessage.value =
      err.response?.data?.balance ||
      err.response?.data?.detail ||
      'Gagal memperbarui kartu pengeluaran.'
  } finally {
    isSubmitting.value = false
  }
}

async function handleDeleteCard() {
  isDeleteConfirmOpen.value = false
  try {
    await boardStore.deleteExpense(props.card.id, props.card.column)
    emit('close')
  } catch (err) {
    console.error('Delete card failed:', err)
  }
}
</script>

<template>
  <div v-if="isOpen && card" class="fixed inset-0 z-50 overflow-y-auto">
    <!-- Backdrop -->
    <div
      class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
      @click="emit('close')"
    ></div>

    <div class="flex min-h-full items-center justify-center p-4">
      <div
        class="relative w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl transition-all border border-slate-200"
      >
        <!-- Modal Top Bar -->
        <div class="flex items-center justify-between pb-3.5 border-b border-slate-100">
          <div class="flex items-center gap-2">
            <!-- Category Badge -->
            <span
              v-if="card.category_name"
              class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold"
              :style="{
                backgroundColor: `${card.category_color}18`,
                color: card.category_color || '#4b5563',
              }"
            >
              <span
                class="w-1.5 h-1.5 rounded-full mr-1.5 shrink-0"
                :style="{ backgroundColor: card.category_color || '#4b5563' }"
              ></span>
              {{ card.category_name }}
            </span>
            <span
              v-else
              class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold text-slate-600 bg-slate-100"
            >
              Umum
            </span>

            <!-- Status Indicator -->
            <span
              v-if="currentColumn?.deducts_balance"
              class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-100 text-emerald-800"
            >
              <CheckCircle2 class="w-3.5 h-3.5 text-emerald-600" />
              <span>Lunas</span>
            </span>
            <span
              v-else
              class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 text-slate-600"
            >
              <Clock class="w-3.5 h-3.5 text-slate-500" />
              <span>{{ currentColumn?.name || 'Rencana' }}</span>
            </span>
          </div>

          <div class="flex items-center gap-1.5">
            <button
              v-if="!isEditing"
              @click="isEditing = true"
              title="Edit Kartu"
              class="p-1.5 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors cursor-pointer"
            >
              <Edit3 class="w-4 h-4" />
            </button>
            <button
              @click="emit('close')"
              class="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
            >
              <X class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- Error Alert -->
        <div
          v-if="errorMessage"
          class="mt-3.5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2"
        >
          <AlertCircle class="w-4 h-4 shrink-0" />
          <span>{{ errorMessage }}</span>
        </div>

        <!-- View Mode -->
        <div v-if="!isEditing" class="mt-4 space-y-4">
          <!-- Title & Nominal -->
          <div>
            <h2 class="text-xl font-bold text-slate-900 leading-snug">
              {{ card.title }}
            </h2>
            <div class="text-2xl font-black text-indigo-600 tracking-tight mt-1.5">
              {{ formatRupiah(card.amount) }}
            </div>
          </div>

          <!-- Metadata Grid -->
          <div class="grid grid-cols-2 gap-3 p-3.5 bg-slate-50 rounded-xl border border-slate-150 text-xs">
            <!-- Wallet -->
            <div class="space-y-1">
              <span class="text-slate-400 flex items-center gap-1">
                <CreditCard class="w-3.5 h-3.5" />
                Dompet
              </span>
              <span class="font-bold text-slate-800 block">
                {{ card.wallet_name || 'Tidak ada' }}
              </span>
            </div>

            <!-- Column -->
            <div class="space-y-1">
              <span class="text-slate-400 flex items-center gap-1">
                <Tag class="w-3.5 h-3.5" />
                Kolom Status
              </span>
              <span class="font-bold text-slate-800 block">
                {{ currentColumn?.name }}
              </span>
            </div>

            <!-- Due Date -->
            <div class="space-y-1">
              <span class="text-slate-400 flex items-center gap-1">
                <Calendar class="w-3.5 h-3.5" />
                Jatuh Tempo
              </span>
              <span class="font-semibold text-slate-700 block">
                {{ formatDate(card.due_date) || '-' }}
              </span>
            </div>

            <!-- Paid Date -->
            <div class="space-y-1">
              <span class="text-slate-400 flex items-center gap-1">
                <CheckCircle2 class="w-3.5 h-3.5" />
                Tanggal Lunas
              </span>
              <span class="font-semibold text-slate-700 block">
                {{ formatDate(card.paid_at) || '-' }}
              </span>
            </div>
          </div>

          <!-- Notes -->
          <div v-if="card.notes" class="space-y-1">
            <span class="text-xs font-semibold text-slate-500 flex items-center gap-1">
              <FileText class="w-3.5 h-3.5" />
              Catatan:
            </span>
            <p class="text-xs text-slate-700 p-3 bg-white border border-slate-200 rounded-xl leading-relaxed whitespace-pre-wrap">
              {{ card.notes }}
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center justify-between pt-4 border-t border-slate-100">
            <button
              @click="isDeleteConfirmOpen = true"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-rose-600 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer"
            >
              <Trash2 class="w-3.5 h-3.5" />
              <span>Hapus Kartu</span>
            </button>

            <button
              @click="isEditing = true"
              class="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs transition-colors cursor-pointer"
            >
              <Edit3 class="w-3.5 h-3.5" />
              <span>Ubah Rincian</span>
            </button>
          </div>
        </div>

        <!-- Edit Mode with CustomSelect and DatePicker -->
        <form v-else @submit.prevent="handleSaveEdit" class="mt-4 space-y-3.5">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Judul Kartu</label>
            <input
              v-model="editForm.title"
              type="text"
              class="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-medium"
              required
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Nominal (Rp)</label>
            <input
              v-model="editForm.amount"
              type="number"
              step="any"
              class="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 font-bold focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
              required
            />
          </div>

          <div class="grid grid-cols-2 gap-2.5">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Kolom Status</label>
              <CustomSelect
                v-model="editForm.column"
                :options="columnOptions"
                placeholder="Pilih Kolom..."
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Dompet Sumber</label>
              <CustomSelect
                v-model="editForm.wallet"
                :options="walletOptions"
                placeholder="Pilih Dompet..."
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2.5">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Kategori</label>
              <CustomSelect
                v-model="editForm.category"
                :options="categoryOptions"
                placeholder="Pilih Kategori..."
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Jatuh Tempo</label>
              <DatePicker
                v-model="editForm.due_date"
                placeholder="Pilih Tanggal..."
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Catatan</label>
            <textarea
              v-model="editForm.notes"
              rows="2"
              class="w-full px-3 py-1.5 text-xs rounded-xl border border-slate-300 resize-none"
            ></textarea>
          </div>

          <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              @click="isEditing = false"
              class="px-3.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg cursor-pointer"
            >
              Batal
            </button>
            <button
              type="submit"
              :disabled="isSubmitting"
              class="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-2xs disabled:opacity-50 cursor-pointer"
            >
              <Save class="w-3.5 h-3.5" />
              <span>{{ isSubmitting ? 'Menyimpan...' : 'Simpan Perubahan' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <ConfirmModal
      :is-open="isDeleteConfirmOpen"
      :title="`Hapus '${card.title}'?`"
      message="Apakah Anda yakin ingin menghapus kartu ini? Jika kartu berada di kolom Lunas, saldo dompet akan otomatis dikembalikan (refund)."
      confirm-text="Hapus Kartu"
      cancel-text="Batal"
      :is-danger="true"
      @confirm="handleDeleteCard"
      @cancel="isDeleteConfirmOpen = false"
    />
  </div>
</template>
