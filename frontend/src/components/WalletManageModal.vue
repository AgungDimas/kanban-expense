<script setup>
import { ref } from 'vue'
import { useWalletStore } from '../stores/walletStore'
import { useBoardStore } from '../stores/boardStore'
import { formatRupiah } from '../utils/formatters'
import ConfirmModal from './ui/ConfirmModal.vue'
import {
  Wallet,
  Plus,
  Trash2,
  Edit2,
  Check,
  X,
  CreditCard,
  AlertCircle,
  HelpCircle,
} from 'lucide-vue-next'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close'])

const walletStore = useWalletStore()
const boardStore = useBoardStore()

const showAddForm = ref(false)
const newWalletForm = ref({ name: '', balance: '0' })
const isAdding = ref(false)
const errorMessage = ref('')

// Editing state
const editingWalletId = ref(null)
const editForm = ref({ name: '', balance: '' })
const isSavingEdit = ref(false)

// Delete confirm dialog
const isConfirmOpen = ref(false)
const walletToDelete = ref(null)

function startEdit(wallet) {
  editingWalletId.value = wallet.id
  editForm.value = {
    name: wallet.name,
    balance: String(wallet.balance),
  }
}

function cancelEdit() {
  editingWalletId.value = null
  editForm.value = { name: '', balance: '' }
}

async function saveEdit(walletId) {
  if (!editForm.value.name.trim()) return
  isSavingEdit.value = true
  errorMessage.value = ''
  try {
    await walletStore.updateWallet(walletId, {
      name: editForm.value.name.trim(),
      balance: Number(editForm.value.balance || 0).toFixed(2),
    })
    cancelEdit()
    boardStore.showToast('Dompet berhasil diperbarui!', 'success')
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memperbarui dompet.'
  } finally {
    isSavingEdit.value = false
  }
}

async function handleAddWallet() {
  if (!newWalletForm.value.name.trim()) {
    errorMessage.value = 'Nama dompet wajib diisi.'
    return
  }
  isAdding.value = true
  errorMessage.value = ''
  try {
    await walletStore.createWallet({
      name: newWalletForm.value.name.trim(),
      balance: Number(newWalletForm.value.balance || 0).toFixed(2),
    })
    newWalletForm.value = { name: '', balance: '0' }
    showAddForm.value = false
    boardStore.showToast('Dompet baru berhasil ditambahkan!', 'success')
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menambahkan dompet.'
  } finally {
    isAdding.value = false
  }
}

function promptDelete(wallet) {
  walletToDelete.value = wallet
  isConfirmOpen.value = true
}

async function executeDelete() {
  if (!walletToDelete.value) return
  isConfirmOpen.value = false
  errorMessage.value = ''
  try {
    await walletStore.deleteWallet(walletToDelete.value.id)
    boardStore.showToast(`Dompet "${walletToDelete.value.name}" berhasil dihapus.`, 'info')
    walletToDelete.value = null
  } catch (err) {
    errorMessage.value =
      err.response?.data?.detail ||
      'Gagal menghapus dompet. Pastikan dompet tidak sedang digunakan oleh kartu pengeluaran.'
  }
}
</script>

