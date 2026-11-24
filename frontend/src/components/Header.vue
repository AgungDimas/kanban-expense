<script setup>
import { computed } from 'vue'
import { useWalletStore } from '../stores/walletStore'
import { formatRupiah } from '../utils/formatters'
import {
  Wallet,
  Plus,
  CreditCard,
  Layers,
  Settings2,
  Calendar,
  PieChart,
} from 'lucide-vue-next'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'kanban',
  },
})

const emit = defineEmits(['openExpenseModal', 'openWalletManageModal', 'changeTab'])
const walletStore = useWalletStore()

const totalBalance = computed(() => walletStore.totalBalance)
const wallets = computed(() => walletStore.wallets)
</script>

<template>
  <header class="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-2xs backdrop-blur-md bg-white/95">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <!-- Brand & Total Saldo -->
        <div class="flex items-center gap-3.5 flex-wrap">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center shadow-md shadow-indigo-100">
              <Layers class="w-5 h-5" />
            </div>
            <div>
              <h1 class="text-base font-bold text-slate-900 leading-tight">Expense Kanban</h1>
              <p class="text-[10px] text-slate-500 font-medium">Smart Bill & Budget Tracker</p>
            </div>
          </div>

          <div class="h-6 w-px bg-slate-200 hidden sm:block"></div>

          <!-- Total Balance Widget (Clickable to manage wallets) -->
          <button
            @click="emit('openWalletManageModal')"
            title="Klik untuk kelola dompet"
            class="group bg-slate-50 hover:bg-slate-100 border border-slate-200/90 rounded-xl px-3 py-1 flex items-center gap-2 transition-all cursor-pointer text-left"
          >
            <div class="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center group-hover:scale-105 transition-transform">
              <Wallet class="w-3.5 h-3.5" />
            </div>
            <div>
              <span class="text-[9px] font-semibold text-slate-400 uppercase tracking-wider block">Total Saldo</span>
              <span class="text-xs font-extrabold text-slate-900 tracking-tight">
                {{ formatRupiah(totalBalance) }}
              </span>
            </div>
          </button>
        </div>

        <!-- Navigation Tabs: Kanban / Kalender / Analitik -->
        <div class="flex items-center bg-slate-100/90 p-1 rounded-xl self-start md:self-auto border border-slate-200/60 text-xs">
          <button
            @click="emit('changeTab', 'kanban')"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer"
            :class="[
              activeTab === 'kanban'
                ? 'bg-white text-indigo-700 shadow-2xs'
                : 'text-slate-600 hover:text-slate-900',
            ]"
          >
            <Layers class="w-3.5 h-3.5" />
            <span>Papan Kanban</span>
          </button>

          <button
            @click="emit('changeTab', 'calendar')"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer"
            :class="[
              activeTab === 'calendar'
                ? 'bg-white text-indigo-700 shadow-2xs'
                : 'text-slate-600 hover:text-slate-900',
            ]"
          >
            <Calendar class="w-3.5 h-3.5" />
            <span>Jadwal Tagihan</span>
          </button>

          <button
            @click="emit('changeTab', 'analytics')"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer"
            :class="[
              activeTab === 'analytics'
                ? 'bg-white text-indigo-700 shadow-2xs'
                : 'text-slate-600 hover:text-slate-900',
            ]"
          >
            <PieChart class="w-3.5 h-3.5" />
            <span>Analitik Budget</span>
          </button>
        </div>

        <!-- Wallets pills & Action Buttons -->
        <div class="flex items-center gap-2 flex-wrap">
          <!-- Action Buttons -->
          <button
            @click="emit('openWalletManageModal')"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-300 rounded-xl shadow-2xs hover:shadow-xs transition-all cursor-pointer"
          >
            <Settings2 class="w-3.5 h-3.5 text-slate-500" />
            <span>Dompet</span>
          </button>

          <button
            @click="emit('openExpenseModal')"
            class="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-sm hover:shadow-md hover:shadow-indigo-200 transition-all cursor-pointer"
          >
            <Plus class="w-4 h-4 stroke-[2.5]" />
            <span>Tambah</span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
