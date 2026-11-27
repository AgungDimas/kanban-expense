<script setup>
import { ref, computed } from 'vue'
import draggable from 'vuedraggable'
import { useBoardStore } from '../stores/boardStore'
import { useWalletStore } from '../stores/walletStore'
import { formatRupiah } from '../utils/formatters'
import ExpenseCard from './ExpenseCard.vue'
import ConfirmModal from './ui/ConfirmModal.vue'
import {
  CheckCircle2,
  Clock,
  Plus,
  HelpCircle,
  Layers,
  RefreshCw,
  Search,
  Filter,
  X,
  ArrowUpDown,
} from 'lucide-vue-next'

const emit = defineEmits(['openExpenseModalWithColumn', 'cardClick'])
const boardStore = useBoardStore()
const walletStore = useWalletStore()

// Drag tracking state
const dragSourceColumnId = ref(null)
const columnsSnapshot = ref(null)
const walletsSnapshot = ref(null)

// Delete card dialog state
const isDeleteConfirmOpen = ref(false)
const cardToDelete = ref(null)

// Filter & Search & Sort states
const searchQuery = ref('')
const filterCategory = ref(null)
const filterWallet = ref(null)
const sortBy = ref('default') // 'default' | 'amount-desc' | 'amount-asc' | 'due-asc'

const isFilterActive = computed(() => {
  return searchQuery.value.trim() !== '' || filterCategory.value !== null || filterWallet.value !== null || sortBy.value !== 'default'
})

function clearFilters() {
  searchQuery.value = ''
  filterCategory.value = null
  filterWallet.value = null
  sortBy.value = 'default'
}

function getSortedCards(cards) {
  if (!cards) return []
  if (sortBy.value === 'default') return cards
  const sorted = [...cards]
  if (sortBy.value === 'amount-desc') {
    sorted.sort((a, b) => Number(b.amount || 0) - Number(a.amount || 0))
  } else if (sortBy.value === 'amount-asc') {
    sorted.sort((a, b) => Number(a.amount || 0) - Number(b.amount || 0))
  } else if (sortBy.value === 'due-asc') {
    sorted.sort((a, b) => {
      if (!a.due_date && !b.due_date) return 0
      if (!a.due_date) return 1
      if (!b.due_date) return -1
      return new Date(a.due_date) - new Date(b.due_date)
    })
  }
  return sorted
}

function isCardMatchingFilter(card) {
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    const matchTitle = card.title.toLowerCase().includes(q)
    const matchNotes = card.notes ? card.notes.toLowerCase().includes(q) : false
    if (!matchTitle && !matchNotes) return false
  }
  if (filterCategory.value !== null && card.category !== filterCategory.value) {
    return false
  }
  if (filterWallet.value !== null && card.wallet !== filterWallet.value) {
    return false
  }
  return true
}

function onDragStart(evt, column) {
  dragSourceColumnId.value = column.id
  columnsSnapshot.value = JSON.parse(JSON.stringify(boardStore.columns))
  walletsSnapshot.value = JSON.parse(JSON.stringify(walletStore.wallets))
}

function calculateNewPosition(cards, index) {
  if (!cards || cards.length === 0) return 1000.0
  if (cards.length === 1) return 1000.0

  if (index === 0) {
    const nextCard = cards[1]
    return nextCard ? nextCard.position / 2.0 : 1000.0
  }

  if (index === cards.length - 1) {
    const prevCard = cards[index - 1]
    return (prevCard ? prevCard.position : 0.0) + 1000.0
  }

  const prevCard = cards[index - 1]
  const nextCard = cards[index + 1]
  return (Number(prevCard.position) + Number(nextCard.position)) / 2.0
}

function onDraggableChange(evt, targetColumn) {
  if (evt.added) {
    const card = evt.added.element
    const newIndex = evt.added.newIndex
    const newPosition = calculateNewPosition(targetColumn.cards, newIndex)

    boardStore.moveCardOptimistic({
      cardId: card.id,
      sourceColumnId: dragSourceColumnId.value,
      targetColumnId: targetColumn.id,
      newPosition,
      previousColumnsSnapshot: columnsSnapshot.value,
      previousWalletsSnapshot: walletsSnapshot.value,
    })
  } else if (evt.moved) {
    const card = evt.moved.element
    const newIndex = evt.moved.newIndex
    const newPosition = calculateNewPosition(targetColumn.cards, newIndex)

    boardStore.moveCardOptimistic({
      cardId: card.id,
      sourceColumnId: targetColumn.id,
      targetColumnId: targetColumn.id,
      newPosition,
      previousColumnsSnapshot: columnsSnapshot.value,
      previousWalletsSnapshot: walletsSnapshot.value,
    })
  }
}