<template>
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
      <!-- Backdrop -->
      <div
        class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
        @click="emit('close')"
      ></div>

      <div class="flex min-h-full items-center justify-center p-4">
        <div
          class="relative w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl transition-all duration-200 border border-slate-200"
        >
        <!-- Modal Header -->
        <div class="flex items-center justify-between pb-4 border-b border-slate-100">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
              <Wallet class="w-5 h-5" />
            </div>
            <div>
              <h2 class="text-base font-bold text-slate-800">Kelola Dompet & Rekening</h2>
              <p class="text-xs text-slate-500">Tambah, ubah saldo, atau hapus dompet digital Anda</p>
            </div>
          </div>
          <button
            @click="emit('close')"
            class="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
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

        <!-- Add Form Toggle & Button -->
        <div class="mt-4 flex items-center justify-between">
          <span class="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Daftar Dompet Aktif ({{ walletStore.wallets.length }})
          </span>
          <button
            @click="showAddForm = !showAddForm"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition-colors cursor-pointer"
          >
            <Plus class="w-3.5 h-3.5" />
            <span>{{ showAddForm ? 'Tutup Form' : 'Tambah Dompet' }}</span>
          </button>
        </div>

        <!-- Inline Add Wallet Form -->
        <div
          v-if="showAddForm"
          class="mt-3 p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3"
        >
          <div class="text-xs font-semibold text-slate-800">Form Dompet Baru:</div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <input
              v-model="newWalletForm.name"
              type="text"
              placeholder="Nama Dompet (BCA, GoPay, dll)"
              class="px-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-white focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
            />
            <input
              v-model="newWalletForm.balance"
              type="number"
              min="0"
              step="any"
              placeholder="Saldo Awal (Rp)"
              class="px-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-white font-semibold focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
            />
          </div>
          <div class="flex justify-end gap-2">
            <button
              @click="showAddForm = false"
              class="px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-200 rounded-lg"
            >
              Batal
            </button>
            <button
              @click="handleAddWallet"
              :disabled="isAdding"
              class="px-4 py-1 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-2xs disabled:opacity-50"
            >
              {{ isAdding ? 'Menyimpan...' : 'Simpan' }}
            </button>
          </div>
        </div>

        <!-- Wallets List -->
        <div class="mt-3 space-y-2 max-h-64 overflow-y-auto pr-1">
          <div
            v-for="w in walletStore.wallets"
            :key="w.id"
            class="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-slate-300 bg-white transition-all shadow-2xs"
          >
            <!-- Normal View Mode -->
            <template v-if="editingWalletId !== w.id">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600 shrink-0">
                  <CreditCard class="w-4 h-4" />
                </div>
                <div>
                  <h4 class="text-xs font-bold text-slate-800">{{ w.name }}</h4>
                  <p class="text-xs font-extrabold text-emerald-700 mt-0.5">
                    {{ formatRupiah(w.balance) }}
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-1.5">
                <button
                  @click="startEdit(w)"
                  title="Ubah Dompet"
                  class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors cursor-pointer"
                >
                  <Edit2 class="w-3.5 h-3.5" />
                </button>
                <button
                  @click="promptDelete(w)"
                  title="Hapus Dompet"
                  class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </template>

            <!-- Edit Mode -->
            <template v-else>
              <div class="flex-1 grid grid-cols-2 gap-2 mr-2">
                <input
                  v-model="editForm.name"
                  type="text"
                  class="px-2.5 py-1 text-xs rounded-lg border border-slate-300 bg-white font-medium focus:border-indigo-500"
                />
                <input
                  v-model="editForm.balance"
                  type="number"
                  step="any"
                  class="px-2.5 py-1 text-xs rounded-lg border border-slate-300 bg-white font-bold text-emerald-700 focus:border-indigo-500"
                />
              </div>
              <div class="flex items-center gap-1 shrink-0">
                <button
                  @click="saveEdit(w.id)"
                  :disabled="isSavingEdit"
                  title="Simpan"
                  class="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded-lg"
                >
                  <Check class="w-4 h-4 stroke-[2.5]" />
                </button>
                <button
                  @click="cancelEdit"
                  title="Batal"
                  class="p-1.5 text-slate-400 hover:bg-slate-100 rounded-lg"
                >
                  <X class="w-4 h-4" />
                </button>
              </div>
            </template>
          </div>

          <!-- Empty state -->
          <div
            v-if="walletStore.wallets.length === 0"
            class="p-8 text-center text-xs text-slate-400 border-2 border-dashed border-slate-200 rounded-xl"
          >
            <HelpCircle class="w-6 h-6 mx-auto mb-2 text-slate-300" />
            <span>Belum ada dompet. Klik tombol "+ Tambah Dompet" di atas untuk menambahkan.</span>
          </div>
        </div>

        <!-- Total Saldo Footer -->
        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
          <span class="font-semibold text-slate-500">Total Saldo Semua Dompet:</span>
          <span class="text-sm font-extrabold text-slate-900">
            {{ formatRupiah(walletStore.totalBalance) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <ConfirmModal
      :is-open="isConfirmOpen"
      :title="`Hapus Dompet '${walletToDelete?.name}'?`"
      :message="`Apakah Anda yakin ingin menghapus dompet '${walletToDelete?.name}'? Tindakan ini tidak dapat dibatalkan.`"
      confirm-text="Hapus Dompet"
      cancel-text="Batal"
      :is-danger="true"
      @confirm="executeDelete"
      @cancel="isConfirmOpen = false"
    />
  </div>
  </Transition>
</template>
