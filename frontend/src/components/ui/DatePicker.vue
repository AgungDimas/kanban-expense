<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, X } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: 'Pilih tanggal...',
  },
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const containerRef = ref(null)

// Current view year & month (0-indexed)
const today = new Date()
const viewYear = ref(today.getFullYear())
const viewMonth = ref(today.getMonth())

const monthsIndo = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]
const dayNames = ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab']

function toggleCalendar() {
  isOpen.value = !isOpen.value
  if (isOpen.value && props.modelValue) {
    const parts = props.modelValue.split('-')
    if (parts.length === 3) {
      viewYear.value = parseInt(parts[0], 10)
      viewMonth.value = parseInt(parts[1], 10) - 1
    }
  }
}

function prevMonth() {
  if (viewMonth.value === 0) {
    viewMonth.value = 11
    viewYear.value--
  } else {
    viewMonth.value--
  }
}

function nextMonth() {
  if (viewMonth.value === 11) {
    viewMonth.value = 0
    viewYear.value++
  } else {
    viewMonth.value++
  }
}

// Generate calendar cells
const calendarDays = computed(() => {
  const year = viewYear.value
  const month = viewMonth.value

  const firstDayIndex = new Date(year, month, 1).getDay()
  const daysInCurrentMonth = new Date(year, month + 1, 0).getDate()
  const daysInPrevMonth = new Date(year, month, 0).getDate()

  const days = []

  // Prev month padding
  for (let i = firstDayIndex - 1; i >= 0; i--) {
    const d = daysInPrevMonth - i
    const prevMonthIdx = month === 0 ? 11 : month - 1
    const prevYear = month === 0 ? year - 1 : year
    days.push({
      dateNum: d,
      isoDate: formatDateIso(prevYear, prevMonthIdx + 1, d),
      isCurrentMonth: false,
    })
  }

  // Current month days
  for (let d = 1; d <= daysInCurrentMonth; d++) {
    days.push({
      dateNum: d,
      isoDate: formatDateIso(year, month + 1, d),
      isCurrentMonth: true,
    })
  }

  // Next month padding to fill 35 or 42 cells
  const remainingCells = 42 - days.length
  for (let d = 1; d <= remainingCells && days.length < 35; d++) {
    const nextMonthIdx = month === 11 ? 0 : month + 1
    const nextYear = month === 11 ? year + 1 : year
    days.push({
      dateNum: d,
      isoDate: formatDateIso(nextYear, nextMonthIdx + 1, d),
      isCurrentMonth: false,
    })
  }

  return days
})

function formatDateIso(y, m, d) {
  const mm = String(m).padStart(2, '0')
  const dd = String(d).padStart(2, '0')
  return `${y}-${mm}-${dd}`
}

function selectDate(isoDate) {
  emit('update:modelValue', isoDate)
  isOpen.value = false
}

function setToday() {
  const now = new Date()
  const iso = formatDateIso(now.getFullYear(), now.getMonth() + 1, now.getDate())
  selectDate(iso)
}

function setTomorrow() {
  const tm = new Date()
  tm.setDate(tm.getDate() + 1)
  const iso = formatDateIso(tm.getFullYear(), tm.getMonth() + 1, tm.getDate())
  selectDate(iso)
}

function setEndOfMonth() {
  const end = new Date(viewYear.value, viewMonth.value + 1, 0)
  const iso = formatDateIso(end.getFullYear(), end.getMonth() + 1, end.getDate())
  selectDate(iso)
}

function clearDate() {
  emit('update:modelValue', '')
  isOpen.value = false
}

const formattedDisplay = computed(() => {
  if (!props.modelValue) return ''
  const parts = props.modelValue.split('-')
  if (parts.length === 3) {
    const y = parts[0]
    const m = monthsIndo[parseInt(parts[1], 10) - 1]
    const d = parseInt(parts[2], 10)
    return `${d} ${m} ${y}`
  }
  return props.modelValue
})

const todayIso = computed(() => {
  const n = new Date()
  return formatDateIso(n.getFullYear(), n.getMonth() + 1, n.getDate())
})

