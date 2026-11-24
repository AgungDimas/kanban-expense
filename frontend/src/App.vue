<script setup>
import { ref, onMounted } from 'vue'
import { useBoardStore } from './stores/boardStore'
import { useWalletStore } from './stores/walletStore'
import Header from './components/Header.vue'
import StatsBar from './components/StatsBar.vue'
import KanbanBoard from './components/KanbanBoard.vue'
import CalendarView from './views/CalendarView.vue'
import AnalyticsView from './views/AnalyticsView.vue'
import ExpenseModal from './components/ExpenseModal.vue'
import WalletManageModal from './components/WalletManageModal.vue'
import CardDetailModal from './components/CardDetailModal.vue'
import Toast from './components/Toast.vue'
import { Loader2 } from 'lucide-vue-next'

const boardStore = useBoardStore()
const walletStore = useWalletStore()

const activeTab = ref('kanban')

const isExpenseModalOpen = ref(false)
const selectedColumnIdForModal = ref(null)
const isWalletManageModalOpen = ref(false)

// Card detail state
const isCardDetailOpen = ref(false)
const selectedCard = ref(null)

function openExpenseModal(columnId = null) {
  selectedColumnIdForModal.value = columnId
  isExpenseModalOpen.value = true
}

function openWalletManageModal() {
  isWalletManageModalOpen.value = true
}

function handleCardClick(card) {
  selectedCard.value = card
  isCardDetailOpen.value = true
}

onMounted(async () => {
  await Promise.all([
    boardStore.fetchBoard(),
    boardStore.fetchCategories(),
    walletStore.fetchWallets(),
  ])
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800 antialiased">
    <!-- Header with Tabs -->
    <Header
      :active-tab="activeTab"
      @change-tab="(tab) => activeTab = tab"
      @open-expense-modal="openExpenseModal"
      @open-wallet-manage-modal="openWalletManageModal"
    />

    <!-- Quick Stats Bar (shown on Kanban & Analytics) -->
    <StatsBar v-if="activeTab === 'kanban'" />

    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col relative overflow-hidden">
      <!-- Loading State -->
      <div
        v-if="boardStore.loading && boardStore.columns.length === 0"
        class="flex-1 flex flex-col items-center justify-center p-8 gap-3 text-slate-400"
      >
        <Loader2 class="w-8 h-8 animate-spin text-indigo-600" />
        <span class="text-sm font-medium">Memuat data papan Kanban...</span>
      </div>

      <!-- Tab 1: Kanban Board View -->
      <KanbanBoard
        v-else-if="activeTab === 'kanban'"
        @open-expense-modal-with-column="openExpenseModal"
        @card-click="handleCardClick"
      />

      <!-- Tab 2: Calendar Schedule View -->
      <div v-else-if="activeTab === 'calendar'" class="flex-1 overflow-y-auto">
        <CalendarView
          @card-click="handleCardClick"
          @open-expense-modal="openExpenseModal"
        />
      </div>

      <!-- Tab 3: Analytics & Budget Breakdown View -->
      <div v-else-if="activeTab === 'analytics'" class="flex-1 overflow-y-auto">
        <AnalyticsView />
      </div>
    </main>

    <!-- Modals & Toasts -->
    <ExpenseModal
      :is-open="isExpenseModalOpen"
      :default-column-id="selectedColumnIdForModal"
      @close="isExpenseModalOpen = false"
    />

    <WalletManageModal
      :is-open="isWalletManageModalOpen"
      @close="isWalletManageModalOpen = false"
    />

    <CardDetailModal
      :is-open="isCardDetailOpen"
      :card="selectedCard"
      @close="isCardDetailOpen = false"
    />

    <Toast />
  </div>
</template>
