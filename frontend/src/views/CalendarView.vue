<script setup>
import { ref, computed } from 'vue'
import { useBoardStore } from '../stores/boardStore'
import { formatRupiah, formatDate } from '../utils/formatters'
import {
  ChevronLeft,
  ChevronRight,
  Calendar as CalendarIcon,
  CheckCircle2,
  Clock,
  Plus,
} from 'lucide-vue-next'

const emit = defineEmits(['cardClick', 'openExpenseModal'])
const boardStore = useBoardStore()

const today = new Date()
const currentYear = ref(today.getFullYear())
const currentMonth = ref(today.getMonth())

const monthsIndo = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]
const dayNames = ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab']

function prevMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

function nextMonth() {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

function goToToday() {
  currentYear.value = today.getFullYear()
  currentMonth.value = today.getMonth()
}

// Flat list of all cards across all columns
const allCards = computed(() => {
  const list = []
  for (const col of boardStore.columns) {
    if (col.cards) {
      for (const card of col.cards) {
        list.push({
          ...card,
          column_deducts_balance: col.deducts_balance,
        })
      }
    }
  }
  return list
})

// Map cards by due_date (YYYY-MM-DD)
const cardsByDate = computed(() => {
  const map = {}
  for (const card of allCards.value) {
    if (card.due_date) {
      if (!map[card.due_date]) {
        map[card.due_date] = []
      }
      map[card.due_date].push(card)
    }
  }
  return map
})

function formatDateIso(y, m, d) {
  const mm = String(m).padStart(2, '0')
  const dd = String(d).padStart(2, '0')
  return `${y}-${mm}-${dd}`
}

const calendarGrid = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value

  const firstDayOfWeek = new Date(year, month, 1).getDay()
  const daysInCurrent = new Date(year, month + 1, 0).getDate()
  const daysInPrev = new Date(year, month, 0).getDate()

  const grid = []

  // Prev month padding
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const d = daysInPrev - i
    const prevMonthIdx = month === 0 ? 11 : month - 1
    const prevYear = month === 0 ? year - 1 : year
    const iso = formatDateIso(prevYear, prevMonthIdx + 1, d)
    grid.push({
      dateNum: d,
      isoDate: iso,
      isCurrentMonth: false,
      cards: cardsByDate.value[iso] || [],
    })
  }

  // Current month
  for (let d = 1; d <= daysInCurrent; d++) {
    const iso = formatDateIso(year, month + 1, d)
    grid.push({
      dateNum: d,
      isoDate: iso,
      isCurrentMonth: true,
      cards: cardsByDate.value[iso] || [],
    })
  }

  // Next month padding
  const totalCells = grid.length > 35 ? 42 : 35
  const remaining = totalCells - grid.length
  for (let d = 1; d <= remaining; d++) {
    const nextMonthIdx = month === 11 ? 0 : month + 1
    const nextYear = month === 11 ? year + 1 : year
    const iso = formatDateIso(nextYear, nextMonthIdx + 1, d)
    grid.push({
      dateNum: d,
      isoDate: iso,
      isCurrentMonth: false,
      cards: cardsByDate.value[iso] || [],
    })
  }

  return grid
})

const todayIso = computed(() => {
  return formatDateIso(today.getFullYear(), today.getMonth() + 1, today.getDate())
})

