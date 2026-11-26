import { defineStore } from 'pinia'
import apiClient from '../api/client'
import { useWalletStore } from './walletStore'

export const useBoardStore = defineStore('board', {
  state: () => ({
    columns: [],
    categories: [],
    loading: false,
    error: null,
    toast: {
      show: false,
      message: '',
      type: 'error', // 'error' | 'success' | 'info'
    },
  }),

  actions: {
    showToast(message, type = 'error') {
      this.toast = {
        show: true,
        message,
        type,
      }
      setTimeout(() => {
        if (this.toast.message === message) {
          this.toast.show = false
        }
      }, 4500)
    },

    hideToast() {
      this.toast.show = false
    },

    async fetchBoard() {
      this.loading = true
      this.error = null
      try {
        const response = await apiClient.get('/board/')
        this.columns = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal memuat papan Kanban'
        this.showToast(this.error, 'error')
      } finally {
        this.loading = false
      }
    },

    async fetchCategories() {
      try {
        const response = await apiClient.get('/categories/')
        this.categories = response.data
      } catch (err) {
        console.error('fetchCategories error:', err)
      }
    },

    async createCategory(payload) {
      try {
        const response = await apiClient.post('/categories/', payload)
        this.categories.push(response.data)
        this.showToast(`Kategori "${response.data.name}" berhasil dibuat!`, 'success')
        return response.data
      } catch (err) {
        const msg = err.response?.data?.detail || 'Gagal membuat kategori'
        this.showToast(msg, 'error')
        throw err
      }
    },

    async updateCategory(categoryId, payload) {
      try {
        const response = await apiClient.patch(`/categories/${categoryId}/`, payload)
        const idx = this.categories.findIndex((c) => c.id === categoryId)
        if (idx !== -1) {
          this.categories[idx] = response.data
        }
        // Also update category color/name in existing cards in board
        for (const col of this.columns) {
          for (const card of col.cards) {
            if (card.category === categoryId) {
              card.category_name = response.data.name
              card.category_color = response.data.color
            }
          }
        }
        this.showToast(`Kategori "${response.data.name}" berhasil diperbarui!`, 'success')
        return response.data
      } catch (err) {
        const msg = err.response?.data?.detail || 'Gagal memperbarui kategori'
        this.showToast(msg, 'error')
        throw err
      }
    },

    async deleteCategory(categoryId) {
      try {
        await apiClient.delete(`/categories/${categoryId}/`)
        this.categories = this.categories.filter((c) => c.id !== categoryId)
        // Set category to null for cards in state
        for (const col of this.columns) {
          for (const card of col.cards) {
            if (card.category === categoryId) {
              card.category = null
              card.category_name = null
            }
          }
        }
        this.showToast('Kategori berhasil dihapus.', 'info')
      } catch (err) {
        const msg = err.response?.data?.detail || 'Gagal menghapus kategori'
        this.showToast(msg, 'error')
        throw err
      }
    },

    async downloadExportCsv() {
      try {
        const baseURL = apiClient.defaults.baseURL || 'http://127.0.0.1:8000/api'
        window.open(`${baseURL}/export/`, '_blank')
        this.showToast('Mengunduh rekapan data pengeluaran (CSV)...', 'info')
      } catch (err) {
        this.showToast('Gagal mengunduh file ekspor', 'error')
      }
    },

    async createExpense(payload) {
      const walletStore = useWalletStore()
      try {
        const response = await apiClient.post('/expenses/', payload)
        const { card, wallet } = response.data

        // Add card to corresponding column in board
        const col = this.columns.find((c) => c.id === card.column)
        if (col) {
          col.cards.push(card)
        }

        // Sync wallet
        if (wallet) {
          walletStore.syncWallet(wallet)
        }

        this.showToast(`Pengeluaran "${card.title}" berhasil ditambahkan!`, 'success')
        return card
      } catch (err) {
        const errorMsg =
          err.response?.data?.balance ||
          err.response?.data?.detail ||
          'Gagal menambahkan pengeluaran'
        this.showToast(errorMsg, 'error')
        throw err
      }
    },

    async updateExpense(cardId, payload) {
      const walletStore = useWalletStore()
      try {
        const response = await apiClient.patch(`/expenses/${cardId}/`, payload)
        const { card, wallet } = response.data

        // Update card in columns
        for (const col of this.columns) {
          const idx = col.cards.findIndex((c) => c.id === cardId)
          if (idx !== -1) {
            if (col.id === card.column) {
              col.cards[idx] = card
            } else {
              col.cards.splice(idx, 1)
              const targetCol = this.columns.find((c) => c.id === card.column)
              if (targetCol) targetCol.cards.push(card)
            }
            break
          }
        }

        if (wallet) {
          walletStore.syncWallet(wallet)
        }

        this.showToast(`Pengeluaran "${card.title}" berhasil diperbarui!`, 'success')
        return card
      } catch (err) {
        const errorMsg =
          err.response?.data?.balance ||
          err.response?.data?.detail ||
          'Gagal memperbarui pengeluaran'
        this.showToast(errorMsg, 'error')
        throw err
      }
    },

    async deleteExpense(cardId, columnId) {
      const walletStore = useWalletStore()
      try {
        const response = await apiClient.delete(`/expenses/${cardId}/`)
        // Remove from column
        const col = this.columns.find((c) => c.id === columnId)
        if (col) {
          col.cards = col.cards.filter((c) => c.id !== cardId)
        }
        // Update wallet if refunded
        if (response.data?.wallet) {
          walletStore.syncWallet(response.data.wallet)
        }
        this.showToast('Pengeluaran berhasil dihapus', 'info')
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Gagal menghapus pengeluaran'
        this.showToast(errorMsg, 'error')
      }
    },

    /**
     * Move card with Optimistic UI & Automatic Rollback on failure.
     */
    async moveCardOptimistic({
      cardId,
      sourceColumnId,
      targetColumnId,
      newPosition,
      previousColumnsSnapshot,
      previousWalletsSnapshot,
    }) {
      const walletStore = useWalletStore()

      const sourceCol = previousColumnsSnapshot.find((c) => c.id === sourceColumnId)
      const targetCol = previousColumnsSnapshot.find((c) => c.id === targetColumnId)
      const card = sourceCol?.cards?.find((c) => c.id === cardId)

      if (!card || !sourceCol || !targetCol) return

      // Optimistic wallet balance adjustment in UI
      if (!sourceCol.deducts_balance && targetCol.deducts_balance) {
        walletStore.updateBalanceOptimistic(card.wallet, -Number(card.amount))
      } else if (sourceCol.deducts_balance && !targetCol.deducts_balance) {
        walletStore.updateBalanceOptimistic(card.wallet, Number(card.amount))
      }

      try {
        const response = await apiClient.patch(`/expenses/${cardId}/move/`, {
          target_column_id: targetColumnId,
          new_position: newPosition,
        })

        const { card: updatedCard, wallet: updatedWallet } = response.data

        // Confirm updated card in the column
        const targetInState = this.columns.find((c) => c.id === targetColumnId)
        if (targetInState) {
          const cardIdx = targetInState.cards.findIndex((c) => c.id === cardId)
          if (cardIdx !== -1) {
            targetInState.cards[cardIdx] = updatedCard
          }
        }

        // Sync confirmed wallet balance
        if (updatedWallet) {
          walletStore.syncWallet(updatedWallet)
        }
      } catch (err) {
        console.warn('Move card failed, performing rollback:', err)

        // 1. Rollback columns & cards
        this.columns = JSON.parse(JSON.stringify(previousColumnsSnapshot))

        // 2. Rollback wallets balance
        walletStore.setWalletsState(previousWalletsSnapshot)

        // 3. Extract and display meaningful error notification
        const errDetail =
          err.response?.data?.balance ||
          err.response?.data?.detail ||
          'Gagal memindahkan kartu. Periksa sisa saldo atau koneksi Anda.'

        this.showToast(errDetail, 'error')
      }
    },
  },
})
