<script setup>
import { computed } from 'vue'
import { formatRupiah, formatDate } from '../utils/formatters'
import { Calendar, CheckCircle2, Wallet, Trash2, GripVertical } from 'lucide-vue-next'

const props = defineProps({
  card: {
    type: Object,
    required: true,
  },
  isPaid: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['delete', 'click'])

const formattedAmount = computed(() => formatRupiah(props.card.amount))
const formattedDueDate = computed(() => formatDate(props.card.due_date))
const formattedPaidDate = computed(() => formatDate(props.card.paid_at))
</script>

<template>
  <div
    @click="emit('click', card)"
    class="group relative bg-white border border-slate-200/90 hover:border-indigo-400 rounded-xl p-3.5 shadow-2xs hover:shadow-md transition-all duration-200 select-none cursor-pointer mb-3"
  >
    <!-- Card Top Row: Category Badge & Delete Action -->
    <div class="flex items-center justify-between gap-2 mb-2">
      <div class="flex items-center gap-1.5">
        <GripVertical class="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600 transition-colors cursor-grab" />
        <span
          v-if="card.category_name"
          class="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold tracking-wide"
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
          class="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold text-slate-500 bg-slate-100"
        >
          Umum
        </span>
      </div>

      <button
        @click.stop="emit('delete', card)"
        title="Hapus Kartu"
        class="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-rose-600 p-1 rounded-md hover:bg-rose-50 transition-all cursor-pointer"
      >
        <Trash2 class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Title -->
    <h3 class="text-sm font-semibold text-slate-900 group-hover:text-indigo-900 transition-colors line-clamp-2 mb-1.5">
      {{ card.title }}
    </h3>

    <!-- Notes if any -->
    <p v-if="card.notes" class="text-xs text-slate-500 line-clamp-1 mb-2">
      {{ card.notes }}
    </p>

    <!-- Amount -->
    <div class="text-base font-extrabold text-slate-900 tracking-tight mb-3">
      {{ formattedAmount }}
    </div>

    <!-- Bottom Meta Row: Wallet & Due Date / Paid Status -->
    <div class="flex items-center justify-between gap-2 pt-2 border-t border-slate-100 text-[11px] text-slate-500">
      <!-- Wallet Info -->
      <div class="flex items-center gap-1 font-medium text-slate-600 truncate">
        <Wallet class="w-3.5 h-3.5 text-slate-400 shrink-0" />
        <span class="truncate">{{ card.wallet_name || 'Dompet' }}</span>
      </div>

      <!-- Paid or Due Date -->
      <div v-if="isPaid || card.paid_at" class="flex items-center gap-1 font-semibold text-emerald-600 shrink-0">
        <CheckCircle2 class="w-3.5 h-3.5" />
        <span>Lunas {{ formattedPaidDate ? `(${formattedPaidDate})` : '' }}</span>
      </div>
      <div v-else-if="card.due_date" class="flex items-center gap-1 font-medium text-slate-500 shrink-0">
        <Calendar class="w-3.5 h-3.5 text-slate-400" />
        <span>{{ formattedDueDate }}</span>
      </div>
    </div>
  </div>
</template>
