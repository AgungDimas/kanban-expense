<script setup>
import { computed } from 'vue'
import { useWalletStore } from '../stores/walletStore'
import { useBoardStore } from '../stores/boardStore'
import { formatRupiah } from '../utils/formatters'
import { Wallet, Clock, CheckCircle2, Bookmark, TrendingUp } from 'lucide-vue-next'

const walletStore = useWalletStore()
const boardStore = useBoardStore()

const totalBalance = computed(() => walletStore.totalBalance)

// Find columns
const unpaidColumn = computed(() =>
  boardStore.columns.find((c) => c.name.toLowerCase().includes('tagihan') || c.name.toLowerCase().includes('belum'))
)

const paidColumn = computed(() =>
  boardStore.columns.find((c) => c.deducts_balance)
)

const wishlistColumn = computed(() =>
  boardStore.columns.find((c) => c.name.toLowerCase().includes('wishlist') || c.name.toLowerCase().includes('rencana'))
)

const totalUnpaid = computed(() => {
  if (!unpaidColumn.value?.cards) return 0
  return unpaidColumn.value.cards.reduce((sum, c) => sum + Number(c.amount || 0), 0)
})

const totalPaid = computed(() => {
  if (!paidColumn.value?.cards) return 0
  return paidColumn.value.cards.reduce((sum, c) => sum + Number(c.amount || 0), 0)
})

const totalWishlist = computed(() => {
  if (!wishlistColumn.value?.cards) return 0
  return wishlistColumn.value.cards.reduce((sum, c) => sum + Number(c.amount || 0), 0)
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <!-- 1. Total Saldo -->
      <div class="bg-white border border-slate-200/90 rounded-2xl p-3.5 shadow-2xs flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
          <Wallet class="w-5 h-5" />
        </div>
        <div class="min-w-0">
          <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block truncate">Total Saldo</span>
          <span class="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight truncate block">
            {{ formatRupiah(totalBalance) }}
          </span>
        </div>
      </div>

      <!-- 2. Tagihan Belum Dibayar -->
      <div class="bg-white border border-slate-200/90 rounded-2xl p-3.5 shadow-2xs flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
          <Clock class="w-5 h-5" />
        </div>
        <div class="min-w-0">
          <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block truncate">Tagihan Pending</span>
          <span class="text-sm sm:text-base font-extrabold text-amber-700 tracking-tight truncate block">
            {{ formatRupiah(totalUnpaid) }}
          </span>
        </div>
      </div>

      <!-- 3. Pengeluaran Lunas -->
      <div class="bg-white border border-slate-200/90 rounded-2xl p-3.5 shadow-2xs flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
          <CheckCircle2 class="w-5 h-5" />
        </div>
        <div class="min-w-0">
          <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block truncate">Total Terbayar</span>
          <span class="text-sm sm:text-base font-extrabold text-indigo-700 tracking-tight truncate block">
            {{ formatRupiah(totalPaid) }}
          </span>
        </div>
      </div>

      <!-- 4. Rencana / Wishlist -->
      <div class="bg-white border border-slate-200/90 rounded-2xl p-3.5 shadow-2xs flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
          <Bookmark class="w-5 h-5" />
        </div>
        <div class="min-w-0">
          <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block truncate">Wishlist Target</span>
          <span class="text-sm sm:text-base font-extrabold text-purple-700 tracking-tight truncate block">
            {{ formatRupiah(totalWishlist) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
