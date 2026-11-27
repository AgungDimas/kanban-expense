<script setup>
import { computed } from 'vue'
import { useBoardStore } from '../stores/boardStore'
import { useWalletStore } from '../stores/walletStore'
import { formatRupiah } from '../utils/formatters'
import {
  PieChart,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Wallet,
  Sparkles,
} from 'lucide-vue-next'

const boardStore = useBoardStore()
const walletStore = useWalletStore()

// Flat list of all cards
const allCards = computed(() => {
  const list = []
  for (const col of boardStore.columns) {
    if (col.cards) {
      for (const card of col.cards) {
        list.push({
          ...card,
          is_paid: col.deducts_balance || !!card.paid_at,
        })
      }
    }
  }
  return list
})

// Budget Tracking per Category
const categoryBudgetStats = computed(() => {
  return boardStore.categories.map((cat) => {
    // Sum spent (cards that are paid or all cards in this category)
    const categoryCards = allCards.value.filter((c) => c.category === cat.id)
    const spentPaid = categoryCards
      .filter((c) => c.is_paid)
      .reduce((sum, c) => sum + Number(c.amount || 0), 0)
    const spentTotal = categoryCards.reduce((sum, c) => sum + Number(c.amount || 0), 0)

    const budget = Number(cat.monthly_budget || 0)
    const percentPaid = budget > 0 ? Math.min(Math.round((spentPaid / budget) * 100), 100) : 0
    const percentTotal = budget > 0 ? Math.round((spentTotal / budget) * 100) : 0
    const remaining = Math.max(budget - spentPaid, 0)
    const isOverbudget = spentPaid > budget

    return {
      id: cat.id,
      name: cat.name,
      color: cat.color,
      budget,
      spentPaid,
      spentTotal,
      percentPaid,
      percentTotal,
      remaining,
      isOverbudget,
      cardCount: categoryCards.length,
    }
  })
})

// Wallet Spending Breakdown
const walletStats = computed(() => {
  return walletStore.wallets.map((w) => {
    const walletCards = allCards.value.filter((c) => c.wallet === w.id)
    const totalSpent = walletCards
      .filter((c) => c.is_paid)
      .reduce((sum, c) => sum + Number(c.amount || 0), 0)
    const pendingSpent = walletCards
      .filter((c) => !c.is_paid)
      .reduce((sum, c) => sum + Number(c.amount || 0), 0)

    return {
      id: w.id,
      name: w.name,
      balance: Number(w.balance || 0),
      totalSpent,
      pendingSpent,
      cardCount: walletCards.length,
    }
  })
})

// Quick Smart Insights
const largestExpense = computed(() => {
  if (allCards.value.length === 0) return null
  return [...allCards.value].sort((a, b) => Number(b.amount) - Number(a.amount))[0]
})

const topSpentCategory = computed(() => {
  const sorted = [...categoryBudgetStats.value].sort((a, b) => b.spentPaid - a.spentPaid)
  return sorted[0] || null
})

const totalMonthlyPaid = computed(() => {
  return allCards.value
    .filter((c) => c.is_paid)
    .reduce((sum, c) => sum + Number(c.amount || 0), 0)
})

const totalMonthlyBudget = computed(() => {
  return boardStore.categories.reduce((sum, c) => sum + Number(c.monthly_budget || 0), 0)
})

const overallBudgetPercent = computed(() => {
  if (totalMonthlyBudget.value === 0) return 0
  return Math.round((totalMonthlyPaid.value / totalMonthlyBudget.value) * 100)
})