function promptDeleteCard(card) {
  cardToDelete.value = card
  isDeleteConfirmOpen.value = true
}

async function executeDeleteCard() {
  if (!cardToDelete.value) return
  const { id, column } = cardToDelete.value
  isDeleteConfirmOpen.value = false
  cardToDelete.value = null
  await boardStore.deleteExpense(id, column)
}

function getColumnTotal(cards) {
  if (!cards) return 0
  return cards
    .filter((c) => isCardMatchingFilter(c))
    .reduce((sum, c) => sum + Number(c.amount || 0), 0)
}

function getVisibleCardsCount(cards) {
  if (!cards) return 0
  return cards.filter((c) => isCardMatchingFilter(c)).length
}
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- Search & Filter Bar -->
    <div class="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 pt-3 pb-1">
      <div class="flex items-center gap-2.5 flex-wrap bg-white p-2.5 rounded-2xl border border-slate-200/90 shadow-2xs text-xs">
        <!-- Search Input -->
        <div class="relative flex-1 min-w-48">
          <Search class="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Cari pengeluaran, tagihan, atau catatan..."
            class="w-full pl-9 pr-3 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:border-indigo-500 focus:outline-hidden transition-all"
          />
        </div>

        <!-- Filter Category -->
        <div class="flex items-center gap-1.5">
          <Filter class="w-3.5 h-3.5 text-slate-400" />
          <select
            v-model="filterCategory"
            class="px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:border-indigo-500 focus:outline-hidden cursor-pointer"
          >
            <option :value="null">Semua Kategori</option>
            <option v-for="cat in boardStore.categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>

        <!-- Filter Wallet -->
        <div>
          <select
            v-model="filterWallet"
            class="px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:border-indigo-500 focus:outline-hidden cursor-pointer"
          >
            <option :value="null">Semua Dompet</option>
            <option v-for="w in walletStore.wallets" :key="w.id" :value="w.id">
              {{ w.name }}
            </option>
          </select>
        </div>

        <!-- Sort Select -->
        <div class="flex items-center gap-1.5">
          <ArrowUpDown class="w-3.5 h-3.5 text-slate-400" />
          <select
            v-model="sortBy"
            class="px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:border-indigo-500 focus:outline-hidden cursor-pointer font-medium"
          >
            <option value="default">Urutan Manual (Drag & Drop)</option>
            <option value="amount-desc">Nominal Tertinggi (Rp ↓)</option>
            <option value="amount-asc">Nominal Terendah (Rp ↑)</option>
            <option value="due-asc">Jatuh Tempo Terdekat ⏰</option>
          </select>
        </div>

        <!-- Reset Button -->
        <button
          v-if="isFilterActive"
          @click="clearFilters"
          class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-rose-600 hover:bg-rose-50 transition-colors font-medium cursor-pointer"
        >
          <X class="w-3.5 h-3.5" />
          <span>Reset Filter</span>
        </button>
      </div>
    </div>

    <!-- Kanban Columns Container -->
    <div class="flex-1 overflow-x-auto pb-8 pt-3">
      <!-- Empty State if no columns -->
      <div
        v-if="boardStore.columns.length === 0"
        class="flex flex-col items-center justify-center p-12 text-center text-slate-500 w-full min-h-[350px]"
      >
        <Layers class="w-12 h-12 text-slate-300 mb-3" />
        <h3 class="text-base font-bold text-slate-700">Belum ada kolom papan</h3>
        <p class="text-xs text-slate-500 max-w-sm mt-1">
          Kolom belum termuat atau belum terisi. Klik tombol di bawah untuk memuat ulang.
        </p>
        <button
          @click="boardStore.fetchBoard()"
          class="mt-4 inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs transition-all cursor-pointer"
        >
          <RefreshCw class="w-3.5 h-3.5" />
          <span>Muat Ulang Papan</span>
        </button>
      </div>

      <!-- Columns -->
      <div v-else class="flex items-start gap-6 min-w-max px-4 sm:px-6 lg:px-8">
        <!-- Kanban Column -->
        <div
          v-for="col in boardStore.columns"
          :key="col.id"
          class="w-80 sm:w-92 shrink-0 flex flex-col max-h-[calc(100vh-230px)] bg-slate-100/90 rounded-2xl border border-slate-200/80 shadow-2xs"
        >
          <!-- Column Header -->
          <div class="p-4 pb-3 border-b border-slate-200/70 bg-slate-50/70 rounded-t-2xl">
            <div class="flex items-center justify-between mb-1.5">
              <div class="flex items-center gap-2">
                <h2 class="text-sm font-bold text-slate-800 tracking-tight">
                  {{ col.name }}
                </h2>
                <span class="inline-flex items-center justify-center px-2 py-0.5 text-xs font-semibold rounded-full bg-slate-200/80 text-slate-700">
                  {{ getVisibleCardsCount(col.cards) }}
                </span>
              </div>

              <!-- Deduct status indicator -->
              <span
                v-if="col.deducts_balance"
                class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-100 text-emerald-800"
                title="Kartu di kolom ini langsung memotong saldo dompet"
              >
                <CheckCircle2 class="w-3 h-3 text-emerald-600" />
                <span>Memotong Saldo</span>
              </span>
              <span
                v-else
                class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-200/70 text-slate-600"
                title="Kartu di kolom ini belum memotong saldo"
              >
                <Clock class="w-3 h-3 text-slate-500" />
                <span>Rencana</span>
              </span>
            </div>

            <!-- Total Nominal per Column -->
            <div class="flex items-center justify-between text-xs text-slate-500 font-medium pt-1">
              <span>Subtotal:</span>
              <span class="font-bold text-slate-800">
                {{ formatRupiah(getColumnTotal(col.cards)) }}
              </span>
            </div>
          </div>

          <!-- Draggable Cards Container -->
          <div class="flex-1 overflow-y-auto p-3 min-h-[160px]">
            <!-- Subtle banner when custom sort is active -->
            <div
              v-if="sortBy !== 'default'"
              class="mb-2.5 px-2.5 py-1 bg-amber-50 border border-amber-200/80 rounded-lg text-[10px] text-amber-800 flex items-center justify-between"
            >
              <span>Sortir aktif (drag & drop nonaktif)</span>
              <button
                @click="sortBy = 'default'"
                class="font-bold underline hover:text-amber-950 cursor-pointer ml-1"
              >
                Reset
              </button>
            </div>

            <draggable
              :list="sortBy === 'default' ? col.cards : getSortedCards(col.cards)"
              :disabled="sortBy !== 'default'"
              group="kanban-cards"
              item-key="id"
              ghost-class="opacity-40 border-2 border-dashed border-indigo-400 bg-indigo-50/60 rounded-xl"
              drag-class="rotate-1 scale-102 shadow-xl"
              animation="200"
              @start="(evt) => onDragStart(evt, col)"
              @change="(evt) => onDraggableChange(evt, col)"
              class="min-h-[120px] pb-2"
            >
              <template #item="{ element }">
                <ExpenseCard
                  v-show="isCardMatchingFilter(element)"
                  :card="element"
                  :is-paid="col.deducts_balance"
                  @click="emit('cardClick', element)"
                  @delete="promptDeleteCard"
                />
              </template>
            </draggable>

            <!-- Empty placeholder if no cards -->
            <div
              v-if="!col.cards || col.cards.length === 0"
              class="h-28 border-2 border-dashed border-slate-200 rounded-xl flex flex-col items-center justify-center text-slate-400 text-xs gap-1.5 p-4 text-center select-none"
            >
              <HelpCircle class="w-5 h-5 text-slate-300" />
              <span>Belum ada kartu</span>
              <span class="text-[10px] text-slate-400">Tarik kartu ke sini atau buat baru</span>
            </div>
          </div>

          <!-- Quick Add Card Button in Column Footer -->
          <div class="p-2.5 pt-0">
            <button
              @click="emit('openExpenseModalWithColumn', col.id)"
              class="w-full flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-semibold text-slate-600 hover:text-indigo-600 bg-white/70 hover:bg-white rounded-xl border border-slate-200/80 hover:border-indigo-200 shadow-2xs hover:shadow-xs transition-all cursor-pointer"
            >
              <Plus class="w-3.5 h-3.5" />
              <span>Tambah Kartu</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirm Delete Card Modal -->
    <ConfirmModal
      :is-open="isDeleteConfirmOpen"
      :title="`Hapus '${cardToDelete?.title}'?`"
      message="Apakah Anda yakin ingin menghapus kartu ini? Jika kartu berada di kolom Lunas, saldo dompet akan otomatis di-refund."
      confirm-text="Hapus Kartu"
      cancel-text="Batal"
      :is-danger="true"
      @confirm="executeDeleteCard"
      @cancel="isDeleteConfirmOpen = false"
    />
  </div>
</template>