// Monthly totals
const monthlyTotals = computed(() => {
  let totalDue = 0
  let totalPaid = 0
  let countDue = 0

  for (const cell of calendarGrid.value) {
    if (cell.isCurrentMonth && cell.cards.length > 0) {
      for (const c of cell.cards) {
        totalDue += Number(c.amount || 0)
        countDue++
        if (c.column_deducts_balance || c.paid_at) {
          totalPaid += Number(c.amount || 0)
        }
      }
    }
  }

  return { totalDue, totalPaid, countDue, totalPending: totalDue - totalPaid }
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 space-y-4">
    <!-- Calendar Controls Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
          <CalendarIcon class="w-5 h-5" />
        </div>
        <div>
          <h2 class="text-base font-bold text-slate-900">
            Jadwal & Kalender Tagihan
          </h2>
          <p class="text-xs text-slate-500">
            Visualisasi jatuh tempo tagihan dan rencana pembayaran bulanan
          </p>
        </div>
      </div>

      <!-- Navigation & Month Selector -->
      <div class="flex items-center gap-2">
        <button
          @click="goToToday"
          class="px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors cursor-pointer"
        >
          Hari Ini
        </button>

        <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl">
          <button
            @click="prevMonth"
            class="p-1 rounded-lg text-slate-600 hover:bg-white hover:text-slate-900 transition-colors cursor-pointer"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>
          <span class="px-3 text-xs font-bold text-slate-800 min-w-36 text-center">
            {{ monthsIndo[currentMonth] }} {{ currentYear }}
          </span>
          <button
            @click="nextMonth"
            class="p-1 rounded-lg text-slate-600 hover:bg-white hover:text-slate-900 transition-colors cursor-pointer"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>

        <button
          @click="emit('openExpenseModal')"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs transition-colors cursor-pointer"
        >
          <Plus class="w-3.5 h-3.5 stroke-[2.5]" />
          <span>Tambah Tagihan</span>
        </button>
      </div>
    </div>

    <!-- Monthly Summary Bar -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <div class="bg-white p-3.5 rounded-xl border border-slate-200 text-xs">
        <span class="text-slate-500 font-medium block">Total Tagihan Bulan Ini</span>
        <span class="text-base font-extrabold text-slate-900 mt-0.5 block">
          {{ formatRupiah(monthlyTotals.totalDue) }}
        </span>
      </div>

      <div class="bg-white p-3.5 rounded-xl border border-slate-200 text-xs">
        <span class="text-slate-500 font-medium block">Sudah Terbayar</span>
        <span class="text-base font-extrabold text-emerald-700 mt-0.5 block">
          {{ formatRupiah(monthlyTotals.totalPaid) }}
        </span>
      </div>

      <div class="bg-white p-3.5 rounded-xl border border-slate-200 text-xs">
        <span class="text-slate-500 font-medium block">Sisa Belum Bayar</span>
        <span class="text-base font-extrabold text-amber-700 mt-0.5 block">
          {{ formatRupiah(monthlyTotals.totalPending) }}
        </span>
      </div>
    </div>

    <!-- Calendar Month Table View -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
      <!-- Day Headers -->
      <div class="grid grid-cols-7 border-b border-slate-200 bg-slate-50/70 text-center text-xs font-bold text-slate-600 py-2.5">
        <div v-for="d in dayNames" :key="d" :class="d === 'Min' ? 'text-rose-600' : ''">
          {{ d }}
        </div>
      </div>

      <!-- Calendar Cells -->
      <div class="grid grid-cols-7 auto-rows-fr divide-x divide-y divide-slate-100">
        <div
          v-for="cell in calendarGrid"
          :key="cell.isoDate"
          class="min-h-28 p-2 flex flex-col justify-between transition-colors"
          :class="[
            cell.isCurrentMonth ? 'bg-white' : 'bg-slate-50/50',
            cell.isoDate === todayIso ? 'ring-2 ring-indigo-500/50 ring-inset bg-indigo-50/20' : '',
          ]"
        >
          <!-- Cell Top (Date Number) -->
          <div class="flex items-center justify-between mb-1">
            <span
              class="w-6 h-6 rounded-lg text-xs flex items-center justify-center font-bold"
              :class="[
                cell.isoDate === todayIso
                  ? 'bg-indigo-600 text-white shadow-2xs'
                  : cell.isCurrentMonth
                  ? 'text-slate-700'
                  : 'text-slate-300',
              ]"
            >
              {{ cell.dateNum }}
            </span>

            <span
              v-if="cell.cards.length > 0"
              class="text-[10px] font-semibold text-slate-400"
            >
              {{ cell.cards.length }} item
            </span>
          </div>

          <!-- Cards Stack on this Date -->
          <div class="space-y-1 flex-1 overflow-y-auto max-h-20">
            <div
              v-for="card in cell.cards"
              :key="card.id"
              @click="emit('cardClick', card)"
              class="group px-2 py-1 rounded-lg text-[11px] font-semibold flex items-center justify-between gap-1 transition-all cursor-pointer shadow-2xs hover:scale-102"
              :style="{
                backgroundColor: `${card.category_color || '#6366f1'}15`,
                color: card.category_color || '#4338ca',
                borderLeft: `3px solid ${card.category_color || '#6366f1'}`,
              }"
            >
              <div class="flex items-center gap-1 truncate">
                <CheckCircle2
                  v-if="card.column_deducts_balance || card.paid_at"
                  class="w-3 h-3 text-emerald-600 shrink-0"
                />
                <Clock v-else class="w-3 h-3 text-amber-500 shrink-0" />
                <span class="truncate">{{ card.title }}</span>
              </div>
              <span class="font-bold shrink-0 text-[10px]">
                {{ formatRupiah(card.amount) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