// Donut chart calculation for Category Breakdown
const donutSlices = computed(() => {
  const total = totalMonthlyPaid.value
  if (total <= 0) return []

  const circumference = 2 * Math.PI * 40 // ~251.327
  let cumulativePercent = 0

  return categoryBudgetStats.value
    .filter((cat) => cat.spentPaid > 0)
    .map((cat) => {
      const percent = cat.spentPaid / total
      const strokeDasharray = `${(percent * circumference).toFixed(2)} ${circumference.toFixed(2)}`
      const strokeDashoffset = (-(cumulativePercent * circumference)).toFixed(2)
      cumulativePercent += percent

      return {
        id: cat.id,
        name: cat.name,
        color: cat.color,
        amount: cat.spentPaid,
        percentage: Math.round(percent * 100),
        strokeDasharray,
        strokeDashoffset,
      }
    })
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 space-y-5">
    <!-- Header Page -->
    <div class="flex items-center justify-between bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
          <PieChart class="w-5 h-5" />
        </div>
        <div>
          <h2 class="text-base font-bold text-slate-900">
            Laporan Anggaran & Analitik
          </h2>
          <p class="text-xs text-slate-500">
            Pantau realisasi pengeluaran terhadap batas budget bulanan Anda
          </p>
        </div>
      </div>

      <div class="hidden sm:flex items-center gap-2">
        <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-indigo-50 text-indigo-700">
          <Sparkles class="w-3.5 h-3.5" />
          <span>Real-time Financial Insight</span>
        </span>
      </div>
    </div>

    <!-- Quick Insights Top Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
      <!-- Total Budget vs Terpakai -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs space-y-2">
        <span class="text-xs font-semibold text-slate-500">Total Budget Kategori</span>
        <div class="text-lg font-extrabold text-slate-900">
          {{ formatRupiah(totalMonthlyBudget) }}
        </div>
        <div class="flex items-center justify-between text-xs pt-1 border-t border-slate-100">
          <span class="text-slate-500">Realisasi ({{ overallBudgetPercent }}%):</span>
          <span class="font-bold text-indigo-600">{{ formatRupiah(totalMonthlyPaid) }}</span>
        </div>
      </div>

      <!-- Kategori Terbanyak Pengeluaran -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs space-y-2">
        <span class="text-xs font-semibold text-slate-500">Kategori Terboros</span>
        <div class="text-lg font-extrabold text-slate-900 truncate">
          {{ topSpentCategory?.name || '-' }}
        </div>
        <div class="flex items-center justify-between text-xs pt-1 border-t border-slate-100">
          <span class="text-slate-500">Total Terbayar:</span>
          <span class="font-bold text-rose-600">
            {{ formatRupiah(topSpentCategory?.spentPaid || 0) }}
          </span>
        </div>
      </div>

      <!-- Pengeluaran Nominal Terbesar -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs space-y-2">
        <span class="text-xs font-semibold text-slate-500">Item Terbesar</span>
        <div class="text-lg font-extrabold text-slate-900 truncate">
          {{ largestExpense?.title || '-' }}
        </div>
        <div class="flex items-center justify-between text-xs pt-1 border-t border-slate-100">
          <span class="text-slate-500">Nominal:</span>
          <span class="font-bold text-slate-900">
            {{ formatRupiah(largestExpense?.amount || 0) }}
          </span>
        </div>
      </div>

      <!-- Total Saldo Bersih Dompet -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs space-y-2">
        <span class="text-xs font-semibold text-slate-500">Sisa Likuiditas Dompet</span>
        <div class="text-lg font-extrabold text-emerald-600">
          {{ formatRupiah(walletStore.totalBalance) }}
        </div>
        <div class="flex items-center justify-between text-xs pt-1 border-t border-slate-100">
          <span class="text-slate-500">Jumlah Dompet:</span>
          <span class="font-bold text-slate-700">{{ walletStore.wallets.length }} Dompet</span>
        </div>
      </div>
    </div>

    <!-- Main Grid: Category Budget Bars & Wallet Breakdown -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- 2 Columns: Donut Chart & Category Budget Progress -->
      <div class="lg:col-span-2 space-y-5">
        <!-- Donut Visual Chart Card -->
        <div class="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-2xs space-y-4">
          <div class="border-b border-slate-100 pb-3 flex items-center justify-between">
            <div>
              <h3 class="text-sm font-bold text-slate-900">Distribusi Pengeluaran Kategori</h3>
              <p class="text-xs text-slate-500">Proporsi uang yang sudah terbayar per kategori</p>
            </div>
            <span class="text-xs font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-lg">
              Total: {{ formatRupiah(totalMonthlyPaid) }}
            </span>
          </div>

          <div v-if="donutSlices.length > 0" class="flex flex-col sm:flex-row items-center justify-around gap-6 pt-2">
            <!-- SVG Donut -->
            <div class="relative w-44 h-44 shrink-0 flex items-center justify-center">
              <svg viewBox="0 0 100 100" class="w-full h-full transform -rotate-90">
                <!-- Background track -->
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="transparent"
                  stroke="#f1f5f9"
                  stroke-width="12"
                />
                <!-- Slices -->
                <circle
                  v-for="slice in donutSlices"
                  :key="slice.id"
                  cx="50"
                  cy="50"
                  r="40"
                  fill="transparent"
                  :stroke="slice.color"
                  stroke-width="12"
                  :stroke-dasharray="slice.strokeDasharray"
                  :stroke-dashoffset="slice.strokeDashoffset"
                  class="transition-all duration-500 hover:opacity-80"
                />
              </svg>
              <!-- Center Text inside Donut -->
              <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-2 pointer-events-none">
                <span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Lunas</span>
                <span class="text-xs font-extrabold text-slate-900 leading-tight">
                  {{ formatRupiah(totalMonthlyPaid) }}
                </span>
              </div>
            </div>

            <!-- Legend List -->
            <div class="flex-1 w-full space-y-2.5 max-h-48 overflow-y-auto pr-1">
              <div
                v-for="slice in donutSlices"
                :key="slice.id"
                class="flex items-center justify-between text-xs p-2 rounded-xl bg-slate-50/80 border border-slate-150"
              >
                <div class="flex items-center gap-2 min-w-0">
                  <span
                    class="w-3 h-3 rounded-full shrink-0"
                    :style="{ backgroundColor: slice.color }"
                  ></span>
                  <span class="font-semibold text-slate-800 truncate">{{ slice.name }}</span>
                </div>
                <div class="flex items-center gap-2 shrink-0">
                  <span class="font-extrabold text-slate-900">{{ formatRupiah(slice.amount) }}</span>
                  <span class="text-[11px] font-bold text-slate-500 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                    {{ slice.percentage }}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State for Donut -->
          <div
            v-else
            class="py-8 text-center text-xs text-slate-400 border-2 border-dashed border-slate-200 rounded-xl"
          >
            Belum ada transaksi pengeluaran lunas untuk divisualisasikan. Pindahkan kartu ke kolom Lunas untuk melihat grafik.
          </div>
        </div>

        <!-- Category Budget Progress Bars -->
        <div class="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-2xs space-y-4">
          <div class="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 class="text-sm font-bold text-slate-900">Realisasi Budget per Kategori</h3>
              <p class="text-xs text-slate-500">Perbandingan batas budget bulanan vs uang yang sudah lunas</p>
            </div>
          </div>

        <div class="space-y-4">
          <div
            v-for="cat in categoryBudgetStats"
            :key="cat.id"
            class="p-3.5 rounded-xl border border-slate-150 hover:border-slate-300 transition-all space-y-2 bg-slate-50/50"
          >
            <!-- Title & Numbers -->
            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center gap-2">
                <span
                  class="w-3 h-3 rounded-full"
                  :style="{ backgroundColor: cat.color }"
                ></span>
                <span class="font-bold text-slate-800 text-sm">{{ cat.name }}</span>
                <span class="text-[11px] text-slate-400 font-medium">({{ cat.cardCount }} kartu)</span>
              </div>

              <div class="text-right">
                <span class="font-bold text-slate-900">{{ formatRupiah(cat.spentPaid) }}</span>
                <span class="text-slate-400 font-normal"> / {{ formatRupiah(cat.budget) }}</span>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :style="{
                  width: `${Math.min(cat.percentPaid, 100)}%`,
                  backgroundColor: cat.isOverbudget ? '#ef4444' : cat.color,
                }"
              ></div>
            </div>

            <!-- Footer Meta -->
            <div class="flex items-center justify-between text-[11px]">
              <span
                v-if="cat.isOverbudget"
                class="font-bold text-rose-600 flex items-center gap-1"
              >
                <AlertTriangle class="w-3 h-3" />
                <span>Overbudget! Melebihi batas {{ cat.percentTotal }}%</span>
              </span>
              <span v-else class="text-slate-500">
                Sisa budget: <strong class="text-slate-700">{{ formatRupiah(cat.remaining) }}</strong>
              </span>

              <span class="font-bold text-slate-600">
                {{ cat.percentPaid }}% terpakai
              </span>
            </div>
          </div>

          <div
            v-if="categoryBudgetStats.length === 0"
            class="p-8 text-center text-xs text-slate-400"
          >
            Belum ada kategori pengeluaran.
          </div>
        </div>
      </div>
    </div>

      <!-- 1 Column: Wallet Breakdown -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-2xs space-y-4">
        <div class="border-b border-slate-100 pb-3">
          <h3 class="text-sm font-bold text-slate-900">Distribusi Dompet</h3>
          <p class="text-xs text-slate-500">Pengeluaran & saldo per akun rekening</p>
        </div>

        <div class="space-y-3">
          <div
            v-for="w in walletStats"
            :key="w.id"
            class="p-3 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-slate-600">
                  <Wallet class="w-3.5 h-3.5" />
                </div>
                <span class="text-xs font-bold text-slate-800">{{ w.name }}</span>
              </div>
              <span class="text-xs font-extrabold text-emerald-700">
                {{ formatRupiah(w.balance) }}
              </span>
            </div>

            <div class="flex items-center justify-between text-[11px] pt-1.5 border-t border-slate-200/60 text-slate-500">
              <span>Pengeluaran Lunas:</span>
              <span class="font-semibold text-slate-800">{{ formatRupiah(w.totalSpent) }}</span>
            </div>

            <div class="flex items-center justify-between text-[11px] text-slate-500">
              <span>Tagihan Belum Bayar:</span>
              <span class="font-semibold text-amber-700">{{ formatRupiah(w.pendingSpent) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