function handleClickOutside(e) {
  if (containerRef.value && !containerRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="containerRef" class="relative w-full text-xs">
    <!-- Trigger Input Button -->
    <div
      @click="toggleCalendar"
      class="w-full flex items-center justify-between gap-2 px-3 py-2 bg-white border rounded-xl shadow-2xs transition-all cursor-pointer select-none"
      :class="isOpen ? 'border-indigo-500 ring-2 ring-indigo-500/20' : 'border-slate-300 hover:border-slate-400'"
    >
      <div class="flex items-center gap-2 truncate">
        <CalendarIcon class="w-3.5 h-3.5 text-slate-400 shrink-0" />
        <span v-if="formattedDisplay" class="font-semibold text-slate-800 truncate">
          {{ formattedDisplay }}
        </span>
        <span v-else class="text-slate-400 font-normal truncate">
          {{ placeholder }}
        </span>
      </div>

      <button
        v-if="modelValue"
        type="button"
        @click.stop="clearDate"
        class="text-slate-400 hover:text-slate-600 p-0.5 rounded-md hover:bg-slate-100"
      >
        <X class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Calendar Popover -->
    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="transform opacity-0 scale-95 -translate-y-1"
      enter-to-class="transform opacity-100 scale-100 translate-y-0"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="transform opacity-100 scale-100 translate-y-0"
      leave-to-class="transform opacity-0 scale-95 -translate-y-1"
    >
      <div
        v-if="isOpen"
        class="absolute left-0 z-50 mt-1 w-72 rounded-2xl bg-white border border-slate-200 shadow-xl p-3.5 space-y-3"
      >
        <!-- Header Month & Year -->
        <div class="flex items-center justify-between">
          <button
            type="button"
            @click="prevMonth"
            class="p-1 rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition-colors cursor-pointer"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>

          <span class="font-bold text-xs text-slate-800">
            {{ monthsIndo[viewMonth] }} {{ viewYear }}
          </span>

          <button
            type="button"
            @click="nextMonth"
            class="p-1 rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition-colors cursor-pointer"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>

        <!-- Days of Week Header -->
        <div class="grid grid-cols-7 gap-1 text-center font-bold text-[10px] text-slate-400">
          <span v-for="d in dayNames" :key="d">{{ d }}</span>
        </div>

        <!-- Day Cells Grid -->
        <div class="grid grid-cols-7 gap-1 text-center text-xs">
          <button
            v-for="cell in calendarDays"
            :key="cell.isoDate"
            type="button"
            @click="selectDate(cell.isoDate)"
            class="h-7 w-7 mx-auto rounded-lg flex items-center justify-center font-medium transition-colors cursor-pointer"
            :class="[
              cell.isoDate === modelValue
                ? 'bg-indigo-600 text-white font-bold shadow-xs'
                : cell.isoDate === todayIso
                ? 'border border-indigo-500 text-indigo-600 font-bold'
                : cell.isCurrentMonth
                ? 'text-slate-700 hover:bg-slate-100'
                : 'text-slate-300 hover:bg-slate-50',
            ]"
          >
            {{ cell.dateNum }}
          </button>
        </div>

        <!-- Quick Select Shortcuts -->
        <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] gap-1">
          <button
            type="button"
            @click="setToday"
            class="px-2 py-0.5 rounded-md text-slate-600 hover:bg-slate-100 font-medium"
          >
            Hari Ini
          </button>
          <button
            type="button"
            @click="setTomorrow"
            class="px-2 py-0.5 rounded-md text-slate-600 hover:bg-slate-100 font-medium"
          >
            Besok
          </button>
          <button
            type="button"
            @click="setEndOfMonth"
            class="px-2 py-0.5 rounded-md text-slate-600 hover:bg-slate-100 font-medium"
          >
            Akhir Bulan
          </button>
          <button
            type="button"
            @click="clearDate"
            class="px-2 py-0.5 rounded-md text-rose-600 hover:bg-rose-50 font-medium ml-auto"
          >
            Hapus
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>
